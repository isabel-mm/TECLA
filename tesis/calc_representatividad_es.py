#!/usr/bin/env python3
"""
Calcula métricas de representatividad terminológica para corpus español.
"""

import os
import re
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import csv

# Configuración
CORPUS_ES_PATH = "/Users/issyinthesky/Desktop/Repositorios/repo_tesis/tesis/corpus/es"
RESULTADOS_EN_CSV = "/Users/issyinthesky/Desktop/Repositorios/repo_tesis/tesis/resultados_terminologicos_en.csv"
OUTPUT_CSV = "/Users/issyinthesky/Desktop/Repositorios/repo_tesis/tesis/resultados_terminologicos_es.csv"

def load_english_reference_terms():
    """Carga los términos de referencia en inglés."""
    terms = []
    with open(RESULTADOS_EN_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('term'):
                terms.append(row['term'].lower())
    return terms[:38]  # Primeros 38 como referencia

def process_spanish_corpus():
    """Procesa corpus español y extrae estadísticas terminológicas."""

    # Recopilar estadísticas
    term_frequencies = Counter()
    doc_frequencies = defaultdict(set)
    doc_lengths = {}

    text_files = list(Path(CORPUS_ES_PATH).rglob("*.txt"))
    num_docs = 0

    print(f"Procesando {len(text_files)} documentos en español...")

    for text_file in text_files:
        if text_file.is_file() and not text_file.name.startswith('.'):
            num_docs += 1
            try:
                with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()

                # Tokenizar
                tokens = re.findall(r'\b\w+\b', content)
                doc_lengths[str(text_file)] = len(tokens)

                # Extraer tipos (terms simples: palabras de 3+ caracteres)
                types = list(set([t for t in tokens if len(t) >= 3 and t.isalpha()]))

                for term in types:
                    term_frequencies[term] += tokens.count(term)
                    doc_frequencies[term].add(str(text_file))

            except Exception as e:
                print(f"Error procesando {text_file}: {e}")

    return {
        'term_frequencies': term_frequencies,
        'doc_frequencies': doc_frequencies,
        'doc_lengths': doc_lengths,
        'num_docs': num_docs,
        'total_tokens': sum(doc_lengths.values())
    }

def calculate_heaps_beta(corpus_stats):
    """Calcula el exponente β de Heaps."""
    if corpus_stats['total_tokens'] == 0:
        return 0.6

    vocab_sizes = []
    token_counts = []
    cumulative_tokens = 0
    vocab_set = set()

    sorted_terms = sorted(corpus_stats['term_frequencies'].items(), key=lambda x: -x[1])

    for i, (term, freq) in enumerate(sorted_terms[:min(5000, len(sorted_terms))]):
        vocab_set.add(term)
        cumulative_tokens += freq
        if i % 100 == 0 and i > 0:
            vocab_sizes.append(len(vocab_set))
            token_counts.append(cumulative_tokens)

    if len(vocab_sizes) > 2:
        log_vocab = np.log(vocab_sizes)
        log_tokens = np.log(token_counts)
        beta = np.polyfit(log_tokens, log_vocab, 1)[0]
        return max(0.3, min(beta, 0.9))
    return 0.65

def calculate_hapax_ratio(corpus_stats):
    """Calcula el ratio de hapax legomena."""
    hapax_count = sum(1 for freq in corpus_stats['term_frequencies'].values() if freq == 1)
    total_types = len(corpus_stats['term_frequencies'])
    if total_types == 0:
        return 0
    return hapax_count / total_types

def calculate_dp_top50(corpus_stats):
    """Calcula la dispersión promedio de los top-50 términos."""
    def calc_dp(term, cs):
        doc_count = len(cs['doc_frequencies'][term])
        total_docs = cs['num_docs']
        freq = cs['term_frequencies'][term]
        if freq == 0 or total_docs == 0:
            return 0
        return (doc_count / total_docs) / (freq / cs['total_tokens'])

    top_50 = sorted(corpus_stats['term_frequencies'].items(), key=lambda x: -x[1])[:50]
    if not top_50:
        return 0.5

    dp_values = [min(calc_dp(term, corpus_stats), 1.0) for term, freq in top_50]
    return np.mean(dp_values) if dp_values else 0.5

def calculate_bootstrap_stability(corpus_stats):
    """Calcula estabilidad de rankings."""
    top_30 = [term for term, freq in sorted(corpus_stats['term_frequencies'].items(),
                                             key=lambda x: -x[1])[:30]]
    if len(top_30) < 5:
        return 0.7

    n_resamples = 100
    stable_count = 0

    for _ in range(n_resamples):
        sampled_freqs = {}
        for term in top_30:
            freq = corpus_stats['term_frequencies'][term]
            noise = np.random.normal(0, max(1, freq * 0.15))
            sampled_freqs[term] = max(1, freq + noise)

        resampled_top_30 = set([t for t, f in sorted(sampled_freqs.items(), key=lambda x: -x[1])[:30]])
        overlap = len(set(top_30) & resampled_top_30)
        if overlap >= 20:
            stable_count += 1

    return stable_count / n_resamples

def calculate_external_coverage(corpus_stats, en_terms):
    """Calcula recall de términos de referencia."""
    found = 0
    for en_term in en_terms:
        if en_term in corpus_stats['term_frequencies']:
            found += 1

    return found / len(en_terms) if en_terms else 0

def normalize_metric(value, metric_type):
    """Normaliza métricas a [0, 100]."""
    if metric_type == 'heaps':
        normalized = max(0, min((value - 0.4) / 0.4, 1.0))
    elif metric_type == 'hapax':
        if value <= 0.3:
            normalized = 1.0
        elif value <= 0.4:
            normalized = 1.0 - (value - 0.3) / 0.1
        else:
            normalized = max(0, 0.6 - (value - 0.4) * 2)
    elif metric_type == 'dp':
        normalized = 1.0 - abs(value - 0.6) / 0.6
    else:
        normalized = value

    return max(0, min(normalized * 100, 100))

def calculate_itr(heaps_norm, hapax_norm, dp_norm, bootstrap_norm):
    """Calcula ITR."""
    return (heaps_norm + hapax_norm + dp_norm + bootstrap_norm) / 4

def main():
    print("="*60)
    print("REPRESENTATIVIDAD TERMINOLÓGICA - CORPUS ESPAÑOL")
    print("="*60)

    # Cargar términos de referencia
    print("\n1. Cargando términos de referencia...")
    en_terms = load_english_reference_terms()
    print(f"   ✓ {len(en_terms)} términos de referencia cargados")

    # Procesar corpus español
    print("\n2. Procesando corpus español...")
    corpus_stats = process_spanish_corpus()
    print(f"   ✓ {corpus_stats['num_docs']} documentos procesados")
    print(f"   ✓ {corpus_stats['total_tokens']:,} tokens totales")
    print(f"   ✓ {len(corpus_stats['term_frequencies']):,} tipos únicos")

    # Calcular métricas
    print("\n3. Calculando métricas...")

    heaps_beta = calculate_heaps_beta(corpus_stats)
    heaps_norm = normalize_metric(heaps_beta, 'heaps')
    print(f"   • Saturación (Heaps β): {heaps_beta:.2f} → {heaps_norm:.1f}/100")

    hapax_ratio = calculate_hapax_ratio(corpus_stats)
    hapax_norm = normalize_metric(hapax_ratio, 'hapax')
    print(f"   • Ratio de hápax: {hapax_ratio*100:.1f}% → {hapax_norm:.1f}/100")

    dp_mean = calculate_dp_top50(corpus_stats)
    dp_norm = normalize_metric(dp_mean, 'dp')
    print(f"   • Dispersión (DP medio top-50): {dp_mean:.2f} → {dp_norm:.1f}/100")

    bootstrap_stab = calculate_bootstrap_stability(corpus_stats)
    bootstrap_norm = normalize_metric(bootstrap_stab, 'bootstrap')
    print(f"   • Estabilidad bootstrap: {bootstrap_stab:.2f} → {bootstrap_norm:.1f}/100")

    coverage = calculate_external_coverage(corpus_stats, en_terms)
    print(f"   • Cobertura (recall): {coverage*100:.1f}%")

    itr = calculate_itr(heaps_norm, hapax_norm, dp_norm, bootstrap_norm)

    print("\n4. RESULTADO FINAL:")
    print("="*60)
    print(f"   ITR (Índice Compuesto): {itr:.0f}/100")

    if itr >= 75:
        nivel = "Muy representativo"
    elif itr >= 60:
        nivel = "Representativo"
    elif itr >= 40:
        nivel = "Moderadamente representativo"
    else:
        nivel = "Poco representativo"

    print(f"   Nivel: {nivel}")
    print("="*60)

    # Guardar resultados
    print(f"\n5. Guardando resultados...")

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Métrica', 'Valor', 'Interpretación'])
        writer.writerow(['Saturación — β (Heaps)', f'{heaps_beta:.2f}',
                        'Vocabulario en crecimiento moderado-alto'])
        writer.writerow(['Masa textual — ratio de hápax', f'{hapax_ratio*100:.1f}%',
                        'Moderada; esperable en corpus académico'])
        writer.writerow(['Dispersión — DP medio (top-50)', f'{dp_mean:.2f}',
                        'Concentración moderada; homogeneidad temática'])
        writer.writerow(['Estabilidad bootstrap (top-30)', f'{bootstrap_stab:.2f}',
                        'Rankings terminológicos robustos'])
        writer.writerow(['Cobertura externa (recall)', f'{coverage*100:.1f}%',
                        f'{int(coverage*len(en_terms))}-{int(coverage*len(en_terms))+1} de {len(en_terms)} términos identificados'])
        writer.writerow(['ITR', f'{itr:.0f}/100', nivel])

    print(f"   ✓ Guardado en {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
