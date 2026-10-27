---
title: "TECLA: guía de uso"
subtitle: "Versión 2.2.0"
lang: es
toc: true
toc-depth: 2
numbersections: true
colorlinks: true
linkcolor: "violeta"
urlcolor: "violeta"
toccolor: "black"
geometry: "a4paper, margin=2.4cm"
fontsize: 11pt
header-includes:
  - \usepackage{xcolor}
  - \definecolor{violeta}{HTML}{6D28D9}
  - \usepackage{float}
  - \floatplacement{figure}{H}
  - \usepackage{titling}
  - \pretitle{\begin{center}\includegraphics[width=2.6cm]{gui/assets/logo.png}\par\vspace{0.6cm}\Huge\bfseries}
  - \posttitle{\par\end{center}}
---

\newpage

# Qué es TECLA

TECLA es una herramienta de código abierto para trabajar con la terminología de un dominio a partir de sus textos. Reúne en un mismo entorno las fases del trabajo terminográfico basado en corpus:

1. **preparar el corpus**: convertir los documentos a texto, limpiarlos y analizarlos lingüísticamente;
2. **extraer los candidatos a término**, combinando patrones gramaticales y medidas estadísticas;
3. **comprobar si el corpus es suficiente** para representar la terminología del dominio;
4. **revisar** los candidatos y **exportar** el inventario.

Puede usarse de tres maneras: con una interfaz gráfica de escritorio, que no exige programar; desde la línea de comandos; y desde un programa en Python. Las tres se apoyan en los mismos módulos y, con los mismos parámetros, producen los mismos resultados.

TECLA se ejecuta en el propio ordenador: los documentos no se envían a ningún servidor. Trabaja con textos en **español** y en **inglés**.

- Página de presentación: <https://isabel-mm.github.io/TECLA/>
- Código fuente: <https://github.com/isabel-mm/TECLA>

# Instalación

## Requisitos

- Python 3.9 o superior.
- Git, para descargar el código.
- Unos 2 GB de espacio libre, sobre todo para los modelos lingüísticos.

## Pasos

En una terminal (en Windows, el Símbolo del sistema o PowerShell):

```bash
git clone https://github.com/isabel-mm/TECLA.git
cd TECLA
pip install -e .
```

A continuación se descargan los modelos lingüísticos de spaCy, uno por lengua:

```bash
python -m spacy download es_core_news_md
python -m spacy download en_core_web_lg
```

Basta con instalar el de la lengua con la que se vaya a trabajar. Si un modelo no está instalado, TECLA intenta descargarlo la primera vez que lo necesita.

## Abrir la interfaz gráfica

```bash
python gui/tecla_gui.py
```

## Actualizar a una versión nueva

Para actualizar TECLA no hace falta desinstalar la versión anterior: la nueva se instala encima.

- **Con el instalador de Windows**, basta con descargar y ejecutar el instalador nuevo, con TECLA cerrada. El instalador reconoce la versión anterior y la sustituye en la misma carpeta.
- **En macOS**, se abre el archivo descargado, se arrastra TECLA a la carpeta Aplicaciones y se elige *Reemplazar* cuando el sistema pregunta si se quiere sustituir la que ya existe.
- **Si se instaló desde el código**, basta con actualizarlo desde la carpeta de TECLA:

```bash
git pull
pip install -e .
```

La actualización no afecta al trabajo hecho: los textos, los resultados, la revisión y los metadatos se guardan en la carpeta de trabajo (`_tecla_output`), no en la aplicación, y se conservan. Una versión nueva puede cambiar la lista de candidatos al volver a ejecutar la extracción, por ejemplo si incorpora filtros nuevos; los cambios de cada versión se recogen en el archivo `CHANGELOG.md` del repositorio.

## Probar TECLA sin instalar nada

El repositorio incluye un cuaderno de demostración para Google Colab, que ejecuta la extracción y la evaluación sobre unos pocos textos desde el navegador:

