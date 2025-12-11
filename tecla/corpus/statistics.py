"""
Corpus statistics utilities for the TECLA corpus module.

This module provides:
- document-level descriptive statistics,
- global corpus-level aggregation,
- structured output for integration with TECLA.

Statistics computed (lightweight, text-only):
- token count
- type count (unique tokens)
- type-token ratio (TTR)
- hapax legomena ratio
- stopword proportion
- lexical density
- sentence count
- average sentence length
"""

import os
import csv
import re
from collections import Counter
from .utils import load_stoplist


# ---------------------------------------------------------------------------
# BASIC TOKENISATION UTILITIES
# ---------------------------------------------------------------------------

def _tokenise(text):
    """Minimal whitespace tokeniser."""
    return text.split()


def _sentence_split(text):
    """Simple heuristic sentence segmentation."""
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


# ---------------------------------------------------------------------------
# DOCUMENT-LEVEL STATISTICS
# ---------------------------------------------------------------------------

def compute_document_statistics(text, stopwords=None):
    """
    Compute descriptive statistics for a single document.

    Returns a dict containing:
    - token_count
    - type_count
    - ttr
    - hapax_ratio
    - stopword_ratio
    - lexical_density
    - sentence_count
    - avg_sentence_length
    - stopword_count
    - content_word_count
    - freq_dict
    """

    tokens = _tokenise(text)
    token_count = len(tokens)

    # Types and frequencies
    freq = Counter(tokens)
    type_count = len(freq)

    # TTR
    ttr = type_count / token_count if token_count else 0.0

    # Hapax
    hapax = sum(1 for t in freq if freq[t] == 1)
    hapax_ratio = hapax / type_count if type_count else 0.0

    # Sentence metrics
    sentences = _sentence_split(text)
    sentence_count = len(sentences)

    if sentence_count:
        avg_sentence_length = sum(len(_tokenise(s)) for s in sentences) / sentence_count
    else:
        avg_sentence_length = 0.0

    # Stopwords
    stopword_ratio = None
    stopword_count = 0
    content_word_count = 0

    if stopwords:
        stopword_count = sum(1 for t in tokens if t.lower() in stopwords)
        content_word_count = token_count - stopword_count
        stopword_ratio = stopword_count / token_count if token_count else None
        lexical_density = content_word_count / token_count if token_count else None
    else:
        lexical_density = None

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
        "freq_dict": dict(freq),   # required for global stats
    }


# ---------------------------------------------------------------------------
# GLOBAL (CORPUS-LEVEL) STATISTICS
# ---------------------------------------------------------------------------

def compute_global_statistics(doc_stats):
    """
    Compute full corpus-level statistics by aggregating document-level stats.

    This is NOT the mean of document stats:
    - tokens = sum
    - types = union of all types
    - hapax = types with freq 1 globally
    - stopword_ratio = total_stopwords / total_tokens
    - lexical_density = total_content_words / total_tokens
    - avg_sentence_length = total_tokens / total_sentences
    """

    total_tokens = sum(d["token_count"] for d in doc_stats)

    # Merge vocab and frequencies
    global_freq = {}
    for d in doc_stats:
        for tok, f in d["freq_dict"].items():
            global_freq[tok] = global_freq.get(tok, 0) + f

    total_types = len(global_freq)
    global_hapax = sum(1 for t, f in global_freq.items() if f == 1)

    total_stopwords = sum(d["stopword_count"] for d in doc_stats)
    total_content = sum(d["content_word_count"] for d in doc_stats)

    total_sentences = sum(d["sentence_count"] for d in doc_stats)

    return {
        "filename": "__CORPUS_GLOBAL__",
        "token_count": total_tokens,
        "type_count": total_types,
        "ttr": total_types / total_tokens if total_tokens else 0.0,
        "hapax_ratio": global_hapax / total_types if total_types else 0.0,
        "stopword_ratio": total_stopwords / total_tokens if total_tokens else None,
        "lexical_density": total_content / total_tokens if total_tokens else None,
        "avg_sentence_length": total_tokens / total_sentences if total_sentences else None,
        "sentence_count": total_sentences,
        "stopword_count": total_stopwords,
        "content_word_count": total_content,
        "freq_dict": global_freq,
    }


# ---------------------------------------------------------------------------
# MAIN PUBLIC API
# ---------------------------------------------------------------------------

def corpus_statistics(input_folder, output_csv=None, stoplist=None):
    """
    Compute document-level statistics for all TXT files in a folder
    + global corpus-level statistics.

    Parameters:
        input_folder (str): path to TXT folder
        output_csv (str or None): path to save CSV
        stoplist (str or list or None): optional stoplist

    Returns:
        list[dict]: document statistics + global row at the end
    """

    stopwords = load_stoplist(stoplist) if stoplist else None
    stats_list = []

    for fname in sorted(os.listdir(input_folder)):
        if fname.lower().endswith(".txt"):
            fpath = os.path.join(input_folder, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            stats = compute_document_statistics(text, stopwords)
            stats["filename"] = fname
            stats_list.append(stats)

    # Add global statistics last
    if stats_list:
        global_stats = compute_global_statistics(stats_list)
        stats_list.append(global_stats)

    # Optional CSV output
    if output_csv:
        fieldnames = list(stats_list[0].keys())
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in stats_list:
                writer.writerow(row)

    return stats_list
