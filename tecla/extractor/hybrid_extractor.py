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
from collections import defaultdict, Counter

from tqdm import tqdm

from .linguistic_filter import extract_candidates
from .statistical_filter import compute_statistics
from .tbx_export import export_tbx
from .stop_terms import is_stop_term


TermLength = Union[int, Tuple[int, Optional[int]]]



SUPPORTED_LANGUAGES = {"en", "es"}

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

            # --- Single-document noise filter ---
            if term.get("doc_frequency", 1) == 1 and term.get("frequency", 0) > max_single_doc_freq:
                continue

            cleaned.append(term)

        return cleaned

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
            tuple(entry.lower().split()) for entry in (extra or []) if entry.strip()
        ]

        def _contains_extra(term: Dict[str, Any]) -> bool:
            for form in (term["term"], term.get("lemma", "")):
                tokens = tuple(form.lower().split())
                for seq in extra_seqs:
                    n = len(seq)
                    if any(tokens[i:i + n] == seq for i in range(len(tokens) - n + 1)):
                        return True
            return False

        return [
            t for t in terms
            if not is_stop_term(t.get("lemma", t["term"]), language)
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

            merged_per_doc: Counter = Counter()
            for o in occs:
                merged_per_doc.update(o.get("per_doc", {}))

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
