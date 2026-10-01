from .compute_irt import evaluate_corpus_irt_anotado
from .compute_itr import evaluate_corpus_itr  # alias obsoleto
from .evaluate_corpus import evaluate_corpus
from .term_eval import evaluate_extraction, evaluate_from_csv
from .metrics import (
    compute_growth_curve,
    compute_itc_norm,
    compute_matetr,
    compute_heaps_beta,
    analyze_term_coverage_sampling,
    compute_normalized_mean_coverage,
    compute_irt_anotado,
    compute_itr,  # alias obsoleto
    extract_all_terms,
)

__all__ = [
    "evaluate_corpus_irt_anotado",
    "evaluate_corpus_itr",
    "evaluate_corpus",
    "evaluate_extraction",
    "evaluate_from_csv",
    "compute_growth_curve",
    "compute_itc_norm",
    "compute_matetr",
    "compute_heaps_beta",
    "analyze_term_coverage_sampling",
    "compute_normalized_mean_coverage",
    "compute_irt_anotado",
    "compute_itr",
    "extract_all_terms",
]
