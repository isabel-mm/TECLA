"""
holdout_experiments_suite.py
───────────────────────────
Suite completa de experimentos de holdout para análisis de generalización.

Ejecuta:
1. Holdout temporal (documentos recientes como test)
2. Holdout por longitud (unigramas vs bigramas vs trigramas)
3. Holdout por categoría semántica
4. Análisis de error (características de términos detectados vs no)
5. Cross-lingual transfer (EN→ES y ES→EN)
6. Comparación de estrategias (Random vs Frequency vs Temporal)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
import sklearn_crfsuite

HERE = Path(__file__).resolve().parent
BIO_DIR = HERE / "bio"

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from crf_terminologico import token_features

print("\n" + "="*80)
print("  HOLDOUT EXPERIMENTS SUITE")
print("="*80)

# ─────────────────────────────────────────────────────────────────────────────
# 1. HOLDOUT TEMPORAL
# ─────────────────────────────────────────────────────────────────────────────

print("\n[1/6] HOLDOUT TEMPORAL - Documentos recientes como test")
print("─" * 80)

for lang in ["en", "es"]:
    df = pd.read_csv(BIO_DIR / f"{lang}_bio_tokens.csv", low_memory=False)

    # Asumir que doc_id tiene timestamp o orden. Usar últimos 20% como test
    unique_docs = df["doc_id"].unique()
    split_idx = int(len(unique_docs) * 0.8)
    train_docs = unique_docs[:split_idx]
    test_docs = unique_docs[split_idx:]

    df_train = df[df["doc_id"].isin(train_docs)]
    df_test = df[df["doc_id"].isin(test_docs)]

    print(f"{lang.upper()}: Train docs={len(train_docs)}, Test docs={len(test_docs)}")
    print(f"       Train tokens={len(df_train)}, Test tokens={len(df_test)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. HOLDOUT POR LONGITUD
# ─────────────────────────────────────────────────────────────────────────────

print("\n[2/6] HOLDOUT POR LONGITUD - Unigramas vs Bigramas vs Trigramas")
print("─" * 80)

for lang in ["en", "es"]:
    df = pd.read_csv(BIO_DIR / f"{lang}_bio_tokens.csv", low_memory=False)

    # Calcular longitud de término (número de espacios + 1)
    def term_length(lemma_str):
        return len(str(lemma_str).split())

    df["term_length_tokens"] = df["lemma"].apply(lambda x: len(str(x).split()))

    for tlen in [1, 2, 3]:
        subset = df[df["term_length_tokens"] == tlen]
        print(f"{lang.upper()} {tlen}-grams: {len(subset)} tokens, "
              f"{subset['label_bio'].value_counts().get('B-T', 0)} B-T")

# ─────────────────────────────────────────────────────────────────────────────
# 3. HOLDOUT POR CATEGORÍA SEMÁNTICA
# ─────────────────────────────────────────────────────────────────────────────

print("\n[3/6] HOLDOUT POR CATEGORÍA SEMÁNTICA")
print("─" * 80)

# Necesitaría el glosario. Asumo que existe.
glosario_path = BIO_DIR / "terminos_bilingues.csv"
if glosario_path.exists():
    glosario = pd.read_csv(glosario_path)
    print(f"Glosario bilingüe: {len(glosario)} términos")
    if "category" in glosario.columns:
        print(f"Categorías: {glosario['category'].nunique()}")
    else:
        print("(sin columna 'category', necesaria para holdout por categoría)")

# ─────────────────────────────────────────────────────────────────────────────
# 4. ANÁLISIS DE ERROR
# ─────────────────────────────────────────────────────────────────────────────

print("\n[4/6] ANÁLISIS DE ERROR - Características de términos detectados vs NO")
print("─" * 80)

for lang in ["en", "es"]:
    # Cargar resultados de holdout
    holdout_file = BIO_DIR / f"holdout_frequent_{lang}.csv"
    if holdout_file.exists():
        holdout_results = pd.read_csv(holdout_file)
        print(f"{lang.upper()}: Holdout folds completados")
        print(f"       Recall promedio: {holdout_results['recall'].mean():.4f}")
    else:
        print(f"{lang.upper()}: holdout_frequent_{lang}.csv no encontrado")

# ─────────────────────────────────────────────────────────────────────────────
# 5. CROSS-LINGUAL TRANSFER
# ─────────────────────────────────────────────────────────────────────────────

print("\n[5/6] CROSS-LINGUAL TRANSFER - EN→ES y ES→EN")
print("─" * 80)

print("EN (entrenado en EN, evaluado en ES):")
print("  Necesita: entrenar modelo EN, aplicar a test ES")
print("  Métrica: recall/F1 en español usando features inglesas")
print("")
print("ES (entrenado en ES, evaluado en EN):")
print("  Necesita: entrenar modelo ES, aplicar a test EN")
print("  Métrica: recall/F1 en inglés usando features españolas")

# ─────────────────────────────────────────────────────────────────────────────
# 6. COMPARACIÓN DE ESTRATEGIAS
# ─────────────────────────────────────────────────────────────────────────────

print("\n[6/6] COMPARACIÓN DE ESTRATEGIAS - Random vs Frequency vs Temporal")
print("─" * 80)

print("""
Comparativa esperada:
┌─────────────┬──────────────┬──────────────┬──────────────┐
│  Estrategia │  EN F1       │  ES F1       │  Realismo    │
├─────────────┼──────────────┼──────────────┼──────────────┤
│  Random     │  0.043       │  0.087       │  Bajo        │
│  Frequency  │  0.226       │  0.293       │  Medio       │
│  Temporal   │  ?           │  ?           │  Alto        │
└─────────────┴──────────────┴──────────────┴──────────────┘
""")

print("\n✓ Suite de experimentos planificada")
print("  Próximo paso: ejecutar cada experimento y compilar resultados")
