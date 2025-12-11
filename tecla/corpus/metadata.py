"""
Metadata extraction utilities for TECLA's corpus module.

This module provides heuristics to infer:
- author name,
- publication year,
- document title,
- text type (article / book chapter / other).

The heuristics are based on filename patterns commonly used in academic PDFs.
The goal is not perfect bibliographic accuracy but a reliable, reproducible
approximation suitable for corpus metadata.
"""

import re
import os


YEAR_PATTERN = re.compile(r"(19\d{2}|20\d{2}|210\d)")  # Supports 1900–2109 approx.


def infer_metadata(filename):
    """
    Infer metadata (author, year, title, text_type) from a PDF filename.

    Expected patterns:
        AUTHOR_YYYY_TITLE.pdf
        AUTHOR-YYYY-TITLE.pdf
        TITLE_YYYY.pdf
        TITLE.pdf

    Parameters:
        filename (str): Name of the PDF file or full path.

    Returns:
        dict: {
            'author': str or None,
            'year': int or None,
            'title': str or None,
            'text_type': str
        }
    """
    # Extract just the name without extension
    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]

    # Replace separators with spaces for easier tokenization
    clean_name = name.replace("_", " ").replace("-", " ").strip()

    tokens = clean_name.split()

    # --- Detect year ---------------------------------------------------------
    year = None
    for t in tokens:
        if YEAR_PATTERN.fullmatch(t):
            year = int(t)
            break

    # --- Detect author -------------------------------------------------------
    # Heuristic: the token(s) before the year (if any) are the author
    author = None
    if year is not None:
        idx = tokens.index(str(year))
        if idx > 0:
            # All tokens before the year treated as author phrase
            author = " ".join(tokens[:idx])
    else:
        # If no year found, attempt to infer author by capitalization pattern
        # e.g. "Smith" or "Garcia Lopez"
        possible_author = []
        for t in tokens:
            if t[0].isupper():
                possible_author.append(t)
            else:
                break
        if possible_author:
            author = " ".join(possible_author)

    # --- Detect title --------------------------------------------------------
    title = None
    if year is not None:
        idx = tokens.index(str(year))
        if idx < len(tokens) - 1:
            title = " ".join(tokens[idx + 1:])
    else:
        # Title is everything after author block
        if author:
            author_tokens = author.split()
            rest = tokens[len(author_tokens):]
            if rest:
                title = " ".join(rest)
        else:
            # No clear author-year structure: full name is the title
            title = clean_name

    # Clean title formatting
    if title:
        title = title.replace(".", " ").strip()

    # --- Infer text type (very rough heuristic) -------------------------------
    # We will refine text_type later once page count is available.
    # For now: "unknown".
    text_type = "unknown"

    return {
        "author": author,
        "year": year,
        "title": title,
        "text_type": text_type,
    }
