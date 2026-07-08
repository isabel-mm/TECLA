# OUTLINE EXPANDIDO: Capítulos 1-4
**Para redactar directamente en TESIS_MAIN.md**

---

# CAPÍTULO 1: INTRODUCCIÓN

## 1.1 Motivación y Contexto (500-700 palabras)

### Párrafo 1: ¿Qué es terminología?
- Definición básica: unidades léxicas especializadas
- Importancia: domina en lenguajes especializados
- Ejemplo: medicina, ingeniería, lingüística computacional

### Párrafo 2: Aplicaciones prácticas
- Traducción automática (mantener consistencia términos)
- Sistemas de indexación/búsqueda especializada
- Construcción de glosarios y bases de datos terminológicas
- Minería de textos científicos

### Párrafo 3: El problema actual
- 30+ años de investigación (citar: Kageura, Frantzi, Astrakhantsev)
- Sistemas comerciales aún dependen de diccionarios precompilados
- ¿Por qué falla el aprendizaje automático?
- Razón central: términos son "funcionales, contextuales, dependientes del uso" (Cabré)

### Párrafo 4: La brecha en investigación
- Gap: la mayoría de métodos no validan generalización verdadera
- Problem: K-fold CV tradicional permite data leakage
- Oportunidad: evaluar si modelos aprenden PATRONES o memorizan TOKENS

---

## 1.2 Pregunta de Investigación (200-300 palabras)

### Pregunta central
Escribir como una pregunta que motiva todo el trabajo:
- "¿Pueden modelos de aprendizaje automático reconocer términos completamente nuevos?"
- ¿Qué lo hace difícil? (Zipf distribution, contexto)
- ¿Y en dominios nuevos? (ACTER validation)

### Subpreguntas (3-4)
- Q1: Protocolo de evaluación riguroso (evitar data leakage)
- Q2: Capturar naturaleza contextual de términos
- Q3: Generalización a otros dominios
- Q4: (opcional) Relación con teoría lingüística

---

## 1.3 Contribuciones Principales (300-400 palabras)

### 5 Contribuciones clave (una por párrafo)

**Contribución 1: Protocolo de evaluación riguroso**
- Qué: Holdout de TÉRMINOS (span-level), no K-fold CV
- Por qué: Evita data leakage, fuerza generalización verdadera
- Impacto: Revela verdadero rendimiento (CRF F1=0.05 vs BiLSTM F1=0.74)

**Contribución 2: Análisis de distribución Zipfiana**
- Qué: Demostración de que 50% de términos aparecen <11 veces
- Por qué: Imposible memorizar términos raros, requiere patrones
- Impacto: Explica por qué CRF falla pero BiLSTM generaliza

**Contribución 3: Comparación arquitectónica rigurosa**
- Qué: BiLSTM-CRF vs CRF en múltiples holdout levels (10%, 20%, 30%, 50%)
- Por qué: Muestra memorización vs generalización en acción
- Impacto: Demuestra que embeddings contextuales son críticos

**Contribución 4: Validación externa multidominio**
- Qué: Evaluación en ACTER (4 dominios completamente nuevos)
- Por qué: Prueba generalización real, no solo "memorización afortunada"
- Impacto: F1=0.738 cross-domain demuestra verdadera generalización

**Contribución 5: Conexión teórica**
- Qué: Validación experimental de Harris distributional hypothesis para ATE
- Por qué: Conecta lingüística teórica con machine learning
- Impacto: BiLSTM implementa correctamente la teoría de Cabré

---

## 1.4 Estructura del Documento (150-200 palabras)

Describir brevemente:
- Cap 2: Marco teórico (Cabré, Zipf, Harris)
- Cap 3: Metodología (dataset, features, protocolo)
- Cap 4: Estado del arte (métodos anteriores, gaps)
- Cap 5: Resultados (números, análisis)
- Cap 6: Discusión (implicaciones, limitaciones)

---

# CAPÍTULO 2: MARCO TEÓRICO

## 2.1 Definición Lingüística de Término (400-500 palabras)

### Párrafo 1: Definición de Cabré
- Citar: "La unidad terminológica es aquella cuyo valor especializado no es inherente ni formalmente delimitable, sino funcional, contextual y dependiente del uso"
- Contrastar: definiciones antiguas (inherentes a palabras) vs moderna (funcional)
- Implicación: misma palabra = término O no, según contexto

