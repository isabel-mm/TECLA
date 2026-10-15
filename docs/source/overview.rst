Visión General
===============

TECLA es una herramienta para terminología basada en corpus. Su objetivo es cubrir el flujo completo de trabajo: partir de un conjunto de documentos, convertirlos a texto procesable, limpiarlos, extraer candidatos terminológicos y evaluar los resultados.

Capacidades principales
-----------------------

- Construcción de corpus desde PDF o TXT.
- Limpieza opcional del texto y supresión de ruido estructural.
- Detección automática de la lengua.
- Extracción híbrida mediante patrones POS y puntuación estadística.
- Exportación a CSV y TBX-Basic.
- Estadísticas descriptivas del corpus.
- Evaluación frente a un gold standard.

Arquitectura del proyecto
-------------------------

El repositorio se organiza en varios módulos:

- ``tecla.corpus``: construcción del corpus, limpieza, metadatos, estadísticas y detección de la lengua.
- ``tecla.extractor``: filtrado lingüístico, puntuación estadística, consolidación de términos y exportación TBX.
- ``tecla.evaluation``: evaluación de extracción y métricas de corpus.
- ``pipeline.pipeline``: orquestación del flujo completo.
- ``gui/tecla_gui.py``: interfaz gráfica.

Flujo del pipeline
------------------

``run_tecla_pipeline(...)`` sigue este orden:

1. Detecta si la carpeta de entrada contiene PDF o TXT.
2. Genera ``_tecla_txt/raw`` y ``_tecla_txt/clean``.
3. Produce ``metadata.csv``.
4. Detecta la lengua si el usuario no la indica.
5. Crea representaciones lingüísticas con spaCy.
6. Extrae candidatos mediante gramática POS.
7. Calcula frecuencia, TF-IDF, C-value y ``terminologicity``.
8. Filtra artefactos y stop terms, y agrupa variantes.
9. Devuelve un ranking final de términos.

Modelos lingüísticos
--------------------

TECLA trabaja con textos en español y en inglés, y resuelve automáticamente el modelo spaCy a partir de la lengua:

.. list-table::
   :header-rows: 1

   * - Lengua
     - Modelo
   * - ``en``
     - ``en_core_web_lg``
   * - ``es``
     - ``es_core_news_md``

Si un modelo no está instalado, TECLA intenta descargarlo. Si eso falla, usa un modelo ``blank`` de spaCy. Ese fallback mantiene la ejecución, pero reduce la calidad del etiquetado POS y, por extensión, la calidad de la extracción.

Estructura esperada del corpus
------------------------------

Ejemplo de carpeta de trabajo:

.. code-block:: text

   corpus/
   ├── articulo_01.pdf
   ├── articulo_02.pdf
   ├── articulo_03.txt
   ├── metadata.csv
   └── _tecla_txt/
       ├── raw/
       └── clean/

Cuando el corpus contiene PDF, TECLA realiza la conversión a texto. Si contiene TXT, omite esa fase y empieza en la limpieza.

Salidas de extracción
---------------------

Los resultados devueltos por el extractor incluyen campos como:

- ``term``
- ``lemma``
- ``variants``
- ``language``
- ``length``
- ``frequency``
- ``freq_rel``
- ``doc_frequency``
- ``tf_idf``
- ``c_value``
- ``terminologicity``
- ``patterns``

Estos campos pueden exportarse a CSV o TBX-Basic.
