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

    Supports two layers:
    1. TECLA-pattern files:  <Author, N.>_<YYYY>_<title>.pdf
    2. General heuristic fallback (original implementation)

    Parameters:
        filename (str): PDF name or full path.

    Returns:
        dict: {
            'author': str or None,
            'year': int or None,
            'title': str or None,
            'text_type': 'unknown'
        }
    """

    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]

    # ----------------------------------------------------------------------
    # 1) TECLA naming convention:
    #    Author, N._YYYY_titlewords
    # ----------------------------------------------------------------------
    parts = name.split("_")

    if len(parts) >= 3:
        possible_author = parts[0].strip()
        possible_year = parts[1].strip()

        # Author should contain a comma (Surname, Initial)
        # Year should match YYYY
        if "," in possible_author and re.fullmatch(r"(19|20)\d{2}", possible_year):

            author = possible_author
            year = int(possible_year)

            # Title = everything after the year
            title_parts = parts[2:]
            title = " ".join(title_parts)
            title = title.replace("_", " ").strip()
            title = re.sub(r"\s+", " ", title)

            return {
                "author": author,
                "year": year,
                "title": title,
                "text_type": "unknown",
            }

    # ----------------------------------------------------------------------
    # 2) FALLBACK: general heuristic from original implementation
    # ----------------------------------------------------------------------

    clean_name = name.replace("_", " ").replace("-", " ").strip()
    tokens = clean_name.split()

    # --- Detect year -----------------------------------------------------
    year = None
    for t in tokens:
        if YEAR_PATTERN.fullmatch(t):
            year = int(t)
            break

    # --- Detect author ---------------------------------------------------
    author = None
    if year is not None:
        idx = tokens.index(str(year))
        if idx > 0:
            author = " ".join(tokens[:idx])
    else:
        # Capitalisation heuristic
        possible_author = []
        for t in tokens:
            if t[0].isupper():
                possible_author.append(t)
            else:
                break
        if possible_author:
            author = " ".join(possible_author)

    # --- Detect title ----------------------------------------------------
    title = None
    if year is not None:
        idx = tokens.index(str(year))
        if idx < len(tokens) - 1:
            title = " ".join(tokens[idx + 1:])
    else:
        if author:
            author_tokens = author.split()
            rest = tokens[len(author_tokens):]
            if rest:
                title = " ".join(rest)
        else:
            title = clean_name

    if title:
        title = title.replace(".", " ").strip()

    return {
        "author": author,
        "year": year,
        "title": title,
        "text_type": "unknown",
    }
