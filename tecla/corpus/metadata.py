"""
Metadata extraction utilities for TECLA's corpus module.

Infers author, year, title, text_type and source from filenames.
Works on the full filename string rather than on fixed-position
underscore segments, so it handles many real-world conventions:

    2016_Murphy, B., Riordan, E._Corpus types and uses
    Murphy_2016_Corpus types and uses
    Murphy_Jones_2016_terminology extraction
    2016_corpus_linguistics
    some_paper_without_year_or_author
    Murphy2016CorpusTypes          (no separators)
    Murphy - 2016 - Corpus types   (hyphen-separated)
"""

import re
import os


# ── Year ──────────────────────────────────────────────────────────────────────
_YEAR_RE_STR = re.compile(r"(?<!\d)(19\d{2}|20\d{2}|21\d{2})(?!\d)")

# ── Formal author: "Surname, I." possibly repeated with & / and / , ──────────
# Matches: "Murphy, B.", "Murphy, B., Riordan, E.", "Murphy, B. & Jones, A."
_AUTHOR_FORMAL_RE = re.compile(
    r"[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\-]+(?:,\s*[A-Z]\.)+"
    r"(?:\s*(?:,|&|and)\s*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\-]+(?:,\s*[A-Z]\.)+)*"
)

# ── Simple surname: single capitalised word (used as fallback) ────────────────
_SURNAME_RE = re.compile(r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:-[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?$")

# Words that look capitalised but are almost certainly title / domain words,
# not personal surnames.
_NOT_A_SURNAME = frozenset({
    "Corpus", "Language", "Languages", "Linguistic", "Linguistics",
    "Text", "Texts", "Grammar", "Grammars", "Syntax", "Semantics",
    "Discourse", "Pragmatics", "Terminology", "Terminological",
    "Lexicon", "Lexical", "Morphology", "Phonology", "Phonetics",
    "Translation", "Annotation", "Analysis", "Research", "Study",
    "Studies", "Review", "Survey", "Introduction", "Handbook",
    "Journal", "Proceedings", "Conference", "Workshop", "Symposium",
    "Thesis", "Dissertation", "Report", "Chapter", "Section",
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Chinese", "Arabic", "Japanese", "Korean", "Russian",
    "National", "International", "European", "American",
    "New", "Old", "Modern", "General", "Special", "Applied",
})

# ── Text-type keywords ────────────────────────────────────────────────────────
_TYPE_KEYWORDS: list[tuple[frozenset, str]] = [
    (frozenset({"thesis", "tesis", "dissertation", "disertación", "doctoral"}), "thesis"),
    (frozenset({"proceedings", "proc", "conference", "workshop",
                "symposium", "congreso", "jornadas"}),                          "conference_paper"),
    (frozenset({"report", "technical", "working paper",
                "informe", "reporte", "deliverable"}),                           "report"),
    (frozenset({"book", "handbook", "manual", "guide", "libro",
                "monograph", "monografía", "textbook"}),                         "book"),
    (frozenset({"chapter", "capítulo"}),                                         "book_chapter"),
]

# ── Known short source codes (single-segment match) ──────────────────────────
_KNOWN_SOURCES: dict[str, str] = {
    "ICAME":       "ICAME Journal",
    "Corpora":     "Corpora",
    "IJCL":        "International Journal of Corpus Linguistics",
    "CLLT":        "Corpus Linguistics and Linguistic Theory",
    "Terminology": "Terminology",
    "LRE":         "Language Resources and Evaluation",
    "PLN":         "Procesamiento del Lenguaje Natural",
    "LREC":        "LREC",
    "ACL":         "ACL Anthology",
    "EMNLP":       "EMNLP",
    "COLING":      "COLING",
    "EACL":        "EACL",
    "NAACL":       "NAACL",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_name(name: str) -> str:
    """Normalise the filename stem for further processing."""
    # Replace common separator sequences with a single underscore
    # but preserve commas and periods (used in author initials)
    s = re.sub(r"\s*-\s*", "_", name)   # "Murphy - 2016" → "Murphy_2016"
    s = re.sub(r"_+", "_", s)           # collapse multiple underscores
    return s.strip("_")


def _infer_text_type(title: str | None, source: str | None) -> str:
    if source:
        return "article"
    if not title:
        return "unknown"
    lower = title.lower()
    for keywords, ttype in _TYPE_KEYWORDS:
        if any(kw in lower for kw in keywords):
            return ttype
    return "unknown"


def _extract_formal_author(text: str) -> str | None:
    """Return the first formal-author match in text, or None."""
    m = _AUTHOR_FORMAL_RE.search(text)
    return m.group(0).strip().rstrip(",") if m else None


def _looks_like_surname(word: str) -> bool:
    return (
        bool(_SURNAME_RE.fullmatch(word))
        and word not in _NOT_A_SURNAME
        and not word.isupper()          # avoid acronyms
    )


def _build_title(raw: str) -> str | None:
    """Clean up a raw title string extracted from a filename."""
    t = raw.replace("_", " ").strip(" ,.-")
    t = re.sub(r"\s+", " ", t).strip()
    return t or None


def infer_metadata(filename: str) -> dict:
    """
    Infer metadata (author, year, title, text_type, source) from a filename.

    Strategy
    --------
    1. Find the year anywhere in the string.
    2. Split the name into pre-year and post-year halves.
    3. Look for a formal author pattern ("Surname, I.") in the full name.
    4. If none found, check whether the pre-year part looks like a surname.
    5. The post-year part (minus author if found there) becomes the title.
    6. If there is no year, try to find a formal author anywhere; the rest
       is the title.
    7. Detect text_type from title keywords and source from known codes.

    Falls back gracefully: any field that cannot be reliably inferred is
    returned as None rather than guessed wrongly.
    """
    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]
    name = _clean_name(name)

    # ── 1. Find year ──────────────────────────────────────────────────────
    year_match = _YEAR_RE_STR.search(name)
    year       = int(year_match.group(1)) if year_match else None

    # ── 2. Split around year ──────────────────────────────────────────────
    if year_match:
        pre  = name[:year_match.start()].strip("_").strip()
        post = name[year_match.end():].strip("_").strip()
    else:
        pre  = name
        post = ""

    # ── 3. Find formal author in the whole name ───────────────────────────
    author = _extract_formal_author(name)

    # ── 4. If no formal author, check pre-year for a simple surname ───────
    if author is None and pre:
        # pre may be "Murphy" or "Murphy_Jones" or "Murphy_B"
        pre_parts = [p.strip() for p in pre.split("_") if p.strip()]
        # Take consecutive surname-looking words (at most 3, to allow
        # "García López" but not swallow a whole title)
        surname_parts = []
        for p in pre_parts:
            if _looks_like_surname(p):
                surname_parts.append(p)
            else:
                break           # stop at first non-surname word
        if surname_parts:
            author = " ".join(surname_parts)
            # Remove matched surname parts from pre so they don't end up in title
            for sp in surname_parts:
                pre = re.sub(r"(?<![A-Za-z])" + re.escape(sp) + r"(?![A-Za-z])", "", pre, count=1)
            pre = pre.strip("_").strip()

    # ── 5. Build title from post-year, with pre-year leftovers if any ─────
    # If the author appears AFTER the year (e.g. year-first convention),
    # remove it from post so it doesn't bleed into the title.
    title_raw = post
    if author:
        title_raw = title_raw.replace(author, "", 1).strip("_").strip()

    # If there's still stuff in pre (year-last convention or no year),
    # prepend it to the title
    if pre and pre != author:
        leftover_pre = pre.replace(author or "", "", 1).strip("_").strip() if author else pre
        if leftover_pre:
            title_raw = (leftover_pre + " " + title_raw).strip()

    title = _build_title(title_raw)

    # ── 6. If no year at all, author may be anywhere — try again ─────────
    if year is None and author is None:
        # Everything is title; try formal author heuristic one more time
        author = _extract_formal_author(name)
        if author:
            leftover = name.replace(author, "", 1)
        else:
            leftover = name
        title = _build_title(leftover)

    # ── 7. Source detection (single underscore segment = known code) ──────
    source = None
    for seg in name.split("_"):
        seg = seg.strip()
        if seg in _KNOWN_SOURCES:
            source = _KNOWN_SOURCES[seg]
            if title:
                title = title.replace(seg, "").strip(" ,._-") or title
            break

    text_type = _infer_text_type(title, source)

    return {
        "author":    author or None,
        "year":      year,
        "title":     title,
        "text_type": text_type,
        "source":    source,
    }
