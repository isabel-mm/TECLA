import random
import matplotlib.pyplot as plt
import pandas as pd

def compute_growth_curve(df: pd.DataFrame, seed: int = 42) -> list[int]:
    """
    Calcula la curva de crecimiento de términos únicos (UTs) a partir de un corpus anotado en formato label.

    Parámetros:
        df (pd.DataFrame): DataFrame con columnas 'file_id', 'token' y 'label'.
        seed (int): Semilla aleatoria para barajar los textos.

    Devuelve:
        list[int]: Lista con el número acumulado de términos únicos tras añadir cada texto.
    """
    text_terms = []

    for file_id, group in df.groupby("file_id"):
        tokens = group["token"].tolist()
        labels = group["label"].tolist()
        terms = []
        current_term = []

        for token, label in zip(tokens, labels):
            if label.startswith("B-"):
                if current_term:
                    terms.append(" ".join(current_term))
                current_term = [token]
            elif label.startswith("I-"):
                current_term.append(token)
            else:
                if current_term:
                    terms.append(" ".join(current_term))
                    current_term = []
        if current_term:
            terms.append(" ".join(current_term))
        text_terms.append((file_id, terms))

    # Barajar textos
    random.seed(seed)
    random.shuffle(text_terms)

    # Calcular curva de crecimiento
    unique_terms = set()
    growth_curve = []
    for _, terms in text_terms:
        unique_terms.update([t.lower() for t in terms])
        growth_curve.append(len(unique_terms))

    return growth_curve


def plot_growth_curve(growth_curve: list[int], show: bool = True):
    """
    Grafica la curva de crecimiento de términos únicos.

    Parámetros:
        growth_curve (list[int]): Lista con el número acumulado de términos únicos.
        show (bool): Si True, muestra el gráfico.
    """
    if show:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(growth_curve) + 1), growth_curve, color='#7fcdbb', linewidth=2)
        plt.title("Incremental Term Coverage", fontsize=14, weight='bold')
        plt.xlabel("Number of texts added", fontsize=12)
        plt.ylabel("Accumulated unique terms", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()


def compute_itc_norm(growth_curve: list[int], tail_fraction: float = 0.2) -> float:
    """
    Calcula el índice normalizado de cobertura incremental terminológica (ITC_norm):
    la proporción del inventario final de términos únicos que aportan los últimos
    textos del corpus (por defecto, el último 20 % de la curva de crecimiento).

    Un valor próximo a 0 indica que los últimos textos apenas añaden términos
    nuevos (corpus saturado); un valor alto, que el inventario sigue creciendo.

    Nota: la versión anterior dividía el incremento medio por el total, lo que
    da siempre 1/N (N = número de textos) y no informaba de la saturación.

    Parámetros:
        growth_curve (list[int]): Lista acumulativa de términos únicos por texto.
        tail_fraction (float): Fracción final de textos que se examina (0 < f <= 1).

    Devuelve:
        float: Valor de ITC_norm, entre 0 y 1.
    """
    if not growth_curve or growth_curve[-1] == 0:
        return 0.0
    if not 0 < tail_fraction <= 1:
        raise ValueError("tail_fraction debe estar en el intervalo (0, 1].")
    n = len(growth_curve)
    k = max(1, round(n * tail_fraction))
    before_tail = growth_curve[n - k - 1] if n - k - 1 >= 0 else 0
    itc_norm = (growth_curve[-1] - before_tail) / growth_curve[-1]
    return round(itc_norm, 4)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def compute_matetr(df: pd.DataFrame, window_size: int = 500, step_size: int = 50) -> float:
    """
    Calcula el valor global del Moving-Average Term-Token Ratio (MATeTR) sobre términos reconstruidos desde etiquetas label.

    Parámetros:
        df (pd.DataFrame): DataFrame con las columnas 'file_id', 'token' y 'label'.
        window_size (int): Tamaño de la ventana deslizante (en número de términos).
        step_size (int): Paso entre ventanas.

    Devuelve:
        float: Valor promedio de TTRs locales (MATeTR).
    """
    all_terms = extract_all_terms(df)
    ttr_values = []

    for i in range(0, len(all_terms) - window_size + 1, step_size):
        window = all_terms[i:i + window_size]
        types = set(window)
        ttr = len(types) / len(window)
        ttr_values.append(ttr)

    return round(float(np.mean(ttr_values)), 4)


def plot_matetr(df: pd.DataFrame, window_size: int = 500, step_size: int = 50):
    """
    Grafica el Moving-Average Term-Token Ratio (MATeTR) sobre UTs.

    Parámetros:
        df (pd.DataFrame): DataFrame con las columnas 'file_id', 'token' y 'label'.
        window_size (int): Tamaño de la ventana deslizante.
        step_size (int): Paso entre ventanas.
    """
    all_terms = extract_all_terms(df)
    ttr_values = []
    positions = []

    for i in range(0, len(all_terms) - window_size + 1, step_size):
        window = all_terms[i:i + window_size]
        types = set(window)
        ttr = len(types) / len(window)
        ttr_values.append(ttr)
        positions.append(i)

    mattr_value = np.mean(ttr_values)

    plt.figure(figsize=(10, 6))
    plt.plot(positions, ttr_values, linewidth=2, color='#7fcdbb', label="Local TTR")
    plt.axhline(mattr_value, color='darkred', linestyle='--', linewidth=2, label=f"MATTR = {mattr_value:.4f}")
    plt.title("Moving-Average Term-Token Ratio (MATeTR)", fontsize=14, weight='bold')
    plt.xlabel("Starting Position in Terms", fontsize=12)
    plt.ylabel("MATTR (0–1)", fontsize=12)
    plt.legend(loc="upper right", frameon=True, facecolor='white', edgecolor='black')
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.2f}"))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def extract_all_terms(df: pd.DataFrame) -> list[str]:
    """
    Reconstruye todas las UTs del corpus y devuelve una lista aplanada de términos en minúscula.

    Parámetros:
        df (pd.DataFrame): DataFrame con 'file_id', 'token' y 'label'.

    Devuelve:
        list[str]: Lista de términos normalizados.
    """
    text_terms = []

    for _, group in df.groupby("file_id"):
        tokens = group["token"].tolist()
        labels = group["label"].tolist()
        terms = []
        current_term = []

        for token, label in zip(tokens, labels):
            if label.startswith("B-"):
                if current_term:
                    terms.append(" ".join(current_term))
                current_term = [token]
            elif label.startswith("I-"):
                current_term.append(token)
            else:
                if current_term:
                    terms.append(" ".join(current_term))
                    current_term = []
        if current_term:
            terms.append(" ".join(current_term))

        text_terms.extend(terms)

    return [term.lower() for term in text_terms]


