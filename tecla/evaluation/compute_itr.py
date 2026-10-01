"""Módulo obsoleto: usa tecla.evaluation.compute_irt (se mantiene por compatibilidad)."""
import warnings

from .compute_irt import evaluate_corpus_irt_anotado


def evaluate_corpus_itr(*args, **kwargs) -> dict:
    """Alias obsoleto de evaluate_corpus_irt_anotado."""
    warnings.warn("evaluate_corpus_itr está obsoleto; usa evaluate_corpus_irt_anotado.",
                  DeprecationWarning, stacklevel=2)
    return evaluate_corpus_irt_anotado(*args, **kwargs)
