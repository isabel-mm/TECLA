<p align="center"><img src="gui/assets/logo.png" alt="Logo de TECLA" width="120"></p>

# TECLA

**Term Extraction and Corpus Linguistics Application** · [Página de presentación](https://isabel-mm.github.io/TECLA/) · [Demostración en Google Colab](https://colab.research.google.com/github/isabel-mm/TECLA/blob/main/TECLA_colab_demo.ipynb) · [Guía de uso](TECLA_GUIA_USO.pdf) · [Cambios](CHANGELOG.md)

TECLA es una herramienta en Python para construir corpus especializados, limpiarlos, extraer candidatos terminológicos y evaluar tanto la extracción como la calidad del corpus. El proyecto ofrece dos formas principales de uso:

- una **CLI** para ejecución reproducible desde terminal;
- una **API** de Python para integrarlo en notebooks, pipelines o interfaces gráficas.

## Qué hace TECLA

TECLA combina varias etapas en un mismo flujo:

- construcción de corpus a partir de **PDF** o **TXT**;
- limpieza opcional del texto, incluyendo ruido estructural y bibliografía;
- detección automática de la lengua;
- extracción híbrida de términos mediante patrones POS y puntuación estadística;
- cálculo de métricas de corpus;
- exportación de resultados a **CSV** y **TBX-Basic**;
- evaluación frente a un gold standard en CSV.

## Instalación

Instala el paquete en modo editable:

```bash
pip install -e .
```

Dependencias principales:

- `spacy`
- `pdfminer.six`
- `langid`
- `nltk`
- `pandas`
- `numpy`
- `pyyaml`
- `matplotlib`
- `customtkinter`

### Modelos spaCy

TECLA trabaja con textos en español y en inglés, con estos modelos:

| Lengua | Modelo por defecto |
|---|---|
| `en` | `en_core_web_lg` |
| `es` | `es_core_news_md` |

Es recomendable instalarlos antes de usar TECLA:

```bash
python -m spacy download es_core_news_md
python -m spacy download en_core_web_lg
```

### Crear el ejecutable de Windows

La compilación debe hacerse en Windows. En una consola dentro del repositorio,
instala TECLA y PyInstaller y ejecuta el script incluido:

```bat
python -m pip install -e . pyinstaller
python -m spacy download es_core_news_md
python -m spacy download en_core_web_lg
packaging\windows\build_windows.bat
```

La aplicación se genera como carpeta en `dist\TECLA\` (se abre con
`TECLA.exe`, que necesita la carpeta `_internal` que lo acompaña) y, comprimida
para distribuirla, en `dist\TECLA-windows.zip`. Conviene compilar en un entorno
virtual limpio, para que no se cuelen paquetes ajenos a TECLA.

Si [Inno Setup 6](https://jrsoftware.org/isinfo.php) está instalado
(`winget install JRSoftware.InnoSetup`), el script genera además el instalador
`dist\TECLA-instalador-windows-setup.exe` a partir de `packaging\windows\TECLA.iss`. Se
instala por usuario, sin permisos de administrador, y añade TECLA al menú
Inicio y a la lista de programas para desinstalarla.

Los modelos `es_core_news_md` y `en_core_web_lg` deben estar instalados antes
de compilar: PyInstaller los incluye y la aplicación empaquetada no puede
descargarlos por su cuenta.

### Crear la aplicación de macOS

La compilación debe hacerse en macOS, con los mismos requisitos (TECLA,
PyInstaller y los dos modelos instalados):

```bash
python -m pip install -e . pyinstaller
python -m spacy download es_core_news_md
python -m spacy download en_core_web_lg
./scripts/build_macos_app.sh
```

La aplicación se genera en `dist/TECLA.app` y, para distribuirla, como imagen
de disco en `dist/TECLA-instalador-macos-arm64.dmg`: al abrirla, se arrastra TECLA
a la carpeta Aplicaciones. La imagen solo funciona en la arquitectura en la
que se compila (`arm64` en los Mac con procesador de Apple). La aplicación no
lleva firma de desarrollador de Apple, así que la primera vez hay que
autorizarla en Ajustes del Sistema, «Privacidad y seguridad», con «Abrir
igualmente».

### Publicar una versión

Al crear y subir una etiqueta `v*` (por ejemplo, `v2.1.1`), GitHub Actions
compila el instalador de Windows y la imagen de disco de macOS, con los
modelos incluidos, y los adjunta a una release para descargar. También se
puede ejecutar el workflow manualmente desde la pestaña **Actions**; en ese
caso, los instaladores quedan disponibles como artefactos de compilación.

Si un modelo no está disponible, TECLA intenta descargarlo y, si falla, cae a un `spacy.blank(...)`. Ese fallback permite ejecutar el pipeline, pero reduce la calidad del análisis lingüístico y de la extracción.

## Estructura de trabajo

El pipeline trabaja sobre una carpeta de corpus. Si encuentra PDF, primero los convierte a texto; si encuentra TXT, parte directamente de ellos.

```text
mi_proyecto/
├── corpus/
│   ├── articulo_01.pdf
│   ├── articulo_02.pdf
│   └── articulo_03.txt
└── _tecla_output/
    ├── textos/
    │   ├── raw/
    │   └── clean/
    └── metadata.csv
```

Cuando usas `run_tecla_pipeline(...)`, TECLA genera automáticamente, junto a la
carpeta del corpus y nunca dentro de ella:

- `_tecla_output/textos/raw/`
- `_tecla_output/textos/clean/`
- `_tecla_output/metadata.csv`

Los textos y `metadata.csv` se regeneran en cada ejecución, así que un documento
que se retira del corpus deja de analizarse. El parámetro `output_folder` permite
elegir otra carpeta de salida.

## Uso rápido desde terminal

La entrada principal es:

```bash
tecla --help
```

También puedes ejecutarlo como módulo:

```bash
python -m tecla --help
```

### Extraer términos

```bash
tecla extract \
  --corpus corpus/ \
  --lang es \
  --multiword \
  --percentile 80 \
  --output resultados/terminos.csv \
  --tbx resultados/terminos.tbx
```

Opciones relevantes:

- `--corpus`: carpeta con PDF o TXT;
- `--lang`: código ISO como `es`, `en` o `auto`;
- `--multiword`: deja solo candidatos multipalabra;
- `--percentile`: conserva el percentil superior por `terminologicity`;
- `--top-k`: limita el número final de términos;
- `--output`: exporta a CSV;
- `--tbx`: exporta a TBX-Basic.

Opciones de limpieza expuestas en la CLI actual:

- `--structure`
- `--remove-bibliography`
- `--lemmatize`

### Calcular estadísticas de corpus

```bash
tecla stats \
  --corpus _tecla_output/textos/clean/ \
  --lang es \
  --output resultados/corpus_stats.csv
```

### Evaluar contra un gold standard

```bash
tecla evaluate \
  --extracted resultados/terminos.csv \
  --gold gold.csv \
  --mode exact \
  --verbose
```

Modos disponibles:

- `exact`: compara la forma superficial;
- `lemma`: compara por lema, normalmente usando `--extracted-col lemma`.

## Uso rápido desde Python

### Pipeline completo

```python
from pathlib import Path
from pipeline.pipeline import run_tecla_pipeline

results = run_tecla_pipeline(
    corpus_path=Path("corpus"),
    language="es",
    cleaning_options={
        "structure": True,
        "remove_bibliography_flag": True,
        "lemmatize_flag": False,
    },
    extraction_options={
        "multiword_only": True,
        "percentile": 80,
        "max_term_length": 5,
        "weights": {"tfidf": 0.5, "ncvalue": 0.5},
    },
)

for term in results[:10]:
    print(term["term"], term["terminologicity"])
```

### Construir corpus desde TXT

```python
from tecla.corpus.builder import build_corpus_from_txt

build_corpus_from_txt(
    input_folder="corpus",
    out_folder="_tecla_output/textos",
    metadata_file="_tecla_output/metadata.csv",
    clean=True,
    clean_params={"structure": True, "remove_bibliography_flag": True},
)
```

### Extraer con el extractor directamente

```python
from pathlib import Path

from tecla.corpus.processor import corpus_to_documents
from tecla.extractor.hybrid_extractor import HybridTermExtractor

documents = corpus_to_documents(
    corpus_folder="_tecla_output/textos/clean",
    language="es",
    spacy_model="es_core_news_md",
)

extractor = HybridTermExtractor(language="es")
terms = extractor.extract(
    documents,
    percentile=80,
    term_length=(2, 5),
    output_path=Path("resultados/terminos.csv"),
    tbx_output_path=Path("resultados/terminos.tbx"),
)
```

## Flujo de procesamiento

`run_tecla_pipeline(...)` sigue este orden:

1. Detecta si el corpus contiene PDF o TXT.
2. Construye `raw/` y `clean/` en `_tecla_output/textos/`, borrando los de la ejecución anterior.
3. Genera `_tecla_output/metadata.csv`.
4. Detecta la lengua si `language` es `None` o `"auto"`.
5. Convierte los textos limpios en documentos lingüísticamente anotados.
6. Extrae candidatos con patrones POS.
7. Calcula frecuencia, TF-IDF, C-value y `terminologicity`.
8. Filtra artefactos, variantes y stop terms.
9. Devuelve una lista ordenada por `terminologicity`.

## Campos de salida

Los resultados de extracción pueden incluir, entre otros, estos campos:

| Campo | Descripción |
|---|---|
| `term` | forma superficial del candidato |
| `lemma` | forma lematizada o canónica |
| `variants` | variantes ortográficas o abreviadas |
| `language` | lengua del término |
| `length` | longitud en tokens |
| `frequency` | frecuencia absoluta |
| `freq_rel` | frecuencia relativa |
| `doc_frequency` | número de documentos donde aparece |
| `tf_idf` | peso TF-IDF |
| `c_value` | peso C-value |
| `terminologicity` | puntuación compuesta final |
| `patterns` | patrones lingüísticos que dispararon el candidato |

## Limpieza del corpus

La limpieza es modular y no se activa implícitamente. Entre las operaciones soportadas por `tecla.corpus.cleaning` están:

- recomposición de palabras partidas por guion;
- eliminación de líneas cortas o números de página;
- eliminación de referencias bibliográficas;
- eliminación de metadatos editoriales, captions, keywords y URLs;
- eliminación opcional de stopwords;
- lematización con spaCy.

La CLI expone solo una parte de estas opciones. Para control fino, usa la API.

## Gramática POS personalizada

El extractor usa `tecla/extractor/grammar.yaml`. También puedes pasar otra gramática:

```python
from pathlib import Path
from tecla.extractor.hybrid_extractor import HybridTermExtractor

extractor = HybridTermExtractor(
    language="es",
    grammar_path=Path("mi_gramatica.yaml"),
)
```

Ejemplo mínimo:

```yaml
es:
  - id: ES_NP_DE
    description: Sintagma nominal con preposición de
    pos_pattern: "NOUN+ de NOUN+"
```

## Evaluación

TECLA incluye evaluación de extracción y métricas de corpus.

### Evaluación de extracción

`tecla.evaluation.term_eval` calcula:

- `precision`
- `recall`
- `f1`
- `tp`, `fp`, `fn`

Entrada esperada:

- CSV de términos extraídos;
- CSV gold standard;
- columnas configurables, por defecto `term`.

### Estadísticas de corpus

`tecla.corpus.statistics` calcula por documento:

- `token_count`
- `type_count`
- `ttr`
- `hapax_ratio`
- `stopword_ratio`
- `lexical_density`
- `sentence_count`
- `avg_sentence_length`


## GUI

El repositorio incluye una interfaz en `gui/tecla_gui.py` con pestañas de:

- `Corpus`
- `Extracción`
- `Revisión`
- `Evaluación`

Se ejecuta con:

```bash
python gui/tecla_gui.py
```

## Desarrollo

Ejecutar tests:

```bash
pytest
```

Instalar dependencias de desarrollo:

```bash
pip install -e .[dev]
```

## Documentación Sphinx

Fuentes en `docs/source/`.

Construcción local habitual:

```bash
make -C docs html
```

## Licencia

MIT
