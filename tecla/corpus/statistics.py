"""
Corpus statistics utilities for the TECLA corpus module.

This module provides:
- document-level descriptive statistics,
- optional corpus-level aggregation,
- CSV export of computed statistics.

Statistics computed are intentionally lightweight and rely only on text:
- token count
- type count (unique tokens)
- type-token ratio (TTR)
- lexical density (content words / total words, simple heuristic)
- average sentence length (in words)
- proportion of hapax legomena
- stopword proportion (optional, if a stopword list is provided)

All functions are designed to be transparent and reproducible.
"""

import os
import csv
import re
from collections import Counter
from .utils import ensure_folder, load_stoplist


# ---------------------------------------------------------------------------
# BASIC TOKENISATION UTILITIES
# ---------------------------------------------------------------------------

def _tokenise(text):
    """
    Minimal tokeniser: splits on whitespace.
    TECLA intentionally avoids linguistic assumptions here.

    Parameters:
        text (str)

    Returns:
        list[str]: List of tokens.
    """
    return text.split()


def _sentence_split(text):
    """
    Minimal sentence segmentation using punctuation heuristics.

    Parameters:
        text (str)

    Returns:
        list[str]
    """
    return re.split(r"[.!?]+", text)


# ---------------------------------------------------------------------------
# DOCUMENT-LEVEL STATISTICS
# ---------------------------------------------------------------------------

def compute_document_statistics(text, stopwords=None):
    """
    Compute descriptive statistics for a single document.

    Parameters:
        text (str): Document text.
        stopwords (set[str] or None): Optional set of stopwords.

    Returns:
        dict: Statistics for the document.
    """
    tokens = _tokenise(text)
    token_count = len(tokens)

    types = set(tokens)
    type_count = len(types)

    # Avoid division by zero errors
    ttr = type_count / token_count if token_count > 0 else 0.0

    # Hapax legomena
    freq = Counter(tokens)
    hapax = sum(1 for t in freq if freq[t] == 1)
    hapax_ratio = hapax / type_count if type_count > 0 else 0.0

    # Stopword proportion (optional)
    stopword_ratio = None
    if stopwords:
        sw = sum(1 for t in tokens if t.lower() in stopwords)
        stopword_ratio = sw / token_count if token_count > 0 else 0.0

    # Lexical density (rough heuristic): proportion of tokens not in stopwords
    lexical_density = None
    if stopwords:
        content = sum(1 for t in tokens if t.lower() not in stopwords)
        lexical_density = content / token_count if token_count > 0 else 0.0

    # Average sentence length
    sentences = [s.strip() for s in _sentence_split(text) if s.strip()]
    if sentences:
        avg_sentence_length = sum(len(_tokenise(s)) for s in sentences) / len(sentences)
    else:
        avg_sentence_length = 0.0

    return {
        "token_count": token_count,
        "type_count": type_count,
        "ttr": ttr,
        "hapax_ratio": hapax_ratio,
        "stopword_ratio": stopword_ratio,
        "lexical_density": lexical_density,
        "avg_sentence_length": avg_sentence_length,
    }


# ---------------------------------------------------------------------------
# CORPUS-LEVEL STATISTICS
# ---------------------------------------------------------------------------

def compute_corpus_statistics(stat_rows):
    """
    Compute simple aggregated corpus-level statistics.

    Parameters:
        stat_rows (list[dict]): List of document statistics.

    Returns:
        dict: aggregated means for numeric fields.
    """
    if not stat_rows:
        return {}

    numeric_fields = [
        "token_count", "type_count", "ttr",
        "hapax_ratio", "stopword_ratio",
        "lexical_density", "avg_sentence_length",
    ]

    agg = {}

    for field in numeric_fields:
        values = [row[field] for row in stat_rows if row[field] is not None]
        if values:
            agg[field] = sum(values) / len(values)
        else:
            agg[field] = None

    return agg


# ---------------------------------------------------------------------------
# MAIN PUBLIC FUNCTION: CORPUS STATISTICS
# ---------------------------------------------------------------------------

def corpus_statistics(input_source, output_csv="corpus_stats.csv",
                      stoplist=None, include_corpus_level=True):
    """
    Compute statistics for all documents in a folder OR list of texts.

    Parameters:
        input_source (str or list[str]):
            - Folder path with TXT files, OR
            - List of strings (documents).
        output_csv (str): CSV path to save statistics.
        stoplist (str or list or None): Optional stoplist for lexical metrics.
        include_corpus_level (bool): Whether to compute aggregate corpus stats.

    Returns:
        dict: {
            "documents": list of document-level stats,
            "corpus": aggregated stats (if enabled)
        }
    """
    # Load stopwords if provided
    stopwords = load_stoplist(stoplist) if stoplist else None

    documents = []

    # Case 1: Folder with TXT files
    if isinstance(input_source, str):
        folder = input_source
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Directory not found: {folder}")

        for fname in sorted(os.listdir(folder)):
            if fname.lower().endswith(".txt"):
                fpath = os.path.join(folder, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

                stats = compute_document_statistics(text, stopwords)
                stats["filename"] = fname
                documents.append(stats)

    # Case 2: List of texts
    elif isinstance(input_source, list):
        for i, text in enumerate(input_source):
            stats = compute_document_statistics(text, stopwords)
            stats["filename"] = f"doc_{i+1}"
            documents.append(stats)

    else:
        raise TypeError("input_source must be a folder path or a list of strings.")

    # Corpus-level aggregation
    corpus_stats = compute_corpus_statistics(documents) if include_corpus_level else {}

    # Write CSV ----------------------------------------------------------------
    header = [
        "filename", "token_count", "type_count", "ttr",
        "hapax_ratio", "stopword_ratio", "lexical_density",
        "avg_sentence_length"
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for row in documents:
            writer.writerow([row.get(col, "") for col in header])

    return {
        "documents": documents,
        "corpus": corpus_stats,
    }
