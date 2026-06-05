"""
Ablation study: análisis de impacto de features de baja importancia
basado en las importancias del modelo entrenado
"""

import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Features ordenados por importancia unificada (T = B-T ∪ I-T) según las tablas generadas
# Ordenados de MENOR a MAYOR impacto: candidatos para quitar primero
FEATURES_BY_IMPORTANCE = {
    "en": [
        ("dispersion", 0.0000),
        ("lemma_suffix4", -0.0015),
        ("lemma_suffix3", -0.0021),
        ("in_definition_context", 0.0007),
        ("shape", -0.0128),
        ("is_in_noun_phrase", 0.0272),
        ("document_frequency", 0.0148),
        ("token_length", 0.0172),
        ("is_acronym", 0.0404),
        ("avg_position_in_sentence", 0.0478),
        ("is_titlecase", -0.0265),
        ("is_first_occurrence_in_doc", -0.0291),
        ("sentence_length", -0.0417),
    ],
    "es": [
        ("dispersion", 0.0000),
        ("freq_in_text", -0.0000),
        ("lemma_suffix4", -0.0012),
        ("lemma_suffix3", -0.0016),
        ("is_acronym", -0.0033),
        ("sentence_length", -0.0033),
        ("avg_position_in_sentence", -0.0067),
        ("in_definition_context", 0.0088),
        ("is_titlecase", -0.0100),
        ("is_in_noun_phrase", -0.0178),
        ("document_frequency", 0.0475),
        ("token_length", 0.0184),
        ("is_first_occurrence_in_doc", -0.0249),
    ]
}

def analyze_ablation():
    """Analiza el impacto relativo de features según su importancia"""
    print("\n" + "="*70)
    print("  ABLATION ANALYSIS: Features ordenados por impacto en importancia")
    print("="*70)

    results = []

    for lang, features in FEATURES_BY_IMPORTANCE.items():
        print(f"\n{lang.upper()} - Features ordenados por importancia (de menor a mayor):")
        print("-" * 70)
        print(f"{'Rango':<6} {'Feature':<30} {'Imp. unificada':<20}")
        print("-" * 70)

        for i, (feat, importance) in enumerate(features, 1):
            importance_str = f"{importance:+.4f}"
            marker = " ← QUITAR" if abs(importance) < 0.03 else ""
            print(f"{i:<6} {feat:<30} {importance_str:<20}{marker}")

        # Contar features con importancia muy baja (< 0.03)
        low_importance = [f for f, imp in features if abs(imp) < 0.03]
        print(f"\nCandidatos para quitar ({len(low_importance)}): {', '.join(low_importance)}")

        results.append({
            "language": lang.upper(),
            "low_importance_count": len(low_importance),
            "low_importance_features": ", ".join(low_importance),
        })

    print("\n" + "="*70)
    print("  RECOMENDACIONES")
    print("="*70)
    print("""
Basándose en la importancia unificada para la clase término (B-T ∪ I-T):

QUITAR DEFINITIVAMENTE (importancia ≈ 0, cero discriminación):
  - dispersion: completamente inerte en ambos idiomas
  - lemma_suffix3, lemma_suffix4: patrones morfológicos no discriminan

QUITAR PROBABLEMENTE (importancia muy baja < ±0.03):
  - in_definition_context: patrón definitorio poco útil
  - is_acronym, is_in_noun_phrase: rasgos especializados muy baja cobertura
  - avg_position_in_sentence: posición media poco informativa

CONSIDERAR (importancia baja pero presente):
  - document_frequency, token_length: mínima pero presente
  - sentence_length: bajo pero consistente
  - is_titlecase, is_first_occurrence_in_doc: nuevos, probablemente remover

MANTENER (importancia moderada-alta):
  - has_digit: 0.2510 (EN), 0.0759 (ES) — ÚTIL
  - Todos los demás con importancia > 0.04
""")

    return results

if __name__ == "__main__":
    analyze_ablation()
    print("\n✓ Análisis completado\n")
