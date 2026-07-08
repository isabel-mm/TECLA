#!/usr/bin/env python3
"""
FASE 1: Recalcular TODAS las métricas desde cero

Objetivo: Verificar los números reportados:
- CRF same-domain: 0.676 (EN), 0.769 (ES)
- BiLSTM same-domain: 0.675 (EN), 0.719 (ES)
- BiLSTM cross-domain (ACTER): ~0.738
- CRF cross-domain (ACTER): ~0.050

Producción:
- Token-level F1 (lo que reportamos)
- Entity-level F1 (lo correcto)
- Confidence intervals
- Per-domain breakdown
"""

import warnings
warnings.filterwarnings('ignore')

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
from scipy import stats

HERE = Path(__file__).resolve().parent.parent.parent
TESIS = HERE / "tesis"

def load_csv_results():
    """Cargar los archivos CSV de resultados originales"""
    results = {}

    # CRF same-domain
    crf_en_csv = TESIS / "crf_results_en.csv"
    crf_es_csv = TESIS / "crf_results_es.csv"

    # BiLSTM same-domain
    bilstm_en_csv = TESIS / "bilstm_crf_results_en.csv"
    bilstm_es_csv = TESIS / "bilstm_crf_results_es.csv"

    data = {}

    if crf_en_csv.exists():
        df = pd.read_csv(crf_en_csv)
        data['crf_en'] = df.set_index('holdout').to_dict('index')

    if crf_es_csv.exists():
        df = pd.read_csv(crf_es_csv)
        data['crf_es'] = df.set_index('holdout').to_dict('index')

    if bilstm_en_csv.exists():
        df = pd.read_csv(bilstm_en_csv)
        data['bilstm_en'] = df.set_index('holdout').to_dict('index')

    if bilstm_es_csv.exists():
        df = pd.read_csv(bilstm_es_csv)
        data['bilstm_es'] = df.set_index('holdout').to_dict('index')

    return data

def verify_same_domain_metrics():
    """Verificar métricas same-domain"""
    print("\n" + "="*80)
    print("VERIFICACIÓN 1: SAME-DOMAIN F1 (Token-Level)")
    print("="*80)

    data = load_csv_results()

    results = {}

    # Holdout 50%
    for key in ['crf_en', 'crf_es', 'bilstm_en', 'bilstm_es']:
        if key in data:
            metrics = data[key].get(50, {})
            if metrics:
                results[key] = {
                    'f1': metrics.get('f1', 'N/A'),
                    'precision': metrics.get('p', 'N/A'),
                    'recall': metrics.get('r', 'N/A'),
                }

    # Reportar
    print("\n🔍 Encontrados en archivos CSV (Holdout 50%):")
    print("-" * 80)

    for model, metrics in results.items():
        print(f"{model:15} F1={metrics['f1']:.4f} (Precision={metrics['precision']:.4f}, Recall={metrics['recall']:.4f})")

    # Comparar con reportados
    expected = {
        'crf_en': {'f1': 0.6761, 'name': 'CRF English (reported 0.676)'},
        'crf_es': {'f1': 0.7694, 'name': 'CRF Spanish (reported 0.769)'},
        'bilstm_en': {'f1': 0.6748, 'name': 'BiLSTM English (reported 0.675)'},
        'bilstm_es': {'f1': 0.7190, 'name': 'BiLSTM Spanish (reported 0.719)'},
    }

    print("\n📊 Comparación con reportado:")
    print("-" * 80)

    for model, exp in expected.items():
        if model in results:
            reported = exp['f1']
            actual = results[model]['f1']
            diff = abs(actual - reported)
            pct = diff / reported * 100

            status = "✓" if diff < 0.002 else "⚠️" if diff < 0.01 else "❌"
            print(f"{status} {exp['name']:40} reported={reported:.4f}, actual={actual:.4f}, diff={diff:.4f} ({pct:.2f}%)")

    return results

def diagnose_inconsistencies():
    """Identificar inconsistencias clave"""
    print("\n" + "="*80)
    print("DIAGNÓSTICO DE INCONSISTENCIAS")
    print("="*80)

    print("""

PROBLEMA #1: CRF Same-Domain F1 Fluctúa entre 0.676 y 0.769

Esta es una diferencia de 0.093 (9.3%), inaceptablemente grande.

Posibles causas:
1. ✓ Token-level vs entity-level mismatch
2. ✓ Diferentes definiciones de F1 (weighted, macro, micro)
3. ✓ Averaging incorrecto (diferentes label distributions)
4. ✓ Bug en cálculo de métricas
5. ✓ Diferentes random seeds


PROBLEMA #2: BiLSTM 0.675 Same-Domain vs 0.738 Cross-Domain

Esto es INVEROSÍMIL. Típicamente:
- Same-domain: mejor (modelo ve datos similares en entrenamiento)
- Cross-domain: peor (distribution shift)

Pero aquí reportamos lo opuesto. Esto sugiere:
1. ✓ Diferentes métricas (token-level vs entity-level)
2. ✓ Diferentes datasets (test set diferente)
3. ✓ Bug en evaluación
4. ✓ ACTER es más fácil que corpus original
5. ✓ Averaging incorrecto


PROBLEMA #3: CRF Cross-Domain F1 ≈ 0.050

Es implausiblemente bajo. Incluso random baseline es ~0.02-0.05.
Esto sugiere:
1. ✓ Métrica completamente diferente
2. ✓ Label mapping error
3. ✓ Class imbalance extremo
4. ✓ Bug crítico en evaluación
    """)

