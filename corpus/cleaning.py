"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.

This module offers:
- structural cleaning (optional),
- bibliography removal based on language (optional),
- stopword removal (optional),
- user-defined stoplist filtering (optional),
- lemmatisation via spaCy (optional).

All operations are explicit: nothing is applied automatically.
This guarantees methodological transparency and reproducibility.
"""

import re
import spacy
from .utils import load_stoplist


# ---------------------------------------------------------------------------
# LAZY SPACY MODEL LOADING
# ---------------------------------------------------------------------------

_SPACY_MODELS = {}


def _get_spacy_model(language):
    """
    Lazy loader for spaCy language models.
    Ensures that models are loaded only once.

    Parameters:
        language (str): Language code ("en", "es", ...).

    Returns:
        nlp: spaCy model.

    Raises:
        RuntimeError: If the language model is not installed.
    """
    if language not in _SPACY_MODELS:
        try:
            _SPACY_MODELS[language] = spacy.load(f"{language}_core_web_sm")
        except Exception:
            raise RuntimeError(
                f"spaCy model for '{language}' could not be loaded. "
                f"Install it via: python -m spacy download {language}_core_web_sm"
            )
    return _SPACY_MODELS[language]


# ---------------------------------------------------------------------------
# STRUCTURAL CLEANING
# ---------------------------------------------------------------------------

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$")


def clean_structure(text, remove_short_lines=True, remove_page_numbers=True):
    """
    Apply light structural cleaning to raw text:
    - remove short lines (< 3 words),
    - remove lines that consist solely of page numbers.

    Parameters:
        text (str): Raw text.
        remove_short_lines (bool): Enables removal of short lines.
        remove_page_numbers (bool): Enables removal of page-number-like lines.

    Returns:
        str: Structurally cleaned text.
    """
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if remove_page_numbers and PAGE_NUMBER_LINE.fullmatch(stripped):
            continue

        if remove_short_lines and len(stripped.split()) < 3:
            continue

        cleaned.append(stripped)

    return "\n".join(cleaned)


def remove_numeric_only_lines(text):
    """
    Remove lines that consist exclusively of numbers or numeric markers:
    e.g., "12", "(3)", "- 4 -", "• 15", etc.

    Parameters:
        text (str)

    Returns:
        str: Text without numeric-only lines.
    """
    pattern = r'^\s*[\(\[\{\-–—\*•●"]*\s*\d+\s*[\)\]\}\-–—\*•●"."]*\s*$'
    filtered = [
        line for line in text.splitlines()
        if not re.fullmatch(pattern, line)
    ]
    return "\n".join(filtered)


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY REMOVAL (MULTILINGUAL)
# ---------------------------------------------------------------------------

def _remove_bibliography_generic(text, section_titles, reference_patterns):
    """
    Internal helper for removing bibliography sections based on:
    - detection of bibliography header,
    - confirmation via citation-like patterns in the following text.

    Parameters:
        text (str)
        section_titles (list[str])
        reference_patterns (list[str])

    Returns:
        str
    """
    for title in section_titles:
        match = re.search(title, text, flags=re.IGNORECASE)
        if match:
            start_pos = match.start()
            remaining = text[start_pos:]

            for pattern in reference_patterns:
                if re.search(pattern, remaining):
                    return text[:start_pos].strip()
    return text


# --- Spanish ----------------------------------------------------------------
def remove_bibliography_es(text):
    section_titles = [
        r'\n\s*(?:REFERENCIAS\s+BIBLIOGR[ÁA]FICAS|BIBLIOGRAF[ÍI]A(?:\s+CITADA|\s+REFERENCIADA)?)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*\[\d+\]\s+.+',
        r'\n\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
        r'\n\s*[—\-]\s.+',
        r'\n\s*[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ]+.*\d{4}',
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- English ----------------------------------------------------------------
def remove_bibliography_en(text):
    section_titles = [
        r'\n\s*(?:REFERENCES|BIBLIOGRAPHY|WORKS\s+CITED)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*\[\d+\]\s+.+',
        r'\n\s*[A-Z][a-z]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
        r'\n\s*[—\-]\s.+',
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- German -----------------------------------------------------------------
def remove_bibliography_de(text):
    section_titles = [
        r'\n\s*(?:LITERATUR|QUELLENVERZEICHNIS|BIBLIOGRAPHIE)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*[A-Z][a-zäöüß]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://'
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- French -----------------------------------------------------------------
def remove_bibliography_fr(text):
    section_titles = [
        r'\n\s*(?:RÉFÉRENCES|BIBLIOGRAPHIE|TRAVAUX\s+CITÉS)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*[A-Z][a-z]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- Italian ----------------------------------------------------------------
def remove_bibliography_it(text):
    section_titles = [
        r'\n\s*(?:BIBLIOGRAFIA|RIFERIMENTI\s+BIBLIOGRAFICI|OPERE\s+CITATE)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*[A-Z][a-z]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- Portuguese --------------------------------------------------------------
def remove_bibliography_pt(text):
    section_titles = [
        r'\n\s*(?:REFERÊNCIAS|BIBLIOGRAFIA|OBRAS\s+CITADAS)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*[A-Z][a-z]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


def remove_bibliography(text, language="en"):
    """
    Dispatcher for bibliography removal by language.

    Parameters:
        text (str)
        language (str): 'en', 'es', 'de', 'fr', 'it', 'pt'

    Returns:
        str
    """
    lang = language.lower()

    if lang == "es":
        return remove_bibliography_es(text)
    if lang == "en":
        return remove_bibliography_en(text)
    if lang == "de":
        return remove_bibliography_de(text)
    if lang == "fr":
        return remove_bibliography_fr(text)
    if lang == "it":
        return remove_bibliography_it(text)
    if lang == "pt":
        return remove_bibliography_pt(text)

    return text  # unsupported language -> return unchanged


# ---------------------------------------------------------------------------
# LINGUISTIC CLEANING
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    """
    Remove stopwords from the text.

    Parameters:
        text (str)
        stopwords (set[str])

    Returns:
        str
    """
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in stopwords]
    return " ".join(filtered)


def apply_user_stoplist(text, stoplist):
    """
    Remove user-defined stop words.

    Parameters:
        text (str)
        stoplist (set[str])

    Returns:
        str
    """
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in stoplist]
    return " ".join(filtered)


def lemmatize_text(text, language="en"):
    """
    Lemmatises the text using spaCy.

    Parameters:
        text (str)
        language (str)

    Returns:
        str
    """
    nlp = _get_spacy_model(language)
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if token.lemma_.strip()]
    return " ".join(lemmas)


# ---------------------------------------------------------------------------
# MASTER CLEANING FUNCTION
# ---------------------------------------------------------------------------

def clean_text(
    text,
    structure=False,
    remove_stopwords_flag=False,
    stoplist=None,
    lemmatize_flag=False,
    remove_bibliography_flag=False,
    language="en",
):
    """
    High-level cleaning function used optionally within TECLA's corpus builder.

    Parameters:
        text (str)
        structure (bool): Apply structural cleaning.
        remove_stopwords_flag (bool): Remove spaCy default stopwords.
        stoplist (str or list or None): User-defined stoplist.
        lemmatize_flag (bool): Apply spaCy lemmatisation.
        remove_bibliography_flag (bool): Remove bibliography section.
        language (str): Language code.

    Returns:
        str: Fully cleaned or partially cleaned text.
    """
    cleaned = text

    # --- bibliography removal ------------------------------------------------
    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    # --- structural cleaning --------------------------------------------------
    if structure:
        cleaned = clean_structure(cleaned)

    # --- stopwords ------------------------------------------------------------
    if remove_stopwords_flag:
        nlp = _get_spacy_model(language)
        default_stopwords = {w.lower() for w in nlp.Defaults.stop_words}
        cleaned = remove_stopwords(cleaned, default_stopwords)

    # --- user stoplist --------------------------------------------------------
    if stoplist:
        user_stop = load_stoplist(stoplist)
        cleaned = apply_user_stoplist(cleaned, user_stop)

    # --- lemmatisation --------------------------------------------------------
    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
