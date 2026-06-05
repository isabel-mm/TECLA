"""
Genera un corpus BIO a nivel de token y evalúa clasificadores clásicos
para detección terminológica secuencial.

Cambios respecto a la versión anterior:
  - Entrenamiento con etiquetas BIO completas (B-T, I-T, O)
  - Pesos de clase asimétricos para priorizar recall en B-T e I-T
  - Métricas por clase BIO (B-T, I-T, O) Y colapsadas (T, O)
  - Salidas separadas por lengua (en, es) y combinadas

Salidas:
  bio/{en,es,combined}_bio_tokens.csv
  bio/{en,es,combined}_metricas.csv
  bio/{en,es,combined}_importancia_rasgos.csv
  bio/{en,es,combined}_clases_bio.csv
  bio/{en,es,combined}_clases_bin.csv
  tablas/tabla_bio_metricas_{en,es,combined}.tex
  tablas/tabla_bio_clases_bio_{en,es,combined}.tex
  tablas/tabla_bio_clases_bin_{en,es,combined}.tex
  tablas/tabla_bio_importancia_{en,es,combined}.tex
  tablas/tabla_features_linguistic.tex
  tablas/tabla_features_statistical.tex
"""

from __future__ import annotations

import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score, classification_report,
    f1_score, precision_score, recall_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from anotar_corpus_y_ml import (
    TABLAS_DIR,
    escape_latex,
    load_docs_en,
    load_docs_es,
    load_terms_en,
    load_terms_es,
    normalize,
)


BIO_DIR = HERE / "bio"
BIO_DIR.mkdir(exist_ok=True)

SPACY_MODELS = {"en": "en_core_web_sm", "es": "es_core_news_sm"}

BIO_LABELS    = ["B-T", "I-T", "O"]
BINARY_LABELS = ["T", "O"]

# Pesos asimétricos: B-T y I-T tienen mayor penalización de error
# para priorizar recall en la clase de interés terminológico.
CLASS_WEIGHTS_BIO = {"B-T": 6, "I-T": 4, "O": 1}

DEFINITION_PATTERNS = {
    "en": [
        "is a", "is an", "is defined as", "refers to", "known as",
        "also known as", "is a type of", "is part of",
    ],
    "es": [
        "es un", "es una", "se define como", "se conoce como",
        "se denomina", "se refiere a", "es un tipo de", "forma parte de",
    ],
}

CATEGORICAL_COLS = [
    "pos",
    "tag",
    "dep",
    "shape",
    "lemma_suffix3",   # últimos 3 chars del lema → generaliza morfología
    "lemma_suffix4",   # últimos 4 chars del lema
]

NUMERIC_COLS = [
    "is_stop",
    "is_punct",
    "is_alpha",
    "is_propn",
    "is_noun",
    "is_verb",
    "is_adj",
    "is_in_noun_phrase",
    "is_in_noun_chunk_head",
    "has_adjective_modifier",
    "has_pre_modifier",
    "position_in_sentence",
    "avg_position_in_sentence",
    "is_acronym",
    "token_length",
    "sentence_length",
    "in_definition_context",
    "freq_in_text",
    "freq_global",
    "document_frequency",
    "dispersion",
    "contextual_diversity",
    "tf_idf",
    "lexical_variety",
    "lemma_pos_noun_prob",
    "lemma_pos_verb_prob",
    "lemma_pos_adj_prob",
    "lemma_pos_propn_prob",
]

MODELS = {
    "Logistic Regression": LogisticRegression(
        max_iter=2500,
        class_weight=CLASS_WEIGHTS_BIO,
    ),
    "Linear SVM": LinearSVC(
        class_weight=CLASS_WEIGHTS_BIO,
        max_iter=6000,
    ),
    "SGD Hinge": SGDClassifier(
        loss="hinge",
        class_weight=CLASS_WEIGHTS_BIO,
        max_iter=2000,
        random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        class_weight=CLASS_WEIGHTS_BIO,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
    ),
}

# Sin rasgos de vocabulario léxico: todos los categóricos son ahora interpretables
VOCAB_FEATURES: set = set()


# ─────────────────────────────────────────────────────────────────────────────
# Construcción del corpus BIO
# ─────────────────────────────────────────────────────────────────────────────

def load_language_model(lang: str):
    return spacy.load(SPACY_MODELS[lang], disable=["ner"])


def term_token_sequences(terms, lang: str, nlp) -> dict[str, list[str]]:
    out = {}
    for rec in terms:
        doc = nlp.make_doc(rec.term)
        toks = [normalize(tok.text, lang) for tok in doc if not tok.is_space]
        if toks:
            out[rec.term] = toks
    return out


def build_term_index(term_map: dict[str, list[str]]) -> dict[str, list[tuple[list[str], str]]]:
    index = defaultdict(list)
    for term, seq in term_map.items():
        index[seq[0]].append((seq, term))
    for key in index:
        index[key].sort(key=lambda item: len(item[0]), reverse=True)
    return index


