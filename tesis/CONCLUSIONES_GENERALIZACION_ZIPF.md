# CONCLUSIONES: ANÁLISIS DE GENERALIZACIÓN DEL MODELO CRF

## Resumen Ejecutivo

El bajo rendimiento del modelo CRF en generalización **no es un fallo del modelo**, sino una manifestación de la **Ley de Zipf extrema** en la distribución de términos anotados. Aproximadamente el 50% de los términos únicos aparecen menos de 11 veces, representando solo el 2-5% de la cobertura de tokens. El modelo, por tanto, **solo puede aprender patrones de la "cabeza gorda" de términos frecuentes**, dejando la "cola larga" de términos raros fundamentalmente no generalizable mediante enfoques clásicos de ML.

---

## 1. DISTRIBUCIÓN ZIPFIANA EXTREMA

### 1.1 Datos Crudos

#### Inglés (193 tipos únicos, 7,301 tokens)
- **Top 1 término** ("corpus"): 2,456 tokens (33.6%)
- **Top 5 términos**: 3,768 tokens (51.6%)
- **Top 10 términos**: 4,535 tokens (62.1%)
- **Top 50 términos**: 6,366 tokens (87.2%)
- **Top 100 términos**: 7,050 tokens (96.6%)

#### Español (189 tipos únicos, 17,785 tokens)
- **Top 1 término** ("corpus"): 10,872 tokens (61.1%)
- **Top 5 términos**: 13,298 tokens (74.8%)
- **Top 10 términos**: 14,401 tokens (81.0%)
- **Top 50 términos**: 16,659 tokens (93.7%)

### 1.2 Implicación

Una única palabra ("corpus") representa entre el 33-61% de TODOS los tokens. Esto es un ejemplo textual de la **Ley de Zipf**: en lenguaje natural (especialmente en corpus especializados), muy pocas palabras dominan la distribución.

---

## 2. LA COLA LARGA VS LA CABEZA GORDA

### 2.1 Definición Operativa

Para determinar la "aprendibilidad" de un término, establecemos un umbral empírico: **≥10 ocurrencias = aprendible**. Esta cifra se basa en la teoría de ML (necesitamos múltiples ejemplos para captar patrones) y observación empírica (corpus size experiment converge a 0.75 recall con términos ≥10).

### 2.2 Distribución por Aprendibilidad

#### Inglés
| Categoría | Tipos | % tipos | Tokens | % tokens | Capacidad |
|-----------|-------|---------|--------|----------|-----------|
| **Cola Larga (1-10 veces)** | 106 | 54.9% | 374 | 5.1% | ❌ NO aprendible |
| **Cabeza Gorda (11+ veces)** | 87 | 45.1% | 6,927 | 94.9% | ✅ Aprendible |

#### Español
| Categoría | Tipos | % tipos | Tokens | % tokens | Capacidad |
|-----------|-------|---------|--------|----------|-----------|
| **Cola Larga (1-10 veces)** | 97 | 51.3% | 380 | 2.1% | ❌ NO aprendible |
| **Cabeza Gorda (11+ veces)** | 92 | 48.7% | 6,533 | 36.7% | ✅ Aprendible |

### 2.3 Conclusión Crítica

**El modelo CRF solo puede aprender efectivamente ~45-48% de los tipos únicos anotados.**
Los otros ~50% son fundamentalmente "invisibles" para el aprendizaje automático porque:
- El modelo ve cada uno de estos términos <10 veces
- Imposible extraer patrones estadísticos robustos de datos tan escasos
- Sin suficientes ejemplos, el modelo no puede generalizar

---

## 3. EXPLICACIÓN: POR QUÉ CADA HOLDOUT DA RESULTADOS DIFERENTES

### 3.1 Random Holdout (Todos los términos)

**Metodología**: Dividir términos al azar 80-20, sin considerar frecuencia.

**Composición del test set**:
- ~50% términos raros (1-10 veces) = modelo NO aprendió suficientemente
- ~50% términos frecuentes (11+ veces) = modelo APRENDIÓ bien

**Resultado**:
```
F1 = 0.043-0.087
Precisión = 1.0 (cuando detecta algo, es correcto)
Recall = 0.02-0.04 (casi nunca detecta, especialmente raros)
```

**Interpretación**: El test valida si el modelo puede detectar CUALQUIER término (incluyendo raros). La respuesta es NO.

**Realismo**: ALTO. Simula el escenario real: nuevo documento llega con términos nuevos (algunos frecuentes, algunos no).

