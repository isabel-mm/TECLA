"""
TECLA – Terminology Extraction Evaluation
-----------------------------------------

Computes standard evaluation metrics (precision, recall, F1) by comparing
automatically extracted terms against a gold-standard reference list.

Supports two matching modes:
- exact : surface form must match exactly (case-insensitive).
- lemma : lemmatised forms are compared (requires 'lemma' field in extracted).
"""

from typing import List, Dict, Any, Union


def evaluate_extraction(
    extracted: List[Union[str, Dict[str, Any]]],
    gold: List[str],
    mode: str = "exact",
) -> Dict[str, Any]:
    """
    Evaluate extracted terms against a gold-standard list.

    Parameters
    ----------
    extracted : list of str or list of dict
        Extracted terms. If dicts, uses the 'term' key (exact mode) or
        'lemma' key (lemma mode).
    gold : list of str
        Reference term list (one term per entry, case-insensitive).
    mode : str
        Matching strategy: 'exact' (default) or 'lemma'.

    Returns
    -------
    dict with keys:
        precision, recall, f1, tp, fp, fn,
        true_positives (list), false_positives (list), false_negatives (list)
    """

    if mode not in ("exact", "lemma"):
        raise ValueError(f"Unknown mode '{mode}'. Use 'exact' or 'lemma'.")

    gold_set = {t.lower().strip() for t in gold if t.strip()}

    extracted_terms = _normalise_extracted(extracted, mode)

    tp_terms = [t for t in extracted_terms if t in gold_set]
    fp_terms = [t for t in extracted_terms if t not in gold_set]
    fn_terms = [t for t in gold_set if t not in set(extracted_terms)]

    tp = len(tp_terms)
    fp = len(fp_terms)
    fn = len(fn_terms)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "true_positives": tp_terms,
        "false_positives": fp_terms,
        "false_negatives": fn_terms,
    }


def evaluate_from_csv(
    extracted_csv: str,
    gold_csv: str,
    extracted_col: str = "term",
    gold_col: str = "term",
    mode: str = "exact",
) -> Dict[str, Any]:
    """
    Convenience wrapper: load extracted terms and gold standard from CSV files.

    Parameters
    ----------
    extracted_csv : str
        Path to CSV with extracted terms (must have a term column).
    gold_csv : str
        Path to CSV with gold-standard terms (must have a term column).
    extracted_col : str
        Column name for terms in extracted_csv.
    gold_col : str
        Column name for terms in gold_csv.
    mode : str
        Matching strategy: 'exact' or 'lemma'.

    Returns
    -------
    dict — same as evaluate_extraction().
    """
    import pandas as pd

    extracted_df = pd.read_csv(extracted_csv)
    gold_df = pd.read_csv(gold_csv)

    extracted = extracted_df[extracted_col].dropna().tolist()
    gold = gold_df[gold_col].dropna().tolist()

    return evaluate_extraction(extracted, gold, mode=mode)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalise_extracted(
    extracted: List[Union[str, Dict[str, Any]]],
    mode: str,
) -> List[str]:
    """Flatten extracted terms to a list of lowercase strings."""
    result = []
    for item in extracted:
        if isinstance(item, str):
            result.append(item.lower().strip())
        elif isinstance(item, dict):
            key = "lemma" if mode == "lemma" else "term"
            val = item.get(key, item.get("term", ""))
            result.append(val.lower().strip())
    return result