import pandas as pd
import numpy as np
import random

def analyze_term_coverage_sampling(
    df: pd.DataFrame,
    percentages: list[int] = [25, 50, 75, 90, 100],
    num_trials: int = 500,
    show_stats: bool = False
) -> pd.DataFrame:
    """
    Simula muestreos del corpus a distintos porcentajes y evalúa la cobertura de UTs únicas.

    Parámetros:
        df (pd.DataFrame): DataFrame con anotaciones tokenizadas ('file_id', 'token', 'label').
        percentages (list[int]): Porcentajes del corpus a muestrear.
        num_trials (int): Número de simulaciones por porcentaje.
        show_stats (bool): Si True, imprime resumen estadístico.

    Devuelve:
        pd.DataFrame: Tabla con los resultados de cobertura por muestreo.
    """
    # Reconstrucción de UTs por texto
    df_texts = _build_text_term_df(df)

    # Calcular tamaños de muestra
    total_texts = len(df_texts)
    sample_sizes = [int(total_texts * p / 100) for p in percentages]

    # Simulaciones
    random.seed(42)
    coverage_results = {}
    for size in sample_sizes[:-1]:  # Excluye 100%
        sampled_values = _simulate_sampling(df_texts, size, num_trials)
        coverage_results[size] = sampled_values

    # Valor fijo para el 100%
    all_terms = set(term.lower() for lista in df_texts["terms"] for term in lista)
    coverage_results[total_texts] = [len(all_terms)] * num_trials

    # Armar DataFrame
    df_results = pd.DataFrame({
        f"{p}% ({s} textos)": coverage_results[s]
        for p, s in zip(percentages, sample_sizes)
    })

    if show_stats:
        print("📊 Estadísticas descriptivas de la cobertura de términos únicos:\n")
        print(df_results.describe().round(2).to_markdown())

    return df_results


