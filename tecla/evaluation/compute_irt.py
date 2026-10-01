import pandas as pd
from .metrics import (
    compute_growth_curve,
    compute_itc_norm,
    compute_matetr,
    compute_heaps_beta,
    analyze_term_coverage_sampling,
    compute_normalized_mean_coverage,
    compute_irt_anotado,
)

def evaluate_corpus_irt_anotado(df: pd.DataFrame, lambda_weight: float = 0.5, sampling_trials: int = 500, export_csv: bool = True) -> dict:
    """
    Calcula la variante del Índice de Representatividad Terminológica (IRT) sobre
    un corpus anotado y exporta los resultados a un archivo CSV. No es el IRT de
    la interfaz de TECLA (corpus_metrics.compute_representativity_score).

    Parámetros:
        df (pd.DataFrame): Corpus anotado en formato label ('file_id', 'token', 'label').
        lambda_weight (float): Peso relativo de la cobertura frente a la saturación.
        sampling_trials (int): Número de simulaciones para CMN.
        export_csv (bool): Si True, guarda los resultados en un archivo CSV.

    Devuelve:
        dict: {'IRT': float, 'interpretación': str}
    """
    # ITC norm
    growth_curve = compute_growth_curve(df)
    itc_norm = compute_itc_norm(growth_curve)

    # MATeTR
    mattr = compute_matetr(df)

    # Heaps β
    heaps_data = compute_heaps_beta(df)
    beta = heaps_data["beta"]

    # CMN
    sampling_df = analyze_term_coverage_sampling(df, num_trials=sampling_trials)
    cmn = compute_normalized_mean_coverage(sampling_df)

    # Imprimir resultados
    print(f"CMN: {cmn}")
    print(f"ITC_norm: {itc_norm}")
    print(f"MATTR: {mattr}")
    print(f"β: {beta}")

    # IRT final
    irt_result = compute_irt_anotado(cmn=cmn, itc_norm=itc_norm, mattr=mattr, beta=beta, lambda_weight=lambda_weight)

    if export_csv:
        results_df = pd.DataFrame([{
            "CMN": cmn,
            "ITC_norm": itc_norm,
            "MATTR": mattr,
            "β": beta,
            "IRT": irt_result["IRT"],
            "interpretación": irt_result["interpretación"]
        }])
        results_df.to_csv("irt_results.csv", index=False)
        print("✅ Resultados exportados a 'irt_results.csv'")

    return irt_result
