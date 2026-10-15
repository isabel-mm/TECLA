Inicio Rápido
=============

Instalación
-----------

Instala TECLA en modo editable:

.. code-block:: bash

   pip install -e .

Para desarrollo:

.. code-block:: bash

   pip install -e .[dev]

Instala también los modelos spaCy necesarios para tu lengua:

.. code-block:: bash

   python -m spacy download es_core_news_md
   python -m spacy download en_core_web_lg

Uso desde la CLI
----------------

La CLI se instala como ``tecla``:

.. code-block:: bash

   tecla --help

También puede ejecutarse como módulo:

.. code-block:: bash

   python -m tecla --help

Extraer términos
^^^^^^^^^^^^^^^^

.. code-block:: bash

   tecla extract \
     --corpus corpus/ \
     --lang es \
     --multiword \
     --percentile 80 \
     --output resultados/terminos.csv \
     --tbx resultados/terminos.tbx

Calcular estadísticas de corpus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   tecla stats \
     --corpus _tecla_output/textos/clean/ \
     --lang es \
     --output resultados/corpus_stats.csv

Evaluar frente a un gold standard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   tecla evaluate \
     --extracted resultados/terminos.csv \
     --gold gold.csv \
     --mode lemma \
     --extracted-col lemma \
     --verbose

Uso desde Python
----------------

Pipeline completo
^^^^^^^^^^^^^^^^^

.. code-block:: python

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
           "weights": {"tfidf": 0.6, "cvalue": 0.4},
       },
   )

   for term in results[:10]:
       print(term["term"], term["terminologicity"])

Extractor directo
^^^^^^^^^^^^^^^^^

.. code-block:: python

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

Consejos de uso
---------------

- Usa ``language="auto"`` si el corpus es monolingüe pero no quieres fijar la lengua manualmente.
- Usa ``--multiword`` o ``term_length=(2, ...)`` si buscas unidades terminológicas multipalabra.
- Usa una gramática POS propia si trabajas con un dominio muy especializado.
- Para control detallado de limpieza, usa la API en lugar de la CLI.