<https://colab.research.google.com/github/isabel-mm/TECLA/blob/main/TECLA_colab_demo.ipynb>

Incluye unos textos sintéticos de prueba. Es una muestra, no la forma de trabajo: los textos que se cargan en el cuaderno se copian a una sesión de Google, por lo que no deben usarse documentos confidenciales ni sujetos a derechos de autor.

# Preparar la carpeta de trabajo

TECLA trabaja sobre una **carpeta de trabajo** que contiene una subcarpeta llamada `corpus` con los documentos, en PDF o en texto plano (TXT):

```
mi_proyecto/                <- carpeta de trabajo
└── corpus/
    ├── Rojo, G._2021_Introducción a la lingüística de corpus.pdf
    ├── Casas Gómez, M. y Varo Varo, C. (coords.)_2023_La terminología de la semántica.pdf
    └── ...
```

Dos recomendaciones:

- **Una sola lengua por corpus.** La gramática de patrones y el modelo lingüístico se eligen para todo el corpus.
- **Nombres de archivo informativos.** Si el nombre sigue el esquema `Autor_Año_Título`, TECLA deduce de él el autor, el año y el título de cada documento, que después pueden corregirse a mano. El autor es todo lo que va antes del año, de modo que admite apellidos compuestos y varios autores. Es también lo que permite a TECLA saber qué autores emplean cada candidato.

Todo lo que TECLA genera se guarda dentro de la carpeta de trabajo (véase la sección «Qué archivos genera»); los documentos originales no se modifican.

# La interfaz gráfica, paso a paso

La ventana tiene dos zonas. A la izquierda, el **panel de configuración**: carpeta de trabajo, lengua, tipo de candidatos, perfil de puntuación, ajustes de extracción y el botón *Ejecutar*. A la derecha, las **cuatro pantallas** del flujo, a las que se accede por los pasos numerados de la parte superior: *Corpus*, *Extracción*, *Evaluación* y *Revisión*. El paso en curso aparece resaltado y los completados quedan marcados. El botón *Siguiente*, en la esquina inferior derecha de cada pantalla, lleva al paso siguiente.

![Pantalla inicial.](web/img/inicio.png){width=100%}

## Antes de ejecutar

1. **Carpeta de trabajo.** Se pulsa *Elegir carpeta…* y se selecciona la carpeta de trabajo (la que contiene la subcarpeta `corpus`).
2. **Lengua.** *Español*, *inglés* o *auto*, que la detecta a partir de los textos.
3. **Candidatos monoléxicos.** Por defecto solo se extraen candidatos de dos o más palabras. Si se marca *Incluir candidatos monoléxicos*, se extraen también los de una palabra.
4. **Perfil de puntuación.** Decide cuánto pesa cada medida en el índice de terminologicidad:
   - *Frecuencia* (0,6 para el *TF-IDF* y 0,4 para el *NC-value*): favorece los candidatos muy presentes en el corpus.
   - *Equilibrado* (0,5 y 0,5): es el valor por defecto.
   - *Complejidad* (0,2 y 0,8): favorece los candidatos de varias palabras bien delimitados por su contexto.
5. Se pulsa **Ejecutar**. El registro del proceso muestra cada etapa. El análisis lingüístico es la más lenta: un corpus de un millón y medio de palabras tarda unos dos minutos en un ordenador portátil.

## Paso 1: Corpus

Muestra las cifras del corpus (documentos, *tokens*, oraciones, tipos y relación entre tipos y *tokens*) y una tabla con los datos de cada documento:

| Columna | Qué indica |
|---|---|
| Tokens | Número de palabras y signos del documento |
| Oraciones | Número de oraciones |
| Tipos | Número de lemas distintos |
| TTR | Tipos entre *tokens* |
| Hápax | Proporción de tipos que aparecen una sola vez en el documento |
| Dens. léx. | Proporción de palabras de contenido entre las palabras |
| Long. or. | *Tokens* por oración, de media |

