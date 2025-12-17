# tecla/app/pipeline.py

from tecla.corpus.builder import build_corpus
from tecla.extractor.hybrid_extractor import HybridTermExtractor


def run_tecla_pipeline(
    corpus_path: str,
    language: str,
    *,
    multiword_only: bool = True,
    weights: dict | None = None,
    percentile: int = 90,
) -> list[dict]:
    """
    Orchestrates the TECLA extraction pipeline.
    """

    # 1. Build corpus
    documents = build_corpus(
        input_folder=corpus_path,
        out_folder=f"{corpus_path}/_tecla_txt",
        metadata_file=f"{corpus_path}/metadata.csv",
        clean=True,
        clean_params={
            "structure": True,
            "lemmatize_flag": True,
            "remove_bibliography_flag": True,
            "language": language,
        },
        compute_stats=False,
    )

    # 2. Configure extractor
    extractor = HybridTermExtractor(
        language=language,
        weights=weights,
    )

    term_length = (2, None) if multiword_only else None

    # 3. Extract terms
    results = extractor.extract(
        documents=documents,
        percentile=percentile,
        term_length=term_length,
    )

    return results
