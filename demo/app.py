"""
Demostración en línea de TECLA (Term Extraction and Corpus Linguistics Application).

Ejecuta el mismo flujo que la aplicación de escritorio —limpieza, análisis
lingüístico y extracción de candidatos a término— sobre unos pocos textos.
Es un escaparate: para trabajar con un corpus propio, instala TECLA en tu
ordenador (https://github.com/isabel-mm/TECLA), donde los textos no salen de él.
"""
import csv
import shutil
import tempfile
from pathlib import Path

import gradio as gr

from pipeline.pipeline import run_tecla_pipeline
from tecla.extractor.tbx_export import export_tbx

AQUI = Path(__file__).resolve().parent
EJEMPLOS = AQUI / "ejemplos"

MAX_ARCHIVOS = 20
MAX_BYTES = 3 * 1024 * 1024   # 3 MB en total
MAX_FILAS = 500

PERFILES = {
    "Frecuencia":  {"tfidf": 0.6, "ncvalue": 0.4},
    "Equilibrado": {"tfidf": 0.5, "ncvalue": 0.5},
    "Complejidad": {"tfidf": 0.2, "ncvalue": 0.8},
}
LENGUAS = {"Detección automática": None, "Español": "es", "Inglés": "en"}

COLUMNAS = ["#", "Candidato", "Variantes", "Terminologicidad", "TF-IDF", "C-value",
            "NC-value", "Frecuencia", "Frec. por mil", "Documentos"]
COLUMNAS_DOC = ["Documento", "Tokens", "Oraciones", "Tipos", "TTR"]