Al seleccionar un documento, el panel inferior permite completar o corregir sus **metadatos** (autor, año, temática, fuente y notas). El botón *Exportar CSV* guarda la tabla completa.

![Pantalla Corpus.](web/img/corpus.png){width=100%}

## Paso 2: Extracción

La extracción tiene dos etapas. La primera es **lingüística**: se buscan en el texto las secuencias que siguen los patrones gramaticales habituales de los términos de cada lengua (por ejemplo, un nombre seguido de un adjetivo en español, o una serie de nombres en inglés). La segunda es **estadística**: para cada candidato se calculan varias medidas, que se combinan en un **índice de terminologicidad** entre 0 y 1.

| Columna | Qué indica |
|---|---|
| Candidato | La forma con que aparece más a menudo en los textos, preferiblemente en singular |
| Variantes | Las demás formas, resumidas por tipo (en plural, con mayúscula inicial, en mayúsculas, sin tilde, con guion o espacio); las que no son una variante previsible se muestran tal cual |
| Score | Índice de terminologicidad, con una barra que lo representa |
| TF-IDF | Frecuencia ponderada por el número de documentos en que aparece |
| C-val | *C-value*: penaliza a los candidatos que aparecen sobre todo dentro de otros más largos |
| NC-val | *NC-value*: amplía el *C-value* con la información de las palabras que rodean al candidato |
| Frec | Frecuencia absoluta |
| Frec/mil | Frecuencia por mil *tokens* |
| Docs | Número de documentos en que aparece |
| Autores | Número de autores distintos que lo emplean, según los metadatos de los documentos |

Bajo un mismo candidato se reúnen todas sus formas, aunque el análisis lingüístico les haya asignado lemas distintos: el singular y el plural, las variantes de género de los adjetivos y las formas con y sin tilde (*unidad terminológica* y *unidades terminológicas*, *ficha terminológica* y *ficha terminologica*). Sus frecuencias se suman antes de calcular las medidas. La fila *Qué mide cada columna*, encima de la tabla, explica cada medida al pasar el ratón por su signo de interrogación.

La tabla puede **ordenarse** por cualquiera de las medidas, y las columnas pueden mostrarse u ocultarse con las casillas de la fila *Columnas*. Los botones *CSV* y *TBX* exportan los candidatos seleccionados o, si no hay ninguno seleccionado, todos los que se muestran.

![Pantalla Extracción.](web/img/extraccion.png){width=100%}

## Paso 3: Evaluación

Responde a una pregunta que conviene hacerse antes de dar por bueno un inventario: ¿recoge este corpus la terminología del dominio de forma suficiente? Se pulsa *Calcular representatividad* y TECLA muestra:

- El **Índice de Representatividad Terminológica (IRT)**, de 0 a 100, con una etiqueta (de «escasamente representativo» a «muy representativo») y un texto que separa lo que juega a favor y en contra. Promedia cuatro componentes:
  - *saturación*: si el vocabulario deja de crecer al añadir textos (ley de Heaps);
  - *hápax*: qué proporción de los lemas aparece una sola vez;
  - *dispersión*: si los candidatos principales se reparten por los documentos (medida DP);
  - *estabilidad*: si el núcleo del inventario se mantiene al cambiar los documentos (remuestreo).
- La **dispersión de cada candidato** (DP). Un valor próximo a 0 indica que el candidato se reparte por todos los documentos; uno próximo a 1, que se concentra en uno o en unos pocos, de modo que puede ser un uso propio de un autor.
- Una tabla con los **resultados por prueba**: el valor medido en cada una (exponente de Heaps, proporción de hápax, DP medio y estabilidad) y su puntuación de 0 a 100. El botón *CSV* la exporta, junto con el índice.
- Los **gráficos**: crecimiento del vocabulario, dispersión y distribución de frecuencias.

El IRT es una orientación rápida. Sus umbrales son convenciones de la herramienta, no valores validados empíricamente: conviene leerlo junto con sus componentes y no como un veredicto.