def _build_text_term_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reconstruye las UTs por texto desde etiquetas label y devuelve un DataFrame por texto.

    Parámetros:
        df (pd.DataFrame): DataFrame con 'file_id', 'token' y 'label'.

    Devuelve:
        pd.DataFrame: DataFrame con columnas 'file_id' y 'terms' (lista de términos).
    """
    grouped = []
    for file_id, group in df.groupby("file_id"):
        tokens = group["token"].tolist()
        labels = group["label"].tolist()
        terms = []
        current_term = []

        for token, label in zip(tokens, labels):
            if label.startswith("B-"):
                if current_term:
                    terms.append(" ".join(current_term))
                current_term = [token]
            elif label.startswith("I-"):
                current_term.append(token)
            else:
                if current_term:
                    terms.append(" ".join(current_term))
                    current_term = []
        if current_term:
            terms.append(" ".join(current_term))

        grouped.append((file_id, terms))

    return pd.DataFrame(grouped, columns=["file_id", "terms"])


def _simulate_sampling(df_texts: pd.DataFrame, sample_size: int, num_trials: int = 500) -> list[int]:
    """
    Realiza simulaciones aleatorias del muestreo y calcula la cobertura de UTs únicas.

    Parámetros:
        df_texts (pd.DataFrame): DataFrame con columnas 'file_id' y 'terms'.
        sample_size (int): Número de textos a seleccionar en cada ensayo.
        num_trials (int): Número de simulaciones.

    Devuelve:
        list[int]: Número de UTs únicas por simulación.
    """
    results = []
    for _ in range(num_trials):
        sample = df_texts.sample(n=sample_size, replace=False, random_state=random.randint(0, 100000))
        sample_terms = set(term.lower() for terms in sample["terms"] for term in terms)
        results.append(len(sample_terms))
    return results

def compute_normalized_mean_coverage(df_sampling: pd.DataFrame) -> float:
    """
    Calcula un valor resumen de cobertura media normalizada (CMN), entre 0 y 1.

    Parámetros:
        df_sampling (pd.DataFrame): Resultado de analyze_term_coverage_sampling().

    Devuelve:
        float: Valor promedio de cobertura normalizada en corpus parciales.
    """
    means = df_sampling.mean()

    # Detectar automáticamente la columna del 100%
    full_col = [col for col in df_sampling.columns if col.startswith("100%")]
    if not full_col:
        print("⚠️ No se encontró la columna del 100% en el muestreo.")
        return np.nan

    full_coverage = means[full_col[0]]

    if pd.isna(full_coverage) or full_coverage == 0:
        print("⚠️ El valor de cobertura total es inválido.")
        return np.nan

    # Excluir solo la columna del 100 % para normalizar
    normalized = means.drop(full_col[0]) / full_coverage
    return round(normalized.mean(), 4)


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def compute_heaps_beta(df: pd.DataFrame) -> dict:
    """
    Ajusta la Ley de Heaps y devuelve los parámetros y vectores utilizados.

    Parámetros:
        df (pd.DataFrame): DataFrame con columnas 'file_id', 'token' y 'label'.

    Devuelve:
        dict: {'k': float, 'beta': float, 'tokens': list[int], 'types': list[int], 'predicted_types': list[float]}
    """
    text_terms = _extract_terms_in_order(df)

    all_tokens = []
    seen_types = set()
    heaps_tokens = []
    heaps_types = []

    for term in text_terms:
        term = term.lower()
        all_tokens.append(term)
        seen_types.add(term)
        heaps_tokens.append(len(all_tokens))
        heaps_types.append(len(seen_types))

    if len(heaps_tokens) <= 10:
        raise ValueError("No hay suficientes términos para ajustar la Ley de Heaps (mínimo 11 observaciones).")

    # Ajuste en log-log a partir del punto 10
    log_tokens = np.log(heaps_tokens[10:])
    log_types = np.log(heaps_types[10:])

    if len(log_tokens) == 0 or len(log_types) == 0:
        raise ValueError("Los vectores para el ajuste log-log están vacíos. Verifica el crecimiento de UTs.")

    slope, intercept = np.polyfit(log_tokens, log_types, 1)
    beta = slope
    k = np.exp(intercept)

    predicted_types = [k * n ** beta for n in heaps_tokens]

    return {
        "k": k,
        "beta": beta,
        "tokens": heaps_tokens,
        "types": heaps_types,
        "predicted_types": predicted_types
    }


def plot_heaps_curve(heaps_data: dict):
    """
    Grafica la curva de crecimiento según la Ley de Heaps a partir del resultado de compute_heaps_beta().

    Parámetros:
        heaps_data (dict): Diccionario con las claves 'tokens', 'types', 'predicted_types', 'k', 'beta'.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(heaps_data["tokens"], heaps_data["types"],
             color='#7fcdbb', linewidth=2,
             label="Crecimiento real")
    plt.plot(heaps_data["tokens"], heaps_data["predicted_types"],
             color='darkred', linestyle='--', linewidth=2,
             label=f"Ajuste Heaps: K={heaps_data['k']:.2f}, β={heaps_data['beta']:.3f}")
    plt.title("Ley de Heaps: crecimiento terminológico", fontsize=14, weight='bold')
    plt.xlabel("Tokens (UTs observadas)", fontsize=12)
    plt.ylabel("Tipos (UTs únicas)", fontsize=12)
    plt.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='black')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def _extract_terms_in_order(df: pd.DataFrame) -> list:
    terms = []
    current_term = []
    for _, row in df.iterrows():
        label = row["label"]
        token = row["token"]

        if label == "B-T":
            if current_term:
                terms.append(" ".join(current_term))
            current_term = [token]
        elif label == "I-T":
            current_term.append(token)
        else:
            if current_term:
                terms.append(" ".join(current_term))
                current_term = []

    if current_term:
        terms.append(" ".join(current_term))

    return terms


