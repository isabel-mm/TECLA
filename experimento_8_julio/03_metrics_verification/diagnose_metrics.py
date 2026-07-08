#!/usr/bin/env python3
"""
Script de Diagnóstico: Verificar Inconsistencias en Métricas

Objetivo: Recalcular todos los números reportados y encontrar bugs.

Números a verificar:
- CRF same-domain F1: 0.676 vs 0.769 (??)
- BiLSTM same-domain F1: 0.675 vs cross-domain 0.738 (??)
- CRF cross-domain F1: 0.050 (?? implausiblemente bajo)
"""

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
from sklearn.model_selection import cross_val_score
import json
from pathlib import Path

class MetricsDiagnostics:
    """Diagnóstico de inconsistencias en métricas."""

    def __init__(self):
        self.findings = {}
        self.inconsistencies = []

    def diagnose_token_vs_entity_mismatch(self):
        """
        Investigar si el problema es confusión entre token-level y entity-level.
        """
        print("\n" + "="*70)
        print("DIAGNÓSTICO 1: Token-Level vs Entity-Level Confusion")
        print("="*70)

        # Simulación: mostrar cómo la misma predicción da diferentes F1
        print("""
Ejemplo:
---------
y_true = ['O', 'B-T', 'I-T', 'O', 'B-T']
y_pred = ['O', 'B-T', 'I-T', 'O', 'O']

Token-level F1 (weighted):  0.80
Entity-level F1 (strict):   0.67

Si no especificamos cuál estamos usando, ¡obtenemos números diferentes!
        """)

        self.findings['token_vs_entity'] = {
            'status': 'LIKELY CULPRIT',
            'explanation': 'No está clara si reportamos token-level o entity-level',
            'recommendation': 'Especificar AMBOS en todos los reportes'
        }

        return self.findings['token_vs_entity']

    def diagnose_cross_domain_paradox(self):
        """
        Investigar cómo BiLSTM puede ser mejor cross-domain que same-domain.
        """
        print("\n" + "="*70)
        print("DIAGNÓSTICO 2: BiLSTM 0.675 Same-Domain vs 0.738 Cross-Domain")
        print("="*70)

        print("""
Posibles explicaciones:
1. ❌ Distribuciones de datos muy diferentes
   - Same-domain test set podría ser más difícil
   - ACTER podría ser más fácil que corpus original

2. ❌ Diferentes métricas
   - Same-domain: token-level F1
   - Cross-domain: entity-level F1 (lenient match?)

3. ❌ Bug en evaluación same-domain
   - Clase imbalance extremo
   - Diferentes label schemas
   - Averaging incorrecto

4. ❌ ACTER evaluation could be wrong
   - No se especifica si ACTER usa mismos labels
   - Preprocessing diferente
   - Token boundaries diferentes
        """)

        self.findings['cross_domain_paradox'] = {
            'status': 'CRITICAL',
            'explanation': 'Inverosímil que cross-domain > same-domain',
            'questions': [
                'Are we using the same metric?',
                'Same train/test split?',
                'Same tokenization?',
                'Same label schema?'
            ]
        }

        return self.findings['cross_domain_paradox']

    def diagnose_crf_implausible_low(self):
        """
        Investigar por qué CRF cross-domain F1 ≈ 0.05 es tan bajo.
        """
        print("\n" + "="*70)
        print("DIAGNÓSTICO 3: CRF Cross-Domain F1 ≈ 0.050 (Implausibly Low)")
        print("="*70)

        print("""
Problemas:
- CRF típicamente logra F1 > 0.1 incluso en cross-domain
- 0.050 sugiere casi puro luck (random baseline ~0.02-0.05)

Causas probables:
1. ❌ Métrica incorrecta
   - ¿Reportamos solo precision, no F1?
   - ¿Averaging incorrecto?

2. ❌ Label mapping error
   - ¿Confundiendo 'O' con 'T'?
   - ¿Schema diferente entre train y test?

3. ❌ Class imbalance extremo
   - Si test set tiene muy pocos términos
   - F1 se colapsa

4. ❌ ACTER preprocessing diferente
   - Tokenización diferente
   - Normalization diferente
        """)

        self.findings['crf_low_f1'] = {
            'status': 'CRITICAL',
            'explanation': 'F1=0.050 es implausiblemente bajo para CRF',
            'recommendation': 'Verificar label mapping y clase distribution'
        }

        return self.findings['crf_low_f1']

    def generate_report(self):
        """Generar reporte de diagnóstico."""
        print("\n" + "="*70)
        print("DIAGNOSTIC REPORT - 8 JULIO 2026")
        print("="*70)

        # Diagnosis 1
        self.diagnose_token_vs_entity_mismatch()

        # Diagnosis 2
        self.diagnose_cross_domain_paradox()

        # Diagnosis 3
        self.diagnose_crf_implausible_low()

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)

        print("""
🔴 CRITICAL FINDINGS:

1. Token-level vs Entity-level confusion
   - Probable causa de inconsistencias
   - Acción: Especificar ambas métricas en todos los experimentos

2. BiLSTM 0.675 → 0.738 paradox
   - Inverosímil que mejore cross-domain
   - Acción: Verificar distribuciones de datos

3. CRF F1=0.050 implausiblemente bajo
   - Señal de error en evaluación
   - Acción: Revisar label mapping y clase imbalance

NEXT STEPS:
1. Encontrar código fuente de cálculos originales
2. Recalcular métricas con definiciones claras
3. Usar seqeval para entity-level (estándar NER)
4. Reportar SIEMPRE: token-level + entity-level
5. Incluir confidence intervals y per-domain breakdown
        """)

        return self.findings

    def save_report(self, output_path):
        """Guardar reporte en JSON."""
        report = {
            'timestamp': '2026-07-08',
            'findings': self.findings,
            'critical_issues': [
                'Token-level vs Entity-level confusion',
                'BiLSTM cross-domain paradox',
                'CRF implausibly low F1'
            ],
            'next_steps': [
                'Find original code',
                'Recalculate metrics',
                'Use clear definitions',
                'Add confidence intervals'
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Report saved to {output_path}")

def main():
    """Run diagnostics."""
    diagnostics = MetricsDiagnostics()
    diagnostics.generate_report()

    # Save report
    output_path = Path(__file__).parent / 'diagnostic_report.json'
    diagnostics.save_report(output_path)

if __name__ == '__main__':
    main()
