"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.
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
# LAZY SPACY LOADING
# ---------------------------------------------------------------------------

def _get_spacy_model(language):
    """Load or download the required spaCy model."""
    import spacy.cli

    lang = language.lower()
    model = SPACY_MODEL_TABLE.get(lang)

    if not model:
        print(f"⚠️ No spaCy model for '{language}', using blank('{lang}')")
        nlp = spacy.blank(lang)
        nlp.add_pipe("sentencizer")
        return nlp

    if model in _SPACY_MODELS:
        return _SPACY_MODELS[model]

    try:
        nlp = spacy.load(model)
        _SPACY_MODELS[model] = nlp
        return nlp

    except OSError:
        print(f"⚠️ Missing spaCy model '{model}', trying to download...")
        try:
            spacy.cli.download(model)
            nlp = spacy.load(model)
            _SPACY_MODELS[model] = nlp
            return nlp
        except:
            print(f"❌ Download failed. Using blank('{lang}')")
            nlp = spacy.blank(lang)
            nlp.add_pipe("sentencizer")
            _SPACY_MODELS[model] = nlp
            return nlp


# ---------------------------------------------------------------------------
# STOPWORDS (spaCy + NLTK + extra)
# ---------------------------------------------------------------------------

def get_language_stopwords(language, extra_stoplist=None):
    lang = language.lower()
    combined = set()

    # spaCy stopwords
    try:
        nlp = _get_spacy_model(lang)
        combined |= {w.lower() for w in nlp.Defaults.stop_words}
    except:
        print(f"⚠️ spaCy stopwords unavailable for '{lang}'")

    # NLTK stopwords
    try:
        nltk_lang = NLTK_LANG_MAP.get(lang)
        if nltk_lang:
            combined |= set(nltk_stopwords.words(nltk_lang))
    except:
        try:
            nltk.download("stopwords")
            nltk_lang = NLTK_LANG_MAP.get(lang)
            combined |= set(nltk_stopwords.words(nltk_lang))
        except:
            print(f"⚠️ NLTK stopwords unavailable for '{lang}'")

    # Extra stoplist
    if extra_stoplist:
        if isinstance(extra_stoplist, list):
            combined |= {w.lower() for w in extra_stoplist}
        elif isinstance(extra_stoplist, str):
            try:
                combined |= {w.lower() for w in load_stoplist(extra_stoplist)}
            except:
                print(f"⚠️ Could not load extra stoplist '{extra_stoplist}'")

    return combined


# ---------------------------------------------------------------------------
# STRUCTURAL CLEANING
# ---------------------------------------------------------------------------

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$")

def clean_structure(text, remove_short_lines=True, remove_page_numbers=True):
    result = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if remove_page_numbers and PAGE_NUMBER_LINE.fullmatch(stripped):
            continue
        if remove_short_lines and len(stripped.split()) < 3:
            continue
        result.append(stripped)
    return "\n".join(result)


def remove_numeric_only_lines(text):
    pattern = r'^\s*[\(\[\{\-–—\*•●"]*\s*\d+\s*[\)\]\}\-–—\*•●"."]*\s*$'
    return "\n".join(
        line for line in text.splitlines()
        if not re.fullmatch(pattern, line)
    )


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY REMOVAL — all functions defined BEFORE dispatcher
# ---------------------------------------------------------------------------

def _remove_bib(text, titles, refs):
    for title in titles:
        m = re.search(title, text, flags=re.IGNORECASE)
        if m:
            body = text[m.start():]
            for r in refs:
                if re.search(r, body):
                    return text[:m.start()].strip()
    return text


def remove_bibliography_es(text):
    return _remove_bib(
        text,
        [r'\bREFERENCIAS?\s+BIBLIOGR', r'\bBIBLIOGRAF[ÍI]A\b'],
        [r'\[\d+\]', r'\(\d{4}\)', r'https?://']
    )

def remove_bibliography_en(text):
    return _remove_bib(
        text,
        [r'\bREFERENCES\b', r'\bBIBLIOGRAPHY\b', r'WORKS\s+CITED'],
        [r'\[\d+\]', r'\(\d{4}\)', r'https?://']
    )

def remove_bibliography_fr(text):
    return _remove_bib(
        text,
        [r'\bRÉFÉRENCES\b', r'\bBIBLIOGRAPHIE\b'],
        [r'\(\d{4}\)', r'https?://']
    )

def remove_bibliography_de(text):
    return _remove_bib(
        text,
        [r'\bLITERATUR\b', r'\bBIBLIOGRAPHIE\b'],
        [r'\(\d{4}\)', r'https?://']
    )

def remove_bibliography_it(text):
    return _remove_bib(
        text,
        [r'\bBIBLIOGRAFIA\b'],
        [r'\(\d{4}\)', r'https?://']
    )

def remove_bibliography_pt(text):
    return _remove_bib(
        text,
        [r'\bREFERÊNCIAS\b', r'\bBIBLIOGRAFIA\b'],
        [r'\(\d{4}\)', r'https?://']
    )


# Dispatcher — now everything ABOVE is defined
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
    fn = mapping.get(lang)
    return fn(text) if fn else text


# ---------------------------------------------------------------------------
# LEMMATISATION & STOPWORD APPLICATION
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    return " ".join(t for t in text.split() if t.lower() not in stopwords)

def apply_user_stoplist(text, stoplist):
    stop = {w.lower() for w in stoplist}
    return " ".join(t for t in text.split() if t.lower() not in stop)

def lemmatize_text(text, language="en"):
    nlp = _get_spacy_model(language)
    doc = nlp(text)
    return " ".join(token.lemma_ or token.text for token in doc)


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
        cleaned = apply_user_stoplist(cleaned, load_stoplist(stoplist))

    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