### Párrafo 2: Tres principios de Cabré
- **Contextualidad:** Término EN CONTEXTO, no intrínsecamente
  - Ejemplo: "compound" en química ≠ "compound" en lingüística
- **Funcionalidad:** Rol en comunicación especializada
  - Ejemplo: profesor de física usa "fuerza" técnicamente, estudiante podría no
- **Variabilidad:** Mismo término, diferentes dominios
  - Ejemplo: "Java" (geografía) vs "Java" (programación)

### Párrafo 3: Implicaciones computacionales
- NO puedes identificar términos solo por lista de palabras
- Necesitas CONTEXTO LINGÜÍSTICO
- Modelos deben aprender PATRONES, no memorizar tokens

### Párrafo 4: Conexión con el problema
- Esto explica por qué CRF (memoriza) falla
- Y por qué BiLSTM (aprende patrones contextuales) funciona

---

## 2.2 Operacionalización: Unithood y Termhood (400-500 palabras)

### Párrafo 1: Unithood (Cohesión sintagmática)
- Definición: cuán "unidad" es una secuencia de palabras
- Medidas:
  - Coocurrencia
  - Document frequency
  - Contextual diversity
  - Frecuencia en documento
- Ejemplo: "computational semantics" vs "the computational" (baja unithood)

### Párrafo 2: Termhood (Especialización)
- Definición: cuán característica es del dominio
- Medidas:
  - TF-IDF (frecuencia en dominio, rara en general)
  - Contexto técnico (rodea palabras técnicas)
  - Estructura formal (patrones morfológicos especializados)
- Ejemplo: "algorithm" (termhood alto en CS), "dog" (termhood bajo)

### Párrafo 3: Combinación de ambos
- Término fuerte = unithood ALTO + termhood ALTO
- En realidad: es un continuo, no binario
- Por eso machine learning es útil: aprende pesos

### Párrafo 4: Por qué es difícil
- Unithood y termhood interaccionan complejamente
- Varía según dominio
- No hay lista completa posible (términos nuevos aparecen)

---

## 2.3 Distribución Zipfiana en Terminología (400-500 palabras)

### Párrafo 1: Ley de Zipf (histórico)
- Definición: f(r) = C / r^α
- Original: frecuencia de palabras en lenguaje natural
- En terminología: también aparece, incluso más extrema

### Párrafo 2: Datos cuantitativos
- ~50% de términos aparecen <11 veces
- Top 5% de términos cubren 60-80% de ocurrencias
- Distribución sigue Zipf con α ≈ 0.95-1.2
- Tabla: distribución en tu corpus (EN y ES)

### Párrafo 3: Implicación crítica para ML
- Memorizar = requiere ~50 ejemplos
- Pero 50% de términos: <11 ejemplos
- → IMPOSIBLE memorizar términos raros
- → REQUIERE aprender PATRONES generales

### Párrafo 4: Conexión con BiLSTM vs CRF
- CRF memoriza combinaciones de tokens
- CRF falla en Zipfian tail (términos raros)
- BiLSTM aprende patrones abstractos
- BiLSTM generaliza a términos raros (porque aprende el patrón, no memoriza)

---

## 2.4 Ley de Heaps para Saturación de Corpus (300-400 palabras)

### Párrafo 1: Ley de Heaps
- Definición: V = k × N^β
- V = vocabulary size, N = corpus size, β ≈ 0.68 para español
- Significa: duplicar corpus → vocabulario sube solo ~60%

### Párrafo 2: Implicación
- Agregar más datos NO resuelve el problema Zipfiano
- Siempre habrá términos raros (Zipf es estructura)
- Solución: aprender patrones, no memorizar

### Párrafo 3: En tu corpus
- Inglés: 306K tokens → 193 términos únicos
- Español: 954K tokens → 189 términos únicos
- Ratio: términos adicionales por millón de tokens ≈ constante
- Conclusión: corpus es suficiente, problema es estructura Zipf

---

## 2.5 Hipótesis Distribucional (Harris, 1954) (300-400 palabras)

### Párrafo 1: Definición original
- "You shall know a word by the company it keeps" (Firth, 1957)
- Harris: contexto determina significado
- Implicación: palabras con contextos similares = significados similares