def juilland_dispersion(freqs: list[int]) -> float:
    if not freqs or sum(freqs) == 0:
        return 0.0
    mean = sum(freqs) / len(freqs)
    if mean == 0:
        return 0.0
    sd = math.sqrt(sum((f - mean) ** 2 for f in freqs) / len(freqs))
    return max(0.0, 1 - (sd / mean))


def split_text_for_spacy(text: str, max_chars: int = 250000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            cut = max(
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
            )
            if cut <= start + max_chars // 2:
                cut = end
        else:
            cut = end
        chunks.append(text[start:cut].strip())
        start = cut
    return [chunk for chunk in chunks if chunk]


def mark_bio(sent_tokens, lang: str, index) -> tuple[list[str], list[int]]:
    norm_tokens = [normalize(tok.text, lang) for tok in sent_tokens]
    labels = ["O"] * len(sent_tokens)
    span_lengths = [1] * len(sent_tokens)
    i = 0
    while i < len(sent_tokens):
        current = norm_tokens[i]
        matched = None
        for seq, _term in index.get(current, []):
            end = i + len(seq)
            if end > len(sent_tokens):
                continue
            if norm_tokens[i:end] == seq:
                matched = seq
                break
        if matched is None:
            i += 1
            continue
        labels[i] = "B-T"
        span_lengths[i] = len(matched)
        for j in range(i + 1, i + len(matched)):
            labels[j] = "I-T"
            span_lengths[j] = len(matched)
        i += len(matched)
    return labels, span_lengths


def collapse_label(label: str) -> str:
    return "T" if label in {"B-T", "I-T"} else "O"


# ─────────────────────────────────────────────────────────────────────────────
# Recomputación de rasgos estadísticos por fold
# ─────────────────────────────────────────────────────────────────────────────

def recompute_global_stats(df: pd.DataFrame, train_doc_ids: set) -> pd.DataFrame:
    """
    Recomputes the five corpus-global statistical features using only the
    documents in train_doc_ids.  Tokens whose lemma never appears in the
    training partition receive 0 for every global feature.

    Features recomputed:
      freq_global        – total corpus frequency of the lemma
      document_frequency – number of docs containing the lemma
      contextual_diversity – number of unique (doc, sentence) pairs
      dispersion         – Juilland's D across training documents
      tf_idf             – TF × log((n_train+1) / (doc_freq+1))
    """
    df = df.copy()
    n_train_docs = len(train_doc_ids)
    train = df[df["doc_id"].isin(train_doc_ids)]

    # freq_global
    freq_global = train.groupby("lemma").size()

    # document_frequency
    doc_freq = train.groupby("lemma")["doc_id"].nunique()

    # contextual_diversity: unique (doc_id, sentence_id) pairs
    ctx_div = (
        train.drop_duplicates(["lemma", "doc_id", "sentence_id"])
        .groupby("lemma")
        .size()
    )

    # dispersion (Juilland's D) – vectorised over training docs
    per_doc = train.groupby(["lemma", "doc_id"]).size().unstack(fill_value=0)
    # add zero columns for training docs that don't appear in the pivot
    for doc_id in train_doc_ids:
        if doc_id not in per_doc.columns:
            per_doc[doc_id] = 0
    counts = per_doc.values.astype(float)
    means = counts.mean(axis=1)
    stds  = np.sqrt(((counts - means[:, None]) ** 2).mean(axis=1))
    with np.errstate(divide="ignore", invalid="ignore"):
        cv = np.where(means > 0, stds / means, 0.0)
    dispersion_vals = np.maximum(0.0, 1.0 - cv)
    dispersion_map = dict(zip(per_doc.index, dispersion_vals))

    # write back
    df["freq_global"]         = df["lemma"].map(freq_global).fillna(0.0)
    df["document_frequency"]  = df["lemma"].map(doc_freq).fillna(0.0)
    df["contextual_diversity"]= df["lemma"].map(ctx_div).fillna(0.0)
    df["dispersion"]          = df["lemma"].map(dispersion_map).fillna(0.0)

    # tf_idf: per-document TF × training-only IDF
    df["tf_idf"] = (
        (df["freq_in_text"] / df["doc_length_tokens"].clip(lower=1))
        * np.log((n_train_docs + 1) / (df["document_frequency"] + 1))
    )

    return df


def process_language(lang: str, docs, terms) -> pd.DataFrame:
    nlp = load_language_model(lang)
    term_map = term_token_sequences(terms, lang, nlp)
    term_index = build_term_index(term_map)

    rows = []
    lemma_global = Counter()
    lemma_docsets = defaultdict(set)
    lemma_sentence_sets = defaultdict(set)
    lemma_pos = defaultdict(Counter)
    lemma_doc_freqs = defaultdict(lambda: Counter())
    lemma_doc_positions = defaultdict(list)
    doc_token_counts = {}
    doc_lexical_variety = {}

    for doc_meta in docs:
        doc_id = f"{lang.upper()}::{doc_meta['doc_id']}"
        path = doc_meta["path"]
        chunk_docs = list(nlp.pipe(split_text_for_spacy(doc_meta["text"]), batch_size=2))
        tokens_all = [tok for chunk in chunk_docs for tok in chunk if not tok.is_space]
        lemmas_doc = [normalize(tok.lemma_ or tok.text, lang) for tok in tokens_all if not tok.is_punct]
        doc_token_counts[doc_id] = len(tokens_all)
        doc_lexical_variety[doc_id] = len(set(lemmas_doc)) / max(len(lemmas_doc), 1)

        doc_lemma_counter = Counter()
        doc_lemma_sentence_set = defaultdict(set)

        noun_chunk_token_ids = set()
        noun_chunk_heads = set()
        global_offset = 0
        sent_global_idx = 0
        for chunk_doc in chunk_docs:
            for chunk in chunk_doc.noun_chunks:
                for tok in chunk:
                    noun_chunk_token_ids.add(global_offset + tok.i)
                noun_chunk_heads.add(global_offset + chunk.root.i)

            for sent in chunk_doc.sents:
                sent_tokens = [tok for tok in sent if not tok.is_space]
                if not sent_tokens:
                    continue
                sent_text_norm = normalize(sent.text, lang)
                in_definition = int(
                    any(pattern in sent_text_norm for pattern in DEFINITION_PATTERNS[lang])
                )
                labels, span_lengths = mark_bio(sent_tokens, lang, term_index)

                for tok_idx, tok in enumerate(sent_tokens):
                    lemma = normalize(tok.lemma_ or tok.text, lang)
                    doc_lemma_counter[lemma] += 1
                    doc_lemma_sentence_set[lemma].add(sent_global_idx)
                    lemma_global[lemma] += 1
                    lemma_docsets[lemma].add(doc_id)
                    lemma_sentence_sets[lemma].add(f"{doc_id}::{sent_global_idx}")
                    lemma_pos[lemma][tok.pos_] += 1
                    lemma_doc_positions[(doc_id, lemma)].append(
                        tok_idx / max(len(sent_tokens) - 1, 1)
                    )

                    token_global_id = global_offset + tok.i
                    rows.append(
                        {
                            "language": lang.upper(),
                            "doc_id": doc_id,
                            "path": path,
                            "sentence_id": sent_global_idx,
                            "token_id": token_global_id,
                            "token": tok.text,
                            "token_lower": normalize(tok.text, lang),
                            "lemma": lemma,
                            "lemma_suffix3": lemma[-3:] if len(lemma) >= 3 else lemma,
                            "lemma_suffix4": lemma[-4:] if len(lemma) >= 4 else lemma,
                            "pos": tok.pos_,
                            "tag": tok.tag_,
                            "dep": tok.dep_,
                            "shape": tok.shape_,
                            "label_bio": labels[tok_idx],
                            "label": collapse_label(labels[tok_idx]),
                            "span_length": span_lengths[tok_idx],
                            "is_stop": int(tok.is_stop),
                            "is_punct": int(tok.is_punct),
                            "is_alpha": int(tok.is_alpha),
                            "is_propn": int(tok.pos_ == "PROPN"),
                            "is_noun": int(tok.pos_ == "NOUN"),
                            "is_verb": int(tok.pos_ == "VERB"),
                            "is_adj": int(tok.pos_ == "ADJ"),
                            "is_in_noun_phrase": int(token_global_id in noun_chunk_token_ids),
                            "is_in_noun_chunk_head": int(token_global_id in noun_chunk_heads),
                            "has_adjective_modifier": int(
                                any(child.dep_ == "amod" or child.pos_ == "ADJ" for child in tok.children)
                            ),
                            "has_pre_modifier": int(
                                any(
                                    child.i < tok.i and child.pos_ in {"ADJ", "NOUN", "PROPN", "NUM"}
                                    for child in tok.children
                                )
                            ),
                            "position_in_sentence": round(tok_idx / max(len(sent_tokens) - 1, 1), 6),
                            "is_acronym": int(tok.text.isupper() and len(tok.text) > 1 and tok.text.isalpha()),
                            "token_length": len(tok.text),
                            "sentence_length": len(sent_tokens),
                            "in_definition_context": in_definition,
                            "doc_length_tokens": len(tokens_all),
                        }
                    )
                sent_global_idx += 1
            global_offset += len(chunk_doc)

        for lemma, count in doc_lemma_counter.items():
            lemma_doc_freqs[lemma][doc_id] = count

    df = pd.DataFrame(rows)
    n_docs = len(docs)

    for lemma, counts in lemma_pos.items():
        total = sum(counts.values()) or 1
        counts["NOUN_PROB"] = counts.get("NOUN", 0) / total
        counts["VERB_PROB"] = counts.get("VERB", 0) / total
        counts["ADJ_PROB"] = counts.get("ADJ", 0) / total
        counts["PROPN_PROB"] = counts.get("PROPN", 0) / total

    doc_token_lemma_count = (
        df.groupby(["doc_id", "lemma"]).size().rename("freq_in_text").reset_index()
    )
    df = df.merge(doc_token_lemma_count, on=["doc_id", "lemma"], how="left")

    avg_pos_doc = []
    for (doc_id, lemma), vals in lemma_doc_positions.items():
        avg_pos_doc.append(
            {
                "doc_id": doc_id,
                "lemma": lemma,
                "avg_position_in_sentence": sum(vals) / len(vals),
            }
        )
    df = df.merge(pd.DataFrame(avg_pos_doc), on=["doc_id", "lemma"], how="left")

    df["freq_global"] = df["lemma"].map(lemma_global).astype(float)
    df["document_frequency"] = df["lemma"].map(lambda x: len(lemma_docsets[x])).astype(float)
    df["contextual_diversity"] = df["lemma"].map(lambda x: len(lemma_sentence_sets[x])).astype(float)
    df["dispersion"] = df["lemma"].map(
        lambda x: juilland_dispersion(
            [lemma_doc_freqs[x].get(doc["doc_id"], 0) for doc in docs]
        )
    )
    df["lexical_variety"] = df["doc_id"].map(doc_lexical_variety).astype(float)
    df["lemma_pos_noun_prob"] = df["lemma"].map(lambda x: lemma_pos[x]["NOUN_PROB"]).astype(float)
    df["lemma_pos_verb_prob"] = df["lemma"].map(lambda x: lemma_pos[x]["VERB_PROB"]).astype(float)
    df["lemma_pos_adj_prob"] = df["lemma"].map(lambda x: lemma_pos[x]["ADJ_PROB"]).astype(float)
    df["lemma_pos_propn_prob"] = df["lemma"].map(lambda x: lemma_pos[x]["PROPN_PROB"]).astype(float)

    df["tf_idf"] = (
        (df["freq_in_text"] / df["doc_length_tokens"].clip(lower=1))
        * np.log((n_docs + 1) / (df["document_frequency"] + 1))
    )
    df["freq_in_text"] = df["freq_in_text"].astype(float)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline de clasificación
# ─────────────────────────────────────────────────────────────────────────────

def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=5),
                CATEGORICAL_COLS,
            ),
            ("num", StandardScaler(), NUMERIC_COLS),
        ],
        remainder="drop",
    )


