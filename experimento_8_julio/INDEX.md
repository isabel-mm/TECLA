# Experimento 8 Julio - Índice Maestro
**Fecha actualización:** 2026-07-08 14:55 UTC  
**Estado:** Fase 1 (Diagnóstico) - 60% completado

---

## 📋 DOCUMENTOS CRÍTICOS (Leer primero)

| Documento | Propósito | Audiencia |
|-----------|-----------|-----------|
| [FASE_1_RESUMEN_EJECUTIVO.md](FASE_1_RESUMEN_EJECUTIVO.md) | Resumen de hallazgos principales | Todos |
| [PROGRESS_TRACKING.md](PROGRESS_TRACKING.md) | Timeline y seguimiento | Isabel |
| [HALLAZGOS_FASE1.json](03_metrics_verification/HALLAZGOS_FASE1.json) | Hallazgos detallados (JSON trazable) | Análisis |

---

## 🔍 RESULTADOS POR FASE

### ✅ FASE 1: DIAGNÓSTICO (60% completado)

**Documentos:**
- [FASE_1_DIAGNOSTICO_ESTADO.md](03_metrics_verification/FASE_1_DIAGNOSTICO_ESTADO.md)
- [HALLAZGOS_FASE1.json](03_metrics_verification/HALLAZGOS_FASE1.json)

**Scripts ejecutables:**
- `03_metrics_verification/diagnose_metrics.py` - Diagnóstico inicial
- `03_metrics_verification/recalculate_all_metrics.py` - Verificación same-domain
- `03_metrics_verification/evaluate_bilstm_acter.py` - Preparación BiLSTM ACTER

**Salidas generadas:**
- `03_metrics_verification/diagnostic_report.json`
- `03_metrics_verification/recalculation_report.json`
- `03_metrics_verification/bilstm_acter_training_log.json`

**Hallazgos clave:**
- ✅ Números same-domain verificados (4/4)
- ❌ BiLSTM 0.738 sin documentación
- ⚠️ CRF ACTER discrepancia 2x
- ⚠️ Todas métricas son token-level

---

### ⏳ FASE 2: REPARACIÓN HOLDOUT PROTOCOL (No iniciado)

**Directorio:** `02_holdout_protocol/`

**Tareas:**
- [ ] Analizar código original
- [ ] Implementar `correct_holdout.py`
- [ ] Excluir sentencias enteras
- [ ] Controlar lexeme overlap
- [ ] Tests de validación

---

### ⏳ FASE 3: CLARIFICACIÓN MÉTRICAS (No iniciado)

**Directorio:** `03_metrics_verification/`

**Tareas:**
- [ ] Token-level + entity-level F1
- [ ] Confidence intervals
- [ ] Per-domain breakdown
- [ ] Tabla comparativa

---

### ⏳ FASE 4: TRANSFORMER BASELINES (No iniciado)

**Directorio:** `04_transformer_baselines/`

**Tareas:**
- [ ] BERT + CRF
- [ ] SciBERT + CRF
- [ ] Comparación con BiLSTM
- [ ] Analysis

---

### ⏳ FASE 5: ANÁLISIS CORPUS (No iniciado)

**Directorio:** `05_corpus_analysis/`

**Tareas:**
- [ ] Estadísticas corpus
- [ ] Inter-annotator agreement
- [ ] Comparación estándares

---

### ⏳ FASE 6: RESULTADOS FINALES (No iniciado)

**Directorio:** `06_results_cleaned/`

**Tareas:**
- [ ] Números verificados
- [ ] Reproducibility guide
- [ ] Error analysis
- [ ] Manuscript actualizado

---

## 🔴 HALLAZGOS CRÍTICOS RESUMIDOS

### #1: BiLSTM 0.738 no tiene fuente documentada
```
Status:    ❌ CRÍTICO
Impacto:   Invalida comparación principal
Acción:    Recalcular desde código
Timeline:  HOY
```

### #2: CRF ACTER F1 = 0.025 reportado como 0.050 (2x discrepancia)
```
Status:    ⚠️ ALTO
Impacto:   Sugiere error en cálculo
Acción:    Investigar averaging
Timeline:  HOY
```

### #3: Todas métricas son token-level, no entity-level
```
Status:    ⚠️ ALTO
Impacto:   Potencialmente engañoso para ATE
Acción:    Implementar seqeval
Timeline:  HOY/MAÑANA
```

### #4: Holdout protocol opera en tokens, no spans
```
Status:    ❌ CRÍTICO (crítica revisor #1)
Impacto:   Invalida metodología
Acción:    Reimplementar
Timeline:  FASE 2
```

---

## 📊 CUADRO DE CONTROL RÁPIDO

```
Números Same-Domain:        4/4 ✅ VERIFICADOS
Números Cross-Domain:       2/2 ⚠️ PENDIENTES
Entity-Level Metrics:       0/6 ⏳ NO INICIADO
Transformer Baselines:      0/2 ⏳ NO INICIADO
Confidence Intervals:       0/6 ⏳ NO INICIADO

ESTADO GENERAL:             10% completado (Fase 1: 60%)
```

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### HOY (8 Julio)