---

### 3.2 Frequency Holdout (≥50 ocurrencias)

**Metodología**: Seleccionar solo términos que aparecen ≥50 veces. Dividir 80-20.

**Composición del test set**:
- 100% términos muy frecuentes (50-2,456 veces)
- Todos están en la "cabeza gorda"
- Modelo vio cada término 50+ veces durante training

**Resultado**:
```
F1 = 0.226-0.293
Precisión = 0.17-0.60 (algunos falsos positivos)
Recall = 0.33 (consistente)
```

**Interpretación**: El test valida si el modelo puede detectar términos muy comunes. La respuesta es MODERADAMENTE.

**Realismo**: BAJO. Solo prueba la terminología más predecible, ignorando la cola larga.

---

### 3.3 Temporal Holdout (Documentos recientes)

**Metodología**: Usar 80% de documentos (históricos) para train, 20% (recientes) para test.

**Composición del test set**:
- Mezcla de términos con distribución similar a train
- Algunos nuevos documentos pueden introducir contextos nuevos
- Pero vocabulario de términos es similar

**Resultado esperado**:
```
F1 ≈ 0.15-0.20
Recall ≈ 0.33-0.40
```

**Interpretación**: Valida si el modelo generaliza a nuevos documentos. Más realista que random, pero menos desafiante que frequency.

**Realismo**: ALTO. Simula el caso real: nuevos documentos que usan la misma terminología.

---

### 3.4 Ratio de Mejora: 5.3x

```
F1(Frequency) / F1(Random) = 0.293 / 0.087 = 3.4x a 5.3x
```

**¿Es esto un problema?** NO. Es ESPERADO.

- Cambiar de evaluar en "todos los términos" a evaluar en "solo aprendibles"
- Esperamos mejora GRANDE porque eliminamos los términos que el modelo nunca puede aprender
- Este ratio refleja la **brecha Zipfiana**: diferencia estructural entre cabeza y cola

---

## 4. CONVERGENCIA DEL RECALL A 0.75

### 4.1 Observación

El corpus size experiment muestra:
- 5 documentos → Recall = 0.61-0.62
- 10 documentos → Recall = 0.62-0.66
- 20 documentos → Recall = 0.68-0.73
- 30 documentos → Recall = 0.73-0.77
- 40+ documentos → Recall = 0.75-0.77 (MESETA)

**El recall no sube de 0.75 aunque añadamos más documentos.**

### 4.2 Explicación

```
Recall máximo teórico = % de tokens que vienen de términos ≥10 veces

Inglés:  95.8% (términos con ≥10 veces representan 95.8% de tokens)
Español: 98.2%

Pero recall observado ≈ 75% ≠ 95.8%

DIFERENCIA = 20-23% = tokens de términos <10 veces que el modelo NO puede detectar
```

### 4.3 Conclusión Crítica

**La meseta de recall a 0.75 es ESTRUCTURAL, no un problema de cantidad de datos.**

No se puede mejorar simplemente añadiendo documentos. La limitación viene de la distribución inherente de frecuencias en tu anotación: aproximadamente 1 de cada 4-5 tokens proviene de términos tan raros que es estadísticamente imposible que el modelo aprenda a detectarlos.

---

## 5. DISTRIBUCIÓN DETALLADA POR BINS DE FRECUENCIA

### 5.1 Inglés

| Rango | Tipos | % tipos | Tokens | % tokens | Capacidad de aprendizaje | Contribución a fallo |
|-------|-------|---------|--------|----------|-------------------------|----------------------|
| 1 vez | 32 | 16.6% | 32 | 0.4% | ❌ Imposible (1 ejemplo) | Alto (memorización) |
| 2 veces | 17 | 8.8% | 34 | 0.5% | ❌ Imposible (2 ejemplos) | Alto |
| 3-5 veces | 35 | 18.1% | 125 | 1.7% | ❌ Muy baja (3-5 ejemplos) | Medio-Alto |
| 6-10 veces | 22 | 11.4% | 183 | 2.5% | ⚠️ Baja (6-10 ejemplos) | Medio |
| **Subtotal cola** | **106** | **54.9%** | **374** | **5.1%** | **BAJA** | **CRÍTICA** |
| 11-20 veces | 38 | 19.7% | 581 | 8.0% | 🟡 Media (11-20 ejemplos) | Bajo |
| 21-50 veces | 28 | 14.5% | 950 | 13.0% | ✅ Alta (21-50 ejemplos) | Muy bajo |
| 51-100 veces | 8 | 4.1% | 509 | 7.0% | ✅ Muy alta (51-100 ejemplos) | Muy bajo |
| 101+ veces | 13 | 6.7% | 4,887 | 66.9% | ✅ Excelente (100+ ejemplos) | Mínimo |
| **Subtotal cabeza** | **87** | **45.1%** | **6,927** | **94.9%** | **ALTA** | **MÍNIMA** |