Dos análisis opcionales necesitan un fichero aportado por el usuario:

- **Cobertura frente a una lista de referencia.** Con *Cargar lista…* se carga un CSV con una columna llamada `term` (un glosario, por ejemplo), y TECLA indica qué parte de esa lista aparece entre los candidatos.
- ***Keyness* frente a un corpus de referencia.** Con *Cargar referencia…* se carga un CSV con una columna de lemas y otra de frecuencias, y TECLA calcula qué candidatos son característicos del corpus analizado frente a ese corpus de referencia.

![Pantalla Evaluación.](web/img/evaluacion.png){width=100%}

## Paso 4: Revisión

Ningún sistema automático sustituye el juicio del especialista. En esta pantalla cada candidato se marca como *aprobado*, *rechazado* o *pendiente*. La lista de la izquierda puede filtrarse por estado, y encima de ella se ve el progreso: cuántos candidatos se han revisado, cuántos se han aprobado y rechazado, y el porcentaje, con una barra.

Para cada candidato, el panel de la derecha muestra, en este orden:

1. **El candidato y su estado.** Bajo la forma del candidato, un resumen de sus variantes («También en plural y con mayúscula inicial»); al pulsarlo se despliegan todas las formas, cada una con su tipo.
2. **El aviso de uso de autor.** Si todas las apariciones del candidato están en textos de los mismos autores, TECLA lo indica, porque puede tratarse de un uso propio de esos autores y no de un término asentado. La casilla *Posible uso propio de autor/es* permite dejarlo anotado.
3. **Las concordancias**: las apariciones del candidato en los textos, con su contexto a izquierda y derecha y el documento de procedencia, en forma abreviada («Casas Gómez y Varo Varo (2023)»). Se muestran hasta 500 y pueden filtrarse por documento. Al pulsar una línea se ve la oración completa. El botón *CSV* exporta todas las apariciones.
4. **Los datos de la extracción**, en una tabla con todas las medidas del candidato.
5. **Las notas.**

La revisión se guarda automáticamente en la carpeta de trabajo, junto con la lista de candidatos. Al volver a abrir TECLA con la misma carpeta, un aviso ofrece **continuar la revisión** donde se dejó, sin volver a ejecutar la extracción; *Empezar de nuevo* archiva la revisión anterior como copia, sin borrarla. Si el corpus ha cambiado desde entonces, el aviso lo indica: conviene volver a ejecutar la extracción, y las decisiones ya tomadas se conservan. Cuando el corpus produce muchos candidatos, la lista muestra los 300 primeros; el filtro por estado permite llegar al resto.

Los botones de la parte superior exportan los **términos revisados** en CSV o JSON (con sus cifras, su estado, la marca de uso de autor y las notas) o en TXT (un término por línea). Por defecto se exportan los aprobados; con la casilla *incluir los rechazados*, también estos, con su estado.

![Pantalla Revisión.](web/img/revision.png){width=100%}

# Ajustes de extracción

Se abren con el botón *Ajustes de extracción…* del panel de la izquierda, que resume debajo los ajustes cambiados. Cada opción tiene un signo de interrogación que explica, al pasar el ratón, para qué sirve. Los valores numéricos se escriben o se ajustan con los botones − y +.

- **Filtros**, que se aplican al momento: frecuencia mínima (por defecto, 2; con 1 se incluyen los hápax), puntuación mínima del índice y percentil mínimo. Lo que queda tras los filtros es el resultado de la extracción: lo que muestran la tabla, la revisión y la evaluación, y lo que se exporta.
- **Longitud máxima de los candidatos**, en palabras (por defecto, 5).
- **Otra lengua en el corpus**, para textos con partes en la otra lengua, como los resúmenes en inglés de los artículos en español. Se pueden descartar los párrafos escritos en ella antes del análisis y excluir los candidatos que contengan sus palabras vacías.
- **Stoplist adicional.** Palabras, separadas por comas, que no deben formar parte de ningún candidato. También puede cargarse desde un fichero de texto, con una palabra por línea.
- **Gramática de patrones.** Por defecto se usa la gramática incluida, que cubre el español y el inglés. Puede sustituirse por un fichero `.yaml` propio, por ejemplo para adaptarla a un dominio.

