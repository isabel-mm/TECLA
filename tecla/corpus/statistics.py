"""
Corpus statistics utilities for the TECLA corpus module.

This module provides:
- document-level descriptive statistics,
- corpus-level global aggregation,
- unified stopword integration,
- optional CSV export.

Lightweight statistics computed:
- token count
- type count
- type-token ratio (TTR)
- hapax ratio
- stopword proportion
- lexical density
- sentence count
- average sentence length
"""

import os
import csv
import re
from collections import Counter

# Import stopword system from cleaning
from .cleaning import get_language_stopwords
from .utils import load_stoplist


# ---------------------------------------------------------------------------
# TOKENISATION AND SENTENCE SPLITTING
# ---------------------------------------------------------------------------

def _tokenise(text):
    """Minimal whitespace tokeniser."""
    return text.split()


def _sentence_split(text):
    """Simple punctuation-based segmentation."""
    sents = re.split(r"[.!?]+", text)
    return [s.strip() for s in sents if s.strip()]


# ---------------------------------------------------------------------------
# DOCUMENT-LEVEL STATISTICS
# ---------------------------------------------------------------------------

def compute_document_statistics(text, stopwords=None):
    """
    Compute descriptive statistics for a single document.

    Returns a dict with all fields needed for global aggregation.
    """

    tokens = _tokenise(text)
    token_count = len(tokens)

    # Frequency dictionary
    freq = Counter(tokens)
    type_count = len(freq)

    # TTR
    ttr = type_count / token_count if token_count else 0.0

    # Hapax legomena
    hapax = sum(1 for t in freq if freq[t] == 1)
    hapax_ratio = hapax / type_count if type_count else 0.0

    # Sentence metrics
    sentences = _sentence_split(text)
    sentence_count = len(sentences)
    avg_sentence_length = (
        sum(len(_tokenise(s)) for s in sentences) / sentence_count
        if sentence_count else 0.0
    )

    # Stopwords / lexical density
    stopword_count = 0
    content_word_count = 0
    stopword_ratio = None
    lexical_density = None

    if stopwords:
        stopword_count = sum(1 for t in tokens if t.lower() in stopwords)
        content_word_count = token_count - stopword_count

        stopword_ratio = stopword_count / token_count if token_count else None
        lexical_density = content_word_count / token_count if token_count else None

    return {
        "token_count": token_count,
        "type_count": type_count,
        "ttr": ttr,
        "hapax_ratio": hapax_ratio,
        "stopword_ratio": stopword_ratio,
        "lexical_density": lexical_density,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "stopword_count": stopword_count,
        "content_word_count": content_word_count,
        "freq_dict": dict(freq),
    }


# ---------------------------------------------------------------------------
# GLOBAL CORPUS-LEVEL STATISTICS
# ---------------------------------------------------------------------------

def compute_global_statistics(doc_stats):
    """
    Compute full corpus-level statistics by aggregating raw counts.

    NOT averages — true corpus-level stats:
    - tokens: sum
    - types: vocabulary union
    - hapax: types with global freq = 1
    - avg_sentence_length: total_tokens / total_sentences
    """

    total_tokens = sum(d["token_count"] for d in doc_stats)

    # Merge frequencies
    global_freq = {}
    for d in doc_stats:
        for tok, f in d["freq_dict"].items():
            global_freq[tok] = global_freq.get(tok, 0) + f

    total_types = len(global_freq)
    global_hapax = sum(1 for t, f in global_freq.items() if f == 1)

    # Stopword totals
    total_stopwords = sum(d["stopword_count"] for d in doc_stats)
    total_content = sum(d["content_word_count"] for d in doc_stats)

    # Sentence totals
    total_sentences = sum(d["sentence_count"] for d in doc_stats)

    return {
        "filename": "__CORPUS_GLOBAL__",
        "token_count": total_tokens,
        "type_count": total_types,
        "ttr": total_types / total_tokens if total_tokens else 0.0,
        "hapax_ratio": global_hapax / total_types if total_types else 0.0,
        "stopword_ratio": total_stopwords / total_tokens if total_tokens else None,
        "lexical_density": total_content / total_tokens if total_tokens else None,
        "avg_sentence_length": (
            total_tokens / total_sentences if total_sentences else None
        ),
        "stopword_count": total_stopwords,
        "content_word_count": total_content,
        "freq_dict": global_freq,
        "sentence_count": total_sentences,
    }


# ---------------------------------------------------------------------------
# MAIN API: CORPUS STATISTICS
# ---------------------------------------------------------------------------

def corpus_statistics(
    input_folder,
    language="en",
    stoplist=None,
    extra_stoplist=None,
    output_csv=None
):
    """
    Compute statistics for all documents in a folder.

    Parameters:
        input_folder (str) — folder with TXT files
        language (str) — used for stopword lookup
        stoplist (None | list | path) — user-defined stopword list
        extra_stoplist (None | list | path) — additional words to remove
        output_csv (str | None) — optional CSV output path

    Returns:
        list[dict] with per-document statistics.
    """

    # Combined stopword system
    default_stopwords = get_language_stopwords(language, extra_stoplist)

    # Merge explicit user stoplist (optional)
    if stoplist:
        try:
            if isinstance(stoplist, str):
                user_sw = load_stoplist(stoplist)
            elif isinstance(stoplist, list):
                user_sw = stoplist
            else:
                raise TypeError("Invalid stoplist type.")

            default_stopwords |= {w.lower() for w in user_sw}

        except Exception:
            print(f"⚠️ Warning: could not load stoplist '{stoplist}'.")

    stats_list = []

    for fname in sorted(os.listdir(input_folder)):
        if fname.lower().endswith(".txt"):
            fpath = os.path.join(input_folder, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            stats = compute_document_statistics(text, default_stopwords)
            stats["filename"] = fname
            stats_list.append(stats)

    # CSV output
    if output_csv:
        header = [
            "filename", "token_count", "type_count", "ttr",
            "hapax_ratio", "stopword_ratio", "lexical_density",
            "sentence_count", "avg_sentence_length"
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for row in stats_list:
                writer.writerow([row.get(col, "") for col in header])

    return stats_list