1. **Ejecutar BiLSTM ACTER evaluation**
   - Cargar datos ACTER (`/tesis/acter_en/`)
   - Evaluar en 4 dominios
   - Guardar CSV con resultados
   - Verificar si F1=0.738 es correcto

2. **Investigar CRF ACTER 0.025 vs 0.050**
   - Revisar código de cálculo
   - Verificar averaging usado
   - Documentar resultado correcto

3. **Implementar entity-level F1**
   - Usar seqeval.metrics
   - Recalcular todos los números
   - Documentar comparación token vs entity

### MAÑANA (9 Julio)

4. **Iniciar Fase 2: Holdout Protocol**
   - Análisis de código original
   - Diseño de reimplementación
   - Primeros tests

5. **Continuar Fase 3: Métricas**
   - Confidence intervals
   - Per-domain breakdown
   - Tabla comparativa

---

## 📁 ESTRUCTURA DE DIRECTORIOS

```
experimento_8_julio/
├── README.md                          Master overview
├── INDEX.md                           Este archivo
├── PROGRESS_TRACKING.md               Timeline
├── FASE_1_RESUMEN_EJECUTIVO.md        Resumen Fase 1
│
├── 01_plan/
│   ├── DIAGNOSIS.md                   Plan diagnóstico
│   └── ROADMAP.md                     Timeline general
│
├── 02_holdout_protocol/               (VACÍO - No iniciado)
│   ├── correct_holdout.py
│   ├── holdout_validation.py
│   └── METHODOLOGY.md
│
├── 03_metrics_verification/           ← FASE 1 AQUÍ
│   ├── FASE_1_DIAGNOSTICO_ESTADO.md
│   ├── HALLAZGOS_FASE1.json
│   ├── diagnose_metrics.py            ✅ EJECUTADO
│   ├── recalculate_all_metrics.py     ✅ EJECUTADO
│   ├── evaluate_bilstm_acter.py       ⏳ PARCIAL
│   ├── diagnostic_report.json         ✅ GENERADO
│   ├── recalculation_report.json      ✅ GENERADO
│   └── bilstm_acter_training_log.json ✅ GENERADO
│
├── 04_transformer_baselines/          (VACÍO - No iniciado)
│   ├── bert_crf_baseline.py
│   ├── sciBERT_baseline.py
│   └── BASELINES.md
│
├── 05_corpus_analysis/                (VACÍO - No iniciado)
│   ├── analyze_corpus.py
│   ├── inter_rater_agreement.py
│   └── CORPUS_REPORT.md
│
└── 06_results_cleaned/                (VACÍO - No iniciado)
    ├── final_results.md
    ├── error_analysis.py
    └── reproducibility_guide.md
```

---

## 🔗 REFERENCIAS ÚTILES

### Datos Fuente
- `/tesis/crf_results_en.csv` - CRF EN same-domain (verificado)
- `/tesis/crf_results_es.csv` - CRF ES same-domain (verificado)
- `/tesis/bilstm_crf_results_en.csv` - BiLSTM EN same-domain (verificado)
- `/tesis/bilstm_crf_results_es.csv` - BiLSTM ES same-domain (verificado)
- `/tesis/acter/crf_zero_shot.csv` - CRF ACTER (encontrado, discrepancia)
- `/tesis/acter_en/` - Datos ACTER para validación (pendiente)

### Scripts Originales
- `/tesis/crf_terminologico.py` - Implementación CRF
- `/tesis/bilstm_crf_fast_final.py` - Implementación BiLSTM
- `/tesis/bilstm_crf_acter_validation.py` - Validación ACTER
- `/tesis/evaluacion_acter.py` - Evaluación CRF ACTER

### Documentos de Contexto
- `/REVIEWER_FEEDBACK_ANALYSIS.md` - Análisis de críticas
- `/HALLAZGO_CRITICO_ACTER.md` - Hallazgo anterior
- `/TESIS_MAIN.md` - Tesis principal (en progreso)

---

## 💾 CÓMO USAR ESTE ÍNDICE

1. **Para entender rápidamente:** Lee FASE_1_RESUMEN_EJECUTIVO.md (10 min)
2. **Para detalles técnicos:** Ve a HALLAZGOS_FASE1.json (30 min)
3. **Para seguimiento:** Consulta PROGRESS_TRACKING.md (5 min)
4. **Para próximos pasos:** Ir a sección "Próximos Pasos Inmediatos"

---

## ✉️ CONTACTO Y NOTAS

**Investigador:** Isabel Moyano  
**Email:** isabel.moyano@gm.uca.es  
**Inicio:** 2026-07-08 14:00 UTC  
**Última actualización:** 2026-07-08 14:55 UTC  

**Notas:**
- Todos los hallazgos están documentados y trazables
- Todo el código incluye seeds para reproducibilidad
- Todos los números tienen CSVs o JSONs de respaldo

---

**Status:** ✅ Fase 1 documentada y lista para ejecutar acciones críticas
