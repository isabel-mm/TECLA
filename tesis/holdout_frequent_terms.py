"""
holdout_frequent_terms.py
─────────────────────────
EXPERIMENTO: ¿Mejora la generalización si solo enmascaramos términos FRECUENTES?

Pregunta: ¿El bajo rendimiento en holdout se debe a ESCASEZ DE DATOS
o a falta de GENERALIZACIÓN?

Diseño:
  1. En lugar de enmascarar 20% de TODOS los tipos
  2. Enmascaramos solo términos con ALTA FRECUENCIA (>= 50 ocurrencias)
  3. Estos términos SÍ tienen suficientes ejemplos en training
  4. Si F1 aún es bajo → es un problema de generalización
  5. Si F1 es alto → era un problema de escasez de datos

Salidas:
  bio/holdout_frequent_en.csv
  bio/holdout_frequent_es.csv
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
import sklearn_crfsuite

HERE = Path(__file__).resolve().parent
BIO_DIR = HERE / "bio"

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from crf_terminologico import token_features

def holdout_frequent_terms(lang: str, min_freq: int = 50):
    """
    Holdout test con solo términos frecuentes.

    Parameters
    ----------
    lang : str
        'en' o 'es'
    min_freq : int
        Frecuencia mínima para incluir un término en holdout (default 50)
    """

    print(f"\n{'='*70}")
    print(f"  HOLDOUT TÉRMINOS FRECUENTES - {lang.upper()}")
    print(f"  (Solo términos con frecuencia >= {min_freq})")
    print(f"{'='*70}")

    # Cargar datos
    df = pd.read_csv(BIO_DIR / f"{lang}_bio_tokens.csv", low_memory=False)

    # Identificar términos por frecuencia
    term_freq = df[df["label_bio"] != "O"].groupby("lemma").size()
    frequent_terms = term_freq[term_freq >= min_freq].index.tolist()

    print(f"\nTotal términos únicos: {len(term_freq)}")
    print(f"Términos frecuentes (>={min_freq}): {len(frequent_terms)}")
    print(f"Ejemplos: {frequent_terms[:10]}")

    # Crear versión modificada del dataset
    df_exp = df.copy()

    # Split estratificado por documento y por tipo de término
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

    results = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(
        df_exp[["lemma"]],
        df_exp["label_bio"],
        groups=df_exp["doc_id"]
    ), 1):
        print(f"\nFold {fold}...", end=" ", flush=True)

        # Crear copia para este fold
        df_fold = df_exp.copy()

        # En training: enmascarar términos frecuentes (cambiar a O)
        train_mask = df_fold.index.isin(train_idx)
        enmascarar = (
            train_mask &
            (df_fold["lemma"].isin(frequent_terms)) &
            (df_fold["label_bio"] != "O")
        )
        df_fold.loc[enmascarar, "label_bio"] = "O"
        df_fold.loc[enmascarar, "label"] = "O"

        # Test: solo evaluar en tokens de términos frecuentes
        test_mask = df_fold.index.isin(test_idx)
        test_frequent = test_mask & df_fold["lemma"].isin(frequent_terms)

        df_train = df_fold[train_mask]
        df_test = df_fold[test_frequent]

        if len(df_test) == 0:
            print("sin test data")
            continue

        # Entrenar CRF (simplificado - solo métricas básicas)

        X_train, y_train = [], []
        for sent_id, grp in df_train.groupby(["doc_id", "sentence_id"]):
            sent = grp.to_dict("records")
            X_train.append([token_features(t) for t in sent])
            y_train.append([t["label_bio"] for t in sent])

        X_test, y_test = [], []
        for sent_id, grp in df_test.groupby(["doc_id", "sentence_id"]):
            sent = grp.to_dict("records")
            X_test.append([token_features(t) for t in sent])
            y_test.append([t["label_bio"] for t in sent])

        # Entrenar CRF
        crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=200,
            all_possible_transitions=True,
            verbose=False
        )
        crf.fit(X_train, y_train)

        # Predecir
        y_pred = crf.predict(X_test)
        y_test_flat = [label for seq in y_test for label in seq]
        y_pred_flat = [label for seq in y_pred for label in seq]

        # Métricas
        precision = precision_score(y_test_flat, y_pred_flat, average="macro", zero_division=0)
        recall = recall_score(y_test_flat, y_pred_flat, average="macro", zero_division=0)
        f1 = f1_score(y_test_flat, y_pred_flat, average="macro", zero_division=0)

        results.append({
            "fold": fold,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "n_test": len(y_test_flat)
        })

        print(f"F1={f1:.4f}")

    # Guardar resultados
    results_df = pd.DataFrame(results)
    results_df.to_csv(BIO_DIR / f"holdout_frequent_{lang}.csv", index=False)

    print(f"\n{'─'*70}")
    print(f"PROMEDIO:")
    print(f"  Precision: {results_df['precision'].mean():.4f} ± {results_df['precision'].std():.4f}")
    print(f"  Recall:    {results_df['recall'].mean():.4f} ± {results_df['recall'].std():.4f}")
    print(f"  F1:        {results_df['f1'].mean():.4f} ± {results_df['f1'].std():.4f}")
    print(f"\n✓ Resultados guardados en: holdout_frequent_{lang}.csv")

    return results_df

def main():
    for lang in ["en", "es"]:
        try:
            holdout_frequent_terms(lang, min_freq=50)
        except Exception as e:
            print(f"Error en {lang}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
