CLI
===

TECLA instala un ejecutable llamado ``tecla`` definido en ``pyproject.toml``:

.. code-block:: bash

   tecla --help

Subcomando ``extract``
----------------------

Extrae términos de una carpeta con PDF o TXT.

.. code-block:: bash

   tecla extract --corpus corpus/ --lang es --output terminos.csv

Argumentos:

- ``--corpus``: carpeta del corpus.
- ``--lang``: lengua, por ejemplo ``es`` o ``en``.
- ``--output``: ruta de salida CSV.
- ``--tbx``: ruta de salida TBX.
- ``--top-k``: número máximo de términos devueltos.
- ``--percentile``: conserva solo el percentil superior del ranking.
- ``--multiword``: restringe la salida a términos de dos o más tokens.
- ``--structure``: activa limpieza estructural.
- ``--remove-bibliography``: elimina la bibliografía del texto.
- ``--lemmatize``: activa lematización durante la limpieza.
- ``--tfidf-weight``: peso de TF-IDF en la combinación final. El peso de C-value se calcula como ``1.0 - tfidf_weight``.

Observaciones:

- La CLI actual pasa el corpus al pipeline general. Si hay PDF, se convierten primero; si hay TXT, se procesan directamente.
- El ranking final se ordena por ``terminologicity``.

Subcomando ``stats``
--------------------

Calcula estadísticas descriptivas para una carpeta de TXT.

.. code-block:: bash

   tecla stats --corpus corpus/_tecla_txt/clean/ --lang es --output stats.csv

Argumentos:

- ``--corpus``: carpeta con archivos ``.txt``.
- ``--lang``: lengua usada para recuperar las palabras vacías.
- ``--output``: CSV de salida opcional.

Campos de salida:

- ``token_count``
- ``type_count``
- ``ttr``
- ``hapax_ratio``
- ``stopword_ratio``
- ``lexical_density``
- ``sentence_count``
- ``avg_sentence_length``

Subcomando ``evaluate``
-----------------------

Evalúa una extracción frente a un gold standard.

.. code-block:: bash

   tecla evaluate --extracted terminos.csv --gold gold.csv --mode exact

Argumentos:

- ``--extracted``: CSV con la extracción.
- ``--gold``: CSV con la lista de referencia.
- ``--extracted-col``: columna del CSV de extracción, por defecto ``term``.
- ``--gold-col``: columna del gold standard, por defecto ``term``.
- ``--mode``: ``exact`` o ``lemma``.
- ``--verbose``: imprime falsos negativos.

Nota:

- Si usas ``--mode lemma``, normalmente también debes indicar ``--extracted-col lemma`` para que la comparación use la columna lematizada del CSV.

Salida esperada:

- ``precision``
- ``recall``
- ``f1``
- ``tp``
- ``fp``
- ``fn``

Ejemplo completo
----------------

.. code-block:: bash

   tecla extract \
     --corpus corpus/ \
     --lang es \
     --multiword \
     --percentile 80 \
     --output resultados/terminos.csv \
     --tbx resultados/terminos.tbx

   tecla evaluate \
     --extracted resultados/terminos.csv \
     --gold gold.csv \
     --mode exact
