"""
TECLA – Linguistic Filter
------------------------

This module implements the linguistic filtering stage of the hybrid
terminology extraction pipeline. It applies POS-based grammatical
patterns to preprocessed documents in order to identify structurally
plausible term candidates (unithood).

The module does NOT compute frequencies, weights or rankings.
"""

from pathlib import Path
from typing import List, Dict, Any
import yaml


# ---------------------------------------------------------------------
# Grammar loading
# ---------------------------------------------------------------------

def load_grammar(grammar_path: Path) -> Dict[str, Any]:
    """
    Load the POS-based grammar from a YAML file.

    Parameters
    ----------
    grammar_path : Path
        Path to the grammar.yaml file.

    Returns
    -------
    dict
        Parsed grammar grouped by language.
    """
    with open(grammar_path, "r", encoding="utf-8") as f:
        grammar = yaml.safe_load(f)
    return grammar


# ---------------------------------------------------------------------
# Core linguistic filter
# ---------------------------------------------------------------------

def extract_candidates(
    documents: List[Dict[str, Any]],
    language: str,
    grammar_path: Path
) -> List[Dict[str, Any]]:
    """
    Extract term candidates from preprocessed documents using
    POS-based grammatical patterns.

    Parameters
    ----------
    documents : list of dict
        Preprocessed documents. Each document must contain:
        - doc_id : str
        - tokens : list of dicts with at least 'text', 'lemma', 'pos'

    language : str
        Language code (e.g. 'en', 'es').

    grammar_path : Path
        Path to the POS grammar YAML file.

    Returns
    -------
    list of dict
        List of candidate term occurrences.
    """

    grammar = load_grammar(grammar_path)

    if language not in grammar:
        raise ValueError(f"No grammar defined for language '{language}'")

    patterns = grammar[language]
    candidates = []

    for doc in documents:
        doc_id = doc.get("doc_id")
        tokens = doc.get("tokens", [])

        pos_sequence = [tok["pos"] for tok in tokens]

        for pattern in patterns:
            pattern_id = pattern["id"]
            pos_pattern = pattern["pos_pattern"].split()

            matches = _match_pos_pattern(pos_sequence, pos_pattern)

            for start, end in matches:
                span_tokens = tokens[start:end]

                term_text = " ".join(tok["text"] for tok in span_tokens)
                term_lemma = " ".join(tok["lemma"] for tok in span_tokens)

                candidate = {
                    "term": term_text,
                    "lemma": term_lemma,
                    "tokens": span_tokens,
                    "length": len(span_tokens),
                    "pattern_id": pattern_id,
                    "doc_id": doc_id,
                    "language": language
                }

                candidates.append(candidate)

    return candidates


# ---------------------------------------------------------------------
# Pattern matching utilities
# ---------------------------------------------------------------------

def _match_pos_pattern(
    pos_sequence: List[str],
    pattern: List[str]
) -> List[tuple]:
    """
    Match a POS pattern against a POS sequence.

    Supports:
    - literal POS tags (e.g. 'NOUN')
    - repetitions with '+' suffix (e.g. 'NOUN+')
    - optional repetition via '*' suffix (e.g. '(ADJ|NOUN)*')

    Returns
    -------
    list of tuples
        (start_index, end_index) for each match.
    """

    matches = []
    seq_len = len(pos_sequence)
    pat_len = len(pattern)

    i = 0
    while i < seq_len:
        j = i
        k = 0

        while j < seq_len and k < pat_len:
            pat = pattern[k]

            # Handle repetition operators
            if pat.endswith("+"):
                base = pat[:-1]
                if pos_sequence[j] != base:
                    break
                while j < seq_len and pos_sequence[j] == base:
                    j += 1
                k += 1

            elif pat.endswith("*"):
                base = pat[:-1].strip("()")
                allowed = base.split("|")
                while j < seq_len and pos_sequence[j] in allowed:
                    j += 1
                k += 1

            else:
                if pos_sequence[j] != pat:
                    break
                j += 1
                k += 1

        if k == pat_len:
            matches.append((i, j))

        i += 1

    return matches