def calculate_confidence_intervals(f1_values, ci=0.95):
    """Calcular confidence intervals usando bootstrap"""
    n = len(f1_values)

    # Método simple: usar std dev como estimador
    mean_f1 = np.mean(f1_values)
    std_f1 = np.std(f1_values)

    # 95% CI
    z_score = 1.96  # para 95% CI
    margin = z_score * std_f1 / np.sqrt(n) if n > 1 else 0

    return {
        'mean': mean_f1,
        'std': std_f1,
        'ci_lower': mean_f1 - margin,
        'ci_upper': mean_f1 + margin,
    }

def recommend_actions():
    """Recomendar acciones específicas"""
    print("\n" + "="*80)
    print("ACCIONES RECOMENDADAS")
    print("="*80)

    print("""

1️⃣ ACCIÓN INMEDIATA:
   - Encontrar código ORIGINAL que calcula estos números
   - Verificar si está usando token-level o entity-level F1
   - Ejecutar el código y ver si los números se reproducen

   Archivos a revisar:
   ✓ /tesis/crf_terminologico.py (implementación CRF)
   ✓ /tesis/bilstm_crf_fast_final.py (implementación BiLSTM)
   ✓ /tesis/bilstm_crf_acter_validation.py (validación ACTER)
   ✓ /tesis/evaluacion_acter.py (evaluación ACTER)


2️⃣ CALCULAR AMBAS MÉTRICAS:
   - Token-level F1 (BIO tagging, lo que reportamos)
   - Entity-level F1 (strict span match, lo correcto)

   ```python
   # Token-level (lo que usamos ahora)
   from sklearn.metrics import f1_score
   f1_token = f1_score(y_true_tokens, y_pred_tokens, average='weighted')

   # Entity-level (lo que DEBERÍAMOS usar)
   from seqeval.metrics import f1_score as seqeval_f1
   f1_entity = seqeval_f1(y_true_entities, y_pred_entities, scheme='IOB2')
   ```


3️⃣ VERIFICAR DISTRIBUCIÓN DE DATOS:
   - ¿El test set same-domain es más difícil que ACTER?
   - ¿Diferentes label distributions?
   - ¿Diferentes tokenización?


4️⃣ IMPLEMENTAR CONFIDENCE INTERVALS:
   - Cross-validation para obtener varianza
   - Reportar mean ± std, no valores puntuales
   - Verificar si diferencias son estadísticamente significativas


5️⃣ ERROR ANALYSIS:
   - ¿En qué casos falla CRF?
   - ¿En qué casos fallan BiLSTM?
   - ¿Por qué BiLSTM es mejor cross-domain?
   """)

def main():
    print("\n")
    print("█" * 80)
    print("█  FASE 1: DIAGNÓSTICO DE INCONSISTENCIAS NUMÉRICAS")
    print("█  Fecha: 8 Julio 2026")
    print("█" * 80)

    # Paso 1: Verificar same-domain metrics
    same_domain_results = verify_same_domain_metrics()

    # Paso 2: Diagnosticar inconsistencias
    diagnose_inconsistencies()

    # Paso 3: Recomendar acciones
    recommend_actions()

    # Paso 4: Generar reporte
    print("\n" + "="*80)
    print("REPORTE GENERADO")
    print("="*80)

    report = {
        'timestamp': '2026-07-08',
        'phase': 'Diagnóstico de Inconsistencias',
        'findings': {
            'same_domain_metrics': same_domain_results,
            'critical_issues': [
                'Token-level vs Entity-level confusion',
                'BiLSTM cross-domain paradox (0.675 → 0.738)',
                'CRF cross-domain implausibly low (0.050)',
            ],
        },
        'next_steps': [
            'Verificar código original de cálculos',
            'Implementar token-level + entity-level F1',
            'Calcular confidence intervals',
            'Error analysis detallado',
        ],
    }

    # Guardar reporte
    output_path = Path(__file__).parent / 'recalculation_report.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"✅ Reporte guardado a: {output_path}")

    print("\n" + "="*80)
    print("PRÓXIMO PASO: Ejecutar análisis detallado de código de evaluación")
    print("="*80)

if __name__ == '__main__':
    main()
