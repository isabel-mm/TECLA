# Cambios en TECLA

## 2.1.1

### Correcciones

- **Formas verbales tomadas por términos.** El etiquetador analiza a veces como sustantivo una forma verbal, como *es* en *es decir*, y TECLA la proponía como candidato. Las formas más frecuentes de *ser*, *estar* y *haber* (y de *be*, *have* y *do* en inglés) ya no pueden formar parte de un candidato.
- **Números, abreviaturas y numerales romanos.** Se descartan los candidatos que contienen cifras (años, páginas), abreviaturas con punto (*p.*, *ej.*, *a. C.*), numerales romanos (*siglo XVII*) o palabras propias de las referencias bibliográficas (*cf*, *op. cit.*, *et al.*, *vol.*).
- **Nombres de autores citados.** TECLA reconoce en el propio corpus las citas autor-año, como *Casas Gómez (2006)*, y descarta los candidatos formados solo por esos nombres (*Casas Gómez*, *M. Casas Gómez*). Las siglas y los nombres de recursos, como *British National Corpus*, se conservan.
- **Encabezados y pies de página repetidos.** La limpieza elimina las líneas cortas que se repiten muchas veces en un mismo documento, como el título de un libro o el nombre de su autor en cada página. Además de candidatos falsos, inflaban la frecuencia de las palabras que contienen.
- **Vocabulario académico general.** La lista de exclusión incluye ahora sustantivos generales que el filtro de categorías dejaba pasar: *parte*, *punto*, *modo*, *hecho*, *cosa*, *manera*, *vez*, *lado* y, en inglés, *way*, *fact*, *one*, *thing*, *lot*, *part*, *point*, *sort* y *matter*.

## 2.1.0

### Novedades

- **Ajustes de extracción en una ventana propia.** Las antiguas *Opciones avanzadas* se abren ahora desde un botón visible del panel izquierdo, que resume debajo los ajustes cambiados. Cada opción lleva un signo de interrogación que explica para qué sirve, y la ventana permite restablecer los valores por defecto.
- **Valores numéricos que se escriben.** La frecuencia mínima, la puntuación mínima y la longitud máxima se escriben o se ajustan con los botones − y +, en lugar de con barras deslizantes.
- **Otra lengua en el corpus.** Dos opciones nuevas para los textos con partes en la otra lengua, como los resúmenes en inglés de los artículos en español: descartar los párrafos escritos en ella antes del análisis y excluir los candidatos que contengan sus palabras vacías.
- **Los filtros definen el resultado.** Lo que queda tras los filtros (frecuencia, puntuación, percentil y candidatos monoléxicos) es lo que muestran la tabla, la revisión, la evaluación y los gráficos, y lo que se exporta. Los filtros se aplican al momento, sin volver a ejecutar.
- **Estadísticas del corpus guardadas automáticamente.** En cada ejecución, TECLA guarda la tabla de estadísticas en `_tecla_output/estadisticas_corpus.csv`. La pantalla *Corpus* tiene un botón para abrirla y otro para guardar una copia.
- **Más cifras.** La pantalla *Corpus* añade, para el corpus completo, la media de *tokens* por documento y por oración, la proporción de hápax y la densidad léxica. La pantalla *Extracción* muestra los candidatos que pasan los filtros, los extraídos en total, cuántos son poliléxicos y monoléxicos, y qué proporción aparece en dos o más documentos.
- **Instaladores con nombre fijo.** Los instaladores se llaman `TECLA-instalador-windows-setup.exe` y `TECLA-instalador-macos-arm64.dmg`, de modo que los enlaces de descarga apuntan siempre a la última versión.

### Correcciones

- **Los documentos retirados del corpus se seguían analizando.** TECLA no borraba los textos convertidos en ejecuciones anteriores, así que un documento eliminado de la carpeta `corpus` seguía formando parte del análisis. Ahora esos textos se regeneran en cada ejecución.
- **Los hápax no aparecían nunca.** La extracción descartaba siempre los candidatos de frecuencia 1, de modo que la frecuencia mínima 1 y la casilla *Excluir hápax* no tenían efecto. La frecuencia mínima es ahora 2 por defecto, que da el mismo resultado que antes, y con 1 se incluyen los hápax. La casilla, que ya no hace falta, se ha retirado.
- **La longitud máxima no pasaba de seis palabras**, aunque se indicara un valor mayor. Ahora se respeta hasta quince.
- **Los filtros no llegaban a la revisión ni a la evaluación.** Solo cambiaban la tabla y la exportación; la revisión, la evaluación y los gráficos seguían usando todos los candidatos.
- **Las tildes del CSV de estadísticas se veían mal en Excel.** El archivo se guarda ahora en una codificación que Excel reconoce.
- **TECLA solo trabaja con español e inglés**, pero el código y la documentación mencionaban otras lenguas. Si la detección automática encuentra otra lengua, TECLA lo indica desde el principio, en lugar de fallar más adelante.

### Cambios que afectan a proyectos existentes

- **Nueva carpeta de salida.** Todo lo que genera TECLA se guarda en `_tecla_output`, junto a la carpeta `corpus` y nunca dentro de ella, para que no se lea como parte del corpus. Allí quedan los textos convertidos (`textos/`), `metadata.csv`, las estadísticas, los gráficos, el registro de tiempos, la revisión (`revision.json`) y los metadatos corregidos a mano (`metadatos_documentos.json`).
- La revisión y los metadatos guardados por la versión 2.0 en la carpeta de trabajo (`_tecla_revision.json` y `_tecla_metadata.json`) se siguen leyendo, y a partir de la primera vez que se guardan pasan a `_tecla_output`.
- Las carpetas `corpus/_tecla_txt` y el archivo `corpus/metadata.csv` de la versión 2.0 ya no se usan y pueden borrarse.

## 2.0.0

Primera versión con instaladores para Windows y macOS.
