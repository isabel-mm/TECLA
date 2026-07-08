# Progress Tracking - Experimento 8 Julio
**Última actualización: 2026-07-08 14:50 UTC**

---

## 🎯 OBJETIVO GENERAL
Reparar la tesis y resolver 8 críticas de revisores ACL mediante:
1. Diagnóstico de inconsistencias numéricas
2. Reparación de holdout protocol
3. Clarificación de métricas
4. Adición de transformer baselines
5. Análisis de corpus
6. Generación de resultados verificables

---

## ✅ FASE 1: DIAGNÓSTICO (EN PROGRESO)

### ✅ COMPLETADO en Fase 1
- [x] Crear diagnóstico inicial (`diagnose_metrics.py`)
- [x] Verificar números same-domain (`recalculate_all_metrics.py`)
  - CRF EN: 0.6761 ✓
  - CRF ES: 0.7694 ✓
  - BiLSTM EN: 0.6748 ✓
  - BiLSTM ES: 0.7190 ✓
- [x] Encontrar archivos CRF ACTER results
- [x] Identificar BiLSTM 0.738 como "cifra fantasma"
- [x] Documentar hallazgos en JSON trazable
- [x] Crear estado de Fase 1 (FASE_1_DIAGNOSTICO_ESTADO.md)

### ⏳ PENDIENTE en Fase 1
- [ ] Ejecutar completo `bilstm_crf_acter_validation.py` 
  - **Bloqueador:** Requiere datos ACTER
  - **Prioridad:** CRÍTICA
- [ ] Recalcular entity-level F1 (seqeval) para todos los modelos
- [ ] Investigar discrepancia CRF ACTER 0.025 vs 0.050 reportado
- [ ] Error analysis detallado
- [ ] Generar reporte final Fase 1

---

## ⏳ FASE 2: REPARACIÓN DE HOLDOUT PROTOCOL (NO INICIADO)

**Descripción:** Reimplementar holdout para operar en complete spans, no tokens

### Tareas
- [ ] Analizar código original de holdout
- [ ] Implementar `correct_holdout.py`
- [ ] Excluir sentencias enteras (no solo tokens)
- [ ] Controlar lexeme overlap
- [ ] Crear tests de validación

---

## ⏳ FASE 3: CLARIFICACIÓN DE MÉTRICAS (NO INICIADO)

**Descripción:** Reportar tanto token-level como entity-level F1

### Tareas
- [ ] Implementar `metric_calculations.py`
- [ ] Token-level F1 (BIO)
- [ ] Entity-level F1 (strict span match con seqeval)
- [ ] Confidence intervals
- [ ] Per-domain breakdown

---

## ⏳ FASE 4: TRANSFORMER BASELINES (NO INICIADO)

**Descripción:** Implementar BERT/SciBERT + CRF

### Tareas
- [ ] Implementar `bert_crf_baseline.py`
- [ ] Implementar `sciBERT_baseline.py`
- [ ] Comparación directa vs BiLSTM-CRF
- [ ] Análisis de por qué gana cada modelo

---

## ⏳ FASE 5: ANÁLISIS DE CORPUS (NO INICIADO)

**Descripción:** Verificar anotaciones y estadísticas

### Tareas
- [ ] `analyze_corpus.py` - Estadísticas básicas
- [ ] `inter_rater_agreement.py` - Cohen's kappa
- [ ] Comparación con estándares ATE

---

## ⏳ FASE 6: RESULTADOS LIMPIOS (NO INICIADO)

**Descripción:** Generar resultados verificables y reproducibles

### Tareas
- [ ] Compilar `final_results.md`
- [ ] Error analysis completo
- [ ] Guía de replicación
- [ ] Manuscript actualizado

---

## 🔴 HALLAZGOS CRÍTICOS

### Hallazgo 1: BiLSTM 0.738 no tiene fuente
- **Status:** CONFIRMADO
- **Impacto:** CRÍTICO
- **Archivos:** `/03_metrics_verification/HALLAZGOS_FASE1.json`
- **Acción:** Recalcular desde código