Salvo los filtros, los ajustes se aplican la próxima vez que se pulsa *Ejecutar*.

# Qué archivos genera

Todo queda en la carpeta `_tecla_output`, junto a la carpeta `corpus` y nunca dentro de ella, para que TECLA no lo lea como parte del corpus. Los textos, los metadatos deducidos y las estadísticas se regeneran en cada ejecución; el trabajo del usuario (metadatos corregidos y revisión) se conserva.

| Archivo o carpeta | Contenido |
|---|---|
| `_tecla_output/textos/raw/` | Los documentos convertidos a texto, sin limpiar |
| `_tecla_output/textos/clean/` | Los textos limpios, que son los que se analizan |
| `_tecla_output/metadata.csv` | Autor, año y título deducidos del nombre de cada archivo |
| `_tecla_output/estadisticas_corpus.csv` | Las estadísticas de cada documento y del corpus |
| `_tecla_output/metadatos_documentos.json` | Los metadatos corregidos a mano |
| `_tecla_output/revision.json` | El estado, las notas y la marca de uso de autor de cada candidato revisado |
| `_tecla_output/candidatos.json` | La lista de candidatos de la última extracción, para retomar la revisión |
| `_tecla_output/graphs/extraction/` | Gráficos de la extracción (PNG) |
| `_tecla_output/graphs/evaluation/` | Gráficos de la evaluación (PNG) |
| `_tecla_output/tecla_debug.txt` | Registro de tiempos de cada etapa, útil si un proceso va lento |

El inventario se exporta, además, en dos formatos, donde el usuario indique:

- **CSV**: una fila por candidato, con todas sus cifras.
- **TBX-Basic** (ISO 30042): el estándar de intercambio terminológico, con las variantes de cada candidato.

Desde la revisión se exportan, además, los términos revisados (CSV, JSON o TXT) y las concordancias de cada candidato (CSV), y desde la evaluación, los resultados por prueba (CSV). Los cuadros de guardar se abren en la carpeta `_tecla_output`.

# Línea de comandos

Para automatizar tareas o procesar varios corpus seguidos, TECLA ofrece la orden `tecla` con tres operaciones.

## Extraer

```bash
tecla extract --corpus mi_proyecto/corpus --lang es \
      --structure --remove-bibliography \
      --output candidatos.csv --tbx candidatos.tbx
```

| Opción | Qué hace |
|---|---|
| `--corpus` | Carpeta con los documentos (obligatoria) |
| `--lang` | Lengua: `es` o `en` (obligatoria) |
| `--output` | Ruta del CSV de salida |
| `--tbx` | Ruta del TBX de salida |
| `--multiword` | Solo candidatos de dos o más palabras |
| `--top-k` | Número máximo de candidatos |
| `--percentile` | Conserva solo el percentil superior de la lista |
| `--structure` | Limpia el ruido estructural (números de página, líneas sueltas) |
| `--remove-bibliography` | Elimina el bloque de referencias |
| `--lemmatize` | Lematiza durante la limpieza |
| `--tfidf-weight` | Peso del *TF-IDF* en el índice (por defecto, 0,5); el del *NC-value* es el resto |

## Estadísticas del corpus

```bash
tecla stats --corpus mi_proyecto/_tecla_output/textos/clean --lang es --output corpus.csv
```

Calcula, para cada texto, los *tokens*, los tipos, la relación entre ambos, la proporción de hápax, la densidad léxica, el número de oraciones y su longitud media.

## Evaluar una extracción

```bash
tecla evaluate --extracted candidatos.csv --gold glosario.csv --mode lemma --verbose
```

