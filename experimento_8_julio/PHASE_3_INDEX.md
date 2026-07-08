# FASE 3: ÍNDICE COMPLETO
**Fecha Inicio:** 8 Julio 2026  
**Status:** EN EJECUCIÓN

---

## ✅ COMPLETADO

### Parte 1: Holdout Setup (span-level correcto)
- **Script:** `03_metrics_verification/fase3_complete.py`
- **Timestamp:** 2026-07-08T13:01:04 → 2026-07-08T13:05:28
- **Duración:** ~4 minutos
- **Resultado:** ✅ EXITOSO

**Outputs:**
1. `fase3_results.json` — JSON con splits verificados
2. `FASE3_RESULTADOS.md` — Documentación de holdout setup

**Hallazgos:**
```
ENGLISH (306,288 tokens):
  • Term spans: 5,355 (209 únicos)
  • Raros: 140 spans (<10 apariciones)
  • Medium: 52 spans (10-50)
  • Comunes: 17 spans (>50)
  
  Holdout 10%: 20 spans, 339 sentencias excluidas
              Train: 21.5K tokens, Test: 284.8K tokens
  Holdout 20%: 41 spans, 362 sentencias excluidas  
              Train: 9.9K tokens, Test: 296.4K tokens
  Holdout 30%: 62 spans, 372 sentencias excluidas
              Train: 7.1K tokens, Test: 299.2K tokens
  Holdout 50%: 104 spans, 385 sentencias excluidas
              Train: 5.3K tokens, Test: 301.0K tokens

SPANISH (954,943 tokens):
  • Term spans: 12,424 (115 únicos)
  • Raros: 73 spans (<10)
  • Medium: 30 spans (10-50)
  • Comunes: 12 spans (>50)
  
  Holdout 10%: 11 spans, 379 sentencias excluidas
              Train: 595.6K tokens, Test: 359.4K tokens
  Holdout 20%: 22 spans, 2,483 sentencias excluidas
              Train: 272.4K tokens, Test: 682.6K tokens
  Holdout 30%: 33 spans, 2,514 sentencias excluidas
              Train: 269.7K tokens, Test: 685.3K tokens
  Holdout 50%: 57 spans, 2,920 sentencias excluidas
              Train: 244.6K tokens, Test: 710.3K tokens

CRÍTICO: Ningún term span en test aparece en train (✓)
→ NO hay data leakage, holdout es RIGUROSO
```

---

## ⏳ EN EJECUCIÓN

### Parte 2: Entrenamiento CRF + BiLSTM
- **Script:** `03_metrics_verification/fase3_training.py`
- **Timestamp inicio:** 2026-07-08T13:?? (ejecutando en background)
- **Duración estimada:** 10-20 minutos (menos de lo estimado previamente)
- **Resultado:** PENDIENTE

**Qué hace:**
1. Carga datos EN/ES con splits pre-verificados (de Parte 1)
2. Para cada idioma Y cada holdout (10%, 20%, 30%, 50%):
   - Extrae features CRF (20+ rasgos)
   - Entrena CRF con sklearn-crfsuite
   - Entrena BiLSTM (versión simplificada PyTorch)
   - Calcula F1 token-level (sklearn.metrics)
   - Calcula F1 entity-level (seqeval.metrics)
   - Guarda resultados

**Outputs esperados:**
- `fase3_training_results.csv` — Tabla con todas las métricas
- `FASE3_TRAINING_SUMMARY.md` — Interpretación de resultados

---

## 📋 PRÓXIMOS PASOS (Después Fase 3)

### Paso A: Incorporar números en TESIS_MAIN.md
**Documento:** `/tesis/TESIS_MAIN.md`  
**Sección:** Capítulo 5 (Resultados)

Tabla esperada:
```
Language | Model    | Holdout | Token_F1 | Entity_F1 | Train_Tokens | Test_Tokens
---------|----------|---------|----------|-----------|--------------|----------
EN       | CRF      | 10%     | 0.XXX    | 0.XXX     | 21.5K        | 284.8K
EN       | CRF      | 20%     | 0.XXX    | 0.XXX     | 9.9K         | 296.4K
EN       | CRF      | 30%     | 0.XXX    | 0.XXX     | 7.1K         | 299.2K
EN       | CRF      | 50%     | 0.XXX    | 0.XXX     | 5.3K         | 301.0K
EN       | BiLSTM   | 10%     | 0.XXX    | 0.XXX     | 21.5K        | 284.8K
... (similar para ES)
```

### Paso B: Redactar Capítulos 1-4 (si no completado)
- Cap 1: Introducción (3-4 páginas)
- Cap 2: Marco Teórico (6-8 páginas)
- Cap 3: Metodología (6-8 páginas)
- Cap 4: Estado del Arte (6-8 páginas)

Nota: Gran parte ya redactada en TESIS_MAIN.md

### Paso C: Análisis Comparativo
Crear sección 5.6 en Capítulo 5:

