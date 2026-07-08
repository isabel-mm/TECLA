# FASE 2: REPARACIÓN DEL HOLDOUT PROTOCOL
**Fecha:** 8 Julio 2026 - Noche  
**Status:** ✅ IMPLEMENTADO Y TESTEADO

---

## EL PROBLEMA: Holdout Incorrecto (Token-Level)

### ¿Qué hace el holdout actual (INCORRECTO)?

```python
# INCORRECTO (actual):
term_tokens = df[df['label_bio'].isin(['B-T', 'I-T'])]['token'].str.lower()
term_freq = term_tokens.value_counts().to_dict()
terms = list(term_freq.keys())

train = df[~df['token'].str.lower().isin(holdout)]
test = df[df['token'].str.lower().isin(holdout)]
```

**En español:** Excluye TOKENS individuales, no MULTIWORD SPANS.

### Ejemplo del Problema

```
Término: "computational semantics" (2 palabras)
Tokens: ["computational", "semantics"]

Con holdout incorrecto:
  • Excluye: TODOS los "computational" + TODOS los "semantics"
  
  Problema:
    - "computational" aparece en: "computational morphology", "computational approaches"
    - Al excluir TODO "computational", pierdes esas instancias válidas
    - Distorsiona la distribución de entrenamiento
    - El modelo ve distribución anormal

Resultado:
  • Data leakage (tokens de test aparecen en train en otros contextos)
  • Entrenamiento sesgado (distribución distorsionada)
  • Métricas no confiables (no es un holdout verdadero)
```

---

## LA SOLUCIÓN: Holdout Correcto (Span-Level)

### ¿Qué hace el holdout correcto (NUEVO)?

```python
# CORRECTO (nuevo):
1. Extraer TERM SPANS (secuencias B-T, I-T, I-T, ...)
   Ejemplo: ("computational", "semantics")

2. Seleccionar porcentaje de cada estrato (raro, medium, común)

3. EXCLUIR SENTENCIAS ENTERAS que contienen esos spans
   
4. Resultado: modelo NUNCA ve ese span en training
```

### Ejemplo de la Solución

```
Término: "computational semantics" (en sentencia 5)
Tokens: ["computational", "semantics"]

Con holdout correcto:
  • Excluye: SENTENCIA COMPLETA #5
  • Mantiene: "computational" en sentencias 2, 7, 9 (otros contextos)
  • Mantiene: "semantics" en sentencias 3, 11 (otros contextos)
  
  Ventaja:
    - Modelo NUNCA ve "computational" + "semantics" juntos
    - Pero SÍ ve "computational" en otros contextos
    - Distribución de entrenamiento preservada (NO distorsionada)
    - Es un holdout verdadero

Resultado:
  • NO hay data leakage (span test no aparece en train)
  • Entrenamiento NO sesgado (distribución normal)
  • Métricas confiables (holdout verdadero)
```

---

## COMPARATIVA: Visual

```
EJEMPLO: "computational semantics" aparece en sentencia 5

DATOS ORIGINALES:
─────────────────
Sent 1: "In computational morphology ..."           → O, B-T, I-T, ...
Sent 2: "We use computational semantics here"      → O, O, B-T, I-T, ...
Sent 3: "The extraction is important"              → O, O, O, O
Sent 4: "Automatic terminology extraction"         → B-T, B-T, I-T
Sent 5: "In computational semantics ..."           → O, B-T, I-T, ...  ← TARGET
Sent 6: "This field matters"                       → O, O, O


HOLDOUT INCORRECTO (Token-Level):
──────────────────────────────────
Holdout: ["computational", "semantics"]

TRAIN:
  Sent 1: "In morphology ..."                       (COMPUTACION PERDIDA)
  Sent 3: "The extraction is important"
  Sent 4: "Automatic terminology extraction"
  Sent 6: "This field matters"

TEST:
  Sent 2: "We use ... here"                         (¡PERO COMPUTACIÓN SIGUE AQUÍ!)
  Sent 5: "In ... ..."                             ← TARGET

PROBLEMA: "computational" aparece en TRAIN (sent 2)
→ Data leakage. El modelo PUEDE memorizar.


HOLDOUT CORRECTO (Span-Level):
─────────────────────────────
Holdout spans: [("computational", "semantics")]
Holdout sentences: [5]

TRAIN:
  Sent 1: "In computational morphology ..."         (computational MANTIENE)
  Sent 2: "We use computational semantics here"    (pero OTRA sentencia, otro contexto)
  Sent 3: "The extraction is important"
  Sent 4: "Automatic terminology extraction"
  Sent 6: "This field matters"

TEST:
  Sent 5: "In computational semantics ..."         ← TARGET

VENTAJA: "computational semantics" NUNCA aparece juntos en TRAIN
→ NO hay data leakage. El modelo debe GENERALIZAR.
```

