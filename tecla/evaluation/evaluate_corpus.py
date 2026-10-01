"""
TECLA – Evaluación de representatividad terminológica del corpus
----------------------------------------------------------------
Ejecutar:
    python -m tecla.evaluation.evaluate_corpus <ruta_corpus> [opciones]

Ejemplos:
    python -m tecla.evaluation.evaluate_corpus corpus/en --lang en
    python -m tecla.evaluation.evaluate_corpus corpus/es --lang es --output resultados_es.csv
    python -m tecla.evaluation.evaluate_corpus corpus/en --lang en --gold glosario_en.csv

El corpus debe ser la carpeta que contiene los PDFs o TXTs.
Si se indica --gold, el CSV debe tener al menos una columna 'term'.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada principal
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_corpus(
    corpus_path: Path,
    language: str = "auto",
    gold_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    n_bootstrap: int = 200,
    top_n_stability: int = 30,
) -> Dict[str, Any]:
    """
    Evalúa la representatividad terminológica de un corpus.

    Parámetros
    ----------
    corpus_path : Path
        Carpeta con los PDFs o TXTs del corpus.
    language : str
        Código de lengua ('en', 'es', 'auto').
    gold_path : Path, opcional
        CSV con columna 'term': estándar de referencia externo para cobertura.
    output_path : Path, opcional
        Ruta para guardar el informe en CSV.
    n_bootstrap : int
        Iteraciones del bootstrap de estabilidad (default 200).
    top_n_stability : int
        Número de términos top a evaluar en estabilidad (default 30).

    Devuelve
    -------
    dict con todas las métricas y la puntuación compuesta.
    """
    from pipeline.pipeline import run_tecla_pipeline
    from tecla.evaluation.corpus_metrics import (
        compute_heaps,
        compute_hapax_ratio,
        compute_dp,
        dp_stats,
        compute_bootstrap_stability,
        compute_term_adequacy,
        compute_representativity_score,
    )

    # ── 1. Ejecutar pipeline y capturar documentos ────────────────────────────
    _captured: Dict[str, Any] = {}

    def _on_corpus_ready(docs, _, lang):
        _captured["documents"] = docs
        _captured["language"] = lang

    print(f"\n{'═' * 60}")
    print(f"  TECLA — Evaluación de representatividad")
    print(f"  Corpus : {corpus_path}")
    print(f"{'═' * 60}\n")

    results = run_tecla_pipeline(
        corpus_path=corpus_path,
        language=None if language == "auto" else language,
        cleaning_options={
            "structure": True,
            "remove_bibliography_flag": True,
            "remove_captions_flag": True,
            "remove_section_headers_flag": True,
        },
        extraction_options={
            "weights": {"tfidf": 0.5, "ncvalue": 0.5},
        },
        on_progress=lambda msg: print(f"  {msg}"),
        on_corpus_ready=_on_corpus_ready,
    )

    documents: List[Dict[str, Any]] = _captured.get("documents", [])
    if not documents:
        print("✗  No se procesó ningún documento.")
        return {}

    n_docs = len(documents)
    total_tokens = sum(len(d.get("tokens", [])) for d in documents)

    # ── 2. Construir doc_stats (necesario para DP y bootstrap) ───────────────
    doc_stats = [
        {"doc_id": d["doc_id"], "tokens": len(d.get("tokens", []))}
        for d in documents
    ]

    # ── 3. Calcular métricas ──────────────────────────────────────────────────
    print("\n  Calculando métricas de representatividad…")

    heaps   = compute_heaps(documents)
    hapax   = compute_hapax_ratio(documents)

    if results:
        dp_scores  = compute_dp(results, doc_stats)
        dp_summary = dp_stats(dp_scores, results, top_n=min(50, len(results)))
        stability  = compute_bootstrap_stability(
            results, doc_stats,
            n_bootstrap=n_bootstrap,
            top_n=min(top_n_stability, len(results)),
        )
        adequacy = compute_term_adequacy(results, n_docs, total_tokens)
    else:
        dp_summary = {"mean": 0.5, "median": 0.5, "pct_high": 0.0}
        stability  = {"stability_index": None, "term_stability": {}, "n_bootstrap": 0}
        adequacy   = {}

    score = compute_representativity_score(heaps, hapax, dp_summary, stability)

    # ── 4. Cobertura contra estándar externo (opcional) ───────────────────────
    coverage: Optional[Dict[str, Any]] = None
    if gold_path is not None:
        from tecla.evaluation.term_eval import evaluate_extraction
        import csv as _csv
        try:
            with open(gold_path, encoding="utf-8") as f:
                gold_terms = [row["term"] for row in _csv.DictReader(f) if row.get("term")]
            coverage = evaluate_extraction(results, gold_terms, mode="exact")
        except Exception as exc:
            print(f"  ⚠  No se pudo calcular cobertura: {exc}")

    # ── 5. Imprimir informe ───────────────────────────────────────────────────
    report = _build_report(
        documents, results, heaps, hapax, dp_summary,
        stability, adequacy, score, coverage,
    )
    _print_report(report)

    # ── 6. Guardar CSV si se pidió ────────────────────────────────────────────
    if output_path is not None:
        _save_report_csv(report, output_path)
        print(f"\n  Informe guardado en: {output_path}\n")

    return report


# ─────────────────────────────────────────────────────────────────────────────
# Construcción del informe
# ─────────────────────────────────────────────────────────────────────────────

def _build_report(
    documents, results, heaps, hapax, dp_summary,
    stability, adequacy, score, coverage,
) -> Dict[str, Any]:

    n_docs       = len(documents)
    total_tokens = sum(len(d.get("tokens", [])) for d in documents)
    n_terms      = len(results)

    beta     = heaps.get("beta")
    beta_min, beta_max = 0.2, 0.8
    norm_beta = (
        round(max(0.0, min(1.0, (beta_max - beta) / (beta_max - beta_min))), 4)
        if beta is not None else None
    )

    return {
        # Corpus
        "n_documentos":    n_docs,
        "total_tokens":    total_tokens,
        "total_terminos":  n_terms,

        # Saturación — Heaps
        "heaps_k":         heaps.get("k"),
        "heaps_beta":      beta,
        "heaps_norm_beta": norm_beta,
        "heaps_interp":    heaps.get("interpretation", ""),

        # Masa textual — Hápax
        "hapax_ratio":     hapax.get("ratio"),
        "hapax_n":         hapax.get("n_hapax"),
        "vocab_types":     hapax.get("n_types"),

        # Dispersión — DP de Gries
        "dp_mean":         dp_summary.get("mean"),
        "dp_median":       dp_summary.get("median"),
        "dp_pct_bien_dist": dp_summary.get("pct_high"),

        # Estabilidad — Bootstrap
        "estabilidad_idx": stability.get("stability_index"),
        "bootstrap_iters": stability.get("n_bootstrap"),

        # Adecuación terminológica
        "densidad_term":   adequacy.get("density"),
        "tasa_confirmacion": adequacy.get("confirmation_rate"),
        "cobertura_clave": adequacy.get("key_coverage"),
        "ratio_multip":    adequacy.get("multiword_ratio"),

        # Puntuación compuesta
        "puntuacion":      score.get("score"),
        "nivel":           score.get("label"),
        "descripcion":     score.get("description"),

        # Cobertura externa (opcional)
        "cobertura_ext_precision": coverage.get("precision") if coverage else None,
        "cobertura_ext_recall":    coverage.get("recall")    if coverage else None,
        "cobertura_ext_f1":        coverage.get("f1")        if coverage else None,
    }


def _print_report(r: Dict[str, Any]) -> None:
    sep = "─" * 60

    print(f"\n{sep}")
    print("  CORPUS")
    print(sep)
    print(f"  Documentos          : {r['n_documentos']}")
    print(f"  Tokens totales      : {r['total_tokens']:,}")
    print(f"  Términos extraídos  : {r['total_terminos']}")

    print(f"\n{sep}")
    print("  SATURACIÓN  (Ley de Heaps — tokens del corpus)")
    print(sep)
    if r["heaps_beta"] is not None:
        print(f"  K                   : {r['heaps_k']:.3f}")
        print(f"  β                   : {r['heaps_beta']:.4f}  →  Norm-β = {r['heaps_norm_beta']:.4f}")
        print(f"  Interpretación      : {r['heaps_interp']}")
    else:
        print("  Corpus insuficiente para ajustar Heaps.")

    print(f"\n{sep}")
    print("  MASA TEXTUAL  (ratio de hápax)")
    print(sep)
    print(f"  Tipos de vocabulario: {r['vocab_types']:,}")
    print(f"  Hápax               : {r['hapax_n']:,}  ({r['hapax_ratio']:.1%})")
    if r["hapax_ratio"] is not None:
        if r["hapax_ratio"] > 0.40:
            print("  ⚠  Ratio alto: el corpus puede carecer de suficiente masa textual.")
        elif r["hapax_ratio"] < 0.20:
            print("  ✓  Ratio bajo: los términos aparecen con buena frecuencia.")

    print(f"\n{sep}")
    print("  DISPERSIÓN  (DP de Gries — distribución de términos)")
    print(sep)
    if r["dp_mean"] is not None:
        print(f"  DP medio (top 50)   : {r['dp_mean']:.4f}  (0 = dispersión perfecta, 1 = concentrado)")
        print(f"  DP mediana          : {r['dp_median']:.4f}")
        print(f"  % bien distribuidos : {r['dp_pct_bien_dist']:.1%}  (DP < 0.40)")
        if r["dp_mean"] < 0.35:
            print("  ✓  Términos principales bien distribuidos en el corpus.")
        elif r["dp_mean"] > 0.60:
            print("  ⚠  Los términos principales están concentrados en pocos documentos.")

    print(f"\n{sep}")
    print("  ESTABILIDAD  (bootstrap de rankings)")
    print(sep)
    if r["estabilidad_idx"] is not None:
        print(f"  Índice de estabilidad: {r['estabilidad_idx']:.4f}  ({r['bootstrap_iters']} iteraciones)")
        if r["estabilidad_idx"] >= 0.75:
            print("  ✓  Rankings terminológicos estables.")
        elif r["estabilidad_idx"] < 0.50:
            print("  ⚠  Rankings inestables: el corpus puede ser insuficiente.")
    else:
        print("  No calculado (corpus con un solo documento).")

    print(f"\n{sep}")
    print("  ADECUACIÓN TERMINOLÓGICA")
    print(sep)
    if r["densidad_term"] is not None:
        print(f"  Densidad terminológica  : {r['densidad_term']:.4%}")
        print(f"  Tasa de confirmación    : {r['tasa_confirmacion']:.1%}  (términos en ≥2 docs)")
        print(f"  Cobertura términos clave: {r['cobertura_clave']:.1%}")
        print(f"  Ratio multipalabra      : {r['ratio_multip']:.1%}")

    if r["cobertura_ext_recall"] is not None:
        print(f"\n{sep}")
        print("  COBERTURA EXTERNA  (vs. estándar de referencia)")
        print(sep)
        print(f"  Precisión : {r['cobertura_ext_precision']:.1%}")
        print(f"  Recall    : {r['cobertura_ext_recall']:.1%}   ← % del glosario cubierto por el corpus")
        print(f"  F1        : {r['cobertura_ext_f1']:.1%}")

    print(f"\n{'═' * 60}")
    score = r["puntuacion"]
    label = r["nivel"]
    color_sym = "✓✓" if score >= 75 else ("✓" if score >= 60 else ("△" if score >= 40 else "✗"))
    print(f"  PUNTUACIÓN COMPUESTA : {score}/100  —  {color_sym}  {label.upper()}")
    if r["descripcion"]:
        print(f"\n  {r['descripcion']}")
    print(f"{'═' * 60}\n")


def _save_report_csv(report: Dict[str, Any], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["métrica", "valor"])
        for k, v in report.items():
            writer.writerow([k, v])


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Evaluación de representatividad terminológica de un corpus con TECLA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("corpus", type=Path, help="Carpeta del corpus (PDFs o TXTs).")
    p.add_argument(
        "--lang", default="auto",
        help="Lengua del corpus: en, es, fr… o 'auto' para detección automática (por defecto: auto).",
    )
    p.add_argument(
        "--output", type=Path, default=None,
        help="Ruta donde guardar el informe en CSV.",
    )
    p.add_argument(
        "--gold", type=Path, default=None,
        help="CSV con columna 'term': estándar de referencia externo para cobertura.",
    )
    p.add_argument(
        "--bootstrap", type=int, default=200,
        help="Iteraciones del bootstrap de estabilidad (por defecto: 200).",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    evaluate_corpus(
        corpus_path=args.corpus,
        language=args.lang,
        gold_path=args.gold,
        output_path=args.output,
        n_bootstrap=args.bootstrap,
    )
