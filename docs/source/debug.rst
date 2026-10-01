Log de depuración
=================

TECLA escribe automáticamente un archivo ``tecla_debug.txt`` en el directorio de trabajo
cada vez que se lanza el pipeline. El archivo se **añade** en cada ejecución (no se sobreescribe),
lo que permite comparar tiempos entre distintas ejecuciones o corpus.

Formato del log
---------------

Cada entrada tiene la forma::

    FECHA HORA  NIVEL     MENSAJE

Las sesiones están separadas por una línea de cabecera:

.. code-block:: text

    2026-04-29 14:05:01  INFO      ════════════════════════════════════════
    2026-04-29 14:05:01  INFO      NUEVA SESIÓN TECLA  corpus: /mis/pdfs
    2026-04-29 14:05:01  INFO      ════════════════════════════════════════
    2026-04-29 14:05:01  INFO      [INICIO] Conversión PDF→TXT (5 archivos)
    2026-04-29 14:05:07  INFO      [FIN]    Conversión PDF→TXT (5 archivos) — 6.03 s
    2026-04-29 14:05:07  INFO      Lengua detectada: es
    2026-04-29 14:05:07  INFO      [INICIO] Procesamiento spaCy — modelo 'es_core_news_md'
    2026-04-29 14:05:51  INFO      [FIN]    Procesamiento spaCy — modelo 'es_core_news_md' — 44.21 s
    2026-04-29 14:05:51  INFO      Corpus: 12 docs, 187,430 tokens
    2026-04-29 14:05:51  INFO      [INICIO] Extracción de candidatos (percentil=80)
    2026-04-29 14:05:53  INFO      [FIN]    Extracción de candidatos (percentil=80) — 1.87 s
    2026-04-29 14:05:53  INFO      Extracción completada: 312 candidatos

Etapas temporizadas
-------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Etapa
     - Descripción
   * - Conversión PDF→TXT
     - Extracción de texto desde PDF con pdfminer. Puede ser lenta en corpus grandes o PDFs con imágenes.
   * - Limpieza TXT
     - Aplicación de filtros de limpieza sobre texto plano.
   * - Detección de la lengua
     - Identificación automática de la lengua del corpus mediante langid.
   * - Procesamiento spaCy
     - Anotación lingüística completa (tokenización, POS, lematización, dependencias). Suele ser la etapa más lenta, especialmente en corpus de más de 100.000 tokens.
   * - Extracción de candidatos
     - Filtrado POS, cálculo de puntuaciones estadísticas (TF-IDF, C-value) y consolidación de variantes.

Uso desde la API
----------------

El módulo ``tecla.debug`` se puede usar directamente si construyes un pipeline propio:

.. code-block:: python

    from tecla.debug import log, timer, start_session

    start_session("/ruta/al/corpus")

    with timer("Mi etapa personalizada"):
        resultado = mi_funcion_pesada(...)

    log(f"Resultado: {len(resultado)} elementos")

``timer`` es un gestor de contexto que registra el tiempo transcurrido al salir del bloque.
``log`` escribe un mensaje libre en el archivo.
``start_session`` escribe la cabecera de sesión; es opcional pero recomendable.

Localización del archivo
------------------------

``tecla_debug.txt`` se crea en el **directorio de trabajo en el momento de ejecutar el pipeline**,
es decir, el directorio desde el que lanzas Python o desde el que corre la GUI.

Para borrar el historial, elimina el archivo manualmente::

    rm tecla_debug.txt

No se borra automáticamente entre ejecuciones.
