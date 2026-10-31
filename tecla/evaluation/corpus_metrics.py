"""
TECLA – Corpus Representativity Metrics
----------------------------------------
Six metrics computed directly from TECLA's native data structures.
No BIO annotation or external reference corpus required (except keyness).

1. Heaps' Law on raw tokens         — vocabulary saturation
2. Hapax ratio                      — textual mass indicator
3. DP (Gries 2008)                  — term dispersion across documents
4. Bootstrap ranking stability      — confidence in top-N rankings
5. Shannon entropy on 'tema' field  — genre/register diversity
6. Log-likelihood keyness (G²)      — domain specificity vs reference
"""

import math
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# 1. Heaps' Law  V(n) = K · n^β
# ─────────────────────────────────────────────────────────────────────────────

def compute_heaps(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ajusta la ley de Heaps sobre los lemas de las palabras alfabéticas, en el
    orden de los documentos, con unos 5000 puntos de la curva y todos ellos en
    el ajuste (mismo método que el cap. 3 de la tesis).
    β próximo a 0 → vocabulario saturado; próximo a 1 → sigue creciendo.
    """
    import numpy as np

    seen: set = set()
    tokens_x: List[int] = []
    types_y: List[int] = []

    total_est = sum(len(d.get("tokens", [])) for d in documents)
    step = max(1, total_est // 5_000)

    counter = 0
    for doc in documents:
        for tok in doc.get("tokens", []):
            lemma = tok.get("lemma", "").lower()
            if not lemma or not tok.get("text", lemma).isalpha():
                continue
            seen.add(lemma)
            counter += 1
            if counter % step == 0:
                tokens_x.append(counter)
                types_y.append(len(seen))

    # Always include the final point
    if not tokens_x or tokens_x[-1] != counter:
        tokens_x.append(counter)
        types_y.append(len(seen))

    if len(tokens_x) < 10:
        return {
            "k": None, "beta": None,
            "tokens": tokens_x, "types": types_y, "predicted": [],
            "total_tokens": counter, "total_types": len(seen),
            "interpretation": "Corpus demasiado pequeño para ajustar Heaps.",
        }

    log_n = np.log(np.array(tokens_x, dtype=float))
    log_v = np.log(np.array(types_y, dtype=float))
    slope, intercept = np.polyfit(log_n, log_v, 1)
    beta = float(slope)
    k = float(math.exp(intercept))
    predicted = [k * n ** beta for n in tokens_x]

    return {
        "k":             round(k, 3),
        "beta":          round(beta, 4),
        "tokens":        tokens_x,
        "types":         types_y,
        "predicted":     predicted,
        "total_tokens":  counter,
        "total_types":   len(seen),
        "interpretation": _beta_label(beta),
    }


def _beta_label(beta: float) -> str:
    if beta < 0.35:
        return "Saturación alta — vocabulario prácticamente estable."
    elif beta < 0.45:
        return "Saturación moderada-alta."
    elif beta < 0.55:
        return "Saturación moderada — añadir más textos mejoraría la cobertura."
    elif beta < 0.65:
        return "Saturación moderada-baja — vocabulario aún en crecimiento notable."
    else:
        return "Saturación baja — el corpus sigue creciendo."


# ─────────────────────────────────────────────────────────────────────────────
# 2. Hapax ratio
# ─────────────────────────────────────────────────────────────────────────────

def compute_hapax_ratio(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Proportion of vocabulary types (lemmas) that appear only once in the
    raw corpus.  Computed from the corpus token stream so that it is
    independent of any min_freq threshold applied during extraction.

    A high hapax ratio (> 0.40) indicates that the corpus lacks sufficient
    textual mass to confirm most vocabulary items.
    """
    if not documents:
        return {"ratio": 0.0, "n_hapax": 0, "n_types": 0}

    freq: Counter = Counter()
    for doc in documents:
        for tok in doc.get("tokens", []):
            lemma = tok.get("lemma", "").strip()
            if lemma:
                freq[lemma] += 1

    n_types  = len(freq)
    n_hapax  = sum(1 for f in freq.values() if f == 1)
    ratio    = round(n_hapax / n_types, 4) if n_types else 0.0

    return {"ratio": ratio, "n_hapax": n_hapax, "n_types": n_types}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Gries' DP — Deviation of Proportions
# ─────────────────────────────────────────────────────────────────────────────

def compute_dp(
    results: List[Dict[str, Any]],
    doc_stats: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Gries (2008) DP:  DP(w) = Σ_i |f_i/F − s_i| / 2
      f_i = freq of w in doc i,  F = total freq,  s_i = relative doc size.
    0 = perfectly dispersed, 1 = maximally concentrated.
    """
    total_tokens = sum(d["tokens"] for d in doc_stats)
    if total_tokens == 0:
        return {}

    doc_size = {d["doc_id"]: d["tokens"] / total_tokens for d in doc_stats}
    doc_ids  = [d["doc_id"] for d in doc_stats]

    dp_scores: Dict[str, float] = {}
    for term in results:
        lemma   = term["lemma"]
        per_doc = term.get("per_doc", {})
        F       = sum(per_doc.values())  # use actual sum to avoid consolidation inflation

        if F == 0:
            dp_scores[lemma] = 1.0
            continue

        total = sum(abs(per_doc.get(d, 0) / F - doc_size.get(d, 0.0)) for d in doc_ids)
        dp_scores[lemma] = round(total / 2, 4)

    return dp_scores


def _freq(term: Dict[str, Any]) -> int:
    """Frecuencia de una unidad: suma de sus apariciones por documento."""
    per_doc = term.get("per_doc") or {}
    return sum(per_doc.values()) if per_doc else int(term.get("frequency", 0))


def top_by_frequency(results: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Las n unidades más frecuentes (criterio del cap. 3 de la tesis)."""
    return sorted(results, key=_freq, reverse=True)[:n]


def dp_stats(
    dp_scores: Dict[str, float],
    results: List[Dict[str, Any]],
    top_n: int = 50,
) -> Dict[str, Any]:
    """DP medio de las top_n unidades más frecuentes (como en el cap. 3 de la tesis)."""
    top_lemmas = [t["lemma"] for t in top_by_frequency(results, top_n)]
    top_dp = [dp_scores[l] for l in top_lemmas if l in dp_scores]
    if not top_dp:
        return {"mean": 0.5, "pct_high": 0.0}

    sorted_dp = sorted(top_dp)
    return {
        "mean":     round(sum(top_dp) / len(top_dp), 4),
        "median":   round(sorted_dp[len(sorted_dp) // 2], 4),
        "pct_high": round(sum(1 for v in top_dp if v < 0.40) / len(top_dp), 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Bootstrap ranking stability
# ─────────────────────────────────────────────────────────────────────────────

def compute_bootstrap_stability(
    results: List[Dict[str, Any]],
    doc_stats: List[Dict[str, Any]],
    n_bootstrap: int = 200,
    top_n: int = 30,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Proporción de las top_n unidades más frecuentes que siguen entre las top_n
    al remuestrear los documentos con reposición (B = n_bootstrap). El orden es
    el mismo, por frecuencia, en el corpus original y en cada remuestreo, como
    en el cap. 3 de la tesis.
    """
    rng     = random.Random(seed)
    doc_ids = [d["doc_id"] for d in doc_stats]
    n_docs  = len(doc_ids)

    if n_docs < 2 or not results:
        return {"stability_index": None, "term_stability": {}, "n_bootstrap": 0}

    per_doc_lookup = {t["lemma"]: t.get("per_doc", {}) for t in results}
    original_top   = {t["lemma"] for t in top_by_frequency(results, top_n)}

    in_top: Dict[str, int] = defaultdict(int)

    for _ in range(n_bootstrap):
        sampled  = [rng.choice(doc_ids) for _ in range(n_docs)]
        s_count  = Counter(sampled)

        boot_freq = {
            lemma: sum(per_doc.get(d, 0) * cnt for d, cnt in s_count.items())
            for lemma, per_doc in per_doc_lookup.items()
        }

        boot_top = {
            lemma
            for lemma, _ in sorted(boot_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        }
        for lemma in boot_top:
            in_top[lemma] += 1

    term_stability  = {l: round(c / n_bootstrap, 4) for l, c in in_top.items()}
    orig_stab       = [term_stability.get(l, 0.0) for l in original_top]
    stability_index = round(sum(orig_stab) / len(orig_stab), 4) if orig_stab else 0.0

    return {
        "stability_index": stability_index,
        "term_stability":  term_stability,
        "n_bootstrap":     n_bootstrap,
        "top_n":           top_n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Shannon entropy on metadata field
# ─────────────────────────────────────────────────────────────────────────────

def compute_genre_entropy(
    corpus_metadata: Dict[str, Dict[str, str]],
    field: str = "tema",
) -> Dict[str, Any]:
    """
    Shannon entropy H over a metadata field (default: 'tema').
    H' = H / log₂(n_categories) ∈ [0, 1].  Higher = more balanced diversity.
    """
    values = [
        meta.get(field, "").strip()
        for meta in corpus_metadata.values()
        if meta.get(field, "").strip()
    ]

    if not values:
        return {
            "entropy": None, "entropy_norm": None,
            "n_categories": 0, "distribution": {},
            "warning": f"Ningún documento tiene el campo '{field}' rellenado.",
        }

    counts = Counter(values)
    n      = sum(counts.values())
    probs  = [c / n for c in counts.values()]
    h      = -sum(p * math.log2(p) for p in probs if p > 0)
    n_cats = len(counts)
    h_norm = h / math.log2(n_cats) if n_cats > 1 else 1.0

    return {
        "entropy":      round(h, 4),
        "entropy_norm": round(h_norm, 4),
        "n_categories": n_cats,
        "distribution": dict(counts.most_common()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. Log-likelihood keyness (G²)
# ─────────────────────────────────────────────────────────────────────────────

def compute_keyness(
    results: List[Dict[str, Any]],
    reference: Dict[str, float],
    corpus_size: int,
    reference_size: int,
) -> List[Dict[str, Any]]:
    """
    Log-likelihood keyness (G²) and log ratio for single-word terms.
    Only single-word terms are compared (reference corpora rarely cover multiword terms).
    """
    rows = []
    for term in results:
        lemma = term["lemma"]
        if " " in lemma:
            continue
        a  = term["frequency"]
        b  = reference.get(lemma, 0.0)
        N1, N2 = corpus_size, reference_size
        if a == 0 or N1 == 0 or N2 == 0:
            continue
        E1 = N1 * (a + b) / (N1 + N2)
        E2 = N2 * (a + b) / (N1 + N2)
        g2 = 2 * (
            (a * math.log(a / E1) if a > 0 and E1 > 0 else 0.0) +
            (b * math.log(b / E2) if b > 0 and E2 > 0 else 0.0)
        )
        log_ratio = math.log2((a / N1 + 1e-9) / (b / N2 + 1e-9))
        rows.append({
            "lemma":      lemma,
            "freq_corp":  a,
            "freq_ref":   round(b, 1),
            "g2":         round(g2, 2),
            "log_ratio":  round(log_ratio, 3),
            "direction":  "▲" if a / N1 >= b / N2 else "▼",
        })
    return sorted(rows, key=lambda x: x["g2"], reverse=True)


def load_reference_corpus(path: str) -> Tuple[Dict[str, float], int]:
    """
    Load a reference frequency list from CSV.
    Expected columns: one for lemma/word, one for frequency/count.
    """
    import csv
    reference: Dict[str, float] = {}
    total = 0.0

    with open(path, encoding="utf-8") as f:
        reader    = csv.DictReader(f)
        fields    = reader.fieldnames or []
        freq_col  = next((c for c in fields if c.lower() in
                          ("frequency", "freq", "count", "n", "frecuencia")),
                         fields[1] if len(fields) > 1 else None)
        lemma_col = next((c for c in fields if c.lower() in
                          ("lemma", "word", "token", "term", "lema", "palabra")),
                         fields[0] if fields else None)
        if not freq_col or not lemma_col:
            raise ValueError("El CSV debe tener columnas 'lemma'/'word' y 'frequency'/'count'.")
        for row in reader:
            lemma = row[lemma_col].strip().lower()
            try:
                freq = float(row[freq_col])
            except (ValueError, KeyError):
                continue
            reference[lemma] = freq
            total += freq

    return reference, int(total)


# ─────────────────────────────────────────────────────────────────────────────
# Terminological adequacy metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_term_adequacy(
    results: List[Dict[str, Any]],
    n_docs: int,
    total_tokens: int,
) -> Dict[str, Any]:
    """
    Metrics that measure whether the corpus is adequate for terminology
    extraction, computed directly from the extracted term list.

    Returns
    -------
    dict with keys:
        density           – term tokens / total tokens  (terminological richness)
        confirmation_rate – proportion of CT in ≥ 2 documents
        key_coverage      – mean doc coverage (doc_freq/n_docs) of top-20 % CT
        multiword_ratio   – proportion of CT with ≥ 2 tokens
        n_terms           – number of extracted CT
    """
    empty = {
        "density": 0.0, "confirmation_rate": 0.0,
        "key_coverage": 0.0, "multiword_ratio": 0.0, "n_terms": 0,
    }
    if not results or n_docs == 0 or total_tokens == 0:
        return empty

    n = len(results)

    # 1. Terminological density
    density = sum(t.get("frequency", 0) for t in results) / total_tokens

    # 2. Confirmation rate: CT confirmed in 2+ documents
    confirmed = sum(1 for t in results if t.get("doc_frequency", 1) >= 2)
    confirmation_rate = confirmed / n

    # 3. Key-term coverage: top-20 % CT by terminologicity
    n_top    = max(1, n // 5)
    top      = sorted(results, key=lambda t: t.get("terminologicity", 0), reverse=True)[:n_top]
    key_coverage = sum(t.get("doc_frequency", 1) / n_docs for t in top) / len(top)

    # 4. Multiword proportion
    multiword_ratio = sum(1 for t in results if t.get("length", 1) >= 2) / n

    return {
        "density":           round(density, 5),
        "confirmation_rate": round(confirmation_rate, 4),
        "key_coverage":      round(key_coverage, 4),
        "multiword_ratio":   round(multiword_ratio, 4),
        "n_terms":           n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Composite representativity score
# ─────────────────────────────────────────────────────────────────────────────

def compute_representativity_score(
    heaps: Dict[str, Any],
    hapax: Dict[str, Any],
    dp_summary: Dict[str, Any],
    stability: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Índice de Representatividad Terminológica (IRT), escala 0–100: es el índice
    que muestra la interfaz de TECLA y el que se describe en la tesis (cap. 8).

    Media, con el mismo peso, de hasta tres componentes normalizados en [0, 1]
    (más alto = corpus más adecuado):
      - saturación  = 1 − (β − 0,25) / 0,65         (β de Heaps sobre lemas)
      - dispersión  = (0,80 − DP medio) / 0,40       (DP de las 50 unidades más frecuentes)
      - estabilidad = índice bootstrap                (opcional)
    La proporción de hápax se sigue calculando como dato descriptivo, pero no
    entra en el índice: describe el vocabulario, no la terminología.
    Interpretación: ≥ 75 muy representativo; 60–74 representativo;
    40–59 moderadamente; 25–39 poco; < 25 escasamente representativo.
    """
    weights: Dict[str, float] = {}

    # ── Saturation — Heaps β (weight 0.25) ───────────────────────────────
    if heaps.get("beta") is not None:
        sat = max(0.0, min(1.0, 1.0 - (heaps["beta"] - 0.25) / 0.65))
        weights["saturación"] = (sat, 0.25)

    # ── Dispersion / DP (weight 0.25) ─────────────────────────────────────
    dp_s = max(0.0, min(1.0, (0.80 - dp_summary.get("mean", 0.5)) / 0.40))
    weights["dispersión"] = (dp_s, 0.25)

    # ── Bootstrap stability — optional (weight 0.25) ──────────────────────
    if stability and stability.get("stability_index") is not None:
        weights["estabilidad"] = (stability["stability_index"], 0.25)

    if not weights:
        return {"score": 0, "label": "Sin datos", "color": "#6b7280",
                "description": "", "components": {}}

    total_w = sum(w for _, w in weights.values())
    score   = round(sum(v * w for v, w in weights.values()) / total_w * 100)

    # Expose plain component dict for callers
    components: List[Tuple[str, float]] = [(k, v) for k, (v, _) in weights.items()]

    if score >= 75:
        label, color = "muy representativo",              "#16a34a"
    elif score >= 60:
        label, color = "representativo",                  "#65a30d"
    elif score >= 40:
        label, color = "moderadamente representativo",    "#d97706"
    elif score >= 25:
        label, color = "poco representativo",             "#ea580c"
    else:
        label, color = "escasamente representativo",      "#dc2626"

    # Natural-language description: what pulls the index up and what pulls
    # it down, read from the same components that make up the score, so that
    # the text can never contradict the label.
    def _num(x: float, nd: int = 2) -> str:
        return "{:.{}f}".format(x, nd).replace(".", ",")

    beta = heaps.get("beta")
    dp_m = dp_summary.get("mean", 0.5)
    texts = {
        "saturación": (
            "el vocabulario está cerca de saturarse (exponente de Heaps = {})".format(_num(beta or 0)),
            "el vocabulario crece a un ritmo moderado (exponente de Heaps = {})".format(_num(beta or 0)),
            "el vocabulario sigue creciendo (exponente de Heaps = {}), de modo que nuevos textos "
            "aportarían vocabulario nuevo".format(_num(beta or 0)),
        ),
        "dispersión": (
            "las unidades más frecuentes se reparten por los documentos "
            "(DP medio = {})".format(_num(dp_m)),
            "las unidades más frecuentes se reparten de forma desigual "
            "(DP medio = {})".format(_num(dp_m)),
            "las unidades más frecuentes se concentran en pocos documentos "
            "(DP medio = {})".format(_num(dp_m)),
        ),
        "estabilidad": (
            "el núcleo del inventario se mantiene al cambiar los documentos",
            "el núcleo del inventario varía en parte según los documentos",
            "el núcleo del inventario cambia según los documentos que se incluyan",
        ),
    }
    pros = [texts[k][0] for k, v in components if v >= 0.66]
    mids = [texts[k][1] for k, v in components if 0.40 <= v < 0.66]
    cons = [texts[k][2] for k, v in components if v < 0.40]
    sentences = []
    if pros:
        sentences.append("A favor: " + "; ".join(pros) + ".")
    if mids:
        sentences.append("En un punto intermedio: " + "; ".join(mids) + ".")
    if cons:
        sentences.append("En contra: " + "; ".join(cons) + ".")
    description = " ".join(sentences)

    return {
        "score":       score,
        "label":       label,
        "color":       color,
        "description": description,
        "components":  {k: round(v * 100) for k, v in components},
    }