def sample_training_frame(df: pd.DataFrame, o_ratio: int = 4) -> pd.DataFrame:
    positive = df[df["label_bio"] != "O"]
    outside  = df[df["label_bio"] == "O"]
    target_o = min(len(outside), len(positive) * o_ratio)
    sampled_o = outside.sample(n=target_o, random_state=42)
    sampled = pd.concat([positive, sampled_o], ignore_index=True)
    return sampled.sample(frac=1.0, random_state=42).reset_index(drop=True)


def feature_name_groups(preprocessor) -> dict[str, list[int]]:
    groups = defaultdict(list)
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_COLS)
    all_names = list(cat_names) + list(NUMERIC_COLS)
    for idx, name in enumerate(all_names):
        base = None
        for feat in CATEGORICAL_COLS:
            if name.startswith(f"{feat}_"):
                base = feat
                break
        if base is None:
            base = name
        groups[base].append(idx)
    return groups


def aggregate_importance(pipeline, X_sample, y_sample) -> pd.DataFrame:
    """
    Devuelve importancia de TODOS los rasgos interpretables desglosada por clase:
      - Imp_BT  : importancia para la etiqueta B-T
      - Imp_IT  : importancia para la etiqueta I-T
      - Imp_T   : media(B-T, I-T) — importancia unificada para TÉRMINO
      - Imp_O   : importancia para la etiqueta O (referencia)

    Para modelos lineales usa coef_ (media de |pesos| de las dummies OHE).
    Para Random Forest usa feature_importances_ (agnóstico de clase) en las
    tres columnas término y entrena adicionalmente un clasificador binario T/O
    para desambiguar la dirección.
    """
    pre    = pipeline.named_steps["pre"]
    clf    = pipeline.named_steps["clf"]
    groups = feature_name_groups(pre)
    feature_cols = [f for f in CATEGORICAL_COLS + NUMERIC_COLS if f not in VOCAB_FEATURES]

    if hasattr(clf, "coef_"):
        coef = clf.coef_                        # shape (n_classes, n_feats)
        classes = list(clf.classes_)

        def col_vec(label):
            if label in classes:
                return coef[classes.index(label)]   # pesos con signo
            return np.zeros(coef.shape[1])

        vec_bt = col_vec("B-T")
        vec_it = col_vec("I-T")
        vec_o  = col_vec("O")

        # Media de pesos CON SIGNO: positivo = favorece la etiqueta
        def score(vec, idxs):
            return float(vec[idxs].mean()) if idxs else 0.0

        rows = []
        for feat in feature_cols:
            idxs = groups.get(feat, [])
            imp_bt = score(vec_bt, idxs)
            imp_it = score(vec_it, idxs)
            imp_o  = score(vec_o,  idxs)
            imp_t  = (imp_bt + imp_it) / 2
            rows.append({"Rasgo": feat,
                         "Imp_BT": imp_bt, "Imp_IT": imp_it,
                         "Imp_T": imp_t,   "Imp_O": imp_o})

    elif hasattr(clf, "feature_importances_"):
        fi = clf.feature_importances_           # class-agnostic

        # Clasificador binario T/O para estimar dirección
        X_tr = pre.transform(X_sample)
        y_bin = np.array(["T" if l in {"B-T","I-T"} else "O" for l in y_sample])
        lr_bin = LogisticRegression(max_iter=500, class_weight={"T":4,"O":1}).fit(X_tr, y_bin)
        coef_t = lr_bin.coef_[0]               # weight hacia clase T

        rows = []
        for feat in feature_cols:
            idxs = groups.get(feat, [])
            imp   = float(fi[idxs].sum())       if idxs else 0.0
            direc = float(np.abs(coef_t[idxs]).mean()) if idxs else 0.0
            rows.append({"Rasgo": feat,
                         "Imp_BT": imp, "Imp_IT": imp,
                         "Imp_T": imp,  "Imp_O": direc})
    else:
        raise ValueError("El clasificador no expone coef_ ni feature_importances_.")

    df = pd.DataFrame(rows).sort_values("Imp_T", ascending=False).reset_index(drop=True)
    return df


