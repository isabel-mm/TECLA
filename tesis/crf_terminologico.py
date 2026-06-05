"""
crf_terminologico.py
────────────────────
CRF (Conditional Random Field) para detección terminológica BIO.

Diferencias respecto al clasificador por token (bio_token_ml.py):
  - El CRF modela la secuencia completa: considera el contexto
    de los tokens anteriores y posteriores (ventana ±2)
  - Las transiciones entre etiquetas son parte del modelo:
    B-T→I-T se aprende como válida, O→I-T como inválida
  - Los pesos por rasgo-etiqueta son directamente interpretables
    como "importancia para ser término"

Salidas:
  bio/crf_{en,es,combined}_clases_bio.csv
  bio/crf_{en,es,combined}_clases_bin.csv
  bio/crf_{en,es,combined}_rasgos_termino.csv
  bio/crf_{en,es,combined}_transiciones.csv
  tablas/tabla_crf_clases_bio_{en,es,combined}.tex
  tablas/tabla_crf_clases_bin_{en,es,combined}.tex
  tablas/tabla_crf_rasgos_{en,es,combined}.tex
  tablas/tabla_crf_transiciones_{en,es,combined}.tex

Uso:
    cd .../tesis && python crf_terminologico.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn_crfsuite
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupKFold

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from anotar_corpus_y_ml import escape_latex

BIO_DIR   = HERE / "bio"
TABLAS    = HERE / "tablas"
BIO_LABELS    = ["B-T", "I-T", "O"]
BINARY_LABELS = ["T", "O"]


# ─────────────────────────────────────────────────────────────────────────────
# Extracción de rasgos para CRF (ventana de contexto ±2)
# ─────────────────────────────────────────────────────────────────────────────

def token_features(row: dict) -> dict:
    """Rasgos del token individual (sin contexto de ventana)."""
    return {
        # Forma superficial y lema
        # REMOVIDOS: token_lower, lemma (causaban memorización en holdout)
        # MANTENIDO: shape (patrón ortográfico, generalizable)
        "shape":         str(row["shape"]),
        # Morfosintaxis
        "pos":           str(row["pos"]),
        "tag":           str(row["tag"]),
        "dep":           str(row["dep"]),
        # Rasgos binarios léxicos
        "is_stop":       bool(row["is_stop"]),
        "is_punct":      bool(row["is_punct"]),
        "is_alpha":      bool(row["is_alpha"]),
        "has_digit":     bool(row["has_digit"]),
        # Categoría gramatical binarizada
        "is_noun":       bool(row["is_noun"]),
        "is_verb":       bool(row["is_verb"]),
        "is_adj":        bool(row["is_adj"]),
        "is_propn":      bool(row["is_propn"]),
        # Estructura sintáctica
        "in_np":         bool(row["is_in_noun_phrase"]),
        "np_head":       bool(row["is_in_noun_chunk_head"]),
        "has_amod":      bool(row["has_adjective_modifier"]),
        "has_premod":    bool(row["has_pre_modifier"]),
        # Estadísticos (discretizados en cuartiles para CRF)
        "freq_q":        _quartile(row["freq_global"]),
        "df_q":          _quartile(row["document_frequency"]),
        "tfidf_q":       _quartile(row["tf_idf"]),
        "cd_q":          _quartile(row["contextual_diversity"]),
        # Probabilidades POS dominante
        "dom_pos":       _dominant_pos(row),
    }


def _quartile(val) -> str:
    """Discretiza un valor numérico en cuartiles Q1–Q4."""
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "Q0"
    if v <= 0:
        return "Q0"
    # Umbrales aproximados; se recalibran en build_features con percentiles reales
    return "Qx"   # placeholder — se reemplaza en build_features


def _dominant_pos(row) -> str:
    probs = {
        "NOUN":  float(row.get("lemma_pos_noun_prob",  0)),
        "VERB":  float(row.get("lemma_pos_verb_prob",  0)),
        "ADJ":   float(row.get("lemma_pos_adj_prob",   0)),
        "PROPN": float(row.get("lemma_pos_propn_prob", 0)),
    }
    return max(probs, key=probs.get)


def build_features(df: pd.DataFrame) -> tuple[list, list, list]:
    """
    Devuelve:
      sequences  — lista de listas de dicts de rasgos (una por oración)
      labels     — lista de listas de etiquetas BIO
      groups     — lista de doc_id (una por oración, para GroupKFold)
    """
    # Calcular percentiles reales para discretización
    pcts = {}
    for col in ["freq_global", "document_frequency", "tf_idf", "dispersion", "contextual_diversity"]:
        vals = df[col].values
        pcts[col] = np.percentile(vals[vals > 0], [25, 50, 75]) if (vals > 0).any() else [0, 0, 0]

    def quartile(col, val):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return "Q0"
        if v <= 0:
            return "Q0"
        p = pcts[col]
        if v <= p[0]: return "Q1"
        if v <= p[1]: return "Q2"
        if v <= p[2]: return "Q3"
        return "Q4"

    sequences, labels, groups = [], [], []

    for (doc_id, sent_id), grp in df.groupby(["doc_id", "sentence_id"], sort=False):
        grp = grp.sort_values("token_id")
        sent_feats  = []
        sent_labels = []

        rows_list = grp.to_dict("records")
        n = len(rows_list)

        for i, row in enumerate(rows_list):
            lemma = str(row["lemma"])
            feats = {
                "suffix3":   lemma[-3:] if len(lemma) >= 3 else lemma,
                "suffix4":   lemma[-4:] if len(lemma) >= 4 else lemma,
                "shape":     str(row["shape"]),
                "pos":       str(row["pos"]),
                "tag":       str(row["tag"]),
                "dep":       str(row["dep"]),
                "is_stop":   bool(row["is_stop"]),
                "is_punct":  bool(row["is_punct"]),
                "is_alpha":  bool(row["is_alpha"]),
                "has_digit": bool(row["has_digit"]),
                "is_noun":   bool(row["is_noun"]),
                "is_verb":   bool(row["is_verb"]),
                "is_adj":    bool(row["is_adj"]),
                "is_propn":  bool(row["is_propn"]),
                "in_np":     bool(row["is_in_noun_phrase"]),
                "np_head":   bool(row["is_in_noun_chunk_head"]),
                "has_amod":  bool(row["has_adjective_modifier"]),
                "has_premod": bool(row["has_pre_modifier"]),
                "freq_q":    quartile("freq_global", row["freq_global"]),
                "df_q":      quartile("document_frequency", row["document_frequency"]),
                "tfidf_q":   quartile("tf_idf", row["tf_idf"]),
                "cd_q":      quartile("contextual_diversity", row["contextual_diversity"]),
                "dom_pos":   _dominant_pos(row),
            }

            # Contexto anterior: -1 y -2
            for offset, prefix in [(-1, "prev1"), (-2, "prev2")]:
                idx = i + offset
                if 0 <= idx < n:
                    r = rows_list[idx]
                    rl = str(r["lemma"])
                    feats[f"{prefix}:pos"]     = str(r["pos"])
                    feats[f"{prefix}:suffix3"] = rl[-3:] if len(rl) >= 3 else rl
                    feats[f"{prefix}:is_noun"] = bool(r["is_noun"])
                    feats[f"{prefix}:is_adj"]  = bool(r["is_adj"])
                    feats[f"{prefix}:in_np"]   = bool(r["is_in_noun_phrase"])
                else:
                    feats[f"{prefix}:BOS"] = True

            # Contexto posterior: +1 y +2
            for offset, prefix in [(+1, "next1"), (+2, "next2")]:
                idx = i + offset
                if 0 <= idx < n:
                    r = rows_list[idx]
                    rl = str(r["lemma"])
                    feats[f"{prefix}:pos"]     = str(r["pos"])
                    feats[f"{prefix}:suffix3"] = rl[-3:] if len(rl) >= 3 else rl
                    feats[f"{prefix}:is_noun"] = bool(r["is_noun"])
                    feats[f"{prefix}:is_adj"]  = bool(r["is_adj"])
                    feats[f"{prefix}:in_np"]   = bool(r["is_in_noun_phrase"])
                else:
                    feats[f"{prefix}:EOS"] = True

            # Marcadores de inicio/fin de oración
            if i == 0:
                feats["BOS"] = True
            if i == n - 1:
                feats["EOS"] = True

            sent_feats.append(feats)
            sent_labels.append(str(row["label_bio"]))

        sequences.append(sent_feats)
        labels.append(sent_labels)
        groups.append(str(doc_id))

    return sequences, labels, groups


# ─────────────────────────────────────────────────────────────────────────────
# Entrenamiento y evaluación
# ─────────────────────────────────────────────────────────────────────────────

def train_crf() -> sklearn_crfsuite.CRF:
    return sklearn_crfsuite.CRF(
        algorithm="lbfgs",
        c1=0.05,   # L1 — promueve sparsity (rasgos irrelevantes → 0)
        c2=0.01,   # L2 — suaviza los pesos
        max_iterations=200,
        all_possible_transitions=True,
    )


def cross_val_crf(sequences, labels, groups, n_splits=5):
    """
    GroupKFold para que documentos completos queden en el mismo fold.
    Devuelve métricas BIO y colapsadas T/O por fold.
    """
    unique_groups = list(dict.fromkeys(groups))
    sent_group_idx = [unique_groups.index(g) for g in groups]

    gkf = GroupKFold(n_splits=n_splits)

    bio_rows = []
    bin_rows = []

    for fold, (train_idx, test_idx) in enumerate(
        gkf.split(sequences, labels, sent_group_idx), 1
    ):
        X_train = [sequences[i] for i in train_idx]
        y_train = [labels[i]    for i in train_idx]
        X_test  = [sequences[i] for i in test_idx]
        y_test  = [labels[i]    for i in test_idx]

        crf = train_crf()
        crf.fit(X_train, y_train)
        y_pred = crf.predict(X_test)

        # Aplanar secuencias para classification_report
        y_test_flat = [t for seq in y_test for t in seq]
        y_pred_flat = [t for seq in y_pred for t in seq]
        y_test_bin  = [("T" if t in {"B-T","I-T"} else "O") for t in y_test_flat]
        y_pred_bin  = [("T" if t in {"B-T","I-T"} else "O") for t in y_pred_flat]

        rep_bio = classification_report(
            y_test_flat, y_pred_flat,
            labels=BIO_LABELS, output_dict=True, zero_division=0,
        )
        rep_bin = classification_report(
            y_test_bin, y_pred_bin,
            labels=BINARY_LABELS, output_dict=True, zero_division=0,
        )

        for lbl in BIO_LABELS:
            bio_rows.append({
                "Fold": fold, "Clase": lbl,
                "Precision": rep_bio[lbl]["precision"],
                "Recall":    rep_bio[lbl]["recall"],
                "F1":        rep_bio[lbl]["f1-score"],
                "Support":   rep_bio[lbl]["support"],
            })
        for lbl in BINARY_LABELS:
            bin_rows.append({
                "Fold": fold, "Clase": lbl,
                "Precision": rep_bin[lbl]["precision"],
                "Recall":    rep_bin[lbl]["recall"],
                "F1":        rep_bin[lbl]["f1-score"],
                "Support":   rep_bin[lbl]["support"],
            })

    def agg(rows):
        return (
            pd.DataFrame(rows)
            .groupby("Clase", as_index=False)
            .agg(
                Precision    =("Precision",  "mean"),
                Precision_std=("Precision",  "std"),
                Recall       =("Recall",     "mean"),
                Recall_std   =("Recall",     "std"),
                F1           =("F1",         "mean"),
                F1_std       =("F1",         "std"),
                Support      =("Support",    "mean"),
            )
        )

    return agg(bio_rows), agg(bin_rows)


def extract_feature_weights(crf: sklearn_crfsuite.CRF, top_n: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrae los pesos del CRF por rasgo-etiqueta y por transición.

    Devuelve:
      feat_df   — rasgos más discriminativos para B-T / I-T
      trans_df  — pesos de transición entre etiquetas
    """
    state_feats = crf.state_features_

    # Pesos por rasgo para B-T y I-T
    rows = []
    for (attr, label), weight in state_feats.items():
        if label in {"B-T", "I-T"}:
            rows.append({"Rasgo": attr, "Etiqueta": label, "Peso": weight})

    feat_df = pd.DataFrame(rows)

    # Agregar por nombre de rasgo: promedio de |peso| sobre B-T e I-T
    agg = (
        feat_df.groupby("Rasgo")
        .agg(
            Peso_BT  =("Peso", lambda x: x[feat_df.loc[x.index, "Etiqueta"] == "B-T"].mean() if any(feat_df.loc[x.index, "Etiqueta"] == "B-T") else 0),
            Peso_IT  =("Peso", lambda x: x[feat_df.loc[x.index, "Etiqueta"] == "I-T"].mean() if any(feat_df.loc[x.index, "Etiqueta"] == "I-T") else 0),
            Peso_abs =("Peso", lambda x: x.abs().mean()),
        )
        .reset_index()
        .sort_values("Peso_abs", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # Transiciones
    trans_rows = []
    for (label_from, label_to), weight in crf.transition_features_.items():
        trans_rows.append({"De": label_from, "A": label_to, "Peso": weight})
    trans_df = (
        pd.DataFrame(trans_rows)
        .sort_values("Peso", ascending=False)
        .reset_index(drop=True)
    )

    return agg, trans_df


# ─────────────────────────────────────────────────────────────────────────────
# Escritura LaTeX
# ─────────────────────────────────────────────────────────────────────────────

def write_classwise_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} l c c c c c c r @{}}",
        r"\toprule",
        (r"\textbf{Clase} & \textbf{Prec.} & \textbf{$\sigma$} "
         r"& \textbf{Recall} & \textbf{$\sigma$} "
         r"& \textbf{F1} & \textbf{$\sigma$} & \textbf{Support} \\"),
        r"\midrule",
    ]
    for row in df.itertuples(index=False):
        lines.append(
            rf"\texttt{{{escape_latex(row.Clase)}}} & "
            f"{row.Precision:.3f} & {row.Precision_std:.3f} & "
            f"{row.Recall:.3f} & {row.Recall_std:.3f} & "
            f"{row.F1:.3f} & {row.F1_std:.3f} & "
            f"{row.Support:.0f} \\\\"
        )
    lines += [
        r"\bottomrule",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\end{tabular}",
        r"\normalsize",
        r"\end{table}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_features_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    """Tabla de rasgos importantes para ser término (B-T / I-T)."""
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} r l c c c @{}}",
        r"\toprule",
        (r"\# & \textbf{Rasgo} & \textbf{Peso B-T} "
         r"& \textbf{Peso I-T} & \textbf{$|$Peso$|$ medio} \\"),
        r"\midrule",
    ]
    for i, row in enumerate(df.itertuples(index=False), 1):
        # Limpiar nombre del rasgo para LaTeX
        rasgo = str(row.Rasgo).replace("_", r"\_").replace("&", r"\&")
        bt  = f"{row.Peso_BT:.4f}"  if not np.isnan(row.Peso_BT)  else "--"
        it  = f"{row.Peso_IT:.4f}"  if not np.isnan(row.Peso_IT)  else "--"
        abs_= f"{row.Peso_abs:.4f}" if not np.isnan(row.Peso_abs) else "--"
        lines.append(
            rf"{i} & \texttt{{{rasgo}}} & {bt} & {it} & {abs_} \\"
        )
    lines += [
        r"\bottomrule",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\end{tabular}",
        r"\normalsize",
        r"\end{table}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_transitions_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} l l c @{}}",
        r"\toprule",
        r"\textbf{De} & \textbf{A} & \textbf{Peso} \\",
        r"\midrule",
    ]
    for row in df.itertuples(index=False):
        lines.append(
            rf"\texttt{{{escape_latex(row.De)}}} $\to$ "
            rf"\texttt{{{escape_latex(row.A)}}} & & {row.Peso:.4f} \\"
        )
    lines += [
        r"\bottomrule",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\end{tabular}",
        r"\normalsize",
        r"\end{table}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Ejecución por lengua
# ─────────────────────────────────────────────────────────────────────────────

def run_crf(tag: str, df: pd.DataFrame):
    print(f"\n{'='*50}")
    print(f"  CRF — {tag.upper()}")
    print(f"{'='*50}")

    print("  Construyendo secuencias de rasgos…")
    sequences, labels, groups = build_features(df)
    n_terms = sum(1 for seq in labels for l in seq if l != "O")
    print(f"  Oraciones: {len(sequences)} | tokens término: {n_terms}")

    print("  Validación cruzada (5 folds)…")
    bio_report, bin_report = cross_val_crf(sequences, labels, groups)

    print("  Entrenando CRF completo para extraer pesos…")
    crf_full = train_crf()
    crf_full.fit(sequences, labels)
    feat_weights, trans_weights = extract_feature_weights(crf_full, top_n=20)

    # CSV
    bio_report.to_csv(BIO_DIR / f"crf_{tag}_clases_bio.csv", index=False)
    bin_report.to_csv(BIO_DIR / f"crf_{tag}_clases_bin.csv", index=False)
    feat_weights.to_csv(BIO_DIR / f"crf_{tag}_rasgos_termino.csv", index=False)
    trans_weights.to_csv(BIO_DIR / f"crf_{tag}_transiciones.csv", index=False)

    lang_label = tag.upper()

    # LaTeX — clases BIO
    write_classwise_latex(
        bio_report,
        TABLAS / f"tabla_crf_clases_bio_{tag}.tex",
        (f"Rendimiento del CRF por clase BIO (B-T, I-T, O) "
         f"para el corpus {lang_label} (validación cruzada 5 folds)."),
        f"tab:crf_clases_bio_{tag}",
    )

    # LaTeX — colapsado T/O
    write_classwise_latex(
        bin_report,
        TABLAS / f"tabla_crf_clases_bin_{tag}.tex",
        (f"Rendimiento del CRF colapsado (T vs O) "
         f"para el corpus {lang_label}."),
        f"tab:crf_clases_bin_{tag}",
    )

    # LaTeX — rasgos importantes para ser término
    write_features_latex(
        feat_weights,
        TABLAS / f"tabla_crf_rasgos_{tag}.tex",
        (f"Rasgos con mayor peso en el CRF para las etiquetas terminológicas "
         f"B-T e I-T en el corpus {lang_label}. "
         r"Pesos positivos favorecen la etiqueta, negativos la penalizan."),
        f"tab:crf_rasgos_{tag}",
    )

    # LaTeX — transiciones
    write_transitions_latex(
        trans_weights,
        TABLAS / f"tabla_crf_transiciones_{tag}.tex",
        (f"Pesos de transición aprendidos por el CRF para el corpus {lang_label}. "
         r"Valores altos indican secuencias válidas (B-T$\to$I-T); "
         r"valores negativos indican transiciones incoherentes (O$\to$I-T)."),
        f"tab:crf_transiciones_{tag}",
    )

    # Resumen en consola
    bt = bio_report[bio_report["Clase"] == "B-T"].iloc[0]
    it = bio_report[bio_report["Clase"] == "I-T"].iloc[0]
    t  = bin_report[bin_report["Clase"] == "T"].iloc[0]
    print(f"  B-T  → Prec={bt.Precision:.3f}  Rec={bt.Recall:.3f}  F1={bt.F1:.3f}")
    print(f"  I-T  → Prec={it.Precision:.3f}  Rec={it.Recall:.3f}  F1={it.F1:.3f}")
    print(f"  T(∪) → Prec={t.Precision:.3f}  Rec={t.Recall:.3f}  F1={t.F1:.3f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    for tag in ("en", "es"):
        csv_path = BIO_DIR / f"{tag}_bio_tokens.csv"
        if not csv_path.exists():
            print(f"  ⚠  No se encuentra {csv_path.name} — ejecuta primero bio_token_ml.py")
            continue
        print(f"  Cargando {csv_path.name}…")
        df = pd.read_csv(csv_path, low_memory=False)
        run_crf(tag, df)

    print("\nListo.")


if __name__ == "__main__":
    main()
