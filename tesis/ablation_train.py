"""
Ablation study: entrena modelos quitando features de baja importancia
y mide impacto en F1 y Recall
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import sys

HERE = Path(__file__).resolve().parent
BIO_DIR = HERE / "bio"

sys.path.insert(0, str(HERE))
from bio_token_ml import NUMERIC_COLS, CLASS_WEIGHTS_BIO

# Escenarios de ablation
ABLATION_SCENARIOS = {
    "baseline": [],
    "sin_dispersion": ["dispersion"],
    "sin_suffixes": ["lemma_suffix3", "lemma_suffix4"],
    "sin_low_morpho": ["dispersion", "lemma_suffix3", "lemma_suffix4", "in_definition_context", "is_acronym"],
    "sin_low_posicion": ["dispersion", "lemma_suffix3", "lemma_suffix4", "avg_position_in_sentence", "is_in_noun_phrase"],
    "sin_nuevos_features": ["dispersion", "lemma_suffix3", "lemma_suffix4", "is_titlecase", "is_first_occurrence_in_doc"],
    "sin_baja_importancia": [
        "dispersion", "lemma_suffix3", "lemma_suffix4", "in_definition_context",
        "is_acronym", "is_in_noun_phrase", "avg_position_in_sentence",
        "is_titlecase", "is_first_occurrence_in_doc"
    ],
}

def evaluate_scenario(df, scenario_name, excluded_features):
    """Entrena y evalúa modelo sin ciertos features (solo features numéricas escaladas)"""
    numeric_filtered = [f for f in NUMERIC_COLS if f not in excluded_features]

    X = df[numeric_filtered].copy()
    y = df["label_bio"].copy()

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    groups = df["doc_id"].values

    metrics = {"f1_macro": [], "f1_weighted": [], "recall_macro": [], "precision_macro": []}

    for train_idx, test_idx in cv.split(X, y, groups=groups):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        clf = LogisticRegression(
            max_iter=2500,
            class_weight=CLASS_WEIGHTS_BIO,
            random_state=42,
            n_jobs=-1
        )
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)

        metrics["f1_macro"].append(f1_score(y_test, y_pred, average="macro", zero_division=0))
        metrics["f1_weighted"].append(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        metrics["recall_macro"].append(recall_score(y_test, y_pred, average="macro", zero_division=0))
        metrics["precision_macro"].append(precision_score(y_test, y_pred, average="macro", zero_division=0))

    return {
        "f1_macro": f"{np.mean(metrics['f1_macro']):.4f}",
        "f1_macro_std": f"{np.std(metrics['f1_macro']):.4f}",
        "f1_weighted": f"{np.mean(metrics['f1_weighted']):.4f}",
        "recall_macro": f"{np.mean(metrics['recall_macro']):.4f}",
        "precision_macro": f"{np.mean(metrics['precision_macro']):.4f}",
    }

def main():
    print("\n" + "="*80)
    print("  ABLATION STUDY: Impacto de remover features de baja importancia")
    print("="*80)

    results = []

    for lang, fname in [("en", "en_bio_tokens.csv"), ("es", "es_bio_tokens.csv")]:
        print(f"\n{'='*80}")
        print(f"  Corpus {lang.upper()}")
        print(f"{'='*80}")

        df = pd.read_csv(BIO_DIR / fname, low_memory=False)
        print(f"Dataset: {len(df):,} tokens")

        for scenario_name, excluded_features in ABLATION_SCENARIOS.items():
            print(f"\n  {scenario_name:30s} (sin {len(excluded_features)} features)...", end=" ", flush=True)

            metrics = evaluate_scenario(df, scenario_name, excluded_features)

            print(f"F1={metrics['f1_macro']} ± {metrics['f1_macro_std']}")

            results.append({
                "language": lang.upper(),
                "scenario": scenario_name,
                "excluded_count": len(excluded_features),
                "excluded_features": ", ".join(excluded_features) if excluded_features else "ninguno",
                "f1_macro": metrics["f1_macro"],
                "f1_macro_std": metrics["f1_macro_std"],
                "f1_weighted": metrics["f1_weighted"],
                "recall_macro": metrics["recall_macro"],
                "precision_macro": metrics["precision_macro"],
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv(BIO_DIR / "ablation_train_results.csv", index=False)

    print("\n" + "="*80)
    print("  RESUMEN")
    print("="*80)

    for lang in ["EN", "ES"]:
        lang_df = results_df[results_df["language"] == lang].sort_values("excluded_count")
        print(f"\n{lang}:")
        baseline_f1 = float(lang_df[lang_df["scenario"] == "baseline"]["f1_macro"].values[0])

        for _, row in lang_df.iterrows():
            f1 = float(row["f1_macro"])
            delta = f1 - baseline_f1
            delta_str = f"{delta:+.4f}" if delta != 0 else "igual"

            marker = " ← OK" if abs(delta) < 0.005 else " ← IMPACTO"
            print(f"  {row['scenario']:30s} F1={row['f1_macro']} ({delta_str}){marker}")

    print(f"\n✓ Resultados guardados en ablation_train_results.csv\n")

if __name__ == "__main__":
    main()
