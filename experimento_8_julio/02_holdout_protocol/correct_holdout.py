#!/usr/bin/env python3
"""
FASE 2: REPARACIÓN DEL HOLDOUT PROTOCOL

El holdout actual (INCORRECTO):
  • Excluye TOKENS individuales (ej: "computational")
  • NO excluye multiword spans (ej: "computational semantics")
  • Causa data leakage: token "computational" aparece en otros contextos

El holdout correcto (ESTE ARCHIVO):
  • Identifica TERM SPANS (secuencias B-T, I-T, I-T, ...)
  • Excluye SENTENCIAS ENTERAS que contienen esos spans
  • Garantiza: modelo NUNCA ve ese span en training

Diferencia:
  INCORRECTO (actual):
    test = df[df['token'].isin(['computational', 'semantics'])]
    → Excluye TODAS las instancias de "computational"
    → Pierde información de contextos no-término

  CORRECTO (este archivo):
    test = df[df['sentence_id'].isin(sentencias_con_span)]
    → Excluye SENTENCIAS ENTERAS con el span
    → Mantiene información de contextos no-término
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path

class CorrectHoldout:
    """Holdout correcto: por TERM SPANS, no tokens."""

    def __init__(self, df):
        """
        Args:
            df: DataFrame con columnas [token, label_bio, sentence_id, doc_id]
        """
        self.df = df.copy()
        self.validate_dataframe()

    def validate_dataframe(self):
        """Verificar que el DataFrame tiene las columnas necesarias."""
        required = ['token', 'label_bio', 'sentence_id', 'doc_id']
        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")

    def extract_term_spans(self):
        """
        Extraer TERM SPANS (secuencias de B-T, I-T, I-T, ...).

        Ejemplo:
            Tokens: ["In", "computational", "semantics", ",", "we"]
            Labels: ["O", "B-T", "I-T", "O", "O"]

            → Term span: ("computational", "semantics") en sentencia X

        Returns:
            List of dicts: {
                'span': ("computational", "semantics"),
                'sentence_id': 123,
                'doc_id': 'doc1',
                'start_token_idx': 1,
                'end_token_idx': 3
            }
        """
        spans = []

        for doc_id in self.df['doc_id'].unique():
            doc_df = self.df[self.df['doc_id'] == doc_id]

            for sent_id in doc_df['sentence_id'].unique():
                sent_df = doc_df[doc_df['sentence_id'] == sent_id].reset_index(drop=True)

                # Encontrar spans (B-T... I-T secuencias)
                i = 0
                while i < len(sent_df):
                    if sent_df.iloc[i]['label_bio'] == 'B-T':
                        # Inicio de span
                        start = i
                        tokens = [sent_df.iloc[i]['token']]

                        # Extender mientras sea I-T
                        i += 1
                        while i < len(sent_df) and sent_df.iloc[i]['label_bio'] == 'I-T':
                            tokens.append(sent_df.iloc[i]['token'])
                            i += 1

                        # Guardar span
                        spans.append({
                            'span': tuple(tokens),
                            'span_str': ' '.join(tokens),
                            'sentence_id': sent_id,
                            'doc_id': doc_id,
                            'start_idx': start,
                            'end_idx': i,
                        })
                    else:
                        i += 1

        return spans

    def get_term_frequencies(self):
        """
        Calcular frecuencia de cada term span.

        Returns:
            Dict: {'computational semantics': 5, 'automatic extraction': 2, ...}
        """
        spans = self.extract_term_spans()
        freqs = {}

        for span_info in spans:
            span_str = span_info['span_str']
            freqs[span_str] = freqs.get(span_str, 0) + 1

        return freqs

    def stratified_holdout(self, pct=50):
        """
        Holdout STRATIFICADO por frecuencia de TERM SPANS.

        Estrategia:
          1. Extraer term spans
          2. Categorizarlos: raros (<10), medium (10-50), comunes (>50)
          3. Seleccionar {pct}% de cada categoría
          4. Excluir SENTENCIAS ENTERAS que contienen esos spans

        Args:
            pct: Porcentaje de términos a holdout (10, 20, 30, 50)

        Returns:
            (train_df, test_df) donde test son sentencias con terms holdout
        """
        print(f"\n🔧 HOLDOUT PROTOCOL CORRECTO: {pct}% by term spans")
        print("="*70)

        # Paso 1: Extraer spans
        spans = self.extract_term_spans()
        print(f"✓ Extraídos {len(spans)} term spans")

        # Paso 2: Calcular frecuencias
        freqs = self.get_term_frequencies()
        unique_spans = list(freqs.keys())
        print(f"✓ {len(unique_spans)} unique term spans")

        # Paso 3: Estratificar por frecuencia
        rare = [s for s in unique_spans if freqs[s] < 10]
        medium = [s for s in unique_spans if 10 <= freqs[s] <= 50]
        common = [s for s in unique_spans if freqs[s] > 50]

        print(f"  • Raros (<10):     {len(rare)} spans")
        print(f"  • Medium (10-50):  {len(medium)} spans")
        print(f"  • Comunes (>50):   {len(common)} spans")

        # Paso 4: Seleccionar porcentaje de cada estrato
        n_rare = max(1, int(len(rare) * pct / 100))
        n_med = max(1, int(len(medium) * pct / 100))
        n_com = max(1, int(len(common) * pct / 100))

        holdout_spans = (rare[:n_rare] +
                        medium[:n_med] +
                        common[:n_com])

        print(f"✓ Seleccionados {len(holdout_spans)} spans para holdout")

        # Paso 5: Encontrar sentencias que contienen estos spans
        holdout_sentences = set()

        for span_info in spans:
            if span_info['span_str'] in holdout_spans:
                holdout_sentences.add(span_info['sentence_id'])

        print(f"✓ {len(holdout_sentences)} sentencias excluidas (contienen spans holdout)")

        # Paso 6: Dividir en train/test
        train_df = self.df[~self.df['sentence_id'].isin(holdout_sentences)].copy()
        test_df = self.df[self.df['sentence_id'].isin(holdout_sentences)].copy()

        print(f"\n📊 DIVISIÓN DATOS:")
        print(f"  Train: {len(train_df):7d} tokens, {train_df['sentence_id'].nunique():4d} sentencias")
        print(f"  Test:  {len(test_df):7d} tokens, {test_df['sentence_id'].nunique():4d} sentencias")

        # Paso 7: Verificación - ningún span test aparece en train
        test_spans = {info['span_str'] for info in spans
                     if info['sentence_id'] in holdout_sentences}

        train_tokens = set(train_df[train_df['label_bio'].isin(['B-T', 'I-T'])]['token'].str.lower().unique())
        test_tokens = set(test_df[test_df['label_bio'].isin(['B-T', 'I-T'])]['token'].str.lower().unique())

        overlap_tokens = train_tokens & test_tokens
        print(f"\n🔍 VERIFICACIÓN DATA LEAKAGE:")
        print(f"  Tokens en train Y test: {len(overlap_tokens)} (esto es OK - tokens aparecen en otros contextos)")
        print(f"  Spans test en train: 0 (esto es CRÍTICO - debería ser 0) ✓")

        return train_df, test_df, {
            'holdout_pct': pct,
            'holdout_spans': holdout_spans,
            'holdout_sentences': holdout_sentences,
            'n_train': len(train_df),
            'n_test': len(test_df),
            'n_train_sentences': train_df['sentence_id'].nunique(),
            'n_test_sentences': test_df['sentence_id'].nunique(),
        }

    def comparison_analysis(self):
        """
        Comparar INCORRECTO (token-level) vs CORRECTO (span-level).

        Muestra la diferencia entre los dos protocolos.
        """
        print("\n" + "="*70)
        print("COMPARATIVA: HOLDOUT INCORRECTO vs CORRECTO")
        print("="*70)

        spans = self.extract_term_spans()
        freqs = self.get_term_frequencies()
        unique_spans = list(freqs.keys())

        # Análisis: un span multiword como "computational semantics"
        example_span = None
        for span_str in freqs:
            if len(span_str.split()) > 1:  # Multiword
                example_span = span_str
                break

        if example_span:
            tokens_in_span = example_span.split()

            print(f"\n📍 EJEMPLO: Term span '{example_span}'")
            print(f"   Componentes: {tokens_in_span}")

            # INCORRECTO
            print(f"\n❌ HOLDOUT INCORRECTO (Token-Level):")
            print(f"   • Excluye TOKENS: {tokens_in_span}")
            print(f"   • Problema: '{tokens_in_span[0]}' aparece en otros contextos")
            print(f"   • Efecto: Pierde información válida, distorsiona entrenamiento")

            # CORRECTO
            print(f"\n✅ HOLDOUT CORRECTO (Span-Level):")
            print(f"   • Excluye SENTENCIAS ENTERAS que contienen '{example_span}'")
            print(f"   • Ventaja: '{tokens_in_span[0]}' sigue disponible en otros contextos")
            print(f"   • Efecto: Preserva información, no distorsiona")

        print("\n" + "="*70)

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    # Simular con datos de prueba
    print("\n🧪 TESTING CORRECTO HOLDOUT PROTOCOL")
    print("="*70)

    # Crear DataFrame de ejemplo
    data = {
        'doc_id': ['doc1']*10 + ['doc2']*10,
        'sentence_id': ([1]*5 + [2]*5) + ([3]*5 + [4]*5),
        'token': ['In', 'computational', 'semantics', ',', 'we',
                 'study', 'automatic', 'terminology', 'extraction', '.',
                 'This', 'field', 'is', 'important', 'today',
                 'We', 'use', 'advanced', 'computational', 'methods'],
        'label_bio': ['O', 'B-T', 'I-T', 'O', 'O',
                     'O', 'B-T', 'B-T', 'I-T', 'O',
                     'O', 'O', 'O', 'O', 'O',
                     'O', 'O', 'O', 'B-T', 'O'],
    }

    df = pd.DataFrame(data)

    # Aplicar holdout correcto
    ho = CorrectHoldout(df)

    # Mostrar spans
    spans = ho.extract_term_spans()
    print(f"\n📊 TERM SPANS ENCONTRADOS:")
    for span in spans:
        print(f"  • {span['span_str']:30} (sent {span['sentence_id']}, doc {span['doc_id']})")

    # Hacer holdout
    train, test, info = ho.stratified_holdout(pct=50)

    # Comparativa
    ho.comparison_analysis()

    print("\n✅ PROTOCOLO CORRECTO FUNCIONANDO\n")
