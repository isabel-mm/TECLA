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
# MODEL SELECTION TABLE
# ---------------------------------------------------------------------------

# Mapping TECLA languages to their appropriate spaCy models
SPACY_MODEL_TABLE = {
    "en": "en_core_web_sm",      # English uses 'web'
    "es": "es_core_news_sm",     # Spanish uses 'news'
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}

_SPACY_MODELS = {}


# ---------------------------------------------------------------------------
# LAZY SPACY MODEL LOADING
# ---------------------------------------------------------------------------

def _get_spacy_model(language):
    """
    Load a spaCy model for the given language.

    Behavior:
    1. Try to load the appropriate model from SPACY_MODEL_TABLE.
    2. If missing, automatically download it.
    3. If download fails (no internet), fallback to a blank model.

    This ensures TECLA NEVER crashes because of unavailable spaCy models.
    """

    import spacy.cli

    lang = language.lower()
    model_name = SPACY_MODEL_TABLE.get(lang)

    if not model_name:
        # Unsupported language → fallback immediately
        print(
            f"⚠️ No spaCy model defined for language '{language}'. "
            f"Using 'spacy.blank(\"{language}\")' as fallback."
        )
        nlp = spacy.blank(language)
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp

    # Return cached model if already loaded
    if model_name in _SPACY_MODELS:
        return _SPACY_MODELS[model_name]

    # 1. Try loading the model directly
    try:
        nlp = spacy.load(model_name)
        _SPACY_MODELS[model_name] = nlp
        return nlp

    except OSError:
        print(f"⚠️ spaCy model '{model_name}' not found. Attempting download...")

        # 2. Download model automatically
        try:
            spacy.cli.download(model_name)
            print(f"✅ Model '{model_name}' downloaded successfully.")
            nlp = spacy.load(model_name)
            _SPACY_MODELS[model_name] = nlp
            return nlp

        except Exception:
            # 3. Final fallback
            print(
                f"⚠️ Could not download '{model_name}'. "
                f"Using a minimal model 'spacy.blank(\"{language}\")'."
            )
            nlp = spacy.blank(language)
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
    Apply light structural cleaning:
    - remove short lines (< 3 words),
    - remove lines consisting solely of page numbers.
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
    Examples: "12", "(3)", "- 4 -", "• 15", etc.
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
        r'\n\s*(?:REFERENCIAS\s+BIBLIOGR[ÁA]FICAS|BIBLIOGRAF[ÍI]A(?:\s+CITADA|\s+REFERENCIADA)?)\s*\n'
    ]
    reference_patterns = [
        r'\n\s*\d+\.\s+.+',
        r'\n\s*\[\d+\]\s+.+',
        r'\n\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+,\s[A-Z]\.\s*\(?\d{4}\)?',
        r'\n\s*https?://',
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
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in stoplist]
    return " ".join(filtered)


def lemmatize_text(text, language="en"):
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
    """
    cleaned = text

    # --- bibliography removal ------------------------------------------------
    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    # --- structural cleaning --------------------------------------------------
    if structure:
        cleaned = clean_structure(cleaned)

    # --- stopword removal -----------------------------------------------------
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
