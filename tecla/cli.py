"""
TECLA – Command-Line Interface

Usage examples
--------------
    # Extract terms from a PDF corpus
    tecla extract --corpus pdfs/ --lang es --multiword --top-k 100

    # Extract and export to CSV + TBX
    tecla extract --corpus pdfs/ --lang es --output terms.csv --tbx terms.tbx

    # Compute corpus statistics
    tecla stats --corpus corpus_txt/clean/ --lang es --output stats.csv

    # Evaluate extracted terms against a gold standard
    tecla evaluate --extracted terms.csv --gold gold.csv --mode exact
"""

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Subcommand: extract
# ---------------------------------------------------------------------------

def _cmd_extract(args):
    from pipeline.pipeline import run_tecla_pipeline

    cleaning = {
        "structure": args.structure,
        "remove_bibliography_flag": args.remove_bibliography,
        "lemmatize_flag": args.lemmatize,
    }

    extraction = {
        "multiword_only": args.multiword,
        "percentile": args.percentile,
        "weights": {"tfidf": args.tfidf_weight, "ncvalue": 1.0 - args.tfidf_weight},
    }

    results = run_tecla_pipeline(
        corpus_path=Path(args.corpus),
        language=args.lang,
        cleaning_options=cleaning,
        extraction_options=extraction,
    )

    if not results:
        print("No terms extracted.", file=sys.stderr)
        return

    if args.top_k:
        results = results[: args.top_k]

    # --- CSV output ---
    if args.output:
        import csv
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "term", "lemma", "language", "length", "frequency",
            "doc_frequency", "tf_idf", "c_value", "terminologicity",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Results saved to '{args.output}'")

    # --- TBX output ---
    if args.tbx:
        from tecla.extractor.tbx_export import export_tbx
        export_tbx(results, args.tbx, language=args.lang)

    # --- Console output ---
    print(f"\nExtracted {len(results)} terms\n")
    for i, t in enumerate(results[:20], 1):
        print(f"  {i:>3}. {t['term']:<40} {t['terminologicity']:.4f}")
    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more.")


# ---------------------------------------------------------------------------
# Subcommand: stats
# ---------------------------------------------------------------------------

def _cmd_stats(args):
    from tecla.corpus.statistics import corpus_statistics

    doc_stats = corpus_statistics(
        input_folder=args.corpus,
        language=args.lang,
        output_csv=args.output or None,
    )

    print(f"\nCorpus statistics — {len(doc_stats)} document(s)\n")
    header = f"{'File':<35} {'Tokens':>8} {'Types':>8} {'TTR':>6} {'Sents':>6}"
    print(header)
    print("-" * len(header))
    for d in doc_stats:
        print(
            f"  {d['filename']:<33} {d['token_count']:>8} "
            f"{d['type_count']:>8} {d['ttr']:>6.3f} {d['sentence_count']:>6}"
        )

    if args.output:
        print(f"\n✅ Statistics saved to '{args.output}'")


# ---------------------------------------------------------------------------
# Subcommand: evaluate
# ---------------------------------------------------------------------------

def _cmd_evaluate(args):
    from tecla.evaluation.term_eval import evaluate_from_csv

    results = evaluate_from_csv(
        extracted_csv=args.extracted,
        gold_csv=args.gold,
        extracted_col=args.extracted_col,
        gold_col=args.gold_col,
        mode=args.mode,
    )

    print(f"\nEvaluation results (mode={args.mode})\n")
    print(f"  Precision : {results['precision']:.4f}")
    print(f"  Recall    : {results['recall']:.4f}")
    print(f"  F1        : {results['f1']:.4f}")
    print(f"  TP={results['tp']}  FP={results['fp']}  FN={results['fn']}")

    if args.verbose:
        if results["false_negatives"]:
            print(f"\nFalse negatives (in gold, not extracted):")
            for t in sorted(results["false_negatives"])[:20]:
                print(f"  - {t}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tecla",
        description="TECLA – Toolkit for Corpus-based Terminology Extraction",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- extract ----
    p_extract = sub.add_parser("extract", help="Extract terms from a corpus.")
    p_extract.add_argument("--corpus", required=True, help="Path to corpus folder (PDFs).")
    p_extract.add_argument("--lang", required=True, help="Language code (en, es, fr…).")
    p_extract.add_argument("--output", default=None, help="CSV output path.")
    p_extract.add_argument("--tbx", default=None, help="TBX output path.")
    p_extract.add_argument("--top-k", type=int, default=None, dest="top_k")
    p_extract.add_argument("--percentile", type=float, default=None)
    p_extract.add_argument("--multiword", action="store_true", default=False)
    p_extract.add_argument("--structure", action="store_true", default=False)
    p_extract.add_argument("--remove-bibliography", action="store_true", default=False)
    p_extract.add_argument("--lemmatize", action="store_true", default=False)
    p_extract.add_argument("--tfidf-weight", type=float, default=0.5, dest="tfidf_weight")

    # ---- stats ----
    p_stats = sub.add_parser("stats", help="Compute corpus statistics.")
    p_stats.add_argument("--corpus", required=True, help="Path to folder with .txt files.")
    p_stats.add_argument("--lang", default="en", help="Language code.")
    p_stats.add_argument("--output", default=None, help="CSV output path.")

    # ---- evaluate ----
    p_eval = sub.add_parser("evaluate", help="Evaluate extraction against a gold standard.")
    p_eval.add_argument("--extracted", required=True, help="CSV with extracted terms.")
    p_eval.add_argument("--gold", required=True, help="CSV with gold-standard terms.")
    p_eval.add_argument("--extracted-col", default="term", dest="extracted_col")
    p_eval.add_argument("--gold-col", default="term", dest="gold_col")
    p_eval.add_argument("--mode", choices=["exact", "lemma"], default="exact")
    p_eval.add_argument("--verbose", action="store_true", default=False)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = _build_parser()
    args = parser.parse_args()

    dispatch = {
        "extract": _cmd_extract,
        "stats": _cmd_stats,
        "evaluate": _cmd_evaluate,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
