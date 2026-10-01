"""
tecla/debug.py
──────────────
Logger de depuración con tiempos de ejecución.

Escribe en ``tecla_debug.txt`` dentro del directorio de trabajo actual
cada vez que se ejecuta el pipeline. Las sesiones se acumulan en el
mismo archivo (no se sobreescribe).

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


def _get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    log_path = Path.cwd() / "tecla_debug.txt"

    logger = logging.getLogger("tecla.debug")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(fh)

    logger.propagate = False
    _logger = logger
    return logger


def start_session(corpus_path: str = "") -> None:
    """Escribe una cabecera de sesión en el archivo de debug."""
    logger = _get_logger()
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
