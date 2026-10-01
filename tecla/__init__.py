"""
TECLA: Toolkit for Corpus-based Terminology Extraction.

Quick start
-----------
    from tecla import build_corpus, HybridTermExtractor
    from tecla.corpus.processor import corpus_to_documents

    build_corpus("my_pdfs/", out_folder="corpus_txt/", clean=True,
                 clean_params={"language": "es", "structure": True})

    docs = corpus_to_documents("corpus_txt/clean/", language="es",
                               spacy_model="es_core_news_md")

    extractor = HybridTermExtractor(language="es")
    terms = extractor.extract(docs, top_k=100)
"""

from .corpus.builder import build_corpus, build_corpus_from_txt
from .corpus.cleaning import clean_text
from .corpus.statistics import corpus_statistics
from .corpus.metadata import infer_metadata
from .corpus.language_detection import detect_language
from .extractor.hybrid_extractor import HybridTermExtractor
from .evaluation.term_eval import evaluate_extraction

__all__ = [
    "build_corpus",
    "build_corpus_from_txt",
    "clean_text",
    "corpus_statistics",
    "infer_metadata",
    "detect_language",
    "HybridTermExtractor",
    "evaluate_extraction",
]
