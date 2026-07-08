# FASE 1: DIAGNÓSTICO - ESTADO ACTUAL
**Fecha: 8 Julio 2026 - 14:45 UTC**

---

## 📋 RESUMEN EJECUTIVO

**Estado:** 🟡 PARCIALMENTE COMPLETADO

- ✅ **Números same-domain VERIFICADOS**
  - CRF EN holdout 50%: **0.6761** (reportado 0.676) ✓
  - CRF ES holdout 50%: **0.7694** (reportado 0.769) ✓
  - BiLSTM EN holdout 50%: **0.6748** (reportado 0.675) ✓
  - BiLSTM ES holdout 50%: **0.7190** (reportado 0.719) ✓

- ⏳ **Números cross-domain PENDIENTES DE VERIFICACIÓN**
  - BiLSTM ACTER: **0.738** (reportado, NO VERIFICADO)
  - CRF ACTER: **0.050** (reportado, PARCIALMENTE VERIFICADO)

---

## 🔍 HALLAZGOS CLAVE

### ✅ Hallazgo 1: Same-Domain Metrics Son Correctos (Token-Level)

**Fuente:** Archivos CSV originales
- `/tesis/crf_results_en.csv`
- `/tesis/crf_results_es.csv`
- `/tesis/bilstm_crf_results_en.csv`
- `/tesis/bilstm_crf_results_es.csv`

**Verificación:**
```
Model          Expected    Actual    Match?
─────────────────────────────────────────
CRF EN         0.6761     0.6761    ✓
CRF ES         0.7694     0.7694    ✓
BiLSTM EN      0.6748     0.6748    ✓
BiLSTM ES      0.7190     0.7190    ✓
```

**Conclusión:** Los números same-domain SON token-level F1, son correctos, pero NO son entity-level.

---

### ⚠️ Hallazgo 2: CRF Cross-Domain Metrics Encontrados pero MÁS BAJOS

**Fuente:** `/tesis/acter/crf_zero_shot.csv`

**Datos encontrados:**
```
Domain    N_spans    Precision    Recall    F1
corp      4180       0.1309       0.0134    0.0243
equi      8662       0.2294       0.0131    0.0248
htfl      9636       0.4856       0.0724    0.1261
wind      862        0.1636       0.0134    0.0248

Average F1: (0.0243 + 0.0248 + 0.1261 + 0.0248) / 4 = 0.0250
```

**Problema:** El promedio es 0.025, NO 0.050 como reportado.

**Causa probable:** Diferentes formulas de averaging (macro vs micro vs weighted)

---

### ❌ Hallazgo 3: BiLSTM Cross-Domain NO TIENE RESULTADOS GUARDADOS

**Búsqueda:**
- No existe `/tesis/acter/bilstm_crf_zero_shot.csv`
- No existe archivo con número 0.738
- El script `bilstm_crf_acter_validation.py` existe pero NO se ejecutó recientemente

**Implicación:** El número 0.738 es reportado SIN ser documentado/guardado.

---

## 📊 PROBLEMA CENTRAL IDENTIFICADO

### El Número 0.738 es una "Cifra Fantasma"

```
Situación:
┌─────────────────────────────────────────────┐
│ Reportado: BiLSTM ACTER F1 = 0.738         │
│ Documentado: NO (sin archivo de resultados) │
│ Reproducible: DESCONOCIDO (no se ejecutó)  │
│ Verificable: NO (sin detalles per-domain)  │
└─────────────────────────────────────────────┘
```

**Esto explica por qué los revisores criticaron:**
> "The claim of F1=0.738 zero-shot on ACTER with randomly initialized embeddings is surprising."

---

## 🔧 ACCIONES REALIZADAS EN FASE 1