### Párrafo 2: En terminología
- Término = unidad con significado especializado
- Su significado está en cómo se DISTRIBUYE en contextos especializados
- Ejemplo: "extraction" en contextos de "automatic term extraction"
- BiLSTM aprende embeddings que capturan distribución

### Párrafo 3: Conexión con BiLSTM
- LSTM bidireccional = procesa distribución de palabras alrededor
- Embeddings = representaciones de distribuciones
- CRF tradicional = solo contexto local (±2 palabras)
- BiLSTM = contexto global (toda la sentencia)

### Párrafo 4: Por qué funciona
- BiLSTM captura distribución global
- Puede reconocer patrones nuevos que siguen la distribución
- Incluso si término específico no fue visto

---

# CAPÍTULO 3: METODOLOGÍA

## 3.1 Dataset (300-400 palabras)

### Párrafo 1: Corpus de referencia
- Lingüística de Corpus (EN/ES)
- Tamaño: 306K tokens (EN), 954K tokens (ES)
- Términos anotados: 193 (EN), 189 (ES)
- Dominios: principalmente lingüística computacional, procesamiento de lenguaje natural

### Párrafo 2: Proceso de anotación (3 capas)
- Capa 1: Preanotación automática + glosarios
- Capa 2: Validación de términos extraídos (extraction + C-value)
- Capa 3: Anotación manual (expert linguist)
- Resultado: corpus triple-anotado

### Párrafo 3: Estadísticas
- Tokens por término: media X, mediana Y, std Z
- Multiword vs uniword: X% multiword
- Distribución Zipfiana: 50% términos <11 veces
- Tabla: estadísticas por idioma

### Párrafo 4: Por qué este corpus
- Real (no sintético)
- Bien anotado (3 capas)
- Multiidioma (EN/ES)
- Pequeño pero suficiente (Heaps Law)

---

## 3.2 Ingeniería de Características (32 Rasgos) (400-500 palabras)

### Párrafo 1: Features organizados en categorías
**Morphosyntactic (8):**
- POS, tag, dep, is_noun, is_verb, is_adj, is_propn, shape

**Lexical (6):**
- is_stop, is_punct, is_alpha, has_digit, has_amod, has_premod

**Syntactic (4):**
- in_np, np_head, has_adjective_modifier, has_pre_modifier

**Statistical (8):**
- freq_q (quartil), df_q, tfidf_q, contextual_diversity_q
- [discretizados para CRF]

**Distributional (6):**
- Dominant POS, contextual_diversity, etc.

### Párrafo 2: Por qué estos rasgos
- Linguistically motivated (Cabré, Kageura)
- Computationally efficient
- Generalizan bien (no token-específicos)
- Documentados en literatura (C-value, TF-IDF)

### Párrafo 3: Normalización
- Features discretos → como-es
- Features numéricos → quartiles (para CRF)
- Razón: CRF trabajo mejor con features binarios/discretos

### Párrafo 4: Para BiLSTM
- BiLSTM NO usa features explícitos
- Aprende embeddings directamente
- Features solo para CRF baseline

---

## 3.3 Arquitecturas Evaluadas (400-500 palabras)

### Párrafo 1: CRF (Baseline)
- Definición: Conditional Random Field para etiquetado de secuencias
- Por qué CRF: estándar en NLP, interpretable, features explícitos
- Configuración: sklearn-crfsuite, default settings
- Features: los 32 rasgos lingüísticos

### Párrafo 2: BiLSTM-CRF (Propuesto)
- Definición: BiLSTM bidireccional + CRF layer (Viterbi decoding)
- Embedding: 100-dim (random initialization, no pretrained)
- LSTM: 2 layers, 200 hidden units, dropout 0.3, 0.5
- Features: APRENDIDAS (embeddings), no explícitos
- Por qué: captura patrones contextuales abstractos

### Párrafo 3: Por qué BiLSTM > CRF
- CRF = contexto local (±2 palabras)
- BiLSTM = contexto global (LSTM memory)
- CRF = memoriza combinaciones
- BiLSTM = aprende distribuciones

### Párrafo 4: Implementación
- Framework: PyTorch
- Loss: CRF negative log-likelihood
- Optimizer: Adam (lr=0.001)
- Epochs: 10 (suficiente por Heaps Law)

---

## 3.4 Protocolo de Evaluación: Holdout Span-Level (600-800 palabras)

