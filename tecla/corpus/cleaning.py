"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.

This module offers:
- structural cleaning (optional),
- bibliography removal based on language (optional),
- stopword removal (optional: spaCy + NLTK + extra list),
- user-defined stoplist filtering (optional),
- lemmatisation via spaCy (optional).

Design principles:
- Nothing is applied implicitly.
- Every operation is explicit, controlled by flags.
- Always fails gracefully (never breaks corpus building).
"""

import re
import spacy
from .utils import load_stoplist

# ---------------------------------------------------------------------------
# STOPWORD MANAGEMENT (spaCy + NLTK + user)
# ---------------------------------------------------------------------------

import nltk
from nltk.corpus import stopwords as nltk_stopwords

NLTK_LANG_MAP = {
    "es": "spanish",
    "en": "english",
    "fr": "french",
    "de": "german",
    "pt": "portuguese",
    "it": "italian",
}


def get_language_stopwords(language, extra_stoplist=None):
    """
    Returns a unified stopword set combining:
    - spaCy's default stopwords
    - NLTK stopwords (if available)
    - optional extra stoplist provided by user

    Always returns a Python set().
    """

    lang = language.lower()
    combined = set()

    # ------------------------------- spaCy STOPWORDS ---------------------------
    try:
        nlp = _get_spacy_model(lang)
        combined |= {w.lower() for w in nlp.Defaults.stop_words}
    except Exception:
        print(f"⚠️ Could not load spaCy stopwords for '{lang}'.")

    # ------------------------------- NLTK STOPWORDS ----------------------------
    nltk_lang = NLTK_LANG_MAP.get(lang)
    if nltk_lang:
        try:
            nltk_sw = nltk_stopwords.words(nltk_lang)
        except LookupError:
            print(f"📥 Downloading NLTK stopwords for '{nltk_lang}'...")
            nltk.download("stopwords")
            nltk_sw = nltk_stopwords.words(nltk_lang)
        except Exception:
            print(f"⚠️ Error loading NLTK stopwords for '{lang}'.")
            nltk_sw = []
        combined |= {w.lower() for w in nltk_sw}

    # ------------------------------- EXTRA STOPLIST ----------------------------
    if extra_stoplist:
        if isinstance(extra_stoplist, list):
            combined |= {w.lower() for w in extra_stoplist}

        elif isinstance(extra_stoplist, str):  # path to .txt file
            try:
                extra = load_stoplist(extra_stoplist)
                combined |= {w.lower() for w in extra}
            except Exception:
                print(f"⚠️ Could not load extra stoplist file '{extra_stoplist}'. Skipping.")

    return combined


# ---------------------------------------------------------------------------
# SPACY MODELS
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


def _get_spacy_model(language):
    """
    Robust spaCy model loader:

    1. Try to load installed model.
    2. If not installed, download it.
    3. If download fails, fallback to spacy.blank(language).

    Always returns an NLP object.
    """

    import spacy.cli

    lang = language.lower()
    model_name = SPACY_MODEL_TABLE.get(lang)

    # Unsupported language -> blank model
    if not model_name:
        print(f"⚠️ No spaCy model registered for '{language}'. Using blank model.")
        nlp = spacy.blank(lang)
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp

    # Cached model?
    if model_name in _SPACY_MODELS:
        print(f"🔄 Using cached spaCy model: {model_name}")
        return _SPACY_MODELS[model_name]

    # Try loading installed model
    print(f"🔍 Attempting to load spaCy model: {model_name}")
    try:
        nlp = spacy.load(model_name)
        print(f"✅ Loaded spaCy model: {model_name}")
        _SPACY_MODELS[model_name] = nlp
        return nlp

    except OSError:
        print(f"⚠️ spaCy model '{model_name}' not found. Attempting download…")

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
    """Remove page numbers and extremely short lines."""
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
    """Remove lines containing only numbers or numeric markers."""
    pattern = r'^\s*[\(\[\{\-–—\*•●"]*\s*\d+\s*[\)\]\}\-–—\*•●"."]*\s*$'
    return "\n".join(
        line for line in text.splitlines()
        if not re.fullmatch(pattern, line)
    )


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY REMOVAL
# ---------------------------------------------------------------------------

def _remove_bibliography_generic(text, section_titles, ref_patterns):
    """Internal helper for bibliography section deletion."""
    for title in section_titles:
        match = re.search(title, text, flags=re.IGNORECASE)
        if match:
            start = match.start()
            tail = text[start:]
            for patt in ref_patterns:
                if re.search(patt, tail):
                    return text[:start].strip()
    return text


def remove_bibliography(text, language="en"):
    lang = language.lower()
    mapping = {
        "es": ([
            r'\bREFERENCIAS?\s+BIBLIOGR[ÁA]FICAS?\b',
            r'\bBIBLIOGRAF[ÍI]A\b'
        ], [r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s']),
        "en": ([
            r'\bREFERENCES\b',
            r'\bBIBLIOGRAPHY\b',
            r'\bWORKS\s+CITED\b'
        ], [r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s']),
        "fr": ([
            r'\bRÉFÉRENCES\b',
            r'\bBIBLIOGRAPHIE\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "de": ([
            r'\bLITERATUR\b',
            r'\bBIBLIOGRAPHIE\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "it": ([
            r'\bBIBLIOGRAFIA\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "pt": ([
            r'\bREFERÊNCIAS\b',
            r'\bBIBLIOGRAFIA\b'
        ], [r'\(\d{4}\)', r'https?://']),
    }

    if lang not in mapping:
        return text

    sec_titles, ref_patts = mapping[lang]
    return _remove_bibliography_generic(text, sec_titles, ref_patts)


# ---------------------------------------------------------------------------
# STOPWORDS & LEMMATISATION
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    return " ".join(t for t in text.split() if t.lower() not in stopwords)


def apply_user_stoplist(text, stoplist):
    stopset = {w.lower() for w in stoplist}
    return " ".join(t for t in text.split() if t.lower() not in stopset)


def lemmatize_text(text, language="en"):
    nlp = _get_spacy_model(language)
    doc = nlp(text)
    return " ".join(token.lemma_ if token.lemma_ else token.text for token in doc)


# ---------------------------------------------------------------------------
# MASTER CLEANING FUNCTION
# ---------------------------------------------------------------------------

def clean_text(
    text,
    structure=False,
    remove_stopwords_flag=False,
    stoplist=None,
    extra_stoplist=None,
    lemmatize_flag=False,
    remove_bibliography_flag=False,
    language="en",
):
    """
    Main public cleaning function.
    Fully modular: the user decides each component.
    """

    cleaned = text

    # ------------------------------ Bibliography ------------------------------
    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    # ------------------------------ Structural -------------------------------
    if structure:
        cleaned = clean_structure(cleaned)

    # ------------------------------ Stopwords (combined) ----------------------
    if remove_stopwords_flag:
        sw = get_language_stopwords(language, extra_stoplist)
        if sw:
            cleaned = remove_stopwords(cleaned, sw)
        else:
            print(f"⚠️ No stopwords available for language '{language}'.")

    # ------------------------------ User stoplist -----------------------------
    if stoplist:
        if isinstance(stoplist, str):  # path to .txt
            try:
                user_stop = load_stoplist(stoplist)
                cleaned = apply_user_stoplist(cleaned, user_stop)
            except Exception:
                print(f"⚠️ Invalid stoplist file '{stoplist}'. Skipping.")

        elif isinstance(stoplist, list):
            cleaned = apply_user_stoplist(cleaned, stoplist)

        else:
            print(f"⚠️ Ignoring invalid stoplist value: must be list or file path.")

    # ------------------------------ Lemmatization -----------------------------
    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