```
5.6 ANÁLISIS COMPARATIVO: CRF vs BiLSTM

¿Cambió CRF significativamente con holdout correcto?
¿BiLSTM mantiene su ventaja en todos los holdouts?
¿Existe threshold donde memorización falsa se quiebra?
→ Responder con números
```

### Paso D: Fase 4 (Si tiempo lo permite)
**Objective:** Transformer baselines

Scripts:
- `bert_crf_baseline.py` — BERT + CRF
- `scibert_crf_baseline.py` — SciBERT + CRF

Outputs:
- `transformer_baselines_results.csv`
- Comparación: BERT vs BiLSTM vs CRF

### Paso E: Fase 5 (Corpus Statistics)
**Objective:** Análisis estadístico del corpus

Métricas:
- Distribución Zipf (α, coeficiente)
- Ley de Heaps (β)
- Inter-annotator agreement (Cohen's Kappa)
- Distribución term frequency (tablas)

---

## 📊 ESTRUCTURA ACTUAL DE EXPERIMENTO_8_JULIO

```
experimento_8_julio/
├── INDEX.md                                    ← Master index
├── PHASE_3_INDEX.md                           ← Este archivo
├── OUTLINE_CAPITULOS_1-4.md                   ← Outline detallado
│
├── FASE_1_RESUMEN_EJECUTIVO.md                ✅ Diagnóstico inicial
├── FASE_1_DIAGNOSTICO_ESTADO.md               ✅ Problemas encontrados
│
├── FASE_2_EXPLICACION.md                      ✅ Explicación holdout
├── ACTER_VERIFICACION_FINAL.md                ✅ BiLSTM=0.7377
│
├── 02_holdout_protocol/
│   ├── correct_holdout.py                     ✅ Implementación span-level
│   └── FASE_2_EXPLICACION.md
│
├── 03_metrics_verification/
│   ├── fase3_complete.py                      ✅ Setup holdout (completado)
│   ├── fase3_training.py                      ⏳ Entrenar CRF+BiLSTM
│   ├── fase3_results.json                     ✅ Splits verificados
│   ├── FASE3_RESULTADOS.md                    ✅ Reporte Parte 1
│   └── [próximos outputs Parte 2]
│
└── PLAN_FASES_2_6.md                          Plan original
```

---

## 🔑 NÚMEROS CLAVE HASTA AHORA

### Cifras Verificadas (Pre-Fase 3)
| Métrica | Valor | Fuente |
|---------|-------|--------|
| BiLSTM ACTER avg F1 | 0.7377 | bilstm_acter_results.csv (verificado manual) |
| CRF same-domain F1 | 0.676 | Datos históricos |
| CRF cross-domain F1 | 0.050 | ACTER results (promediado incorrectamente antes) |
| EN términos únicos | 224 | df_en[label.isin(['B-T','I-T'])].token.nunique() |
| ES términos únicos | 111 | df_es[label.isin(['B-T','I-T'])].token.nunique() |
| ~50% términos raros | <11 apariciones | Zipf distribution análisis |

### Cifras Por Confirmarse (Fase 3)
| Métrica | Status |
|---------|--------|
| CRF token-level F1 (holdout 10-50%) | PENDIENTE |
| CRF entity-level F1 (holdout 10-50%) | PENDIENTE |
| BiLSTM token-level F1 (holdout 10-50%) | PENDIENTE |
| BiLSTM entity-level F1 (holdout 10-50%) | PENDIENTE |
| Confidence intervals (cross-validation) | PENDIENTE |

---

## 🎯 OBJETIVO FINAL

Al terminar Fase 3:
- ✅ Protocolo correcto de evaluación (span-level holdout) implementado y documentado
- ✅ Datos limpios y divididos sin data leakage
- ✅ Métricas recalculadas con protocolo riguroso
- ✅ Capítulo 5 de tesis puede ser redactado con números verificados
- ✅ Conclusiones sobre memorización vs generalización fundamentadas

---

## 📝 NOTAS IMPORTANTES

1. **Holdout 50% en EN es EXTREMO:** Solo 5.3K tokens de entrenamiento. Esto fuerza la evaluación más rigurosa posible.

2. **Data Leakage: 0 spans en test que aparezcan en train** — Esto es crítico y está verificado. No hay duda sobre la integridad del protocolo.

3. **BiLSTM "simplificado" en fase3_training.py** — La versión real usa modelos preentrenados. Esta es una versión rápida para demostración.

4. **Metrics: Token-level vs Entity-level** — Son métricas diferentes:
   - Token-level: ¿Predijo correctamente este token?
   - Entity-level: ¿Predijo correctamente este SPAN completo?
   - Entity-level es más estricta y realista para terminología.

---

## 🚀 SIGUIENTE ACCIÓN

**Esperar output de `fase3_training.py` (en background)**

Cuando complete:
1. Revisar `fase3_training_results.csv`
2. Comparar CRF vs BiLSTM en cada holdout
3. Documentar hallazgos en TESIS_MAIN.md
4. Proceder a Fase 4 (si hay tiempo) o finalizar
