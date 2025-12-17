# pipeline/pipeline.py

from pathlib import Path
from tecla.corpus.builder import build_corpus
from tecla.extractor.hybrid_extractor import HybridTermExtractor


def run_tecla_pipeline(
    corpus_path: Path,
    language: str,
    cleaning_options: dict,
    extraction_options: dict,
):
    """
    Runs the full TECLA pipeline.

    Parameters
    ----------
    corpus_path : Path
        Folder containing the corpus (PDF or TXT).
    language : str
        Language code ("en", "es").
    cleaning_options : dict
        Options passed to build_corpus(clean_params).
    extraction_options : dict
        Options for term extraction.

    Returns
    -------
    list[dict]
        Extracted terms with scores.
    """

    # ------------------------------------------------------------------
    # 1. Build corpus
    # ------------------------------------------------------------------

    documents = build_corpus(
        input_folder=str(corpus_path),
        out_folder=str(corpus_path / "_tecla_txt"),
        metadata_file=str(corpus_path / "metadata.csv"),
        clean=True,
        clean_params={**cleaning_options, "language": language},
        compute_stats=False,
    )

    # ------------------------------------------------------------------
    # 2. Normalize documents (CRITICAL STEP)
    # ------------------------------------------------------------------

    normalized_docs = []

    for i, doc in enumerate(documents):
        if isinstance(doc, str):
            normalized_docs.append({
                "doc_id": f"doc_{i}",
                "text": doc,
                "language": language,
            })
        elif isinstance(doc, dict):
            normalized_docs.append(doc)
        else:
            raise TypeError(
                f"Unsupported document type: {type(doc)}"
            )

    # ------------------------------------------------------------------
    # 3. Configure extractor
    # ------------------------------------------------------------------

    weights = extraction_options.get("weights")

    extractor = HybridTermExtractor(
        language=language,
        weights=weights,
    )

    # ------------------------------------------------------------------
    # 4. Resolve extraction options
    # ------------------------------------------------------------------

    percentile = extraction_options.get("percentile")

    if extraction_options.get("multiword_only", False):
        term_length = (2, None)
    else:
        term_length = None

    # ------------------------------------------------------------------
    # 5. Extract terms
    # ------------------------------------------------------------------

    results = extractor.extract(
        documents=normalized_docs,
        percentile=percentile,
        term_length=term_length,
    )

    return results