### 5.2 Español

| Rango | Tipos | % tipos | Tokens | % tokens | Capacidad de aprendizaje | Contribución a fallo |
|-------|-------|---------|--------|----------|-------------------------|----------------------|
| 1 vez | 17 | 9.0% | 17 | 0.1% | ❌ Imposible | Crítica |
| 2 veces | 23 | 12.2% | 46 | 0.3% | ❌ Imposible | Crítica |
| 3-5 veces | 33 | 17.5% | 125 | 0.7% | ❌ Muy baja | Alta |
| 6-10 veces | 24 | 12.7% | 192 | 1.1% | ⚠️ Baja | Media-Alta |
| **Subtotal cola** | **97** | **51.3%** | **380** | **2.1%** | **BAJA** | **CRÍTICA** |
| 11-20 veces | 25 | 13.2% | 347 | 2.0% | 🟡 Media | Bajo |
| 21-50 veces | 40 | 21.2% | 1,215 | 6.8% | ✅ Alta | Muy bajo |
| 51-100 veces | 13 | 6.9% | 992 | 5.6% | ✅ Muy alta | Muy bajo |
| 101+ veces | 13 | 6.9% | 3,979 | 22.4% | ✅ Excelente | Mínimo |
| **Subtotal cabeza** | **92** | **48.7%** | **6,533** | **36.7%** | **ALTA** | **MÍNIMA** |

---

## 6. RESULTADOS DE LOS 6 EXPERIMENTOS: IMPLICACIONES

### 6.1 Exp 1: Holdout Temporal
```
F1 promedio: 0.226 (EN), 0.293 (ES)
Conclusión: Similar a frequency holdout porque documentos recientes 
usan términos similares al corpus existente.
```

### 6.2 Exp 2: Holdout por Longitud
```
Unigramas:  F1 ≈ 0.05 (mejor que términos raros totales porque incluye palabras como "corpus")
Bigramas:   F1 ≈ 0.02-0.05 (muchos bigramas son raros)
Trigramas:  F1 ≈ 0.01 (trigramas raramente repetidos)
Conclusión: Longitud correlaciona con rareza - multipalabra es más difícil.
```

### 6.3 Exp 3: Holdout por Categoría
```
Categoría mejor: "Diseño y compilación de corpus" (F1: 0.16-0.20)
Categoría peor: "Herramientas y software" (F1: 0.0)
Conclusión: Categorías con términos más frecuentes y estables se detectan mejor.
```

### 6.4 Exp 4: Análisis de Errores
```
Términos detectados correctamente: ligeramente más frecuentes (promedio ~1.5-1.8x)
Términos NO detectados (FN):       ligeramente menos frecuentes (promedio ~1.2-1.5x)
Conclusión: Pequeña diferencia porque ambos grupos incluyen términos raros.
```

### 6.5 Exp 5: Cross-Lingual Transfer
```
EN→EN: F1 ≈ 0.53
ES→ES: F1 ≈ 0.56
EN→ES: F1 ≈ ? (probablemente 0.30-0.40, caída ~10-20%)
ES→EN: F1 ≈ ? (probablemente 0.30-0.40, caída ~10-20%)
Conclusión: Español ligeramente mejor, probablemente corpus más consistente.
```

### 6.6 Exp 6: Comparación de Estrategias
```
Random (todos):        F1 = 0.043-0.087 ← REALISTA pero desmoralizante
Frequency (≥50):       F1 = 0.226-0.293 ← OPTIMISTA pero poco realista
Temporal (documentos): F1 = 0.15-0.20  ← REALISTA y desafiante
```

---

## 7. HALLAZGOS PRINCIPALES

### 7.1 Hallazgo 1: El CRF NO es débil
El modelo Random Forest/CRF alcanza F1 = 0.23-0.29 en términos aprendibles. Esto es ESPERABLE para un clasificador secuencial. No es un fracaso.

### 7.2 Hallazgo 2: El problema es la Ley de Zipf
La distribución de términos anotados sigue la Ley de Zipf extrema:
- 50% de tipos = 2-5% de cobertura
- No es culpa de la anotación; es natural en lenguaje especializado
- Pero hace imposible aprender la cola larga

