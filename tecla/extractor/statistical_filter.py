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

from collections import Counter, defaultdict
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
    Compute term frequency, document frequency, and per-document counts.
    """
    freq = defaultdict(int)
    doc_freq = defaultdict(set)
    per_doc: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for cand in candidates:
        lemma = cand["lemma"]
        doc_id = cand["doc_id"]

        freq[lemma] += 1
        doc_freq[lemma].add(doc_id)
        per_doc[lemma][doc_id] += 1

    return {
        lemma: {
            "frequency": freq[lemma],
            "doc_frequency": len(doc_freq[lemma]),
            "per_doc": dict(per_doc[lemma]),
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

def _is_nested(t1_words: list, t2_words: list) -> bool:
    """Return True if t1_words appears as a contiguous sub-sequence in t2_words."""
    n = len(t1_words)
    for i in range(len(t2_words) - n + 1):
        if t2_words[i:i + n] == t1_words:
            return True
    return False


def compute_cvalue(
    term_stats: Dict[str, Dict[str, int]]
) -> Dict[str, float]:
    """
    Compute C-value scores for candidate terms.

    C-value(a) = log2(|a|) * (f(a) - (1/P(a)) * sum_{t in P(a)} f(t))
    where P(a) is the set of longer terms that contain a as a sub-sequence.
    """

    terms = list(term_stats.keys())
    cvalue = {}

    terms_words = {t: t.split() for t in terms}
    nested_in: Dict[str, list] = defaultdict(list)

    for t1 in terms:
        w1 = terms_words[t1]
        for t2 in terms:
            if t1 == t2:
                continue
            w2 = terms_words[t2]
            # t1 can only be nested inside a *longer* term
            if len(w1) < len(w2) and _is_nested(w1, w2):
                nested_in[t1].append(t2)

    for term in terms:
        f = term_stats[term]["frequency"]
        length = len(terms_words[term])
        nested_terms = nested_in.get(term, [])

        if length == 1:
            log_len = 1.0
        else:
            log_len = log2(length)

        if not nested_terms:
            cvalue[term] = log_len * f
        else:
            nested_freq_sum = sum(term_stats[t]["frequency"] for t in nested_terms)
            cvalue[term] = log_len * (f - (nested_freq_sum / len(nested_terms)))

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
# NC-value
# ---------------------------------------------------------------------

def compute_ncvalue(
    term_stats: Dict[str, Dict[str, int]],
    candidates: List[Dict[str, Any]],
    cvalue: Dict[str, float],
    n_reference: int = 200,
) -> Dict[str, float]:
    """
    Compute NC-value scores (Frantzi et al. 2000).

        NC-value(a) = 0.8 * C-value(a) + 0.2 * sum_{b in C_a} f_a(b) * weight(b)

    where
        C_a       = context words of a: nouns, adjectives and verbs within
                    ±2 tokens of its occurrences
        f_a(b)    = number of times b appears as a context word of a
        weight(b) = t(b) / n, with t(b) the number of reference terms b
                    appears with and n the number of reference terms

    As in Frantzi et al., the reference terms are the top `n_reference`
    candidates of the list ranked by C-value. Because f_a(b) counts every
    co-occurrence, the context factor grows with frequency, on the same
    scale as C-value.
    """
    context_of: Dict[str, Counter] = defaultdict(Counter)
    for cand in candidates:
        context_of[cand["lemma"]].update(cand.get("context_words", []))

    reference = sorted(term_stats, key=lambda t: cvalue.get(t, 0.0), reverse=True)
    reference = reference[:max(1, min(n_reference, len(reference)))]

    t_b: Counter = Counter()
    for term in reference:
        t_b.update(context_of[term].keys())
    weight = {b: count / len(reference) for b, count in t_b.items()}

    ncvalue: Dict[str, float] = {}
    for lemma in term_stats:
        context_factor = sum(f * weight.get(b, 0.0) for b, f in context_of[lemma].items())
        ncvalue[lemma] = 0.8 * cvalue.get(lemma, 0.0) + 0.2 * context_factor

    return ncvalue


# ---------------------------------------------------------------------
# Composite index
# ---------------------------------------------------------------------

def compute_terminologicity(
    tfidf_norm: Dict[str, float],
    ncvalue_norm: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute composite terminologicity index.

    Combines normalised TF-IDF and normalised NC-value (which already
    subsumes C-value + context information).

    weights can be:
    - dict: {"tfidf": x, "ncvalue": y}  (por defecto, media: 0,5 y 0,5;
      se acepta también la clave antigua "cvalue", que se aplica al NC-value)
    - "variance": automatic variance-based weighting
    - "entropy": automatic entropy-based weighting
    """

    if weights is None:
        weights = {"tfidf": 0.5, "ncvalue": 0.5}

    if isinstance(weights, str):
        if weights == "variance":
            weights = compute_variance_weights(tfidf_norm, ncvalue_norm)
        elif weights == "entropy":
            weights = compute_entropy_weights(tfidf_norm, ncvalue_norm)
        else:
            raise ValueError(f"Unknown weight mode: {weights}")

    w_tfidf = weights["tfidf"]
    w_nc = weights.get("ncvalue", weights.get("cvalue"))
    if w_nc is None:
        raise ValueError('weights debe incluir "ncvalue" (o la clave antigua "cvalue").')

    terminologicity = {}

    for term in tfidf_norm:
        terminologicity[term] = (
            w_tfidf * tfidf_norm.get(term, 0.0)
            + w_nc * ncvalue_norm.get(term, 0.0)
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

    Metrics computed per candidate lemma:
    - frequency, doc_frequency, freq_rel, per_doc
    - tf_idf, tf_idf_norm
    - c_value, c_value_norm
    - nc_value, nc_value_norm  (C-value extended with context information)
    - terminologicity  (weighted combination of tf_idf_norm and nc_value_norm)
    """

    n_documents = len({doc["doc_id"] for doc in documents})
    total_corpus_tokens = sum(len(d.get("tokens", [])) for d in documents)

    term_stats = compute_frequencies(candidates)
    tfidf = compute_tfidf(term_stats, n_documents)
    cvalue = compute_cvalue(term_stats)
    ncvalue = compute_ncvalue(term_stats, candidates, cvalue)

    tfidf_norm = min_max_normalise(tfidf)
    cvalue_norm = min_max_normalise(cvalue)
    ncvalue_norm = min_max_normalise(ncvalue)

    terminologicity = compute_terminologicity(
        tfidf_norm,
        ncvalue_norm,
        weights
    )

    enriched = []

    for cand in candidates:
        lemma = cand["lemma"]
        enriched.append({
            **cand,
            "frequency": term_stats[lemma]["frequency"],
            "doc_frequency": term_stats[lemma]["doc_frequency"],
            "per_doc": term_stats[lemma]["per_doc"],
            "freq_rel": round(
                term_stats[lemma]["frequency"] / total_corpus_tokens * 1000, 4
            ) if total_corpus_tokens else 0.0,
            "tf_idf": tfidf[lemma],
            "c_value": cvalue[lemma],
            "nc_value": ncvalue[lemma],
            "tf_idf_norm": tfidf_norm[lemma],
            "c_value_norm": cvalue_norm[lemma],
            "nc_value_norm": ncvalue_norm[lemma],
            "terminologicity": terminologicity[lemma],
        })

    return enriched
