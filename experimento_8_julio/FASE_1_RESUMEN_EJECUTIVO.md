# FASE 1: DIAGNÓSTICO - RESUMEN EJECUTIVO
**Fecha:** 8 Julio 2026  
**Investigador:** Isabel Moyano  
**Estado:** PARCIALMENTE COMPLETADO (60%)

---

## 🎯 OBJETIVO

Verificar la consistencia y trazabilidad de todos los números reportados en la tesis, identificando:
1. Qué números están verificados y reproducibles
2. Qué números tienen problemas
3. Dónde están las inconsistencias

---

## ✅ RESULTADOS PRINCIPALES

### Hallazgo 1: Números Same-Domain SON CORRECTOS ✅

**Los 4 números same-domain se verificaron exitosamente:**

```
MODELO                REPORTADO    ACTUAL       VERIFICADO
──────────────────────────────────────────────────────────
CRF English (50%)     0.676       0.6761       ✅
CRF Spanish (50%)     0.769       0.7694       ✅
BiLSTM English (50%)  0.675       0.6748       ✅
BiLSTM Spanish (50%)  0.719       0.7190       ✅
```

**Fuente documentada:** Archivos CSV originales en `/tesis/`

**Conclusión:** Estos números son reproducibles y correctos (token-level F1).

---

### Hallazgo 2: BiLSTM 0.738 es una "Cifra Fantasma" ❌

**Hallazgo crítico:**

```
NÚMERO REPORTADO:     F1 = 0.738 (BiLSTM cross-domain ACTER)
ARCHIVO CSV:          NO EXISTE
BÚSQUEDAS REALIZADAS: 
  • /tesis/acter/bilstm_crf_zero_shot.csv - NO ENCONTRADO
  • /tesis/acter/bilstm_acter_results.csv - NO ENCONTRADO
  • grep "0.738" en todo el código - SOLO EN PRESENTACIONES

UBICACIONES DONDE APARECE:
  • grafica_comparativa_final.py (línea 70)
  • generar_ppt_completo.py
  • generar_ppt_actualizado.py

DOCUMENTACIÓN DE ORIGEN: NINGUNA
```

**Implicación:** 

El número 0.738 está reportado como resultado pero no existe archivo con los cálculos. Esto significa:
- No se puede verificar
- No se puede reproducir
- No está respaldado por datos guardados

**¿Por qué esto importa?**

Los revisores criticaron: *"The claim of F1=0.738 zero-shot on ACTER with randomly initialized embeddings is surprising."*

Sin documentación de cómo se obtuvo este número, la crítica es aún más válida.

---

### Hallazgo 3: CRF ACTER tiene Discrepancia 2x ⚠️

**Discrepancia encontrada:**

```
REPORTADO EN PRESENTACIÓN: F1 = 0.050
ENCONTRADO EN CSV:         F1 = 0.025

Per-domain breakdown:
  corp:  F1 = 0.0243
  equi:  F1 = 0.0248
  htfl:  F1 = 0.1261
  wind:  F1 = 0.0248
  
PROMEDIO: (0.0243 + 0.0248 + 0.1261 + 0.0248) / 4 = 0.0250
```

**¿Cuál es el número correcto: 0.050 o 0.025?**

Hay varias posibilidades:
1. Diferentes fórmulas de averaging (macro vs micro vs weighted)
2. Bug en cálculo de promedio
3. Diferentes datasets o métricas

**Investigación necesaria:** Verificar qué averaging se usó para obtener 0.050.

---

## 🔍 PROBLEMA CENTRAL

### Inconsistencia #1: Métricas son Token-Level, no Entity-Level

**Descubierto:** Todos los números reportados usan token-level F1:

```python
from sklearn.metrics import f1_score
f1_token = f1_score(y_true_tokens, y_pred_tokens, average='weighted')
```

**Problema:** Para ATE (Automatic Term Extraction), lo correcto es entity-level F1:

```python
from seqeval.metrics import f1_score as seqeval_f1
f1_entity = seqeval_f1(y_true_spans, y_pred_spans, scheme='IOB2')
```

**Por qué importa:**
- Token-level F1 favorece modelos que predicen 'O' correctamente (clase mayoritaria)
- Entity-level F1 penaliza errores en boundaries de términos
- Los dos números pueden ser muy diferentes

**Ejemplo:** Un modelo que predice O para todo tendría:
- Token-level F1 ≈ 0.8 (porque O es ~80% de los tokens)
- Entity-level F1 ≈ 0.0 (porque no detecta ningún término)

---

### Inconsistencia #2: BiLSTM Better Cross-Domain? (Inverosímil)

**Problema reportado:**

```
BiLSTM same-domain:    0.675
BiLSTM cross-domain:   0.738

¿Cómo puede ser MEJOR en cross-domain?
```

Típicamente:
- Same-domain: el modelo ve datos similares en entrenamiento → F1 alto
- Cross-domain: distribution shift, datos diferentes → F1 bajo

Pero aquí se reporta lo opuesto.

**Explicaciones posibles:**
1. Diferentes test sets (ACTER podría ser más fácil)
2. Diferentes métricas (token-level vs entity-level)
3. Bug en evaluación
4. ACTER tiene distribución de términos más balanceada

**Necesita investigación:** Comparación detallada de datos.

---

## 📊 IMPACTO EN CRÍTICAS DE REVISORES

Este diagnóstico **valida y agrava** las críticas de los revisores:

