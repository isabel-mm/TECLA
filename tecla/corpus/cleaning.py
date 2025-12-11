"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.

This module offers:
- structural cleaning,
- bibliography removal (multilingual),
- stopword removal (spaCy + NLTK + user-defined),
- lemmatisation via spaCy.

All operations are explicit: nothing is applied automatically.
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
    Return a combined stopword set:
    - spaCy stopwords
    - NLTK stopwords (mapped by language)
    - user-provided extra stoplist (optional)
    """

    lang = language.lower()
    combined = set()

    # --- spaCy stopwords ---
    try:
        nlp = _get_spacy_model(lang)
        combined |= {w.lower() for w in nlp.Defaults.stop_words}
    except Exception:
        print(f"⚠️ spaCy stopwords unavailable for '{lang}'.")

    # --- NLTK stopwords ---
    try:
        nltk_lang = NLTK_LANG_MAP.get(lang)
        if nltk_lang:
            try:
                nltk_sw = nltk_stopwords.words(nltk_lang)
            except LookupError:
                nltk.download("stopwords")
                nltk_sw = nltk_stopwords.words(nltk_lang)

            combined |= {w.lower() for w in nltk_sw}
            print(f"✅ Loaded NLTK stopwords for '{nltk_lang}'")
    except Exception:
        print(f"⚠️ Could not load NLTK stopwords for '{lang}'.")

    # --- user extra stoplist ---
    if extra_stoplist:
        try:
            if isinstance(extra_stoplist, list):
                combined |= {w.lower() for w in extra_stoplist}
            elif isinstance(extra_stoplist, str):
                combined |= {w.lower() for w in load_stoplist(extra_stoplist)}
        except Exception:
            print(f"⚠️ Could not load extra stoplist '{extra_stoplist}'.")

    return combined


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
# LAZY LOADING OF SPACY MODELS
# ---------------------------------------------------------------------------

def _get_spacy_model(language):
    """Load or download spaCy model safely."""
    import spacy.cli

    lang = language.lower()
    model_name = SPACY_MODEL_TABLE.get(lang)

    if not model_name:
        print(f"⚠️ No spaCy model for '{lang}'. Using blank model.")
        nlp = spacy.blank(lang)
        nlp.add_pipe("sentencizer")
        return nlp

    if model_name in _SPACY_MODELS:
        print(f"🔄 Using cached spaCy model: {model_name}")
        return _SPACY_MODELS[model_name]

    print(f"🔍 Attempting to load spaCy model: {model_name}")

    try:
        nlp = spacy.load(model_name)
        print(f"✅ Loaded spaCy model: {model_name}")
    except OSError:
        print(f"⚠️ Model '{model_name}' not found. Downloading...")
        try:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
            print(f"🎉 Download successful: {model_name}")
        except Exception:
            print(f"❌ Failed. Using blank model for '{lang}'.")
            nlp = spacy.blank(lang)
            nlp.add_pipe("sentencizer")

    _SPACY_MODELS[model_name] = nlp
    return nlp


# ---------------------------------------------------------------------------
# STRUCTURAL CLEANING
# ---------------------------------------------------------------------------

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$")

def clean_structure(text, remove_short_lines=True, remove_page_numbers=True):
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if remove_page_numbers and PAGE_NUMBER_LINE.fullmatch(s):
            continue
        if remove_short_lines and len(s.split()) < 3:
            continue
        cleaned.append(s)
    return "\n".join(cleaned)

def remove_numeric_only_lines(text):
    pattern = r'^\s*[\(\[\{\-–—\*•●"]*\s*\d+\s*[\)\]\}\-–—\*•●"."]*\s*$'
    return "\n".join(line for line in text.splitlines() if not re.fullmatch(pattern, line))


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY REMOVAL
# ---------------------------------------------------------------------------

def _remove_bibliography_generic(text, section_titles, reference_patterns):
    for title in section_titles:
        match = re.search(title, text, flags=re.IGNORECASE)
        if match:
            start = match.start()
            following = text[start:]
            if any(re.search(p, following) for p in reference_patterns):
                return text[:start].strip()
    return text

# Language-specific variants…

def remove_bibliography(text, language="en"):
    lang = language.lower()
    mapping = {
        "es": remove_bibliography_es,
        "en": remove_bibliography_en,
        "fr": remove_bibliography_fr,
        "de": remove_bibliography_de,
        "it": remove_bibliography_it,
        "pt": remove_bibliography_pt,
    }
    return mapping.get(lang, lambda x: x)(text)


# ---------------------------------------------------------------------------
# STOPWORDS, USER STOPLISTS, LEMMATISATION
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    return " ".join(t for t in text.split() if t.lower() not in stopwords)

def apply_user_stoplist(text, stoplist):
    sl = {w.lower() for w in stoplist}
    return " ".join(t for t in text.split() if t.lower() not in sl)

def lemmatize_text(text, language="en"):
    nlp = _get_spacy_model(language)
    return " ".join(token.lemma_ or token.text for token in nlp(text))


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
    cleaned = text

    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    if structure:
        cleaned = clean_structure(cleaned)

    if remove_stopwords_flag:
        sw = get_language_stopwords(language, extra_stoplist)
        cleaned = remove_stopwords(cleaned, sw)

    if stoplist:
        if isinstance(stoplist, list):
            cleaned = apply_user_stoplist(cleaned, stoplist)
        elif isinstance(stoplist, str):
            cleaned = apply_user_stoplist(cleaned, load_stoplist(stoplist))

    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
