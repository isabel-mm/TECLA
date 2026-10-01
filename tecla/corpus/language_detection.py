"""
Language detection utilities for TECLA.

Wraps langid to provide a simple detect_language() function.
Used by the pipeline when no language is specified explicitly.
"""

from typing import Tuple


def detect_language(text: str, sample_chars: int = 3000) -> Tuple[str, float]:
    """
    Detect the language of a text string.

    Uses the first `sample_chars` characters for efficiency on long texts.

    Parameters
    ----------
    text : str
        Input text.
    sample_chars : int
        Number of characters to sample from the start of the text.

    Returns
    -------
    tuple (lang_code, confidence)
        lang_code : ISO 639-1 code (e.g. 'en', 'es').
        confidence : float score from langid (higher = more confident).
    """
    import langid

    sample = text[:sample_chars].strip()
    if not sample:
        return "en", 0.0

    lang, score = langid.classify(sample)
    return lang, float(score)