### Hallazgo 2: Todas las métricas son token-level, no entity-level
- **Status:** CONFIRMADO
- **Impacto:** ALTO
- **Acción:** Implementar seqeval para entity-level

### Hallazgo 3: CRF ACTER F1 discrepancia 0.025 vs 0.050
- **Status:** ENCONTRADO EN CSV
- **Impacto:** ALTO
- **Acción:** Investigar fórmula de averaging

### Hallazgo 4: Holdout protocol opera en tokens, no spans
- **Status:** CONOCIDO (crítica revisor #1)
- **Impacto:** CRÍTICO
- **Acción:** Reimplementar en Fase 2

---

## 📊 ESTADÍSTICAS

| Métrica | Valor |
|---------|-------|
| Fases identificadas | 6 |
| Fases completadas | 0 (1 en progreso) |
| Problemas identificados | 4 |
| Archivos generados | 9 |
| Números verificados | 4 of 6 |
| Números pendientes | 2 |

---

## 📁 ARCHIVOS CRÍTICOS

### Trazabilidad
- `HALLAZGOS_FASE1.json` - Todos los hallazgos documentados
- `FASE_1_DIAGNOSTICO_ESTADO.md` - Estado actual
- `PROGRESS_TRACKING.md` - Este archivo

### Código
- `03_metrics_verification/diagnose_metrics.py` - Diagnóstico inicial
- `03_metrics_verification/recalculate_all_metrics.py` - Verificación same-domain
- `03_metrics_verification/evaluate_bilstm_acter.py` - Preparación ACTER

### Datos Generados
- `03_metrics_verification/diagnostic_report.json`
- `03_metrics_verification/recalculation_report.json`
- `03_metrics_verification/bilstm_acter_training_log.json`

---

## 🚨 BLOCKERS ACTUALES

### Blocker 1: Datos ACTER para BiLSTM
- **Descripción:** Script está listo pero necesita datos ACTER cargados
- **Resolución:** Usar `/tesis/acter_en/` directamente
- **Prioridad:** CRÍTICA

### Blocker 2: Verificar número 0.738
- **Descripción:** No existe archivo CSV con este resultado
- **Resolución:** Ejecutar evaluación completa
- **Prioridad:** CRÍTICA

---

## ⏱️ TIMELINE ESTIMADO

| Fase | Duración Est. | Estado | Inicio Est. | Fin Est. |
|------|---|---|---|---|
| 1. Diagnóstico | 3h | 60% | Jul 8 14:00 | Jul 8 17:00 |
| 2. Holdout | 4h | 0% | Jul 8 17:00 | Jul 9 09:00 |
| 3. Métricas | 3h | 0% | Jul 9 09:00 | Jul 9 12:00 |
| 4. Baselines | 6h | 0% | Jul 9 12:00 | Jul 9 18:00 |
| 5. Corpus | 3h | 0% | Jul 9 18:00 | Jul 10 09:00 |
| 6. Resultados | 3h | 0% | Jul 10 09:00 | Jul 10 12:00 |
| **TOTAL** | **22h** | **10%** | **Jul 8** | **Jul 10** |

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### Prioridad 1 (Hoy)
1. Ejecutar evaluación BiLSTM ACTER completa
2. Guardar resultados en CSV
3. Documentar discrepancia CRF

### Prioridad 2 (Hoy/Mañana)
1. Implementar entity-level F1
2. Iniciar Fase 2 (holdout protocol)

### Prioridad 3 (Mañana)
1. Transformer baselines
2. Análisis de corpus

---

## 📝 NOTAS

- Todos los scripts incluyen reproducibilidad (seeds, timestamps)
- Todos los hallazgos están documentados en JSON
- Código está separado en fases lógicas
- Documentación es trazable e indexable

---

**Responsable:** Isabel Moyano  
**Último update:** 2026-07-08 14:50 UTC  
**Próximo review:** Después de ejecutar BiLSTM ACTER evaluation