| Crítica del Revisor | Hallazgo en Fase 1 | Severidad |
|---|---|---|
| #1: "Holdout flawed (tokens, not spans)" | Confirmado en código | CRÍTICA |
| #2: "No transformer baselines" | No relacionado con Fase 1 | ALTA |
| #3: "Inconsistencies numéricas" | **CONFIRMADO Y EXPANDIDO** | CRÍTICA |
| #3: "F1=0.738 implausible" | **Sin documentación** | CRÍTICA |
| #3: "Métricas no claras" | **Token-level no especificado** | CRÍTICA |
| #4: "Overclaiming teórico" | No relacionado con Fase 1 | MEDIA |

---

## ✅ ACCIONES COMPLETADAS

| # | Acción | Resultado | Documentación |
|---|--------|-----------|---|
| 1 | Crear script diagnóstico | Diagnóstico inicial completo | `diagnose_metrics.py` |
| 2 | Verificar same-domain | 4 números verificados | CSVs originales |
| 3 | Buscar BiLSTM ACTER | Confirmado: NO EXISTE | Búsquedas doc |
| 4 | Buscar CRF ACTER | Encontrado: discrepancia 2x | `crf_zero_shot.csv` |
| 5 | Documentar hallazgos | JSON trazable | `HALLAZGOS_FASE1.json` |
| 6 | Crear estado Fase 1 | Documento completo | `FASE_1_DIAGNOSTICO_ESTADO.md` |
| 7 | Preparar BiLSTM eval | Script listo para ejecutar | `evaluate_bilstm_acter.py` |

---

## ⏳ ACCIONES PENDIENTES

### Críticas (Sin estas, no podemos continuar)

1. **Ejecutar evaluación BiLSTM ACTER completa**
   - Cargar datos ACTER
   - Evaluar modelo en 4 dominios
   - Guardar F1 por dominio
   - Verificar si 0.738 es correcto

2. **Investigar discrepancia CRF 0.025 vs 0.050**
   - ¿Qué averaging se usó?
   - ¿Hay bug en código?
   - ¿Qué número es correcto?

3. **Implementar entity-level F1 (seqeval)**
   - Recalcular todos los números
   - Comparar token-level vs entity-level
   - Documentar las diferencias

### Importantes (Para Fase 2+)

4. Análisis de distribuciones de datos (¿Por qué BiLSTM mejor cross?)
5. Error analysis detallado (En qué casos falla cada modelo?)
6. Confidence intervals para todos los números

---

## 🎓 LECCIONES APRENDIDAS

### Lección 1: Documentación es Crítica
- Sin archivos CSV, números son "cifras fantasmas"
- Los scripts de presentación pueden contener números no verificables
- Hay que guardar TODOS los resultados intermedios

### Lección 2: Métricas Importan Mucho
- Token-level vs entity-level cambia los resultados significativamente
- Necesita especificarse explícitamente
- Revisores lo notan si está oculto

### Lección 3: Consistency Matters
- Pequeñas discrepancias (0.025 vs 0.050) son rojo flag
- Sugieren bugs o falta de rigor
- Revisor lo nota y reduce confianza

### Lección 4: Reproducibilidad es No-Negotiable
- Si no se puede reproducir desde código, no es válido
- CSVs con números hardcodeados no son suficientes
- Scripts tienen que ser ejecutables

---

## 🔧 RECOMENDACIONES

### A Corto Plazo (Hoy)

1. Ejecutar BiLSTM ACTER evaluation → obtener número real 0.738
2. Documentar CRF ACTER 0.050 vs 0.025 discrepancia
3. Preparar para Fase 2

### A Mediano Plazo (Próximos días)

1. Implementar entity-level F1 para TODOS los experimentos
2. Generar tabla comparativa token-level vs entity-level
3. Crear confidence intervals
4. Reparar holdout protocol

### A Largo Plazo (Para aceptación)

1. Transformer baselines (BERT/SciBERT)
2. Error analysis completo
3. Manuscript actualizado respondiendo a revisores

---

## 📌 CONCLUSIÓN

**Fase 1 ha logrado identificar y documentar los problemas centrales:**

1. ✅ Números same-domain están correctos y verificables
2. ❌ BiLSTM 0.738 no tiene documentación
3. ⚠️ CRF ACTER tiene discrepancia sin explicación
4. ⚠️ Todas las métricas son token-level, no entity-level
5. ⚠️ BiLSTM "mejor" cross-domain es inverosímil

**La conclusión es clara:** La tesis tiene números reportados sin documentación adecuada, y esto explica las críticas de los revisores.

**Para aceptación, NECESITAMOS:**
1. Recalcular y documentar TODOS los números
2. Reportar AMBAS métricas (token + entity)
3. Incluir confidence intervals
4. Ser transparente sobre limitaciones
5. Implementar transformer baselines

---

## 📂 ARCHIVOS DE REFERENCIA

- `HALLAZGOS_FASE1.json` - Todos los hallazgos en formato JSON
- `FASE_1_DIAGNOSTICO_ESTADO.md` - Estado detallado
- `PROGRESS_TRACKING.md` - Timeline y progreso
- `diagnose_metrics.py` - Script diagnóstico
- `recalculate_all_metrics.py` - Verificación same-domain
- `evaluate_bilstm_acter.py` - Preparación para BiLSTM ACTER

---

**Status:** Fase 1 lista para siguiente etapa (recalcular BiLSTM ACTER y entity-level F1)  
**Próximo:** Fase 2 - Reparación de Holdout Protocol
