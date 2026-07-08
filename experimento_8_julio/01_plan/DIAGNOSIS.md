# Plan de Diagnóstico - Inconsistencias Numéricas

**Objetivo:** Encontrar, documentar y reparar todas las inconsistencias en los números reportados.

---

## 🔍 INCONSISTENCIAS IDENTIFICADAS

### Inconsistencia #1: CRF Same-Domain F1 Fluctúa

**Valores reportados:**
- En un lugar: **0.676**
- En otro lugar: **0.769**

**Diferencia:** 0.093 (9.3%) → CRÍTICA

**Posibles causas:**
1. Bug en cálculo de métricas (¿diferentes folds?)
2. Diferentes definiciones de F1 (token-level vs entity-level)
3. Reporting error (transcripción manual)
4. Diferentes random seeds
5. Diferentes label schemas (BIO vs IO)

**Acción:** Recalcular desde código fuente limpio, reportar mean ± std

---

### Inconsistencia #2: BiLSTM Cross-Domain > Same-Domain

**Valores reportados:**
- Same-domain: **0.675**
- Cross-domain (ACTER): **0.738**

**Problema:** Es altamente sospechoso que F1 sea MEJOR cross-domain que same-domain.

**Causas probables:**
1. Métrica diferente (token-level vs span-level)
2. Same-domain usa dataset diferente que ACTER
3. Diferentes label schemas
4. Bug en cálculo cross-domain
5. ACTER es en realidad más fácil que corpus original

**Acción:** 
- Verificar que ambos usan la misma métrica
- Inspeccionar distribuciones de datos
- Error analysis para entender por qué

---

### Inconsistencia #3: CRF Cross-Domain F1 ≈ 0.05 Es Implausibly Low

**Valor reportado:** **0.050**

**Problema:** Incluso CRF simple generalmente logra F1 > 0.1

**Causas probables:**
1. Métrica incorrecta (¿solo precision, no F1?)
2. Label mapping error (¿confundiendo clases?)
3. Class imbalance extremo (¿solo N tokens positivos?)
4. Bug en evaluation code

**Acción:** Recalcular precision y recall separadamente

---

## 📋 INVESTIGACIÓN REQUERIDA

### Paso 1: Localizar Código Fuente de Cálculos

**Buscar:**
```bash
find /Users/issyinthesky/Desktop/Repositorios/repo_tesis \
  -name "*.py" -type f | xargs grep -l "f1_score\|f1.*=" | head -20
```

**Objetivo:** Encontrar exactamente dónde se calculan estos números

---

### Paso 2: Verificar Definiciones de F1

**Preguntas:**
- ¿Token-level (BIO tagging)?
- ¿Entity-level (strict match)?
- ¿Entity-level (lenient match)?
- ¿Macro o micro?
- ¿Support weights?

**Estándar esperado:** Entity-level strict match (más riguroso)

---

### Paso 3: Inspeccionar Datasets

**Para cada experimento:**
```python
# Verificar distribución de datos
- Train/test size
- Class distribution (% O vs B-T vs I-T)
- Número de documentos
- Overlap léxico
```

---

### Paso 4: Recalcular con Código Limpio

**Especificación:**
```python
# METRIC 1: Token-level F1 (BIO)
from sklearn.metrics import f1_score
f1_token = f1_score(y_true, y_pred, average='weighted')

# METRIC 2: Entity-level F1 (strict)
# usar seqeval.metrics.classification_report
from seqeval.metrics import f1_score as seqeval_f1
f1_entity_strict = seqeval_f1(y_true_entities, y_pred_entities, scheme='IOB2')

# METRIC 3: Precision, Recall separadamente
precision, recall, f1, support = classification_report(...)

# Reportar TODOS estos
```

---

### Paso 5: Confidence Intervals

```python
# Para cada métrica, calcular:
from scipy import stats

# Opción 1: Bootstrap
from sklearn.metrics import bootstrap

# Opción 2: Cross-validation
from sklearn.model_selection import cross_validate

# Reportar:
- Mean ± Std Dev
- 95% CI
```

---

## 🔧 ACCIÓN INMEDIATA

### Script que Vamos a Crear: `diagnose_metrics.py`

```python
"""
Script para diagnosticar inconsistencias en métricas.
1. Carga todos los números reportados
2. Compara con códigos fuente
3. Recalcula desde cero
4. Reporta discrepancias
"""
```

**Ubicación:** `02_metrics_verification/diagnose_metrics.py`

---

## 📊 REPORTE ESPERADO

Después del diagnóstico, esperamos un documento como:

```markdown
# Diagnostic Report

## Inconsistencia #1: CRF Same-Domain F1
- Reported 0.676 vs 0.769
- **ROOT CAUSE:** Token-level vs entity-level mismatch
- **CORRECTED:** 0.676 (token-level), 0.65 (entity-level)
- **IMPACT:** Results reordered but conclusions remain

## Inconsistencia #2: BiLSTM Cross > Same-Domain
- Reported 0.675 → 0.738
- **ROOT CAUSE:** Different test set / different metric
- **CORRECTED:** Same-domain 0.67, Cross 0.61 (both entity-level)
- **IMPACT:** Conclusion inverted

## Inconsistencia #3: CRF Cross F1 ≈ 0.05
- Reported 0.050
- **ROOT CAUSE:** [TBD - likely bug in code]
- **CORRECTED:** [recalculated value]
- **IMPACT:** [TBD]
```

---

## ✅ CRITERIOS DE ÉXITO

- [ ] Todos los números recalculados desde código fuente
- [ ] Cada número acompañado de confidence interval
- [ ] Token-level y entity-level reportados separadamente
- [ ] Discrepancias documentadas y explicadas
- [ ] Código reproducible publicado
- [ ] Error analysis mostrando por qué hay cambios

---

**Próximo paso:** Ejecutar `diagnose_metrics.py` y generar reporte