def compute_irt_anotado(
    cmn: float,
    itc_norm: float,
    mattr: float,
    beta: float,
    lambda_weight: float = 0.5
) -> dict:
    """
    Calcula la variante del Índice de Representatividad Terminológica (IRT) sobre
    un corpus anotado, a partir de la cobertura media normalizada y de tres
    indicadores de saturación, y la interpreta cualitativamente.

    IRT_anotado = λ · CMN + (1 − λ) · (1 − (ITC_norm + MATeTR + β) / 3)

    Es distinta del IRT que muestra la interfaz de TECLA
    (corpus_metrics.compute_representativity_score, escala 0–100).

    Parámetros:
        cmn (float): Cobertura media normalizada.
        itc_norm (float): Contribución incremental de términos nuevos.
        mattr (float): Diversidad léxica terminológica (MATeTR).
        beta (float): Parámetro de crecimiento de Heaps.
        lambda_weight (float): Peso de la cobertura frente a la saturación (por defecto 0.5).

    Devuelve:
        dict: {'IRT': float, 'interpretación': str}
    """
    cobertura = cmn
    saturacion = (itc_norm + mattr + beta) / 3
    irt = round(lambda_weight * cobertura + (1 - lambda_weight) * (1 - saturacion), 4)

    if irt >= 0.85:
        interpretacion = "⭐⭐⭐⭐⭐ Altamente representativo: cobertura excelente y saturación estable."
    elif irt >= 0.70:
        interpretacion = "⭐⭐⭐⭐ Representativo: cobertura sólida y crecimiento controlado."
    elif irt >= 0.55:
        interpretacion = "⭐⭐⭐ Parcialmente representativo: corpus en expansión o con léxico disperso."
    elif irt >= 0.40:
        interpretacion = "⭐⭐ Poco representativo: baja cobertura o saturación inestable."
    else:
        interpretacion = "⭐ No representativo: vocabulario escaso, disperso o poco cohesionado."

    return {"IRT": irt, "interpretación": interpretacion}


def compute_itr(*args, **kwargs) -> dict:
    """Alias obsoleto de compute_irt_anotado (se mantiene por compatibilidad)."""
    import warnings
    warnings.warn("compute_itr está obsoleto; usa compute_irt_anotado.", DeprecationWarning, stacklevel=2)
    return compute_irt_anotado(*args, **kwargs)