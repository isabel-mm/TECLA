"""
TECLA – Hybrid Term Extractor
----------------------------

Hybrid terminology extractor implementing:
1) Linguistic filtering (unithood)
2) Statistical weighting (termhood)
3) Consolidation into terminological units

The output is a clean terminological inventory
(one row per term).
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import csv
import re
from collections import defaultdict, Counter

from tqdm import tqdm

from .linguistic_filter import extract_candidates
from .statistical_filter import compute_statistics
from .tbx_export import export_tbx
from .stop_terms import _fold, is_stop_term


TermLength = Union[int, Tuple[int, Optional[int]]]



SUPPORTED_LANGUAGES = {"en", "es"}

# Abbreviations with a full stop: one to three letters ("p.", "ej.", "cf.").
_ABBREVIATION_RE = re.compile(r"^[^\W\d_]{1,3}\.$")
# Well-formed Roman numerals ("XVII", "IV"); "XML" or "LDC" do not match.
_ROMAN_RE = re.compile(
    r"^(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)
# Words of bibliographic references and citations.
_CITATION_TOKENS = frozenset({
    "cf", "op", "cit", "ibid", "ibidem", "id", "et", "al", "vs", "pp",
    "vol", "vols", "ed", "eds", "trad", "coord", "coords", "apud",
})
# Words that make a capitalised sequence the name of a resource rather than
# of a person ("British National Corpus", "Penn Treebank").
_RESOURCE_WORDS = frozenset({
    "corpus", "corpora", "bank", "treebank", "database", "dictionary",
    "diccionario", "project", "proyecto", "toolkit", "tools", "net",
    "wordnet", "consortium", "archive", "archivo", "atlas", "base",
})
_YEAR_RE = re.compile(r"^(1[5-9]|20)\d\d[a-z]?$")
_INITIAL_RE = re.compile(r"^(?:[A-ZÁÉÍÓÚÑ]\.?|Ma\.?|Mª)$")
_NAME_PARTICLES = frozenset({"de", "del", "la", "van", "von", "y", "and", "&", "da", "di"})

def display_variants(term: Dict[str, Any]) -> List[str]:
    """
    Surface forms to show next to a candidate that is displayed by its lemma.

    A candidate is listed by its lemma, while ``term`` holds its most frequent
    surface form and ``variants`` the remaining ones. The forms worth showing
    are therefore all the surface forms except the one already displayed: the
    lemma itself is dropped, so that a candidate is never its own variant.
    """
    shown = term.get("lemma") or term.get("term", "")
    forms: List[str] = []
    for form in [term.get("term", "")] + list(term.get("variants", [])):
        if form and form != shown and form not in forms:
            forms.append(form)
    return forms


def _strip_accents(text: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


_INVARIABLE_ENDINGS = ("us", "is", "ss", "xis")   # corpus, análisis, class, sintaxis


def _fold_word(word: str, language: str, modifier: bool) -> str:
    """Accent-free, lower-case word without number (and, for Spanish
    modifiers, without gender), used only to compare lemmas."""
    w = _strip_accents(word.lower())
    if len(w) > 3 and not w.endswith(_INVARIABLE_ENDINGS):
        if w.endswith("s"):
            w = w[:-1]
    # -es tras consonante (unidad-es, accion-es, red-es): se quita la -e también
    # en singular (nombre / nombres → nombr), para que las dos formas coincidan;
    # no tras s (base / bases, clase / clases)
    if language == "es" and w.endswith("e") and len(w) > 3 and w[-2] in "dlnrjyz":
        w = w[:-1]
    if language == "es" and modifier and len(w) > 3 and w[-1] in "ao":
        w = w[:-1] + "o"
    return w


def lemma_key(lemma: str, language: str = "es") -> str:
    """
    Key that groups the lemmas of one and the same candidate when the
    lemmatiser assigns them inconsistently: differences in accents, in number
    or, in Spanish, in the gender of the modifiers (*unidad terminológica* /
    *unidad terminológico*, *ficha terminológica* / *ficha terminologica*).
    In Spanish the head noun comes first, so only the following words are
    gender-normalised; in English, only number is.
    """
    words = lemma.split()
    return " ".join(_fold_word(w, language, modifier=(language == "es" and i > 0))
                    for i, w in enumerate(words))


_IRREGULAR_PLURALS = {"corpus": {"corpora", "corpuses"}, "datum": {"data"},
                      "analysis": {"analyses"}, "index": {"indices", "indexes"},
                      "criterion": {"criteria"}, "phenomenon": {"phenomena"},
                      "thesis": {"theses"}, "hypothesis": {"hypotheses"}}


def _is_plural_of(word: str, base: str) -> bool:
    """Whether ``word`` is a regular (Spanish or English) plural of ``base``."""
    w, b = _strip_accents(word.lower()), _strip_accents(base.lower())
    if w == b:
        return False
    if w in _IRREGULAR_PLURALS.get(b, ()):
        return True
    return w in {b + "s", b + "es", b[:-1] + "ces", b[:-1] + "ies"}


def classify_variant(lemma: str, form: str) -> str:
    """
    Kind of variant a surface form is with respect to the candidate's lemma:
    ``plural``, ``mayúscula inicial``, ``mayúsculas``, ``ortográfica`` (hyphen
    or spacing) or ``otra`` (any other form, worth showing as it is).
    Several kinds can combine (a plural in capitals counts as both); the
    returned value is a «+»-joined label, e.g. ``plural+mayúsculas``.
    """
    kinds = []
    if form.isupper() and not lemma.isupper():
        kinds.append("mayúsculas")
    elif form[:1].isupper() and not lemma[:1].isupper():
        kinds.append("mayúscula inicial")
    lw, fw = lemma.lower().split(), form.lower().split()
    if lw == fw:
        return "+".join(kinds) or "otra"
    if len(lw) == len(fw) and all(a == b or _is_plural_of(b, a) for a, b in zip(lw, fw)):
        return "+".join(["plural"] + kinds)
    norm = lambda s: s.lower().replace("-", " ").replace("‐", " ").split()
    if norm(lemma) == norm(form):
        return "+".join(["ortográfica"] + kinds)
    if _strip_accents(lemma.lower()) == _strip_accents(form.lower()):
        return "+".join(["sin tilde"] + kinds)
    return "otra"


def surface_forms(term: Dict[str, Any]) -> List[str]:
    """All the surface forms of a candidate, most frequent first."""
    forms: List[str] = []
    for form in [term.get("term", "")] + list(term.get("variants", [])):
        if form and form not in forms:
            forms.append(form)
    freq = term.get("surface_freq") or {}
    return sorted(forms, key=lambda f: -freq.get(f, 0)) if freq else forms


def _is_plural_form(lemma: str, form: str) -> bool:
    """Whether ``form`` is a plural of the candidate: its head noun (the first
    word in Spanish, the last one in English) is a plural of the lemma's."""
    lw, fw = lemma.lower().split(), form.lower().split()
    if not lw or len(lw) != len(fw):
        return False
    return _is_plural_of(fw[0], lw[0]) or _is_plural_of(fw[-1], lw[-1])


