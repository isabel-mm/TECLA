"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.

This module offers:
- structural cleaning (optional),
- bibliography removal based on language (optional),
- stopword removal (optional),
- user-defined stoplist filtering (optional),
- lemmatisation via spaCy (optional).

All operations are explicit: nothing is applied automatically.
This ensures transparency and reproducibility.
"""

import re
import spacy
from .utils import load_stoplist


# ---------------------------------------------------------------------------
# MODEL SELECTION TABLE
# ---------------------------------------------------------------------------

SPACY_MODEL_TABLE = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}

_SPACY_MODELS = {}


# ---------------------------------------------------------------------------
# LAZY SPACY MODEL LOADING (with printed status)
# ---------------------------------------------------------------------------

def _get_spacy_model(language):
    """
    Load a spaCy model for the given language.

    Behaviour:
    1. Try loading the model from SPACY_MODEL_TABLE.
    2. If missing, print a warning and attempt download.
    3. If download fails, fallback to a blank model.
    """

    import spacy.cli

    lang = language.lower()
    model_name = SPACY_MODEL_TABLE.get(lang)

    # Unsupported language → fallback
    if not model_name:
        print(f"⚠️ No spaCy model registered for '{language}'. Using blank model.")
        nlp = spacy.blank(lang)
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp

    # Cached?
    if model_name in _SPACY_MODELS:
        print(f"🔄 Using cached spaCy model: {model_name}")
        return _SPACY_MODELS[model_name]

    # Try loading the model
    print(f"🔍 Attempting to load spaCy model: {model_name}")

    try:
        nlp = spacy.load(model_name)
        print(f"✅ Loaded spaCy model: {model_name}")
        _SPACY_MODELS[model_name] = nlp
        return nlp

    except OSError:
        print(f"⚠️ spaCy model '{model_name}' not found. Attempting download...")

        try:
            spacy.cli.download(model_name)
            print(f"🎉 Download successful: {model_name}")

            nlp = spacy.load(model_name)
            _SPACY_MODELS[model_name] = nlp
            return nlp

        except Exception:
            print(
                f"❌ Download failed for '{model_name}'. "
                f"Using blank model for '{language}'."
            )
            nlp = spacy.blank(lang)
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            _SPACY_MODELS[model_name] = nlp
            return nlp


# ---------------------------------------------------------------------------
# STRUCTURAL CLEANING
# ---------------------------------------------------------------------------

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$")

def clean_structure(text, remove_short_lines=True, remove_page_numbers=True):
    """
    Remove page numbers and very short lines (<3 words).
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
    Remove lines that consist exclusively of numbers or numeric markers.
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
    Internal helper for removing bibliography sections.
    """
    for title in section_titles:
        match = re.search(title, text, flags=re.IGNORECASE)
        if match:
            start = match.start()
            remaining = text[start:]

            for pattern in reference_patterns:
                if re.search(pattern, remaining):
                    return text[:start].strip()

    return text


# --- Spanish ----------------------------------------------------------------

def remove_bibliography_es(text):
    section_titles = [
        r'\bREFERENCIAS?\s+BIBLIOGR[ÁA]FICAS?\b',
        r'\bBIBLIOGRAF[ÍI]A\b'
    ]
    reference_patterns = [
        r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s'
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- English ----------------------------------------------------------------

def remove_bibliography_en(text):
    section_titles = [
        r'\bREFERENCES\b', r'\bBIBLIOGRAPHY\b', r'\bWORKS\s+CITED\b'
    ]
    reference_patterns = [
        r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s'
    ]
    return _remove_bibliography_generic(text, section_titles, reference_patterns)


# --- German -----------------------------------------------------------------

def remove_bibliography_de(text):
    return _remove_bibliography_generic(
        text,
        [r'\bLITERATUR\b', r'\bBIBLIOGRAPHIE\b'],
        [r'\(\d{4}\)', r'https?://']
    )


# --- French -----------------------------------------------------------------

def remove_bibliography_fr(text):
    return _remove_bibliography_generic(
        text,
        [r'\bRÉFÉRENCES\b', r'\bBIBLIOGRAPHIE\b'],
        [r'\(\d{4}\)', r'https?://']
    )


# --- Italian ----------------------------------------------------------------

def remove_bibliography_it(text):
    return _remove_bibliography_generic(
        text,
        [r'\bBIBLIOGRAFIA\b'],
        [r'\(\d{4}\)', r'https?://']
    )


# --- Portuguese --------------------------------------------------------------

def remove_bibliography_pt(text):
    return _remove_bibliography_generic(
        text,
        [r'\bREFERÊNCIAS\b', r'\bBIBLIOGRAFIA\b'],
        [r'\(\d{4}\)', r'https?://']
    )


def remove_bibliography(text, language="en"):
    lang = language.lower()

    if lang == "es": return remove_bibliography_es(text)
    if lang == "en": return remove_bibliography_en(text)
    if lang == "de": return remove_bibliography_de(text)
    if lang == "fr": return remove_bibliography_fr(text)
    if lang == "it": return remove_bibliography_it(text)
    if lang == "pt": return remove_bibliography_pt(text)

    return text


# ---------------------------------------------------------------------------
# STOPWORDS, USER STOPLISTS, LEMMATISATION
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in stopwords]
    return " ".join(filtered)


def apply_user_stoplist(text, stoplist):
    stoplist = {w.lower() for w in stoplist}
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in stoplist]
    return " ".join(filtered)


def lemmatize_text(text, language="en"):
    nlp = _get_spacy_model(language)
    doc = nlp(text)

    lemmas = []
    for token in doc:
        lemma = token.lemma_.strip()
        lemmas.append(lemma if lemma else token.text)

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
    """

    cleaned = text

    # Bibliography removal
    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    # Structural cleaning
    if structure:
        cleaned = clean_structure(cleaned)

    # Stopword removal
    if remove_stopwords_flag:
        nlp = _get_spacy_model(language)
        default_stopwords = {w.lower() for w in nlp.Defaults.stop_words}
        cleaned = remove_stopwords(cleaned, default_stopwords)

    # User stoplist
    if stoplist:
        user_stop = load_stoplist(stoplist)
        cleaned = apply_user_stoplist(cleaned, user_stop)

    # Lemmatization
    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