[ESTE ESTÁ COMPLETO EN TESIS_MAIN.md - ref sección 3.4.1-3.4.5]

**Solo expandir con:**
- Justificación más profunda: por qué span-level es científicamente correcto
- Comparativa visual detallada
- Pseudo-código más completo
- Validación automática (cómo verificamos no data leakage)

---

## 3.5 Validación Externa: ACTER Dataset (300-400 palabras)

### Párrafo 1: ACTER dataset
- 4 dominios independientes: corporate, equestrian, health, energy
- Tamaño: 228K-247K tokens cada uno
- Términos: 72-108 por dominio
- Completamente disjunto de nuestro corpus

### Párrafo 2: Protocolo zero-shot
- Entrenar: nuestro corpus (EN lingüística)
- Evaluar: ACTER (4 dominios técnicos diferentes)
- Sin reentrenamiento (zero-shot)
- Razon: valida generalización verdadera

### Párrafo 3: Por qué es el test definitivo
- Mismo idioma (EN) pero dominios completamente nuevos
- Demuestra si modelo memorizó o aprendió patrones
- Si memoriza: F1 colapsa en dominio nuevo
- Si aprende patrones: F1 se mantiene

### Párrafo 4: Expectativas
- CRF (memoriza): F1 colapsa a ~0.05
- BiLSTM (aprende): F1 se mantiene ~0.73
- Diferencia: revelaría verdadera naturaleza de aprendizaje

---

# CAPÍTULO 4: ESTADO DEL ARTE

## 4.1 Métodos Estadísticos Clásicos (400-500 palabras)

### Párrafo 1: C-value (Frantzi et al., 2000)
- Definición: combina frecuencia + estructura sintagmática
- Fórmula: incluye penalización por aparición dentro de términos mayores
- Ventaja: simple, rápido
- Limitación: basado en frecuencia, no contexto

### Párrafo 2: TF-IDF
- Definición: term frequency × inverse document frequency
- Ventaja: identifica términos raros pero especializados
- Limitación: no considera estructura sintáctica

### Párrafo 3: Kageura-Umino (1996)
- Combina unithood + termhood
- Más sofisticado que C-value o TF-IDF
- Aún basado en frecuencias/coocurrencia
- Limitación: estatístico, no aprende patrones

### Párrafo 4: Limitaciones generales
- Memorizan frecuencias, no patrones
- Fallan en términos raros (Zipfian tail)
- No generalizan a dominios nuevos
- Requieren ajuste manual de pesos por dominio

---

## 4.2 Métodos de Aprendizaje Clásicos (500-600 palabras)

### Párrafo 1: CRF para ATE
- Adaptación de CRF para etiquetado de términos
- Features lingüísticos explícitos (POS, TF-IDF, etc.)
- Mejora respecto a métodos estadísticos
- Pero: aún memoriza combinaciones de features

### Párrafo 2: Máquinas de Soporte Vectorial (SVM)
- Aplicadas a ATE con buenos resultados (¿citar?)
- Problema: token-level classification (no secuencias)
- Ignora contexto de palabras vecinas

### Párrafo 3: Random Forest, Logistic Regression
- También investigados para ATE
- Problema común: ignoran contexto secuencial
- Menos sofisticados que CRF

### Párrafo 4: Limitación común
- Todos dependen de features manuales
- No aprenden representaciones abstractas
- Fallan en Zipfian tail
- Mejora mínima con más datos (Heaps Law)

---

## 4.3 Redes Neuronales para ATE (500-600 palabras)

### Párrafo 1: RNN y LSTM
- LSTM: captura dependencias a largo plazo
- Mejora respecto a RNN simple (vanishing gradient)
- Primeros trabajos: promisores pero limitados

### Párrafo 2: BiLSTM
- Bidireccional: contexto izquierdo + derecho
- Mejora respecto a LSTM unidireccional
- Captura contexto global mejor que CRF (±2 palabras)

### Párrafo 3: BiLSTM + CRF
- Combina: aprendizaje de patrones (BiLSTM) + estructura de secuencia (CRF)
- Transiciones aprendidas automáticamente
- Estado del arte en muchos tareas de etiquetado