def display_form(term: Dict[str, Any]) -> str:
    """
    Form under which a candidate is shown: the most frequent form attested in
    the texts, preferably in the singular and in lower case. The lemma joins
    the base forms of each word and can break agreement (*ficha terminológico*)
    or the term itself (*base de dato*), so it is kept only to group the forms.
    """
    lemma = term.get("lemma") or term.get("term", "")
    forms = surface_forms(term)
    if not forms:
        return lemma
    freq = term.get("surface_freq") or {}
    groups: Dict[str, List[str]] = {}
    for f in forms:
        groups.setdefault(f.lower(), []).append(f)
    total = lambda k: sum(freq.get(f, 0) for f in groups[k])
    keys = list(groups)                      # ya en orden de frecuencia
    singular = [k for k in keys if not _is_plural_form(lemma, k)]
    top = max(keys, key=lambda k: (total(k), -keys.index(k)))
    # el singular solo se prefiere si se usa de verdad (no *datum* frente a *data*)
    sing = max(singular, key=lambda k: (total(k), -keys.index(k))) if singular else None
    best = sing if sing and (not freq or total(sing) >= 0.2 * total(top)) else top
    lower = [f for f in groups[best] if f == f.lower()]
    return lower[0] if lower else groups[best][0]


def describe_variants(term: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summary of a candidate's variants for display: the kinds that occur
    (plural, initial capital, all capitals, orthographic) and the forms that
    are not a predictable variant of the displayed form, worth listing.
    """
    base = display_form(term)
    kinds, others = [], []
    for form in [f for f in surface_forms(term) if f != base]:
        label = classify_variant(base, form)
        if label == "otra":
            others.append(form)
        for k in label.split("+"):
            if k != "otra" and k not in kinds:
                kinds.append(k)
    order = ["plural", "ortográfica", "sin tilde", "mayúscula inicial", "mayúsculas"]
    return {"kinds": sorted(kinds, key=order.index), "others": others}


def variants_summary(term: Dict[str, Any], short: bool = False) -> str:
    """One-line description, e.g. «También en plural y en mayúsculas · otras formas: X».
    With ``short``, a compact version for tables: «plural · mayúsculas · +1 forma»."""
    d = describe_variants(term)
    if short:
        abbr = {"plural": "plural", "ortográfica": "otra grafía", "sin tilde": "sin tilde",
                "mayúscula inicial": "mayúsc. inicial", "mayúsculas": "mayúsculas"}
        parts = [abbr[k] for k in d["kinds"]]
        if d["others"]:
            n = len(d["others"])
            parts.append(f"+{n} forma{'s' if n > 1 else ''}")
        return " · ".join(parts)
    names = {"plural": "en plural", "ortográfica": "con otra grafía (guion o espacio)",
             "sin tilde": "sin tilde",
             "mayúscula inicial": "con mayúscula inicial", "mayúsculas": "en mayúsculas"}
    parts = [names[k] for k in d["kinds"]]
    text = ""
    if parts:
        text = "También " + (parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " y " + parts[-1])
    if d["others"]:
        text += (" · " if text else "") + "Otras formas: " + ", ".join(d["others"])
    return text


class HybridTermExtractor:
    """
    Hybrid terminology extractor based on:
    - POS-based linguistic filtering
    - TF-IDF and C-value statistical weighting
    - Term-level consolidation
    """

    def __init__(
        self,
        language: str,
        grammar_path: Optional[Path] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Lengua no admitida: {language!r}. Lenguas disponibles: "
                + ", ".join(sorted(SUPPORTED_LANGUAGES))
            )
        self.language = language
        self.weights = weights or {"tfidf": 0.5, "ncvalue": 0.5}

        if grammar_path is None:
            self.grammar_path = Path(__file__).parent / "grammar.yaml"
        else:
            self.grammar_path = grammar_path

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def extract(
        self,
        documents: List[Dict[str, Any]],
        *,
        top_k: Optional[int] = None,
        percentile: Optional[float] = None,
        term_length: Optional[TermLength] = None,
        min_freq: int = 2,
        min_doc_freq: int = 1,
        max_span_tokens: int = 6,
        extra_stop_terms: Optional[List[str]] = None,
        extra_stopwords: Optional[List[str]] = None,
        output_path: Optional[Path] = None,
        tbx_output_path: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run the full hybrid extraction pipeline and return
        a consolidated terminological inventory.

        Parameters
        ----------
        documents : list of dict
            Linguistically enriched documents from corpus_to_documents().
        top_k : int, optional
            Keep only the top-k terms by terminologicity score.
        percentile : float, optional
            Keep only terms in the top N-th percentile (0–100).
        term_length : int or (int, int | None), optional
            Filter by number of tokens. E.g. (2, None) for multiword only.
        min_freq : int
            Discard terms with corpus frequency below this value (default 2).
        min_doc_freq : int
            Discard terms appearing in fewer than this many documents (default 1).
        max_span_tokens : int
            Maximum number of tokens in a candidate span (default 6).
        extra_stop_terms : list of str, optional
            User stoplist: words or phrases that must not be part of any
            candidate (matched against surface form and lemma).
        extra_stopwords : list of str, optional
            Single words that may not appear inside a candidate, such as the
            stopwords of another language present in the corpus.
        output_path : Path, optional
            If given, save results to a CSV file.
        tbx_output_path : Path, optional
            If given, save results to a TBX-Basic file (ISO 30042).
        """

        # 1. Linguistic filtering (unithood)
        candidates = extract_candidates(
            documents=documents,
            language=self.language,
            grammar_path=self.grammar_path,
            max_span_tokens=max_span_tokens,
            extra_stopwords=extra_stopwords,
        )

        if not candidates:
            return []

        # 1b. Unify lemmas assigned inconsistently to the same candidate, so
        #     that its forms are counted together in the statistics
        candidates = self._unify_lemmas(candidates)

        # 2. Statistical weighting (termhood)
        enriched = compute_statistics(
            candidates=candidates,
            documents=documents,
            weights=self.weights
        )

        # 3. Consolidation (TERM LEVEL)
        consolidated = self._consolidate_terms(enriched)

        # 4. Optional filtering by term length
        if term_length is not None:
            consolidated = self._filter_by_length(consolidated, term_length)

        if not consolidated:
            return []

        # 5. Remove tokenisation artifacts and single-document noise
        consolidated = self._filter_artifacts(consolidated)

        if not consolidated:
            return []

        # 5b. Remove names of cited authors
        consolidated = self._filter_person_names(consolidated, documents)

        if not consolidated:
            return []

        # 6. Frequency / document-frequency thresholds
        if min_freq > 1 or min_doc_freq > 1:
            consolidated = [
                t for t in consolidated
                if t["frequency"] >= min_freq
                and t["doc_frequency"] >= min_doc_freq
            ]

        if not consolidated:
            return []

        # 7. Stop-term filtering
        consolidated = self._filter_stop_terms(
            consolidated, self.language, extra=extra_stop_terms
        )

        if not consolidated:
            return []

        # 8. Variant detection and grouping
        consolidated = self._group_variants(consolidated)

        # 9. Ranking
        ranked = sorted(
            consolidated,
            key=lambda x: x["terminologicity"],
            reverse=True
        )

        # 10. Optional thresholds
        ranked = self._apply_thresholds(
            ranked,
            top_k=top_k,
            percentile=percentile
        )

        # 11. Optional CSV export
        if output_path is not None:
            self._save_to_csv(ranked, output_path)

        # 12. Optional TBX export
        if tbx_output_path is not None:
            export_tbx(ranked, tbx_output_path, language=self.language)

        return ranked

    # -----------------------------------------------------------------
    # Internal utilities
    # -----------------------------------------------------------------

    @staticmethod
    def _filter_artifacts(
        terms: List[Dict[str, Any]],
        min_token_chars: int = 2,
        max_single_doc_freq: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Remove two classes of noisy candidates:

        1. Tokenisation artifacts — candidates that contain a token made
           entirely of punctuation or shorter than `min_token_chars` chars
           (e.g. "Sub -", "co -", "E -" from hyphenated words).

        2. Single-document high-frequency noise — candidates that appear
           more than `max_single_doc_freq` times but only in one document.
           These are almost always index entries, table-of-contents lines,
           or corpus metadata repeated many times in a single file.
        """
        import string
        punct = set(string.punctuation)

        cleaned = []
        for term in terms:
            # --- Artifact filter ---
            tokens = term.get("term", "").split()
            if any(
                len(t) < min_token_chars or all(c in punct for c in t)
                for t in tokens
            ):
                continue

            # --- Numbers, abbreviations and bibliographic markers ---
            # years and page numbers ("1985", "B2"), abbreviations ending
            # in a full stop ("p.", "ej.", "a. C."), Roman numerals
            # ("siglo XVII") and citation words ("cf", "op", "et al").
            if any(
                any(c.isdigit() for c in t)
                or _ABBREVIATION_RE.match(t)
                or (len(t) > 1 and _ROMAN_RE.match(t))
                or t.lower().strip(".") in _CITATION_TOKENS
                for t in tokens
            ):
                continue

            # --- Single-document noise filter ---
            if term.get("doc_frequency", 1) == 1 and term.get("frequency", 0) > max_single_doc_freq:
                continue

            cleaned.append(term)

        return cleaned

    @staticmethod
    def _cited_names(documents: List[Dict[str, Any]]) -> set:
        """
        Collect the capitalised words that occur in author-year citations
        ("Casas Gómez (2006)", "(Calero Fernández, 1999)", "Coseriu 1977"):
        the run of capitalised tokens immediately before a year, allowing
        an opening parenthesis, a comma or "et al." in between.
        """
        names: set = set()
        for doc in documents:
            sentences = doc.get("sentences") or [doc.get("tokens", [])]
            for sent in sentences:
                texts = [tok.get("text", "") for tok in sent]
                for i, t in enumerate(texts):
                    if not _YEAR_RE.match(t):
                        continue
                    j = i - 1
                    while j >= 0 and texts[j] in {"(", ",", "al", "al.", "et", "."}:
                        j -= 1
                    run = []
                    while j >= 0:
                        w = texts[j]
                        if w[:1].isupper() or _INITIAL_RE.match(w):
                            run.append(w)
                        elif w.lower() in _NAME_PARTICLES and run:
                            pass
                        else:
                            break
                        j -= 1
                    # an acronym alone (BNC, CREA) is not a personal name
                    if run and not (len(run) == 1 and run[0].isupper()):
                        names.update(w for w in run if not _INITIAL_RE.match(w))
        return names

    def _filter_person_names(
        self,
        terms: List[Dict[str, Any]],
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove candidates that are names of cited authors: sequences made
        only of capitalised words and initials whose last word occurs in an
        author-year citation in the corpus ("Casas Gómez", "M. Casas Gómez",
        "Ángeles Calero"). Acronyms and names of resources ("British
        National Corpus") are kept.
        """
        names = self._cited_names(documents)
        if not names:
            return terms

        def _is_person(term: Dict[str, Any]) -> bool:
            tokens = [t for t in term["term"].split() if t.lower() not in _NAME_PARTICLES]
            if not tokens:
                return False
            if any(not (t[:1].isupper() or _INITIAL_RE.match(t)) for t in tokens):
                return False
            if any(t.isupper() and len(t) > 1 for t in tokens):
                return False
            if any(t.lower() in _RESOURCE_WORDS for t in tokens):
                return False
            words = [t for t in tokens if not _INITIAL_RE.match(t)]
            return bool(words) and words[-1] in names

        return [t for t in terms if not _is_person(t)]

    def _filter_stop_terms(
        self,
        terms: List[Dict[str, Any]],
        language: str,
        extra: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Remove candidates whose lemma matches the stop-term list for the
        given language.  Stop-terms are generic academic/methodological
        phrases that pass POS filters but do not designate domain concepts.

        Entries in *extra* (the user stoplist) are stricter: a candidate is
        removed when it contains the entry as a whole word or word sequence,
        either in its surface form or in its lemma.
        """
        extra_seqs = [
            tuple(_fold(entry).split()) for entry in (extra or []) if entry.strip()
        ]

        def _contains_extra(term: Dict[str, Any]) -> bool:
            for form in (term["term"], term.get("lemma", "")):
                tokens = tuple(_fold(form).split())
                for seq in extra_seqs:
                    n = len(seq)
                    if any(tokens[i:i + n] == seq for i in range(len(tokens) - n + 1)):
                        return True
            return False

        return [
            t for t in terms
            if not is_stop_term(t.get("lemma", t["term"]), language)
            # the surface form too: the lemmatiser may alter gender or
            # number ("buena parte" -> "buen parte")
            and not is_stop_term(t["term"], language)
            and not _contains_extra(t)
        ]

    @staticmethod
    def _group_variants(
        terms: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Detect terminological variants and annotate each term with a
        ``variants`` list (other surface forms of the same concept).

        Two types of variants are detected:

        1. **Orthographic variants** — forms that differ only in
           hyphenation or capitalisation, e.g. "machine learning" /
           "machine-learning" / "Machine Learning".  The canonical entry
           is the one with the highest terminologicity score; the rest are
           merged into it and removed from the list.

        2. **Acronyms** — a short ALL-CAPS token (2–5 chars) whose letters
           match the initials of a longer term, e.g. "NLP" ↔
           "natural language processing".  Both forms are kept as separate
           entries; each receives the other as a variant.
        """
        import re

        # ── 1. Orthographic grouping ──────────────────────────────────────
        def _ortho_key(surface: str) -> str:
            """Normalise to lower-case, hyphens → spaces, collapse spaces."""
            return re.sub(r"\s+", " ", surface.lower().replace("-", " ")).strip()

        ortho_buckets: Dict[str, List[int]] = defaultdict(list)
        for idx, t in enumerate(terms):
            ortho_buckets[_ortho_key(t["term"])].append(idx)

        keep_indices: set = set()
        for indices in ortho_buckets.values():
            if len(indices) == 1:
                keep_indices.add(indices[0])
                continue
            # Canonical = highest terminologicity
            canonical_idx = max(indices, key=lambda i: terms[i]["terminologicity"])
            variant_surfaces = [
                terms[i]["term"] for i in indices if i != canonical_idx
            ]
            terms[canonical_idx].setdefault("variants", [])
            terms[canonical_idx]["variants"].extend(variant_surfaces)
            keep_indices.add(canonical_idx)

        terms = [t for i, t in enumerate(terms) if i in keep_indices]

        # Ensure every term has a variants list
        for t in terms:
            t.setdefault("variants", [])

        # ── 2. Acronym linking ────────────────────────────────────────────
        _ACRONYM_RE = re.compile(r"^[A-ZÁÉÍÓÚÑ]{2,5}$")

        acronyms   = {t["term"]: t for t in terms if _ACRONYM_RE.match(t["term"])}
        multiwords = [t for t in terms if not _ACRONYM_RE.match(t["term"])]

        for acro, acro_term in acronyms.items():
            for mw_term in multiwords:
                initials = "".join(
                    w[0].upper()
                    for w in mw_term["lemma"].split()
                    if w
                )
                if initials == acro:
                    # Cross-reference both ways
                    if acro not in mw_term["variants"]:
                        mw_term["variants"].append(acro)
                    if mw_term["term"] not in acro_term["variants"]:
                        acro_term["variants"].append(mw_term["term"])

        return terms

    def _unify_lemmas(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Give the same lemma (the most frequent one of the group) to every
        occurrence whose lemma has the same :func:`lemma_key`."""
        groups: Dict[str, Counter] = defaultdict(Counter)
        for c in candidates:
            groups[lemma_key(c["lemma"], self.language)][c["lemma"]] += 1
        canonical = {key: cnt.most_common(1)[0][0] for key, cnt in groups.items()}
        for c in candidates:
            c["lemma"] = canonical[lemma_key(c["lemma"], self.language)]
        return candidates

    @staticmethod
    def _consolidate_terms(
        occurrences: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate occurrences into terminological units.
        """

        buckets = defaultdict(list)

        for occ in occurrences:
            key = occ.get("lemma") or occ["term"]
            buckets[key].append(occ)

        terms = []

        for lemma, occs in tqdm(
            buckets.items(),
            desc="Consolidating terms",
            unit="term"
        ):
            # Count frequency per surface form; pick the most frequent as canonical.
            # All other distinct surfaces become orthographic pre-variants.
            surf_freq: Counter = Counter(o["term"] for o in occs)
            term_surface = surf_freq.most_common(1)[0][0]
            pre_variants = [s for s in surf_freq if s != term_surface]

            # Todas las apariciones de un mismo lema llevan el mismo recuento por
            # documento (el del lema): se toma una vez, no una por aparición.
            merged_per_doc: Counter = Counter(occs[0].get("per_doc", {}))

            def _avg(field: str) -> float:
                return sum(o.get(field, 0.0) for o in occs) / len(occs)

            terms.append({
                "term": term_surface,
                "lemma": lemma,
                "language": occs[0]["language"],
                "length": occs[0]["length"],
                "frequency": occs[0]["frequency"],
                "doc_frequency": occs[0]["doc_frequency"],
                "freq_rel": _avg("freq_rel"),
                "per_doc": dict(merged_per_doc),
                "patterns": sorted({o["pattern_id"] for o in occs}),
                "tf_idf": _avg("tf_idf"),
                "c_value": _avg("c_value"),
                "nc_value": _avg("nc_value"),
                "tf_idf_norm": _avg("tf_idf_norm"),
                "c_value_norm": _avg("c_value_norm"),
                "nc_value_norm": _avg("nc_value_norm"),
                "terminologicity": _avg("terminologicity"),
                "variants": pre_variants,
                "surface_freq": dict(surf_freq),
            })

        return terms

    @staticmethod
    def _filter_by_length(
        terms: List[Dict[str, Any]],
        term_length: TermLength
    ) -> List[Dict[str, Any]]:
        """
        Filter terms by number of tokens.
        """

        if isinstance(term_length, int):
            return [t for t in terms if t["length"] == term_length]

        min_len, max_len = term_length

        if max_len is None:
            return [t for t in terms if t["length"] >= min_len]

        return [
            t for t in terms
            if min_len <= t["length"] <= max_len
        ]

    @staticmethod
    def _apply_thresholds(
        ranked: List[Dict[str, Any]],
        *,
        top_k: Optional[int],
        percentile: Optional[float]
    ) -> List[Dict[str, Any]]:

        if top_k is not None and percentile is not None:
            raise ValueError("Use either top_k or percentile, not both.")

        if percentile is not None:
            cutoff = int(len(ranked) * (percentile / 100))
            cutoff = max(cutoff, 1)
            return ranked[:cutoff]

        if top_k is not None:
            return ranked[:top_k]

        return ranked

    @staticmethod
    def _save_to_csv(
        results: List[Dict[str, Any]],
        output_path: Path
    ) -> None:
        """
        Save consolidated terminological inventory to CSV.
        """

        if not results:
            return

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "term",
            "lemma",
            "variants",
            "language",
            "length",
            "frequency",
            "freq_rel",
            "doc_frequency",
            "patterns",
            "tf_idf",
            "c_value",
            "nc_value",
            "tf_idf_norm",
            "c_value_norm",
            "nc_value_norm",
            "terminologicity",
        ]

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()

            for row in tqdm(results, desc="Writing CSV", unit="term"):
                row = row.copy()
                row["patterns"] = ";".join(row.get("patterns", []))
                row["variants"] = ";".join(row.get("variants", []))
                writer.writerow(row)
