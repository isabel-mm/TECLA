# pipeline/pipeline.py

import os
from pathlib import Path
from typing import Optional, Callable

from tecla.corpus.builder import build_corpus, build_corpus_from_txt
from tecla.corpus.processor import corpus_to_documents
from tecla.extractor.hybrid_extractor import HybridTermExtractor
from tecla.debug import log as dlog, timer, start_session


_SPACY_MODEL_TABLE = {
    "en": "en_core_web_lg",
    "es": "es_core_news_md",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}


def run_tecla_pipeline(
    corpus_path: Path,
    language: Optional[str],
    cleaning_options: dict,
    extraction_options: dict,
    spacy_model: Optional[str] = None,
    on_progress: Optional[Callable[[str], None]] = None,
    on_corpus_ready: Optional[Callable] = None,
) -> list:
    """
    Run the full TECLA pipeline.

    Parameters
    ----------
    corpus_path : Path
        Folder containing PDFs or TXTs.
    language : str or None
        Language code. Pass None or "auto" to detect automatically.
    cleaning_options : dict
        Options forwarded to build_corpus / build_corpus_from_txt.
    extraction_options : dict
        Options for the term extractor.
    spacy_model : str, optional
        spaCy model name. Derived from language if not given.
    on_progress : callable, optional
        Called with a status string at each pipeline step.
        Useful for GUI progress reporting.
    on_corpus_ready : callable, optional
        Called with (documents, clean_folder, language) after processing.
    """

    def _log(msg: str):
        print(msg)
        dlog(msg)
        if on_progress:
            on_progress(msg)

    start_session(str(corpus_path))

    # ------------------------------------------------------------------
    # 1. Detect input format
    # ------------------------------------------------------------------

    out_folder = str(corpus_path / "_tecla_txt")

    all_files = []
    for dirpath, _, filenames in os.walk(corpus_path):
        if "_tecla_txt" in dirpath:
            continue
        for fname in filenames:
            all_files.append(os.path.join(dirpath, fname))

    has_pdfs = any(f.lower().endswith(".pdf") for f in all_files)
    has_txts = any(f.lower().endswith(".txt") for f in all_files)

    if has_pdfs:
        pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
        _log(f"{len(pdf_files)} archivo(s) PDF encontrados — convirtiendo a texto…")
        with timer(f"Conversión PDF→TXT ({len(pdf_files)} archivo(s))"):
            build_corpus(
                input_folder=str(corpus_path),
                out_folder=out_folder,
                metadata_file=str(corpus_path / "metadata.csv"),
                clean=True,
                clean_params={**cleaning_options},
                compute_stats=False,
            )
        _log("Conversión y limpieza de PDFs completada.")

    elif has_txts:
        txt_files = [f for f in all_files if f.lower().endswith(".txt")]
        _log(f"{len(txt_files)} archivo(s) TXT encontrados — aplicando limpieza…")
        with timer(f"Limpieza TXT ({len(txt_files)} archivo(s))"):
            build_corpus_from_txt(
                input_folder=str(corpus_path),
                out_folder=out_folder,
                metadata_file=str(corpus_path / "metadata.csv"),
                clean=True,
                clean_params={**cleaning_options},
                compute_stats=False,
            )
        _log("¡Limpieza y procesamiento completados!")

    else:
        _log(f"No se encontraron archivos PDF ni TXT en '{corpus_path}'.")
        return []

    clean_folder = str(Path(out_folder) / "clean")

    # ------------------------------------------------------------------
    # 2. Auto-detect language
    # ------------------------------------------------------------------

    if language is None or language == "auto":
        _log("Detectando idioma…")
        with timer("Detección de idioma"):
            language = _detect_language_from_folder(clean_folder)
        _log(f"Idioma detectado: '{language}'")

    # ------------------------------------------------------------------
    # 3. Load spaCy model and build document representations
    # ------------------------------------------------------------------

    resolved_model = spacy_model or _SPACY_MODEL_TABLE.get(
        language, f"{language}_core_news_sm"
    )
    _log(f"Cargando modelo lingüístico '{resolved_model}'…")

    with timer(f"Procesamiento spaCy — modelo '{resolved_model}'"):
        documents = corpus_to_documents(
            corpus_folder=clean_folder,
            language=language,
            spacy_model=resolved_model,
        )

    if not documents:
        _log("No se pudo procesar ningún documento.")
        return []

    total_tokens = sum(len(d["tokens"]) for d in documents)
    _log(f"{len(documents)} documento(s) — {total_tokens:,} tokens procesados.")
    dlog(f"Corpus: {len(documents)} docs, {total_tokens:,} tokens")

    if on_corpus_ready:
        on_corpus_ready(documents, clean_folder, language)

    # ------------------------------------------------------------------
    # 4. Extract term candidates
    # ------------------------------------------------------------------

    _log("Extrayendo candidatos a término…")

    weights = extraction_options.get("weights")
    grammar_path = extraction_options.get("grammar_path")
    extractor = HybridTermExtractor(
        language=language,
        weights=weights,
        grammar_path=Path(grammar_path) if grammar_path else None,
    )

    percentile      = extraction_options.get("percentile")
    multiword_only  = extraction_options.get("multiword_only", False)
    max_term_length = extraction_options.get("max_term_length")
    min_len = 2 if multiword_only else 1
    term_length = (min_len, max_term_length) if max_term_length is not None else (
        (2, None) if multiword_only else None
    )

    _log("Puntuando candidatos...")
    with timer(f"Extracción de candidatos (percentil={percentile})"):
        results = extractor.extract(
            documents=documents,
            percentile=percentile,
            term_length=term_length,
        )

    _log(f"Completado — {len(results)} candidatos extraídos.")
    dlog(f"Extracción completada: {len(results)} candidatos")
    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _detect_language_from_folder(folder: str) -> str:
    from tecla.corpus.language_detection import detect_language

    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith(".txt"):
            fpath = os.path.join(folder, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(3000)
            if text.strip():
                lang, _ = detect_language(text)
                return lang

    return "en"
