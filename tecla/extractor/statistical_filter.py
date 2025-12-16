"""
TECLA – Statistical Filter
-------------------------

This module implements the statistical weighting stage of the hybrid
terminology extraction pipeline. It estimates the degree of
terminologicity (termhood) of candidate terms using TF-IDF and C-value,
and integrates both metrics into a composite index.

The module assumes that candidates have already been identified
through a linguistic filter.
"""

from collections import defaultdict
from math import log2
from typing import List, Dict, Any, Optional
import math


# ---------------------------------------------------------------------
# Frequency utilities
# ---------------------------------------------------------------------

def compute_frequencies(
    candidates: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Compute term frequency and document frequency.
    """
    freq = defaultdict(int)
    doc_freq = defaultdict(set)

    for cand in candidates:
        lemma = cand["lemma"]
        doc_id = cand["doc_id"]

        freq[lemma] += 1
        doc_freq[lemma].add(doc_id)

    return {
        lemma: {
            "frequency": freq[lemma],
            "doc_frequency": len(doc_freq[lemma])
        }
        for lemma in freq
    }


# ---------------------------------------------------------------------
# TF-IDF
# ---------------------------------------------------------------------

def compute_tfidf(
    term_stats: Dict[str, Dict[str, int]],
    n_documents: int
) -> Dict[str, float]:
    """
    Compute TF-IDF scores for candidate terms.
    """
    tfidf = {}

    for term, stats in term_stats.items():
        tf = stats["frequency"]
        df = stats["doc_frequency"]

        idf = log2((n_documents + 1) / (df + 1)) + 1
        tfidf[term] = tf * idf

    return tfidf


# ---------------------------------------------------------------------
# C-value
# ---------------------------------------------------------------------

def compute_cvalue(
    term_stats: Dict[str, Dict[str, int]]
) -> Dict[str, float]:
    """
    Compute C-value scores for candidate terms.
    """

    terms = list(term_stats.keys())
    cvalue = {}

    term_lengths = {t: len(t.split()) for t in terms}
    nested_in = defaultdict(list)

    for t1 in terms:
        for t2 in terms:
            if t1 != t2 and t1 in t2.split():
                nested_in[t1].append(t2)

    for term in terms:
        f = term_stats[term]["frequency"]
        length = term_lengths[term]
        nested_terms = nested_in.get(term, [])

        if not nested_terms:
            cvalue[term] = log2(length) * f
        else:
            nested_freq_sum = sum(term_stats[t]["frequency"] for t in nested_terms)
            cvalue[term] = log2(length) * (f - (nested_freq_sum / len(nested_terms)))

    return cvalue


# ---------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------

def min_max_normalise(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Min–max normalisation of scores to [0,1].
    """
    if not scores:
        return {}

    min_val = min(scores.values())
    max_val = max(scores.values())

    if min_val == max_val:
        return {k: 1.0 for k in scores}

    return {
        k: (v - min_val) / (max_val - min_val)
        for k, v in scores.items()
    }


# ---------------------------------------------------------------------
# Automatic weight estimation
# ---------------------------------------------------------------------

def compute_variance_weights(
    tfidf_norm: Dict[str, float],
    cvalue_norm: Dict[str, float]
) -> Dict[str, float]:
    """
    Estimate weights proportionally to score variance.
    """

    def variance(values):
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    v_tfidf = variance(list(tfidf_norm.values()))
    v_cvalue = variance(list(cvalue_norm.values()))

    total = v_tfidf + v_cvalue

    if total == 0:
        return {"tfidf": 0.5, "cvalue": 0.5}

    return {
        "tfidf": v_tfidf / total,
        "cvalue": v_cvalue / total
    }


def compute_entropy_weights(
    tfidf_norm: Dict[str, float],
    cvalue_norm: Dict[str, float]
) -> Dict[str, float]:
    """
    Estimate weights based on Shannon entropy.
    """

    def entropy(values):
        eps = 1e-12
        probs = [v + eps for v in values]
        s = sum(probs)
        probs = [v / s for v in probs]
        return -sum(p * math.log2(p) for p in probs)

    h_tfidf = entropy(list(tfidf_norm.values()))
    h_cvalue = entropy(list(cvalue_norm.values()))

    inv_tfidf = 1 - h_tfidf
    inv_cvalue = 1 - h_cvalue

    total = inv_tfidf + inv_cvalue

    if total == 0:
        return {"tfidf": 0.5, "cvalue": 0.5}

    return {
        "tfidf": inv_tfidf / total,
        "cvalue": inv_cvalue / total
    }


# ---------------------------------------------------------------------
# Composite index
# ---------------------------------------------------------------------

def compute_terminologicity(
    tfidf_norm: Dict[str, float],
    cvalue_norm: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute composite terminologicity index.

    weights can be:
    - dict: {"tfidf": x, "cvalue": y}
    - "variance": automatic variance-based weighting
    - "entropy": automatic entropy-based weighting
    """

    if weights is None:
        weights = {"tfidf": 0.5, "cvalue": 0.5}

    if isinstance(weights, str):
        if weights == "variance":
            weights = compute_variance_weights(tfidf_norm, cvalue_norm)
        elif weights == "entropy":
            weights = compute_entropy_weights(tfidf_norm, cvalue_norm)
        else:
            raise ValueError(f"Unknown weight mode: {weights}")

    terminologicity = {}

    for term in tfidf_norm:
        terminologicity[term] = (
            weights["tfidf"] * tfidf_norm.get(term, 0.0)
            + weights["cvalue"] * cvalue_norm.get(term, 0.0)
        )

    return terminologicity


# ---------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------

def compute_statistics(
    candidates: List[Dict[str, Any]],
    documents: List[Dict[str, Any]],
    *,
    weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Enrich candidates with statistical metrics and terminologicity index.
    """

    n_documents = len({doc["doc_id"] for doc in documents})

    term_stats = compute_frequencies(candidates)
    tfidf = compute_tfidf(term_stats, n_documents)
    cvalue = compute_cvalue(term_stats)

    tfidf_norm = min_max_normalise(tfidf)
    cvalue_norm = min_max_normalise(cvalue)

    terminologicity = compute_terminologicity(
        tfidf_norm,
        cvalue_norm,
        weights
    )

    enriched = []

    for cand in candidates:
        lemma = cand["lemma"]
        enriched.append({
            **cand,
            "frequency": term_stats[lemma]["frequency"],
            "doc_frequency": term_stats[lemma]["doc_frequency"],
            "tf_idf": tfidf[lemma],
            "c_value": cvalue[lemma],
            "tf_idf_norm": tfidf_norm[lemma],
            "c_value_norm": cvalue_norm[lemma],
            "terminologicity": terminologicity[lemma]
        })

    return enriched
