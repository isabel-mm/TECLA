Uso de la API
=============

Funciones de alto nivel
-----------------------

TECLA expone desde ``tecla`` varios puntos de entrada útiles:

.. code-block:: python

   from tecla import (
       build_corpus,
       build_corpus_from_txt,
       clean_text,
       corpus_statistics,
       infer_metadata,
       detect_language,
       HybridTermExtractor,
       evaluate_extraction,
   )

``build_corpus(...)``
---------------------

Construye un corpus desde PDF:

- descubre PDF;
- infiere metadatos a partir del nombre del archivo;
- convierte PDF a texto;
- aplica limpieza opcional;
- escribe ``raw`` y ``clean``;
- genera ``metadata.csv``;
- puede calcular estadísticas.

``build_corpus_from_txt(...)``
------------------------------

Hace lo mismo, pero partiendo de archivos ``.txt`` y omitiendo la conversión desde PDF.

``HybridTermExtractor``
-----------------------

Es el extractor principal. Combina:

- filtrado lingüístico basado en patrones POS;
- puntuación estadística;
- consolidación y agrupación de variantes.

Ejemplo:

.. code-block:: python

   from pathlib import Path
   from tecla.extractor.hybrid_extractor import HybridTermExtractor

   extractor = HybridTermExtractor(
       language="es",
       grammar_path=Path("mi_gramatica.yaml"),
       weights={"tfidf": 0.6, "cvalue": 0.4},
   )

Parámetros relevantes de ``extract(...)``:

- ``top_k``
- ``percentile``
- ``term_length``
- ``min_freq``
- ``min_doc_freq``
- ``max_span_tokens``
- ``output_path``
- ``tbx_output_path``

``evaluate_extraction(...)``
----------------------------

Evalúa una lista de términos extraídos frente a una lista gold en memoria.

.. code-block:: python

   from tecla import evaluate_extraction

   results = evaluate_extraction(
       extracted=["corpus linguistics", "term extraction"],
       gold=["corpus linguistics", "automatic term extraction"],
       mode="exact",
   )

   print(results["precision"], results["recall"], results["f1"])

Gramática personalizada
-----------------------

La gramática por defecto está en ``tecla/extractor/grammar.yaml``. Puedes usar una propia siempre que mantenga la misma estructura por lengua.

Ejemplo mínimo:

.. code-block:: yaml

   es:
     - id: ES_NP_DE
       description: Sintagma nominal con preposición de
       pos_pattern: "NOUN+ de NOUN+"

Formatos de exportación
-----------------------

- CSV: inventario tabular de candidatos terminológicos.
- TBX-Basic: formato normalizado de intercambio terminológico basado en ISO 30042.
