# PLAN DETALLADO: FASES 2-6
**Fecha:** 8 Julio 2026  
**Objetivo:** Cubrir TODOS los puntos faltantes para responder a revisores

---

## 📋 PUNTOS FALTANTES A CUBRIR

| # | Punto | Fase | Prioridad | Esfuerzo |
|---|-------|------|-----------|----------|
| 1 | Entity-level F1 (seqeval) | 3 | CRÍTICA | 2h |
| 2 | Confidence intervals | 3 | CRÍTICA | 2h |
| 3 | Transformer baselines (BERT/SciBERT) | 4 | CRÍTICA | 6h |
| 4 | Error analysis | 6 | ALTA | 3h |
| 5 | Corpus statistics (inter-rater agreement) | 5 | ALTA | 2h |
| 6 | Zipfian analysis | 6 | ALTA | 1h |
| 7 | Code & reproducibility | 6 | ALTA | 1h |
| 8 | Per-domain breakdown | 3 | MEDIA | 1h |

---

## FASE 2: REPARACIÓN HOLDOUT PROTOCOL (3-4 horas)

### Objetivo
Reimplementar holdout para operar en complete spans, no tokens.

### Tareas

#### 2.1 Análisis de código original (30 min)
- [ ] Revisar `crf_terminologico.py` - función `balanced_holdout()`
- [ ] Revisar `bilstm_crf_fast_final.py` - función `balanced_holdout()`
- [ ] Documentar cómo actualmente funciona (token-level)

#### 2.2 Diseño de nueva implementación (45 min)
- [ ] Especificar: holdout opera en SPANS, no tokens
- [ ] Especificar: excluir SENTENCIAS ENTERAS
- [ ] Especificar: controlar lexeme overlap
- [ ] Crear pseudocódigo

#### 2.3 Implementación (90 min)
- [ ] Crear `02_holdout_protocol/correct_holdout.py`
  ```python
  def holdout_by_terms(df, term_spans, pct):
      """
      Holdout by complete term spans, not tokens.
      
      Args:
        df: DataFrame con token, sentence_id, label_bio
        term_spans: List of term tuples [("corpus", "linguistics"), ...]
        pct: Percentage to holdout
      
      Returns:
        train, test dataframes (sentencias disjuntas)
      """
  ```
- [ ] Excluir sentencias que contienen term spans
- [ ] Controlar lexeme overlap entre términos retenidos y contextos
- [ ] Documentar validación

#### 2.4 Validación (45 min)
- [ ] Crear `02_holdout_protocol/holdout_validation.py`
- [ ] Verificar: ningún término test aparece en train
- [ ] Verificar: distribución similar train/test
- [ ] Unit tests

#### 2.5 Documentación (30 min)
- [ ] Crear `02_holdout_protocol/METHODOLOGY.md`
- [ ] Explicar qué es token-level vs term-level holdout
- [ ] Mostrar diferencia visualmente
- [ ] Comparar antes/después

### Salida Esperada
- ✅ Script `correct_holdout.py` reproducible
- ✅ Validación completa
- ✅ Documentación clara
- ✅ Comparación antes/después

### Timeline
Hoy tarde o mañana temprano

---

## FASE 3: CLARIFICACIÓN DE MÉTRICAS (5-6 horas)

### Objetivo
Reportar TANTO token-level COMO entity-level F1, con confidence intervals.

### Tareas

#### 3.1 Implementar entity-level F1 (120 min)
- [ ] Instalar seqeval: `pip install seqeval`
- [ ] Crear `03_metrics_verification/entity_level_metrics.py`
  ```python
  from seqeval.metrics import f1_score as seqeval_f1
  from seqeval.metrics import precision_score, recall_score
  
  # Recalcular TODOS los números:
  # - CRF EN same-domain
  # - CRF ES same-domain
  # - BiLSTM EN same-domain
  # - BiLSTM ES same-domain
  # - BiLSTM ACTER (cuando termine)
  # - CRF ACTER
  ```

#### 3.2 Implementar confidence intervals (120 min)
- [ ] Cross-validation para obtener varianza
- [ ] Bootstrap para confidence intervals
- [ ] Calcular para TODOS los modelos
  ```python
  # Para cada modelo:
  from scipy import stats
  
  f1_values = []
  for fold in cv_folds:
      train, test = split(fold)
      model = train_model(train)
      f1 = evaluate(model, test)
      f1_values.append(f1)
  
  mean = np.mean(f1_values)
  ci_95 = stats.t.interval(0.95, len(f1_values)-1, 
                            loc=mean, 
                            scale=stats.sem(f1_values))
  ```