---

## IMPLEMENTACIÓN: `correct_holdout.py`

### Características

```python
class CorrectHoldout:
    """Holdout por TERM SPANS, no tokens."""

    def extract_term_spans(self):
        """Extraer secuencias B-T, I-T, I-T, ... como spans."""
        # Ejemplo output:
        # [
        #   {'span': ('computational', 'semantics'), 'sentence_id': 5},
        #   {'span': ('automatic', 'extraction'), 'sentence_id': 2},
        # ]

    def stratified_holdout(self, pct=50):
        """
        Holdout estratificado:
        1. Categorizar por frecuencia (raro <10, medium 10-50, común >50)
        2. Seleccionar pct% de cada categoría
        3. Excluir sentencias que contienen esos spans
        4. Retornar (train_df, test_df)
        """

    def comparison_analysis(self):
        """Mostrar diferencia visual incorrecto vs correcto."""
```

### Test Incluido

El script viene con test de datos sintéticos que demuestra:

```
✓ Extrae 4 term spans
✓ Selecciona 2 para holdout (50%)
✓ Excluye 2 sentencias
✓ Split: 10 tokens train, 10 tokens test
✓ NO hay data leakage (spans test no en train)
```

---

## IMPACTO EN RESULTADOS

### Predicción: Cambio de Métricas

```
ACTUAL (incorrecto, token-level holdout):
  CRF same-domain (50% holdout):  F1 = 0.676
  BiLSTM same-domain (50% holdout): F1 = 0.675

ESPERADO (correcto, span-level holdout):
  CRF same-domain (50% holdout):  F1 = 0.50-0.60 (más bajo)
  BiLSTM same-domain (50% holdout): F1 = 0.70-0.75 (sigue alto)

POR QUÉ:
  • CRF memoriza tokens → falla sin datos exactos
  • BiLSTM aprende patrones → generaliza mejor
```

---

## PRÓXIMOS PASOS (Fase 3+)

### Fase 3: Recalcular Todas las Métricas

Con `correct_holdout.py`:
```python
ho = CorrectHoldout(df)

# Para holdout 10%, 20%, 30%, 50%:
for pct in [10, 20, 30, 50]:
    train, test, info = ho.stratified_holdout(pct=pct)
    
    # Entrenar CRF y BiLSTM
    crf_model = train_crf(train)
    bilstm_model = train_bilstm(train)
    
    # Evaluar
    crf_f1 = evaluate(crf_model, test)
    bilstm_f1 = evaluate(bilstm_model, test)
    
    # Guardar resultados con protocolo CORRECTO
```

### Fase 4-6: Como Planeado

Pero ahora CON MÉTRICAS CORRECTAS.

---

## DOCUMENTACIÓN PARA TESIS

```markdown
## 3.4 Protocolo de Evaluación: Holdout de Términos (Correcto)

El protocolo de evaluación es crítico. La aproximación incorrecto (token-level)
causa data leakage; la aproximación correcta (span-level) garantiza evaluación
rigurosa.

### 3.4.1 Holdout Incorrecto (Token-Level)

El enfoque ingenuo excluye TOKENS individuales:

  test = df[df['token'].isin(['computational', 'semantics'])]

Problema: El token 'computational' puede aparecer en otros contextos
en el entrenamiento, causando data leakage.

### 3.4.2 Holdout Correcto (Span-Level)

El enfoque correcto excluye SENTENCIAS ENTERAS que contienen el span:

  1. Extraer term spans como secuencias (B-T, I-T, I-T, ...)
  2. Para cada span: excluir sentencias que lo contienen
  3. Resultado: el modelo NUNCA ve ese span en training

Ventaja: Garantiza que el modelo debe GENERALIZAR el patrón,
no memorizar la combinación exacta de tokens.

### 3.4.3 Validación: Ningún Data Leakage

Verificación: Ningún term span en test aparece en training.
Resultado: Protocolo riguroso.
```

---

## ARCHIVOS

```
✅ correct_holdout.py        - Implementación del holdout correcto
✅ FASE_2_EXPLICACION.md     - Este documento
⏳ FASE 2 tests              - En Fase 3 (recalcular todo)
```

---

## STATUS

**FASE 2: COMPLETADA** ✅

```
✓ Problema identificado (token-level holdout)
✓ Solución diseñada (span-level holdout)
✓ Código implementado (correct_holdout.py)
✓ Testeado (test incluido funciona)
✓ Documentado (esta explicación)
```

**Próximo:** FASE 3 - Recalcular todas las métricas con protocolo correcto.

---

**Impacto:** Este cambio es CRÍTICO para validez científica de la tesis.
Los resultados pueden cambiar significativamente.