### Párrafo 4: En ATE específicamente
- Pocos estudios evalúan rigorosamente (con holdout span-level)
- Mayoría usan K-fold CV (permite data leakage)
- Nuestro trabajo: primero en evaluar BiLSTM con protocolo riguroso

---

## 4.4 Transformers (BERT, etc.) (300-400 palabras)

### Párrafo 1: BERT y variantes
- Pretrained language models
- Contexto bidireccional profundo
- Funcionan bien en muchas NLP tasks
- En ATE: pueden ser overkill, o simplemente mejores

### Párrafo 2: Por qué NO los usamos (ahora)
- Objetivo: entender si BiLSTM captura lo esencial
- Si BERT gana: es por pretrained, no arquitectura
- Si BiLSTM compite: sugiere embeddings simples suficientes
- Transformers son baseline futuro (Fase 4)

### Párrafo 3: SciBERT
- BERT entrenado en corpus científico
- Potencialmente mejor para ATE en textos técnicos
- Pero: mismo debate que BERT

---

## 4.5 Gaps en la Investigación (400-500 palabras)

### Párrafo 1: Gap 1 - Protocolo de evaluación
- Mayoría de papers usan K-fold CV (permite data leakage)
- Pocos usan holdout de términos
- Ninguno especifica "span-level" vs "token-level"
- **Nuestro trabajo:** Protocolo span-level riguroso

### Párrafo 2: Gap 2 - Validación cross-domain
- Mayoría evalúa same-domain
- Pocos testan generalización a dominios nuevos
- ACTER disponible desde 2016, poco usado para ATE
- **Nuestro trabajo:** Validación rigurosa en 4 dominios ACTER

### Párrafo 3: Gap 3 - Análisis de memorización
- ¿Aprenden patrones o memorizan tokens?
- Nada cuantificado en literatura
- Holdout progresivo (10%, 20%, 30%, 50%) no reportado
- **Nuestro trabajo:** Curva de aprendizaje = memorización vs generalización

### Párrafo 4: Gap 4 - Conexión con teoría lingüística
- Cabré (1999): término = funcional, contextual
- Pocos trabajos validaban esto experimentalmente
- **Nuestro trabajo:** BiLSTM captura contextualidad, valida Cabré

### Párrafo 5: Gap 5 - Distribución Zipfiana
- Zipf = problema estructural (no soluble con más datos)
- Pocos trabajos lo analizan en ATE
- **Nuestro trabajo:** Análisis detallado de impacto en ML

---

## 4.6 Oportunidad/Motivación para nuestro trabajo (200-300 palabras)

Escribir como síntesis de todos los gaps:
- Estado del arte: métodos que funcionan pero no se entiende por qué
- Falta: rigor en protocolo, validación cross-domain, análisis mecanístico
- Necesidad: conectar teoría lingüística con práctica ML
- Nuestro aporte: todo lo anterior, enfocado en GENERALIZACIÓN

---

# NOTAS PARA REDACCIÓN

## Tono
- Académico pero accesible
- Explicaciones intuitivas (símiles cuando sea necesario)
- Citas abundantes pero no abrumadoras
- Active voice preferido

## Estructura de párrafos
- Topic sentence clara
- 2-3 sentencias de desarrollo
- Conclusión o transición
- Longitud: 100-150 palabras típicamente

## Transiciones
- Entre párrafos: usar conectores (however, moreover, therefore)
- Entre secciones: referencia al porqué de la siguiente sección
- Entre capítulos: párrafo transición

## Figuras/Tablas
- Incluir donde tenga sentido (distribuciones Zipf, estadísticas, etc.)
- Captions claras y autoexplicativas
- Referencias en texto (Fig. X shows...)

---

## RESUMEN: Qué redactar

**Capítulo 1:** Introducción (3-4 páginas)
- Motivación, pregunta, contribuciones

**Capítulo 2:** Marco teórico (6-8 páginas)
- Cabré, Unithood/Termhood, Zipf, Heaps, Harris

**Capítulo 3:** Metodología (6-8 páginas)
- Dataset, features, CRF/BiLSTM, Holdout (ya está en MAIN), ACTER

**Capítulo 4:** Estado del arte (6-8 páginas)
- Métodos estadísticos, clásicos ML, redes neuronales, transformers, gaps

**TOTAL:** ~20-30 páginas de prosa académica, lista para defensa.

Este outline es tu template: redacta párrafo por párrafo según estas indicaciones.