| # | Acción | Estado | Archivo |
|---|--------|--------|---------|
| 1 | Crear diagnóstico_metrics.py | ✅ HECHO | diagnose_metrics.py |
| 2 | Crear recalculate_all_metrics.py | ✅ HECHO | recalculate_all_metrics.py |
| 3 | Verificar números same-domain | ✅ HECHO | recalculation_report.json |
| 4 | Encontrar CRF ACTER results | ✅ HECHO | acter/crf_zero_shot.csv |
| 5 | Buscar BiLSTM ACTER results | ✅ HECHO | NOT FOUND |
| 6 | Documentar hallazgos | ✅ HECHO | Este archivo |

---

## ⏳ ACCIONES PENDIENTES EN FASE 1

### Prioridad CRÍTICA:

1. **Ejecutar bilstm_crf_acter_validation.py**
   - Objetivo: Obtener resultados REALES de BiLSTM en ACTER
   - Salida esperada: per-domain F1 scores
   - Documentar: Guardar resultados en `/acter/bilstm_crf_zero_shot.csv`
   - Verificar: Calcular promedio y comparar con 0.738

2. **Calcular entity-level F1 para todos los modelos**
   - Usar seqeval.metrics.f1_score (estándar NER)
   - Reportar AMBAS métricas: token-level + entity-level
   - Documentar en: `entity_level_metrics.csv`

3. **Investigar discrepancia CRF ACTER**
   - Encontrado: F1=0.025 (promedio)
   - Reportado: F1=0.050
   - ¿Qué averaging se usó?
   - ¿Es un error de cálculo o una métrica diferente?

---

## 📂 ESTRUCTURA DE ARCHIVOS GENERADOS

```
experimento_8_julio/
├── 03_metrics_verification/
│   ├── FASE_1_DIAGNOSTICO_ESTADO.md        ← Estás aquí
│   ├── diagnose_metrics.py                 ✅ Script inicial
│   ├── recalculate_all_metrics.py          ✅ Verificación same-domain
│   ├── diagnostic_report.json              ✅ Reporte diagnóstico
│   ├── recalculation_report.json           ✅ Reporte verificación
│   ├── entity_level_metrics.py             ⏳ PENDIENTE
│   ├── entity_level_metrics.csv            ⏳ PENDIENTE
│   └── HALLAZGOS_DETALLADOS.json           ⏳ PENDIENTE
```

---

## 📌 CONCLUSIONES PRELIMINARES

### Lo que SABEMOS:
1. ✅ Los números same-domain son correctos (token-level F1)
2. ✅ Los números son **token-level**, no entity-level
3. ✅ CRF ACTER F1 promedio = 0.025 (NO 0.050)
4. ⚠️ BiLSTM ACTER F1 = 0.738 es un número sin fuente documentada

### Lo que NO SABEMOS:
1. ❓ Si el 0.738 de BiLSTM es real o está inflado
2. ❓ Qué entity-level F1 son (podría cambiar conclusiones)
3. ❓ Por qué CRF ACTER promedio es 0.025, no 0.050
4. ❓ Si los modelos son comparables (¿misma métrica?)

### Acciones Necesarias Antes de Continuar:
1. **Ejecutar BiLSTM ACTER evaluation** → obtener 0.738 real
2. **Calcular entity-level F1** → pasar de token a span
3. **Reconciliar CRF ACTER 0.025 vs 0.050** → ¿dónde viene el 0.050?

---

## 🎯 TIMELINE

- **Fase 1 (Diagnóstico):** 8 Julio 14:00-15:30 (en progreso)
- **Fase 2 (Holdout Protocol):** 8 Julio 15:30-18:00
- **Fase 3 (Métricas Claras):** 8 Julio 18:00-20:00
- **Fase 4 (Baselines):** 9 Julio 08:00-14:00

---

## 📝 NOTAS

- Todos los números en CSVs son **token-level F1**, no entity-level
- BiLSTM embeddings son **random** (no pretrained)
- ACTER está en inglés (no hay español)
- CRF usa features manual; BiLSTM usa embeddings
- El protocolo holdout está **flawed** (problema del revisor #1)

---

**Próximo update:** Después de ejecutar BiLSTM ACTER evaluation