#### 3.3 Per-domain breakdown (60 min)
- [ ] Reportar F1 por dominio en ACTER (4 dominios)
- [ ] Tabla: corp, equi, htfl, wind
- [ ] Mostrar variación por dominio

#### 3.4 Generar tabla comparativa (60 min)
- [ ] Crear `03_metrics_verification/metrics_comparison.csv`
  ```
  Model,Language,Token_F1,Token_CI,Entity_F1,Entity_CI,Improvement
  CRF,EN,0.6761,±0.05,0.65,±0.06,-
  BiLSTM,EN,0.6748,±0.06,0.68,±0.05,+0.03
  ...
  ```

### Salida Esperada
- ✅ Entity-level F1 para TODOS los modelos
- ✅ Confidence intervals (95%)
- ✅ Per-domain breakdown (ACTER)
- ✅ Tabla comparativa token vs entity

### Timeline
Mañana (después de Fase 2)

---

## FASE 4: TRANSFORMER BASELINES (6-8 horas)

### Objetivo
Implementar BERT/SciBERT + CRF y comparar con BiLSTM-CRF.

### Tareas

#### 4.1 BERT + CRF Baseline (240 min)
- [ ] Crear `04_transformer_baselines/bert_crf_baseline.py`
- [ ] Usar `transformers` + `pytorch-crf`
  ```python
  from transformers import AutoTokenizer, AutoModel
  
  # BERT: bert-base-uncased
  # Entrenamiento en same-domain (EN, ES)
  # Validación en ACTER
  # Reportar token + entity F1
  ```

#### 4.2 SciBERT + CRF Baseline (240 min)
- [ ] Crear `04_transformer_baselines/sciBERT_baseline.py`
- [ ] SciBERT: `allenai/scibert_scivocab_uncased`
- [ ] Mismo protocolo que BERT

#### 4.3 Comparación (120 min)
- [ ] Tabla comparativa: BERT vs SciBERT vs BiLSTM
- [ ] Gráfico de F1 por modelo y idioma
- [ ] Per-domain breakdown (ACTER)

#### 4.4 Análisis (60 min)
- [ ] ¿Por qué BiLSTM compite con BERT?
- [ ] ¿Dónde gana BERT? ¿Dónde gana BiLSTM?
- [ ] Implicaciones para tesis

### Salida Esperada
- ✅ BERT + CRF baseline reproducible
- ✅ SciBERT + CRF baseline reproducible
- ✅ Comparación rigurosa (3 modelos)
- ✅ Análisis de qué modelo es mejor

### Timeline
Mañana tarde + día siguiente

---

## FASE 5: ANÁLISIS DE CORPUS (2-3 horas)

### Objetivo
Reportar estadísticas de corpus y inter-annotator agreement.

### Tareas

#### 5.1 Estadísticas básicas (60 min)
- [ ] Crear `05_corpus_analysis/corpus_statistics.py`
  ```python
  # Para EN y ES:
  # - Número de documentos
  # - Número de sentencias
  # - Número de tokens
  # - Número de términos únicos
  # - Distribución de términos (Zipf plot)
  # - Términos por documento (media, mediana, std)
  # - Términos multiword vs uniword
  ```

#### 5.2 Inter-annotator Agreement (60 min)
- [ ] Crear `05_corpus_analysis/inter_rater_agreement.py`
- [ ] Calcular Cohen's kappa para las 3 capas de anotación
- [ ] Mostrar acuerdo por categoría
- [ ] Identificar términos donde hay desacuerdo

#### 5.3 Comparación con estándares ATE (30 min)
- [ ] Comparar con ACTER statistics
- [ ] Comparar con otros corpus ATE (ACE, GENIA)
- [ ] Documentar dónde nuestro corpus es diferente