Compara una extracción con una lista de referencia y calcula la precisión, la cobertura y el F1. Las columnas que se comparan se llaman `term` por defecto y pueden cambiarse con `--extracted-col` y `--gold-col`. El modo `exact` compara las formas tal cual; el modo `lemma`, sus lemas.

# Uso desde Python

El flujo completo puede lanzarse con una sola función:

```python
from pathlib import Path
from pipeline.pipeline import run_tecla_pipeline

candidatos = run_tecla_pipeline(
    corpus_path=Path("mi_proyecto/corpus"),
    language="es",                      # "es", "en" o None para detectarla
    cleaning_options={
        "structure": True,
        "remove_bibliography_flag": True,
        "remove_captions_flag": True,
        "remove_section_headers_flag": True,
    },
    extraction_options={
        "multiword_only": False,        # incluir candidatos monoléxicos
        "max_term_length": 5,
        "weights": {"tfidf": 0.5, "ncvalue": 0.5},
    },
)

candidatos.sort(key=lambda c: -c["terminologicity"])
for c in candidatos[:10]:
    print(c["lemma"], round(c["terminologicity"], 3), c["frequency"])
```

Cada candidato es un diccionario con estos campos:

| Campo | Contenido |
|---|---|
| `lemma` | Forma lematizada |
| `term` | Forma más frecuente en los textos |
| `variants` | Otras formas |
| `patterns` | Patrones gramaticales con que se ha reconocido |
| `terminologicity` | Índice de terminologicidad (0 a 1) |
| `tf_idf`, `c_value`, `nc_value` | Las tres medidas |
| `frequency`, `freq_rel`, `doc_frequency` | Frecuencia absoluta, por mil *tokens* y número de documentos |

Las operaciones de limpieza pueden activarse una a una mediante `cleaning_options`. Además de las cuatro del ejemplo, están disponibles `rejoin_hyphens_flag`, `remove_keyword_lines_flag`, `remove_urls_flag`, `remove_publication_metadata_flag`, `remove_inline_citations_flag`, `remove_journal_metadata_flag`, `remove_statistical_lines_flag`, `remove_stopwords_flag`, `lemmatize_flag` y `extra_stoplist`.

# Problemas frecuentes

**«No se encontró la carpeta 'corpus'».** La carpeta elegida debe ser la carpeta de trabajo, es decir, la que *contiene* la subcarpeta `corpus`, y no la subcarpeta misma.

**No se extrae ningún candidato, o muy pocos.** Lo más habitual es que la lengua seleccionada no sea la de los textos, o que el modelo lingüístico de esa lengua no esté instalado. Conviene comprobar la lengua y volver a ejecutar la orden `python -m spacy download` correspondiente.

**Aparecen palabras generales entre los primeros candidatos.** Es esperable: palabras como *texto* o *lengua* son muy frecuentes en cualquier corpus. Pueden añadirse a la *stoplist adicional*, o rechazarse en la pantalla de revisión.

**Los PDF dan un texto con errores.** La conversión depende de cómo se generó el PDF. Los PDF escaneados, que son imágenes, no contienen texto y deben pasarse antes por un programa de reconocimiento de caracteres (OCR). El resultado de la conversión puede comprobarse en `_tecla_output/textos/clean/`.

**El proceso tarda mucho.** El análisis lingüístico es proporcional al tamaño del corpus. El fichero `_tecla_output/tecla_debug.txt` indica cuánto tarda cada etapa.

**Las cifras de la evaluación parecen poco fiables.** Con corpus muy pequeños lo son: los cuatro componentes del índice necesitan un número razonable de documentos y de palabras para estabilizarse.

# Licencia y contacto

TECLA se distribuye con licencia MIT. El código, las pruebas automáticas y la documentación están en <https://github.com/isabel-mm/TECLA>, donde también pueden comunicarse errores o sugerencias mediante la sección *Issues*.

El nombre es un acrónimo de *Term Extraction and Corpus Linguistics Application*.