def _miles(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def extraer(archivos, ejemplo, lengua, monolexicos, perfil):
    trabajo = Path(tempfile.mkdtemp(prefix="tecla_"))
    corpus = trabajo / "corpus"
    corpus.mkdir()

    if ejemplo != "Cargar textos propios":
        origen = EJEMPLOS / ("en" if "inglés" in ejemplo else "es")
        rutas = sorted(origen.glob("*.txt"))
        lengua = "Inglés" if "inglés" in ejemplo else "Español"
    else:
        rutas = [Path(f if isinstance(f, str) else f.name) for f in (archivos or [])]

    if not rutas:
        raise gr.Error("Sube al menos un texto (TXT o PDF) o elige los textos de ejemplo.")
    if len(rutas) > MAX_ARCHIVOS:
        raise gr.Error(f"La demostración admite hasta {MAX_ARCHIVOS} archivos.")
    if sum(r.stat().st_size for r in rutas) > MAX_BYTES:
        raise gr.Error("La demostración admite hasta 3 MB en total. "
                       "Para corpus mayores, instala TECLA en tu ordenador.")
    for r in rutas:
        shutil.copy(r, corpus / r.name)

    documentos = []
    resultados = run_tecla_pipeline(
        corpus_path=corpus,
        language=LENGUAS[lengua],
        cleaning_options={
            "structure": True,
            "remove_bibliography_flag": True,
            "remove_captions_flag": True,
            "remove_section_headers_flag": True,
        },
        extraction_options={
            "multiword_only": not monolexicos,
            "max_term_length": 5,
            "weights": PERFILES[perfil],
        },
        on_corpus_ready=lambda docs, carpeta, lang: documentos.extend(docs),
    )
    if not resultados:
        raise gr.Error("No se ha extraído ningún candidato. Comprueba la lengua y los textos.")

    resultados.sort(key=lambda t: -t["terminologicity"])

    filas_doc, total_tokens, lemas = [], 0, set()
    for d in documentos:
        tipos = {t["lemma"] for t in d["tokens"]}
        n = len(d["tokens"])
        total_tokens += n
        lemas |= tipos
        filas_doc.append([d["doc_id"], n, len(d.get("sentences", [])), len(tipos),
                          round(len(tipos) / n, 4) if n else 0])

    filas = [[i, t["lemma"], " · ".join(t.get("variants", [])) or "—",
              round(t["terminologicity"], 4), round(t.get("tf_idf", 0), 2),
              round(t.get("c_value", 0), 2), round(t.get("nc_value", 0), 2),
              t["frequency"], round(t.get("freq_rel", 0), 2), t["doc_frequency"]]
             for i, t in enumerate(resultados[:MAX_FILAS], 1)]

    ruta_csv = trabajo / "candidatos_tecla.csv"
    campos = ["term", "lemma", "variants", "patterns", "terminologicity", "tf_idf",
              "c_value", "nc_value", "frequency", "freq_rel", "doc_frequency"]
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for t in resultados:
            fila = {k: t.get(k, "") for k in campos}
            fila["patterns"] = ";".join(t.get("patterns", []))
            fila["variants"] = ";".join(t.get("variants", []))
            w.writerow(fila)
    ruta_tbx = trabajo / "candidatos_tecla.tbx"
    export_tbx(resultados, ruta_tbx, language=LENGUAS[lengua] or "en")

    resumen = (f"**{_miles(len(documentos))}** documentos · **{_miles(total_tokens)}** tokens · "
               f"**{_miles(len(lemas))}** tipos · **{_miles(len(resultados))}** candidatos a término")
    if len(resultados) > MAX_FILAS:
        resumen += f" (se muestran los {MAX_FILAS} primeros; el CSV los incluye todos)"
    return resumen, filas, filas_doc, str(ruta_csv), str(ruta_tbx)


tema = gr.themes.Soft(primary_hue="violet", secondary_hue="teal", neutral_hue="slate")

with gr.Blocks(theme=tema, title="TECLA · demostración") as demo:
    gr.Markdown(
        "# TECLA\n"
        "**Term Extraction and Corpus Linguistics Application** · demostración en línea\n\n"
        "TECLA extrae candidatos a término de un corpus especializado combinando patrones "
        "gramaticales y medidas estadísticas (*TF-IDF*, *C-value*, *NC-value*). Esta página "
        "ejecuta el mismo procedimiento que la aplicación de escritorio sobre unos pocos textos.\n\n"
        "> **Los textos que subas se procesan en un servidor externo.** No subas documentos "
        "confidenciales ni sujetos a derechos de autor. Para trabajar con tu propio corpus, "
        "[instala TECLA en tu ordenador](https://github.com/isabel-mm/TECLA): ahí los textos no salen de él."
    )
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            ejemplo = gr.Radio(
                ["Textos de ejemplo (inglés)", "Textos de ejemplo (español)", "Cargar textos propios"],
                value="Textos de ejemplo (inglés)", label="Corpus",
                info="Los textos de ejemplo son seis textos de prueba sobre lingüística de corpus, "
                     "ficticios y generados con inteligencia artificial (Claude).")
            archivos = gr.File(label="Textos propios (TXT o PDF)", file_count="multiple",
                               file_types=[".txt", ".pdf"], visible=False)
            lengua = gr.Radio(list(LENGUAS), value="Detección automática", label="Lengua")
            monolexicos = gr.Checkbox(value=True, label="Incluir candidatos monoléxicos")
            perfil = gr.Radio(list(PERFILES), value="Equilibrado", label="Perfil de puntuación",
                              info="Peso del TF-IDF frente al NC-value: 0,6 / 0,5 / 0,2.")
            boton = gr.Button("▶ Ejecutar", variant="primary")
        with gr.Column(scale=3):
            resumen = gr.Markdown("Elige un corpus y pulsa **Ejecutar**.")
            with gr.Tab("Candidatos a término"):
                tabla = gr.Dataframe(headers=COLUMNAS, interactive=False, wrap=True)
            with gr.Tab("Corpus"):
                tabla_doc = gr.Dataframe(headers=COLUMNAS_DOC, interactive=False)
            with gr.Row():
                salida_csv = gr.File(label="Candidatos (CSV)")
                salida_tbx = gr.File(label="Candidatos (TBX-Basic)")

    ejemplo.change(lambda e: gr.update(visible=e == "Cargar textos propios"), ejemplo, archivos)
    boton.click(extraer, [archivos, ejemplo, lengua, monolexicos, perfil],
                [resumen, tabla, tabla_doc, salida_csv, salida_tbx])

    gr.Markdown(
        "La evaluación de la representatividad del corpus y la revisión de los candidatos "
        "están en la aplicación de escritorio. Código y documentación: "
        "[github.com/isabel-mm/TECLA](https://github.com/isabel-mm/TECLA) · Licencia MIT."
    )

if __name__ == "__main__":
    demo.launch()
