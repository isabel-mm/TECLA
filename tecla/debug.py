"""
tecla/debug.py
──────────────
Logger de depuración con tiempos de ejecución.

Escribe en ``tecla_debug.txt`` dentro de la carpeta de resultados del
corpus (``_tecla_output/``) cada vez que se ejecuta el pipeline. Las
sesiones se acumulan en el mismo archivo (no se sobreescribe).

Uso desde el pipeline (interno):

    from tecla.debug import log, timer, start_session

    start_session("/ruta/al/corpus")

    with timer("Conversión PDF→TXT (5 archivos)"):
        build_corpus(...)

    log("Lengua detectada: es")

Ejemplo de salida en ``tecla_debug.txt``::

    2026-04-29 14:05:01  INFO  ════════════════════════════════════════
    2026-04-29 14:05:01  INFO  NUEVA SESIÓN TECLA  corpus: /mis/pdfs
    2026-04-29 14:05:01  INFO  ════════════════════════════════════════
    2026-04-29 14:05:01  INFO  [INICIO] Conversión PDF→TXT (5 archivos)
    2026-04-29 14:05:07  INFO  [FIN]    Conversión PDF→TXT (5 archivos) — 6.03 s
    2026-04-29 14:05:07  INFO  Lengua detectada: es
    2026-04-29 14:05:07  INFO  [INICIO] Carga modelo spaCy (es_core_news_md)
    2026-04-29 14:05:09  INFO  [FIN]    Carga modelo spaCy (es_core_news_md) — 1.87 s
    ...
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from pathlib import Path

_logger: logging.Logger | None = None
_log_path: Path | None = None

LOG_NAME = "tecla_debug.txt"


def _log_file(corpus_path: str = "") -> Path:
    """
    Dónde se guarda el registro: en la carpeta de resultados del corpus
    (``<carpeta de trabajo>/_tecla_output/``), junto a los gráficos. Si no se
    conoce el corpus o no se puede escribir ahí, en el directorio actual.
    """
    if corpus_path:
        try:
            out = Path(corpus_path).resolve().parent / "_tecla_output"
            out.mkdir(parents=True, exist_ok=True)
            return out / LOG_NAME
        except OSError:
            pass
    return Path.cwd() / LOG_NAME


def _get_logger(corpus_path: str = "") -> logging.Logger:
    global _logger, _log_path

    wanted = _log_file(corpus_path) if (corpus_path or _log_path is None) else _log_path
    if _logger is not None and wanted == _log_path:
        return _logger

    logger = logging.getLogger("tecla.debug")
    logger.setLevel(logging.DEBUG)
    for handler in list(logger.handlers):      # nueva sesión con otro corpus
        logger.removeHandler(handler)
        handler.close()

    fh = logging.FileHandler(wanted, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    logger.propagate = False
    _logger, _log_path = logger, wanted
    return logger


def start_session(corpus_path: str = "") -> None:
    """Escribe una cabecera de sesión en el archivo de debug."""
    logger = _get_logger(corpus_path)
    sep = "═" * 56
    logger.info(sep)
    logger.info(f"NUEVA SESIÓN TECLA  corpus: {corpus_path or '(no especificado)'}")
    logger.info(sep)


def log(message: str, level: str = "info") -> None:
    """Registra un mensaje en tecla_debug.txt."""
    getattr(_get_logger(), level)(message)


@contextmanager
def timer(label: str):
    """
    Bloque de temporización. Registra inicio, fin y duración.

    Ejemplo::

        with timer("Procesamiento spaCy (3 docs)"):
            documents = corpus_to_documents(...)
    """
    logger = _get_logger()
    logger.info(f"[INICIO] {label}")
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t0
        logger.info(f"[FIN]    {label} — {elapsed:.2f} s")