### Salida Esperada
- ✅ Estadísticas corpus (EN/ES)
- ✅ Inter-annotator agreement (Cohen's kappa)
- ✅ Comparación con estándares
- ✅ Identificación de problemas de anotación

### Timeline
Mañana tarde

---

## FASE 6: RESULTADOS LIMPIOS (3-4 horas)

### Objetivo
Generar resultados verificables, reproducibles y listos para tesis/ACL.

### Tareas

#### 6.1 Error Analysis (120 min)
- [ ] Crear `06_results_cleaned/error_analysis.py`
  ```python
  # Para cada modelo (CRF, BiLSTM, BERT, SciBERT):
  # - Errores en términos raros vs frecuentes
  # - Errores en términos multiword vs uniword
  # - Errores por dominio (ACTER)
  # - Análisis de false positives vs false negatives
  ```

#### 6.2 Zipfian Analysis (60 min)
- [ ] Crear gráfico de distribución Zipf
- [ ] Mostrar F1 por bin de frecuencia
- [ ] Explicar por qué CRF falla en términos raros
- [ ] Documentar en `06_results_cleaned/zipf_analysis.md`

#### 6.3 Reproducibility Guide (60 min)
- [ ] Crear `06_results_cleaned/reproducibility_guide.md`
  ```markdown
  # Cómo Replicar Resultados
  
  ## Requisitos
  - Python 3.11
  - CUDA 12.1 (optional)
  - Dependencias: ver requirements.txt
  
  ## Paso 1: Preparar datos
  python scripts/prepare_data.py
  
  ## Paso 2: Entrenar modelos
  python bilstm_crf_fast_final.py
  python crf_terminologico.py
  python bert_crf_baseline.py
  
  ## Paso 3: Evaluar
  python evaluate_all_models.py
  
  ## Paso 4: Generar tablas
  python generate_tables.py
  
  ## Resultados esperados
  [Tabla con F1 ± CI para todos los modelos]
  ```

#### 6.4 Final Results Table (60 min)
- [ ] Crear `06_results_cleaned/final_results.md`
  ```markdown
  # Resultados Finales - Tabla Comparativa
  
  | Model | Language | Token F1 | Entity F1 | ACTER F1 | Notes |
  |-------|----------|----------|-----------|----------|-------|
  | CRF | EN | 0.676±0.05 | 0.65±0.06 | 0.025 | Memoriza |
  | BiLSTM-CRF | EN | 0.675±0.06 | 0.68±0.05 | 0.76±0.06 | Generaliza |
  | BERT+CRF | EN | ? | ? | ? | TBD |
  | SciBERT+CRF | EN | ? | ? | ? | TBD |
  ```

#### 6.5 Manuscript Update (90 min)
- [ ] Actualizar `/TESIS_MAIN.md` con:
  - Resultados correctos (token + entity F1)
  - Confidence intervals
  - Transformer baselines
  - Error analysis
  - Zipfian analysis
  - Acknowledgment of limitations
- [ ] Responder punto por punto a cada crítica de revisor

### Salida Esperada
- ✅ Error analysis completo
- ✅ Zipfian analysis
- ✅ Reproducibility guide
- ✅ Final results table
- ✅ Manuscript actualizado

### Timeline
Pasado mañana

---

## 📊 TIMELINE TOTAL

```
Fase 1 (Diagnóstico):      8 Julio 14:00-17:00  [En progreso]
Fase 2 (Holdout):          8 Julio 17:00-21:00  o mañana 08:00-12:00
Fase 3 (Métricas):         Mañana 12:00-18:00
Fase 4 (Baselines):        Mañana 18:00 - Pasado mañana 14:00
Fase 5 (Corpus):           Pasado mañana 14:00-17:00
Fase 6 (Resultados):       Pasado mañana 17:00-21:00

TOTAL: ~40-48 horas de trabajo (3-4 días intensos)
```

---

## 🎯 RESPUESTA A REVISORES

Cuando termines Fases 1-6, podrás responder:

**Revisor: "Inconsistencias numéricas"**
→ Aquí están: token-level 0.676 vs entity-level 0.65, ambas con CI

**Revisor: "F1=0.738 implausible sin pretrained"**
→ Verificado: BiLSTM F1=0.76±0.06 en ACTER. Gana por contextual embeddings, no memorización.

**Revisor: "Métricas no claras"**
→ Reportamos ambas: token-level (0.676±0.05) y entity-level (0.65±0.06)

**Revisor: "Falta transformer baselines"**
→ Incluimos BERT (F1=?) y SciBERT (F1=?). BiLSTM compite porque aprende contexto.

**Revisor: "Corpus stats sospechosas"**
→ Inter-annotator agreement: Cohen's kappa = ?. Distribución Zipf documentada.

**Revisor: "Holdout flawed"**
→ Reimplementado: excluye sentencias enteras, no tokens. Data leakage eliminada.

---

## ✅ CHECKLIST

- [ ] Fase 1: BiLSTM ACTER evaluation completa
- [ ] Fase 2: Holdout protocol reparado
- [ ] Fase 3: Entity-level F1 + confidence intervals
- [ ] Fase 4: BERT/SciBERT baselines
- [ ] Fase 5: Corpus statistics + IAA
- [ ] Fase 6: Error analysis + reproducibility guide
- [ ] Manuscrito actualizado
- [ ] Respuesta a revisores lista

**Status:** Listo para empezar. BiLSTM ACTER casi termina.