def evaluate_models(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Manual cross-validation loop with per-fold recomputation of global
    statistical features (freq_global, document_frequency,
    contextual_diversity, dispersion, tf_idf).

    For each fold:
      1. Identify training doc IDs.
      2. Recompute the five global features from training docs only.
      3. Subsample the training set (4:1 O:T ratio).
      4. Train each model and evaluate on the full test partition.
    """
    cv     = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    groups = df["doc_id"]
    y_all  = df["label_bio"]
    X_all  = df[CATEGORICAL_COLS + NUMERIC_COLS]   # used only to drive the split

    accum: dict[str, dict[str, list]] = {
        name: {k: [] for k in [
            "accuracy", "precision_macro", "recall_macro",
            "recall_term", "f1_macro", "f1_weighted",
        ]}
        for name in MODELS
    }

    for fold_i, (train_idx, test_idx) in enumerate(
        cv.split(X_all, y_all, groups), 1
    ):
        train_doc_ids = set(groups.iloc[train_idx].unique())

        # Recompute global stats using only training documents
        df_fold   = recompute_global_stats(df, train_doc_ids)

        train_raw = df_fold.iloc[train_idx]
        test_df   = df_fold.iloc[test_idx]
        train_sampled = sample_training_frame(train_raw)

        X_tr = train_sampled[CATEGORICAL_COLS + NUMERIC_COLS]
        y_tr = train_sampled["label_bio"]
        X_te = test_df[CATEGORICAL_COLS + NUMERIC_COLS]
        y_te = test_df["label_bio"]

        print(f"  fold {fold_i}  train_docs={len(train_doc_ids)}"
              f"  train_tok={len(X_tr)}  test_tok={len(X_te)}")

        for name, clf in MODELS.items():
            pipe = Pipeline([("pre", build_preprocessor()), ("clf", clf)])
            pipe.fit(X_tr, y_tr)
            y_pred = pipe.predict(X_te)

            accum[name]["accuracy"].append(
                accuracy_score(y_te, y_pred))
            accum[name]["precision_macro"].append(
                precision_score(y_te, y_pred, average="macro", zero_division=0))
            accum[name]["recall_macro"].append(
                recall_score(y_te, y_pred, average="macro", zero_division=0))
            accum[name]["recall_term"].append(
                recall_score(y_te, y_pred, labels=["B-T","I-T"],
                             average="macro", zero_division=0))
            accum[name]["f1_macro"].append(
                f1_score(y_te, y_pred, average="macro", zero_division=0))
            accum[name]["f1_weighted"].append(
                f1_score(y_te, y_pred, average="weighted", zero_division=0))

    metric_rows = []
    for name, scores in accum.items():
        metric_rows.append({
            "Clasificador":        name,
            "Accuracy":            np.mean(scores["accuracy"]),
            "Accuracy_std":        np.std(scores["accuracy"]),
            "Precision_macro":     np.mean(scores["precision_macro"]),
            "Precision_macro_std": np.std(scores["precision_macro"]),
            "Recall_macro":        np.mean(scores["recall_macro"]),
            "Recall_macro_std":    np.std(scores["recall_macro"]),
            "Recall_term":         np.mean(scores["recall_term"]),
            "Recall_term_std":     np.std(scores["recall_term"]),
            "F1_macro":            np.mean(scores["f1_macro"]),
            "F1_macro_std":        np.std(scores["f1_macro"]),
            "F1_weighted":         np.mean(scores["f1_weighted"]),
            "F1_weighted_std":     np.std(scores["f1_weighted"]),
        })

    metrics = (
        pd.DataFrame(metric_rows)
        .sort_values(["Recall_term", "F1_macro"], ascending=False)
        .reset_index(drop=True)
    )

    # Fit best model on full corpus (global stats are fine here — no test set)
    best_name     = metrics.iloc[0]["Clasificador"]
    sampled_all   = sample_training_frame(df)
    X_all_sampled = sampled_all[CATEGORICAL_COLS + NUMERIC_COLS]
    y_all_sampled = sampled_all["label_bio"]
    best_pipe     = Pipeline([("pre", build_preprocessor()), ("clf", MODELS[best_name])])
    best_pipe.fit(X_all_sampled, y_all_sampled)

    importance = aggregate_importance(best_pipe, X_all_sampled, y_all_sampled)
    return metrics, importance, best_pipe


def classwise_reports(df: pd.DataFrame, best_pipe) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Devuelve dos DataFrames:
      - bio_report: métricas por clase B-T, I-T, O
      - bin_report: métricas colapsadas T (= B-T + I-T) vs O

    Usa el mismo bucle con recomputación de rasgos globales por fold
    que evaluate_models(), de modo que los resultados sean comparables.
    """
    cv     = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    groups = df["doc_id"]
    y_bio_all = df["label_bio"]
    X_all = df[CATEGORICAL_COLS + NUMERIC_COLS]

    bio_rows = []
    bin_rows = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(X_all, y_bio_all, groups), 1):
        train_doc_ids = set(groups.iloc[train_idx].unique())
        df_fold = recompute_global_stats(df, train_doc_ids)

        train_sampled = sample_training_frame(df_fold.iloc[train_idx])
        test_df       = df_fold.iloc[test_idx]

        X_train    = train_sampled[CATEGORICAL_COLS + NUMERIC_COLS]
        y_train    = train_sampled["label_bio"]
        X_test     = test_df[CATEGORICAL_COLS + NUMERIC_COLS]
        y_test_bio = test_df["label_bio"]
        y_test_bin = test_df["label"]

        best_pipe.fit(X_train, y_train)
        pred_bio = best_pipe.predict(X_test)
        pred_bin = [collapse_label(p) for p in pred_bio]

        # BIO report
        rep_bio = classification_report(
            y_test_bio, pred_bio,
            labels=BIO_LABELS, output_dict=True, zero_division=0,
        )
        for lbl in BIO_LABELS:
            bio_rows.append({
                "Fold":      fold,
                "Clase":     lbl,
                "Precision": rep_bio[lbl]["precision"],
                "Recall":    rep_bio[lbl]["recall"],
                "F1":        rep_bio[lbl]["f1-score"],
                "Support":   rep_bio[lbl]["support"],
            })

        # Binary report
        rep_bin = classification_report(
            y_test_bin, pred_bin,
            labels=BINARY_LABELS, output_dict=True, zero_division=0,
        )
        for lbl in BINARY_LABELS:
            bin_rows.append({
                "Fold":      fold,
                "Clase":     lbl,
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
                Precision=("Precision", "mean"),
                Precision_std=("Precision", "std"),
                Recall=("Recall", "mean"),
                Recall_std=("Recall", "std"),
                F1=("F1", "mean"),
                F1_std=("F1", "std"),
                Support=("Support", "mean"),
            )
        )

    bio_report = agg(bio_rows)
    bin_report = agg(bin_rows)
    return bio_report, bin_report


