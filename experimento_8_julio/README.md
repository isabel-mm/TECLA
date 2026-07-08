# Experimento 8 de Julio: Reparación de Críticas de Revisores

**Objetivo:** Abordar todos los problemas identificados por los revisores y producir resultados reproducibles, rigurosos y creíbles.

**Fecha inicio:** 8 de julio de 2026  
**Status:** 🟡 EN PROGRESO - FASE 1 DIAGNOSTICANDO

---

## 📋 PLAN MAESTRO

### Fase 1: Diagnóstico (Verificar números)
- [ ] 01_plan/DIAGNOSIS.md - Investigar inconsistencias numéricas
- [ ] Verificar de dónde vienen F1=0.738, 0.676, 0.769
- [ ] Recalcular all metrics from scratch
- [ ] Identificar si es bug de cálculo o reporting

### Fase 2: Reparación de Holdout Protocol
- [ ] 02_holdout_protocol/correct_holdout.py - Reimplementar para multiword spans
- [ ] Excluir sentencias enteras, no solo tokens
- [ ] Controlar lexeme overlap
- [ ] Reportar tanto token-level como span-level

### Fase 3: Verificación de Métricas
- [ ] 03_metrics_verification/metric_calculations.py
- [ ] Token-level F1 (BIO)
- [ ] Entity-level F1 (strict match)
- [ ] Per-domain breakdown
- [ ] Confidence intervals y variance

### Fase 4: Añadir Transformer Baselines
- [ ] 04_transformer_baselines/bert_crf_baseline.py
- [ ] SciBERT + CRF
- [ ] BERT + CRF
- [ ] Comparación directa con BiLSTM-CRF

### Fase 5: Análisis de Corpus
- [ ] 05_corpus_analysis/corpus_statistics.py
- [ ] Verificar anotaciones
- [ ] Inter-annotator agreement
- [ ] Coverage del dominio
- [ ] Comparación con estándares ATE

### Fase 6: Resultados Limpios
- [ ] 06_results_cleaned/final_results.md
- [ ] Números verificados y reproducibles
- [ ] Código abierto para replicación
- [ ] Error analysis detallado
- [ ] Per-domain breakdown

---

## 🔴 PROBLEMAS A RESOLVER

| Problema | Acción | Archivo |
|----------|--------|---------|
| Holdout protocol flawed | Reimplementar para spans | 02_holdout_protocol/ |
| Inconsistencias numéricas | Verificar y recalcular | 01_plan/DIAGNOSIS.md |
| F1=0.738 implausible | Error analysis detallado | 03_metrics_verification/ |
| Sin transformer baselines | Implementar BERT/SciBERT | 04_transformer_baselines/ |
| Corpus stats sospechosas | Revisar anotaciones | 05_corpus_analysis/ |
| Métricas no claras | Token + span level | 03_metrics_verification/ |
| ACTER details faltantes | Documentar exactamente | 06_results_cleaned/ |
| Overclaiming teórico | Ser más cautelosos | 06_results_cleaned/final_results.md |

---

## 📁 ESTRUCTURA DE CARPETAS

```
experimento_8_julio/
├── README.md (este archivo)
│
├── 01_plan/
│   ├── DIAGNOSIS.md (plan de investigación)
│   └── ROADMAP.md (timeline)
│
├── 02_holdout_protocol/
│   ├── correct_holdout.py (reimplementación)
│   ├── holdout_validation.py (pruebas)
│   └── METHODOLOGY.md (documentación)
│
├── 03_metrics_verification/
│   ├── metric_calculations.py (recalcular todos)
│   ├── consistency_check.py (detectar bugs)
│   └── METRICS.md (especificación)
│
├── 04_transformer_baselines/
│   ├── bert_crf_baseline.py
│   ├── sciBERT_baseline.py
│   └── BASELINES.md (comparación)
│
├── 05_corpus_analysis/
│   ├── analyze_corpus.py
│   ├── inter_rater_agreement.py
│   └── CORPUS_REPORT.md
│
└── 06_results_cleaned/
    ├── final_results.md (números verificados)
    ├── error_analysis.py
    └── reproducibility_guide.md
```

---

## ✅ CRITERIOS DE ÉXITO

### Fase 1 (Diagnóstico)
- [ ] Números verificados y explicados
- [ ] Bugs identificados y documentados
- [ ] Replicable desde código limpio

### Fase 2 (Holdout)
- [ ] Protocolo opera en complete spans
- [ ] Sentencias enteras excluidas
- [ ] Lexeme overlap controlado
- [ ] Token-level y span-level metrics reportados

### Fase 3 (Métricas)
- [ ] Token-level F1 (BIO)
- [ ] Entity-level F1 (strict)
- [ ] Confidence intervals
- [ ] Variance across seeds
- [ ] Per-domain breakdown

### Fase 4 (Baselines)
- [ ] BERT + CRF implementado
- [ ] SciBERT + CRF implementado
- [ ] Comparación clara vs BiLSTM-CRF
- [ ] Análisis de por qué BiLSTM gana (o pierde)

### Fase 5 (Corpus)
- [ ] Anotaciones verificadas
- [ ] Inter-rater agreement reportado
- [ ] Comparación con estándares ATE
- [ ] Análisis de underannotation

### Fase 6 (Resultados)
- [ ] Números limpios y verificados
- [ ] Código reproducible
- [ ] Error analysis detallado
- [ ] Reconocimiento de limitaciones
- [ ] Guía de replicación

---

## 📊 TIMELINE ESTIMADO

| Fase | Duración | Inicio | Fin |
|------|----------|--------|-----|
| 1. Diagnóstico | 2-3h | Jul 8 | Jul 8 |
| 2. Holdout Protocol | 3-4h | Jul 8 | Jul 8 |
| 3. Métricas | 2-3h | Jul 8 | Jul 8 |
| 4. Transformer Baselines | 4-6h | Jul 8-9 | Jul 9 |
| 5. Corpus Analysis | 2-3h | Jul 9 | Jul 9 |
| 6. Resultados Finales | 2-3h | Jul 9 | Jul 9 |

**Total:** ~18-22 horas de trabajo

---

## 🎯 ENTREGABLES FINALES

1. **Código reproducible** (todos los scripts)
2. **Resultados verificados** (números limpios)
3. **Documentación completa** (cómo replicar)
4. **Error analysis** (por qué esto funciona/no)
5. **Comparación de baselines** (BiLSTM vs BERT)
6. **Manuscrito revisado** (respuesta a revisores)

---

## 📝 NOTAS

- Todos los scripts deben incluir seed/reproducibilidad
- Todos los números deben tener confidence intervals
- Código abierto para que revisores lo verifiquen
- Reconocer limitaciones explícitamente
- No overclaim teórico

---

**Versión:** 1.0  
**Último update:** 8 de julio de 2026 14:30 UTC