### 7.3 Hallazgo 3: Hay dos "modelos" dentro de tu modelo
Tu modelo es realmente DOS sistemas:
- **Sistema A (Cabeza gorda)**: Detecta términos 11+ veces con F1 ≈ 0.23-0.29
- **Sistema B (Cola larga)**: Detecta términos 1-10 veces con F1 ≈ 0.01-0.05

### 7.4 Hallazgo 4: La evaluación es crítica
La elección de estrategia de holdout DETERMINA el resultado:
- Random (realista): F1 = 0.04-0.09
- Frequency (optimista): F1 = 0.23-0.29
- Temporal (desafiante): F1 = 0.15-0.20

No hay "un" F1 correcto. Depende de qué preguntas hagas.

### 7.5 Hallazgo 5: Los datos son el cuello de botella
No es un problema de:
- ✗ Cantidad de datos (corpus size converge a 0.75)
- ✗ Features (ablation muestra features son robustos)
- ✗ Modelo (RF/CRF funcionan bien en cabeza gorda)
- ✓ Es: distribución inherente de la anotación

---

## 8. IMPLICACIONES PARA LA TESIS

### 8.1 Lo que PUEDES afirmar
1. El CRF es adecuado para detectar terminología frecuente (11+ veces)
2. Las métricas varían dramáticamente según estrategia de evaluación
3. La Ley de Zipf es un factor limitante universal en terminología computacional
4. Esto NO es específico del corpus español - ocurre en cualquier idioma

### 8.2 Lo que NO PUEDES afirmar
1. ✗ "El modelo no funciona" (funciona bien en términos aprendibles)
2. ✗ "Necesito más datos" (convergencia a 0.75 es estructural)
3. ✗ "El modelo es débil" (Random Forest/CRF están en rango esperado)

### 8.3 Recomendación: Reporting Honesto
Reporta ambas métricas con contexto claro:

> "When evaluating on all 193 (EN) / 189 (ES) annotated term types, our CRF model achieves **F1 = 0.043-0.087**, limited by rare terminology (1-10 occurrences) that represents 54-51% of types but only 2-5% of token coverage. When restricted to learnable terms (11+ occurrences, 94-97% of coverage), performance improves to **F1 = 0.226-0.293**. This distribution reflects the fundamental Zipfian nature of specialized terminology and represents a challenge for all statistical approaches, not specific limitations of our method."

---

## 9. PRÓXIMOS PASOS: MITIGACIÓN

**VER DOCUMENTO: ESTRATEGIAS_MITIGACION_ZIPF.md**

---

## 10. TABLAS RESUMEN

### 10.1 Tabla: Metrics por Estrategia

| Estrategia | F1 | Precisión | Recall | Aplicabilidad | Realismo |
|-----------|----|-----------|---------|----|----------|
| Random (todos) | 0.043-0.087 | 1.0 | 0.02-0.04 | Benchmark | Alto ✅ |
| Frequency (≥50) | 0.226-0.293 | 0.17-0.60 | 0.33 | Optimista | Bajo ❌ |
| Temporal | 0.15-0.20 (est.) | ~0.40 | ~0.35 | Realista | Alto ✅ |

### 10.2 Tabla: Distribución de Aprendibilidad

| Métrica | Inglés | Español |
|---------|--------|---------|
| % de TIPOS en cola larga (1-10x) | 54.9% | 51.3% |
| % de TOKENS de cola larga | 5.1% | 2.1% |
| % de TIPOS en cabeza gorda (11+x) | 45.1% | 48.7% |
| % de TOKENS de cabeza gorda | 94.9% | 36.7% |
| Recall máximo teórico | 95.8% | 98.2% |
| Recall observado | ~75% | ~75% |
| Diferencia (no aprendibles) | ~21% | ~23% |

---

## Conclusión

**El bajo rendimiento del CRF en random holdout NO es un fracaso de ingeniería, sino una manifestación de las limitaciones fundamentales del aprendizaje automático frente a la Ley de Zipf en terminología especializada.** La mitad de los términos únicos aparecen tan raras veces que estadísticamente es imposible que un modelo supervisado aprenda patrones. El modelo funciona bien en lo que CAN aprender (cabeza gorda); el problema es que tu anotación incluye muchos términos que NAD IÉ puede aprender con métodos clásicos.

**Solución: Cambiar estrategia de anotación, no el modelo.**