# ─────────────────────────────────────────────────────────────────────────────
# Escritura LaTeX
# ─────────────────────────────────────────────────────────────────────────────

def fmt_pm(mean: float, std: float) -> str:
    return rf"{mean:.3f} $\pm$ {std:.3f}"


def write_metrics_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} l c c c c c c @{}}",
        r"\toprule",
        (r"\textbf{Clasificador} & \textbf{Acc.} & \textbf{Prec.\ macro} "
         r"& \textbf{Rec.\ macro} & \textbf{Rec.\ término} "
         r"& \textbf{F1 macro} & \textbf{F1 pond.} \\"),
        r"\midrule",
    ]
    for row in df.itertuples(index=False):
        lines.append(
            f"{escape_latex(row.Clasificador)} & "
            f"{fmt_pm(row.Accuracy, row.Accuracy_std)} & "
            f"{fmt_pm(row.Precision_macro, row.Precision_macro_std)} & "
            f"{fmt_pm(row.Recall_macro, row.Recall_macro_std)} & "
            f"{fmt_pm(row.Recall_term, row.Recall_term_std)} & "
            f"{fmt_pm(row.F1_macro, row.F1_macro_std)} & "
            f"{fmt_pm(row.F1_weighted, row.F1_weighted_std)} \\\\"
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


def write_classwise_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} l c c c c c r @{}}",
        r"\toprule",
        (r"\textbf{Clase} & \textbf{Precisión} & \textbf{$\sigma$} "
         r"& \textbf{Recall} & \textbf{$\sigma$} "
         r"& \textbf{F1} & \textbf{$\sigma$} \quad \textbf{Support} \\"),
        r"\midrule",
    ]
    for row in df.itertuples(index=False):
        lines.append(
            rf"\texttt{{{escape_latex(row.Clase)}}} & "
            f"{row.Precision:.3f} & {row.Precision_std:.3f} & "
            f"{row.Recall:.3f} & {row.Recall_std:.3f} & "
            f"{row.F1:.3f} & {row.F1_std:.3f} \\quad {row.Support:.0f} \\\\"
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


def write_importance_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    """
    Tabla completa de importancia de rasgos desglosada por clase de término.
    Columnas: Rasgo | Imp B-T | Imp I-T | Imp T (unificado) | Imp O
    Ordenada por Imp_T descendente. Se incluyen todos los rasgos interpretables.
    """
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{} r l c c c c @{}}",
        r"\toprule",
        (r"\# & \textbf{Rasgo} & \textbf{Imp.\ B-T} "
         r"& \textbf{Imp.\ I-T} & \textbf{Imp.\ T\,(unif.)} & \textbf{Imp.\ O} \\"),
        r"\midrule",
    ]
    for i, row in enumerate(df.itertuples(index=False), 1):
        lines.append(
            rf"{i} & \texttt{{{escape_latex(row.Rasgo)}}} & "
            f"{row.Imp_BT:.4f} & {row.Imp_IT:.4f} & {row.Imp_T:.4f} & {row.Imp_O:.4f} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\normalsize",
        r"\end{table}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_feature_tables() -> None:
    linguistic = r"""\begin{table}[ht]
\centering
\begingroup
\small
\begin{tabular}{@{}p{5cm}p{6.2cm}p{2.6cm}@{}}
\toprule
\multicolumn{3}{c}{\textbf{Rasgos lingüísticos en el modelado BIO}} \\
\midrule
\textbf{Rasgo} & \textbf{Descripción} & \textbf{Tipo} \\
\midrule
\multicolumn{3}{l}{\textbf{\textit{Formales y léxicos}}} \\
\texttt{token\_lower} & Forma superficial normalizada del token & Categórico \\
\texttt{lemma} & Lema normalizado del token & Categórico \\
\texttt{shape} & Patrón ortográfico general (\texttt{Xxxx}, \texttt{xxxx}, \texttt{dd}) & Categórico \\
\texttt{is\_stop} & Marca si el token es palabra funcional & Binario \\
\texttt{is\_punct} & Marca si el token es puntuación & Binario \\
\texttt{is\_alpha} & Marca si el token es alfabético & Binario \\
\texttt{is\_acronym} & Marca si el token es sigla en mayúsculas & Binario \\
\addlinespace
\multicolumn{3}{l}{\textbf{\textit{Morfosintácticos}}} \\
\texttt{pos} & Categoría gramatical universal del token & Categórico \\
\texttt{tag} & Etiqueta morfosintáctica específica del analizador & Categórico \\
\texttt{dep} & Relación de dependencia sintáctica & Categórico \\
\texttt{is\_noun}, \texttt{is\_verb}, \texttt{is\_adj}, \texttt{is\_propn} & Binarización de categorías gramaticales frecuentes en terminología & Binario \\
\texttt{lemma\_pos\_noun\_prob}, \texttt{lemma\_pos\_verb\_prob}, \texttt{lemma\_pos\_adj\_prob}, \texttt{lemma\_pos\_propn\_prob} & Probabilidades condicionales de POS dado el lema & Continuo \\
\addlinespace
\multicolumn{3}{l}{\textbf{\textit{Estructura sintáctica y discurso}}} \\
\texttt{is\_in\_noun\_phrase} & El token aparece dentro de un sintagma nominal & Binario \\
\texttt{is\_in\_noun\_chunk\_head} & El token es cabeza del sintagma nominal & Binario \\
\texttt{has\_adjective\_modifier} & Presenta modificador adjetival dependiente & Binario \\
\texttt{has\_pre\_modifier} & Presenta modificadores antepuestos & Binario \\
\texttt{position\_in\_sentence} & Posición relativa del token dentro de la oración & Continuo \\
\texttt{avg\_position\_in\_sentence} & Posición media del lema en las oraciones del documento & Continuo \\
\texttt{in\_definition\_context} & El token aparece en una oración con patrón definitorio & Binario \\
\bottomrule
\end{tabular}
\endgroup
\caption{Rasgos lingüísticos incorporados al modelo BIO de detección terminológica.}
\label{tab:features_linguistic}
\end{table}
"""
    statistical = r"""\begin{table}[ht]
\centering
\begingroup
\small
\begin{tabular}{@{}p{5cm}p{6.7cm}p{2.2cm}@{}}
\toprule
\multicolumn{3}{c}{\textbf{Rasgos estadísticos en el modelado BIO}} \\
\midrule
\textbf{Rasgo} & \textbf{Descripción} & \textbf{Tipo} \\
\midrule
\multicolumn{3}{l}{\textbf{\textit{Frecuencia local y global}}} \\
\texttt{freq\_in\_text} & Frecuencia del lema en el documento actual & Continuo \\
\texttt{freq\_global} & Frecuencia total del lema en el corpus & Continuo \\
\texttt{document\_frequency} & Número de documentos en que aparece el lema & Continuo \\
\texttt{tf\_idf} & Peso TF--IDF del lema en el documento & Continuo \\
\addlinespace
\multicolumn{3}{l}{\textbf{\textit{Distribución y diversidad}}} \\
\texttt{dispersion} & Dispersión de Juilland del lema a lo largo del corpus & Continuo \\
\texttt{contextual\_diversity} & Número de contextos oracionales distintos del lema & Continuo \\
\texttt{lexical\_variety} & Variedad léxica del documento de procedencia & Continuo \\
\addlinespace
\multicolumn{3}{l}{\textbf{\textit{Trazabilidad}}} \\
\texttt{doc\_id} & Identificador del documento de origen & Identificador \\
\texttt{sentence\_id} & Identificador de la oración de origen & Identificador \\
\texttt{token\_id} & Identificador posicional del token en el documento & Identificador \\
\bottomrule
\end{tabular}
\endgroup
\caption{Rasgos estadísticos y campos de trazabilidad del dataset BIO para detección terminológica.}
\label{tab:features_statistical}
\end{table}
"""
    (TABLAS_DIR / "tabla_features_linguistic.tex").write_text(linguistic, encoding="utf-8")
    (TABLAS_DIR / "tabla_features_statistical.tex").write_text(statistical, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Ejecución por lengua
# ─────────────────────────────────────────────────────────────────────────────

def run_one(lang: str, docs, terms):
    print(f"\n{'='*50}")
    print(f"  Procesando corpus {lang.upper()}")
    print(f"{'='*50}")

    df = process_language(lang, docs, terms)
    dist = df["label_bio"].value_counts().to_dict()
    print(f"  Distribución BIO: {dist}")

    metrics, importance, best_pipe = evaluate_models(df)
    bio_report, bin_report = classwise_reports(df, best_pipe)

    # CSV
    df.to_csv(BIO_DIR / f"{lang}_bio_tokens.csv", index=False)
    metrics.to_csv(BIO_DIR / f"{lang}_metricas.csv", index=False)
    importance.to_csv(BIO_DIR / f"{lang}_importancia_rasgos.csv", index=False)
    bio_report.to_csv(BIO_DIR / f"{lang}_clases_bio.csv", index=False)
    bin_report.to_csv(BIO_DIR / f"{lang}_clases_bin.csv", index=False)

    lang_upper = lang.upper()
    best_name  = metrics.iloc[0]["Clasificador"]

    # LaTeX — métricas de modelos
    write_metrics_latex(
        metrics,
        TABLAS_DIR / f"tabla_bio_metricas_{lang}.tex",
        (f"Resultados de clasificadores (entrenamiento BIO con recall priorizado) "
         f"para el corpus {lang_upper}. "
         f"\\textit{{Rec.\\ término}} = recall medio sobre B-T e I-T."),
        f"tab:bio_metricas_{lang}",
    )

    # LaTeX — métricas por clase BIO
    write_classwise_latex(
        bio_report,
        TABLAS_DIR / f"tabla_bio_clases_bio_{lang}.tex",
        (f"Rendimiento por clase BIO (B-T, I-T, O) del mejor modelo "
         f"({escape_latex(best_name)}) para el corpus {lang_upper}."),
        f"tab:bio_clases_bio_{lang}",
    )

    # LaTeX — métricas colapsadas T/O
    write_classwise_latex(
        bin_report,
        TABLAS_DIR / f"tabla_bio_clases_bin_{lang}.tex",
        (f"Rendimiento colapsado (T = B-T + I-T vs O) del mejor modelo "
         f"({escape_latex(best_name)}) para el corpus {lang_upper}."),
        f"tab:bio_clases_bin_{lang}",
    )

    # LaTeX — importancia de rasgos
    write_importance_latex(
        importance,
        TABLAS_DIR / f"tabla_bio_importancia_{lang}.tex",
        (f"Importancia de todos los rasgos interpretables del mejor modelo BIO "
         f"para el corpus {lang_upper}, desglosada por etiqueta (B-T, I-T) "
         r"y unificada para la clase término (T = B-T $\cup$ I-T). "
         r"Valores mayores indican mayor discriminación hacia esa etiqueta."),
        f"tab:bio_importancia_{lang}",
    )

    print(f"  Mejor modelo: {best_name}")
    print(f"  Recall término: {metrics.iloc[0]['Recall_term']:.3f} ± {metrics.iloc[0]['Recall_term_std']:.3f}")
    print(f"  F1 macro:       {metrics.iloc[0]['F1_macro']:.3f} ± {metrics.iloc[0]['F1_macro_std']:.3f}")

    return df, metrics, importance, bio_report, bin_report


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    terms_en = load_terms_en()
    terms_es = load_terms_es()
    docs_en  = load_docs_en()
    docs_es  = load_docs_es()

    run_one("en", docs_en, terms_en)
    run_one("es", docs_es, terms_es)
    write_feature_tables()
    print("\nListo.")


if __name__ == "__main__":
    main()
