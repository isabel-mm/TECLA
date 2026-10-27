import csv
import json
import os
import re
from datetime import datetime
import sys
import threading
from collections import Counter
from pathlib import Path

# El ejecutable empaquetado no tiene consola: sin salida estándar, tqdm falla
for _stream in ("stdout", "stderr"):
    if getattr(sys, _stream) is None:
        setattr(sys, _stream, open(os.devnull, "w", encoding="utf-8"))

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from pipeline.pipeline import run_tecla_pipeline
from tecla.extractor.hybrid_extractor import (classify_variant, display_form, lemma_key,
                                              surface_forms, variants_summary)

# ─────────────────────────────────────────────
# Tema y constantes
# ─────────────────────────────────────────────

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── Paleta violeta (la de la web de GLiCor) ──
_ACCENT        = "#7c3aed"   # violeta (resalte principal, botones con texto blanco)
_ACCENT_DIM    = "#6d28d9"   # violeta oscuro (hover)
_ACCENT2       = "#6d28d9"   # violeta oscuro (resalte secundario, botones de contorno)
_TEAL          = "#0d9488"   # verde azulado (pasos completados)
_BG_ROOT       = "#fbfaff"   # fondo general
_BG_CARD       = "#ffffff"   # tarjetas
_BG_CARD2      = "#f5f3ff"   # cabeceras / campos (lavanda)
_BG_LOG        = "#1e1b4b"   # log (terminal oscuro)
_BORDER        = "#e2e8f0"   # bordes suaves
_TEXT          = "#1e1b4b"   # texto principal
_TEXT_MUTED    = "#64748b"   # texto atenuado
_SEG_TEXT      = "#1e1b4b"   # texto en botones segmentados sin seleccionar
_SEG_SELECTED  = "#7c3aed"   # fondo seleccionado en botones segmentados
_SEG_SEL_HOV   = "#6d28d9"   # hover del estado seleccionado
_TEXT_LOG      = "#c4b5fd"   # texto del log
_ROW_ODD       = "#ffffff"
_ROW_EVEN      = "#f8f6ff"
_INFO          = "#4338ca"   # índigo: avisos informativos (no errores)
_INFO_DIM      = "#3730a3"
_STATUS_COLOR  = {"pendiente": "#64748b", "aprobado": "#16a34a", "rechazado": "#dc2626"}

# ── Sidebar (panel lateral lavanda) ──
_SB_BG         = "#f5f3ff"   # fondo sidebar
_SB_SECTION    = "#ede9fe"   # hover / bandas
_SB_TEXT       = "#1e1b4b"   # texto sidebar
_SB_MUTED      = "#64748b"   # texto atenuado sidebar
_SB_BORDER     = "#ddd6fe"   # bordes sidebar (lavanda)
_STEP_PENDING  = "#c4b5fd"   # contorno de los pasos aún no recorridos

_SESSION_FILE  = Path.home() / ".tecla_session.json"
_OUTPUT_DIR    = "_tecla_output"   # lo que genera TECLA, junto a la carpeta «corpus»

# Valores por defecto de los ajustes de extracción
_DEFAULTS = {"max_len": 5, "min_freq": 2, "min_score": 0.0}
_PCT_MAP  = {"—": 0, "p25": 25, "p50": 50, "p75": 75, "p90": 90}
# Recursos gráficos (en el ejecutable empaquetado se sirven desde sys._MEIPASS)
_ASSETS        = Path(getattr(sys, "_MEIPASS", _PROJECT_ROOT)) / "gui" / "assets"

_WEIGHT_PRESETS = {
    "Frecuencia":  {"tfidf": 0.6, "ncvalue": 0.4},
    "Equilibrado": {"tfidf": 0.5, "ncvalue": 0.5},
    "Complejidad": {"tfidf": 0.2, "ncvalue": 0.8},
}
_PRESET_HINTS = {
    "Frecuencia":  "Términos que aparecen mucho a lo largo del corpus.",
    "Equilibrado": "Combina frecuencia y patrón gramatical.",
    "Complejidad": "Términos técnicos largos y anidados.",
}

_METRIC_HELP = {
    "Score": "Terminologicidad: índice de 0 a 1 que combina el TF-IDF y el NC-value según el "
             "perfil elegido (por defecto, a partes iguales). Ordena los candidatos de más a menos "
             "característicos del dominio. No es un umbral: sirve para decidir qué revisar primero.",
    "TF-IDF": "Frecuencia del candidato multiplicada por la frecuencia inversa de documento. "
              "Es alto si el candidato es frecuente y se concentra en algunos documentos, y más "
              "bajo si aparece en casi todos, como las palabras generales.",
    "C-val": "C-value: combina la frecuencia y la longitud del candidato, y descuenta las veces "
             "que aparece dentro de candidatos más largos. Penaliza los fragmentos que casi solo "
             "aparecen formando parte de otra unidad.",
    "NC-val": "NC-value: el C-value ajustado con las palabras que suelen rodear a los términos del "
              "corpus. Favorece a los candidatos que aparecen en contextos típicos de términos.",
    "Frec": "Número de veces que aparece el candidato en el corpus, contando todas sus variantes.",
    "Frec/mil": "Frecuencia relativa: apariciones por cada mil palabras del corpus. Permite "
                "comparar corpus de distinto tamaño.",
    "Docs": "Número de documentos en que aparece. Un término repartido por muchos documentos "
            "suele estar más asentado que uno que solo emplea un autor.",
    "Autores": "Número de autores distintos que emplean el candidato, según los metadatos de los "
               "documentos o su nombre de archivo («Autor_Año_Título»). Si todas sus apariciones "
               "están en textos de un mismo autor, puede tratarse de un uso propio de ese autor "
               "y no de un término asentado en la comunidad.",
}

_EVAL_TESTS_HELP = (
    "Cada prueba mide un aspecto del corpus y se puntúa de 0 a 100; el índice es su media.\n\n"
    "Saturación: exponente de la ley de Heaps. Cuanto más bajo, antes deja de crecer el "
    "vocabulario al añadir textos.\n\n"
    "Hápax: proporción de palabras distintas que aparecen una sola vez. Una proporción alta "
    "indica que aún faltan textos.\n\n"
    "Dispersión: DP medio de los candidatos (0 = repartidos por todo el corpus; 1 = "
    "concentrados en un documento).\n\n"
    "Estabilidad: proporción de los candidatos principales que se mantienen al remuestrear "
    "los documentos. Indica si el resultado depende de qué textos concretos forman el corpus."
)

_CONC_MAX = 500   # concordancias que se muestran por candidato (el CSV las exporta todas)

_SORT_KEY_MAP = {
    "Score":    "terminologicity",
    "TF-IDF":   "tf_idf",
    "C-val":    "c_value",
    "NC-val":   "nc_value",
    "Frec":     "frequency",
    "Frec/mil": "freq_rel",
    "Docs":     "doc_frequency",
    "Candidato": "term",
}


# ─────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────


def _placeholder(parent, text: str):
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=13), text_color=_TEXT_MUTED,
    ).pack(expand=True)


class _Tooltip:
    """Pequeño popup de ayuda que aparece al pasar el ratón."""
    def __init__(self, widget, text: str):
        self._widget = widget
        self._text   = text
        self._tw     = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _=None):
        try:
            x = self._widget.winfo_rootx() + self._widget.winfo_width() + 8
            y = self._widget.winfo_rooty() - 2
        except Exception:
            return
        self._tw = tk.Toplevel(self._widget)
        self._tw.wm_overrideredirect(True)
        self._tw.wm_geometry(f"+{x}+{y}")
        self._tw.configure(bg="#fffde7")
        tk.Label(
            self._tw, text=self._text, justify="left",
            background="#fffde7", foreground="#1a1d35",
            relief="solid", borderwidth=1,
            font=("", 10), wraplength=320, padx=10, pady=8,
        ).pack()

    def _hide(self, _=None):
        if self._tw:
            try:
                self._tw.destroy()
            except Exception:
                pass
            self._tw = None


def _help_icon(parent, tooltip_text: str) -> ctk.CTkLabel:
    """Icono '?' con tooltip al pasar el ratón."""
    lbl = ctk.CTkLabel(
        parent, text="?",
        font=ctk.CTkFont(size=9, weight="bold"),
        text_color="#ffffff",
        fg_color=_ACCENT,
        width=16, height=16,
        corner_radius=8,
        cursor="question_arrow",
    )
    _Tooltip(lbl, tooltip_text)
    return lbl


class _NumberField(ctk.CTkFrame):
    """Campo numérico con botones − y +; el valor también se puede escribir."""

    def __init__(self, master, variable, minimum, maximum, step=1, decimals=0,
                 command=None):
        super().__init__(master, fg_color="transparent")
        self._var, self._min, self._max = variable, minimum, maximum
        self._step, self._decimals, self._command = step, decimals, command
        button = dict(width=28, height=28, corner_radius=6, fg_color=_BG_CARD,
                      hover_color=_SB_SECTION, border_width=1, border_color=_SB_BORDER,
                      text_color=_ACCENT, font=ctk.CTkFont(size=15, weight="bold"))
        ctk.CTkButton(self, text="−", command=lambda: self._bump(-1), **button).pack(side="left")
        self._entry = ctk.CTkEntry(self, width=64, height=28, justify="center",
                                   fg_color=_BG_CARD, border_color=_SB_BORDER,
                                   text_color=_SB_TEXT, font=ctk.CTkFont(size=13))
        self._entry.pack(side="left", padx=4)
        ctk.CTkButton(self, text="+", command=lambda: self._bump(1), **button).pack(side="left")
        self._entry.bind("<Return>", self._commit)
        self._entry.bind("<FocusOut>", self._commit)
        variable.trace_add("write", lambda *_: self._show())
        self._show()

    def _show(self):
        value = self._var.get()
        self._entry.delete(0, "end")
        self._entry.insert(0, f"{value:.{self._decimals}f}" if self._decimals else str(int(value)))

    def _set(self, value):
        value = min(self._max, max(self._min, value))
        value = round(value, self._decimals) if self._decimals else int(round(value))
        changed = value != self._var.get()
        self._var.set(value)
        self._show()
        if changed and self._command:
            self._command()

    def _bump(self, direction):
        self._set(self._var.get() + direction * self._step)

    def _commit(self, _=None):
        try:
            self._set(float(self._entry.get().replace(",", ".")))
        except ValueError:
            self._show()


def _tab_header(tab, title: str, description: str):
    """Encabezado estándar para cada pestaña: título + descripción muted."""
    hdr = ctk.CTkFrame(tab, fg_color="transparent")
    hdr.pack(fill="x", padx=18, pady=(14, 2))
    ctk.CTkLabel(hdr, text=title,
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color=_TEXT, anchor="w").pack(side="left")
    ctk.CTkLabel(tab, text=description,
                 font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED,
                 anchor="w").pack(fill="x", padx=18, pady=(0, 8))


def _miles(n) -> str:
    """Entero con separador de millares (espacio)."""
    return f"{int(n):,}".replace(",", " ")


def _stat_cards(parent, items) -> dict:
    """Fila de tarjetas de cifras. Devuelve {clave: etiqueta del valor}."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=18, pady=(4, 8))
    labels = {}
    for i, (key, caption) in enumerate(items):
        row.grid_columnconfigure(i, weight=1, uniform="cifra")
        card = ctk.CTkFrame(row, fg_color=_BG_CARD, corner_radius=10,
                            border_width=1, border_color=_BORDER)
        card.grid(row=0, column=i, sticky="ew",
                  padx=(0 if i == 0 else 6, 0 if i == len(items) - 1 else 6))
        val = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=20, weight="bold"),
                           text_color=_TEXT, anchor="w")
        val.pack(fill="x", padx=14, pady=(10, 0))
        ctk.CTkLabel(card, text=caption, font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, anchor="w").pack(fill="x", padx=14, pady=(0, 10))
        labels[key] = val
    return labels


class _Segmented(ctk.CTkFrame):
    """Selector segmentado: la opción elegida en violeta con texto blanco."""

    def __init__(self, master, values, variable=None, command=None, font=None,
                 labels=None, **_ignored):
        super().__init__(master, fg_color=_BG_CARD, corner_radius=8,
                         border_width=1, border_color=_SB_BORDER)
        self._var, self._command, self._btns = variable, command, {}
        self._value = variable.get() if variable is not None else None
        for i, v in enumerate(values):
            self.grid_columnconfigure(i, weight=1)
            btn = ctk.CTkButton(self, text=(labels or {}).get(v, v), width=10, height=26,
                                corner_radius=6, font=font or ctk.CTkFont(size=12),
                                command=lambda v=v: self._pick(v))
            btn.grid(row=0, column=i, sticky="ew", pady=3,
                     padx=(3 if i == 0 else 1, 3 if i == len(values) - 1 else 1))
            self._btns[v] = btn
        if variable is not None:
            variable.trace_add("write", lambda *_: self._paint(variable.get()))
        self._paint(self._value)

    def _pick(self, value):
        self.set(value)
        if self._command:
            self._command(value)

    def set(self, value):
        if self._var is not None and self._var.get() != value:
            self._var.set(value)
        self._paint(value)

    def get(self):
        return self._value

    def _paint(self, value):
        self._value = value
        for v, btn in self._btns.items():
            on = v == value
            btn.configure(fg_color=_SEG_SELECTED if on else "transparent",
                          hover_color=_SEG_SEL_HOV if on else _SB_SECTION,
                          text_color="#ffffff" if on else _SEG_TEXT)


class _StepView(ctk.CTkFrame):
    """Pasos numerados del flujo de trabajo (1 Corpus → 2 Extracción → …).

    Sustituye a las pestañas: el paso actual va en violeta y los completados,
    en verde azulado con una marca."""

    def __init__(self, master):
        super().__init__(master, fg_color=_BG_ROOT, corner_radius=0)
        bar = ctk.CTkFrame(self, fg_color=_BG_CARD, corner_radius=10,
                           border_width=1, border_color=_BORDER)
        bar.pack(fill="x", padx=18, pady=(14, 0))
        self._bar = ctk.CTkFrame(bar, fg_color="transparent")
        self._bar.pack(fill="x", padx=14, pady=9)
        self._body = ctk.CTkFrame(self, fg_color=_BG_ROOT, corner_radius=0)
        self._body.pack(fill="both", expand=True)
        self._names, self._frames, self._steps, self._lines = [], {}, {}, []
        self._done, self._current = set(), None

    def add(self, name: str):
        if self._names:
            line = ctk.CTkFrame(self._bar, width=24, height=2, fg_color=_BORDER, corner_radius=0)
            line.pack(side="left", fill="x", expand=True, padx=12)
            self._lines.append(line)
        self._names.append(name)
        go = lambda n=name: self.set(n)
        circle = ctk.CTkButton(self._bar, text=str(len(self._names)), width=26, height=26,
                               corner_radius=13, border_width=2,
                               font=ctk.CTkFont(size=12, weight="bold"), command=go)
        circle.pack(side="left")
        label = ctk.CTkButton(self._bar, text=name, width=10, height=26,
                              fg_color="transparent", hover_color=_BG_CARD2,
                              font=ctk.CTkFont(size=13), command=go)
        label.pack(side="left", padx=(4, 0))
        self._steps[name] = (circle, label)
        self._frames[name] = ctk.CTkFrame(self._body, fg_color=_BG_ROOT, corner_radius=0)
        if self._current is None:
            self.set(name)
        else:
            self._refresh()
        return self._frames[name]

    def tab(self, name: str):
        return self._frames[name]

    def get(self) -> str:
        return self._current

    def set(self, name: str):
        if self._current is not None:
            self._frames[self._current].pack_forget()
        self._current = name
        self._frames[name].pack(fill="both", expand=True)
        self._refresh()

    def mark_done(self, name: str, done: bool = True):
        (self._done.add if done else self._done.discard)(name)
        self._refresh()

    def _refresh(self):
        for i, name in enumerate(self._names):
            circle, label = self._steps[name]
            current, done = name == self._current, name in self._done
            if current:
                circle.configure(text=str(i + 1), fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                                 border_color=_ACCENT, text_color="#ffffff")
            elif done:
                circle.configure(text="✓", fg_color=_TEAL, hover_color=_TEAL,
                                 border_color=_TEAL, text_color="#ffffff")
            else:
                circle.configure(text=str(i + 1), fg_color=_BG_CARD, hover_color=_BG_CARD2,
                                 border_color=_STEP_PENDING, text_color=_TEXT_MUTED)
            label.configure(text_color=_TEXT if (current or done) else _TEXT_MUTED,
                            font=ctk.CTkFont(size=13, weight="bold" if current else "normal"))
            if i < len(self._lines):
                self._lines[i].configure(fg_color=_TEAL if done else _BORDER)


# ─────────────────────────────────────────────
# Aplicación
# ─────────────────────────────────────────────

class TeclaApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("TECLA")
        try:
            self._icon = tk.PhotoImage(file=str(_ASSETS / "logo.png"))
            self.iconphoto(True, self._icon)
        except Exception:
            pass   # sin icono, la ventana usa el del sistema
        self.geometry("1420x800")
        self.minsize(1100, 640)
        self.configure(fg_color=_BG_ROOT)

        # ── Config extracción ──
        self.corpus_path_var    = ctk.StringVar(value="")   # directorio de trabajo
        self.grammar_path_var   = ctk.StringVar(value="")
        self.language_var       = ctk.StringVar(value="es")
        self._include_mono_var  = ctk.BooleanVar(value=False)

        self.weight_preset      = ctk.StringVar(value="Equilibrado")

        # ── Ajustes de extracción (ventana aparte) ──
        # Los filtros se aplican al momento; el resto, al volver a ejecutar.
        self.max_term_length_var = ctk.IntVar(value=_DEFAULTS["max_len"])
        self._min_freq_var      = ctk.IntVar(value=_DEFAULTS["min_freq"])
        self._min_score_var     = ctk.DoubleVar(value=_DEFAULTS["min_score"])
        self._percentile_choice = ctk.StringVar(value="—")
        self._drop_other_var    = ctk.BooleanVar(value=False)
        self._other_sw_var      = ctk.BooleanVar(value=False)
        self._stoplist_var      = ctk.StringVar(value="")
        self._settings_win      = None
        self._running         = False

        # ── Datos post-extracción ──
        self._all_results    = []     # CTs completos del pipeline
        self._results        = []     # CTs que pasan los filtros: el resultado
        self._results_data   = []     # filtrados+ordenados (para display)
        self._results_job    = None   # actualización diferida tras cambiar filtros
        self._doc_stats      = []     # [{doc_id, tokens, sentences, types}]
        self._documents      = []     # documentos enriquecidos (para evaluación)
        self._clean_folder   = ""
        self._corpus_types   = 0      # tipos (lemas distintos) del corpus completo
        self._corpus_summary = {}     # hápax, densidad léxica… del corpus completo

        # ── Evaluación ──
        self._eval_running   = False
        self._eval_dp_scores = {}     # lemma → DP score
        self._eval_btn       = None   # se asigna al construir el tab
        self._eval_done      = False

        # ── Cobertura externa (lista de referencia opcional) ──
        self._gold_terms     = []     # lista de términos del glosario cargado
        self._gold_path      = None   # Path del CSV cargado

        # ── Metadatos del corpus ──
        self._corpus_metadata   = {}   # doc_id → {autor, año, tema, fuente, notas}
        self._meta_selected_doc = None

        # ── Ordenación ──
        self._sort_key_var   = ctk.StringVar(value="Score")
        self._sort_reverse   = True

        # ── Columnas visibles en la tabla de CTs ──
        self._col_visible = {}   # col_id → BooleanVar

        # ── Revisión ──
        self._review_data    = {}     # CT → {status, notes}
        self._rev_selected   = None
        self._rev_term_btns  = {}     # CT → botón
        self._rev_more_label = None   # aviso de candidatos no mostrados
        self._conc_texts     = None   # textos del corpus para las concordancias
        self._conc_loading   = False
        self._conc_cache     = {}     # CT → [(documento, inicio, fin)]
        self._conc_doc_map   = {}
        self._eval_raw       = {}     # datos brutos de la evaluación (tabla y CSV)
        self._eval_rep       = None
        self._eval_stab      = None

        self._build_ui()
        self._load_session()
        self.after(700, self._offer_resume)

    # ═══════════════════════════════════════════
    # Layout principal
    # ═══════════════════════════════════════════

    def _build_ui(self):
        self._sidebar = ctk.CTkFrame(self, width=290, fg_color=_SB_BG, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Línea separadora entre sidebar y contenido
        ctk.CTkFrame(self, width=1, fg_color=_BORDER, corner_radius=0).pack(side="left", fill="y")

        self._tabview = _StepView(self)
        self._tabview.pack(side="right", fill="both", expand=True)

        for name in ("Corpus", "Extracción", "Evaluación", "Revisión"):
            self._tabview.add(name)

        # Definir estilo de Treeview una sola vez (compartido por todas las tablas)
        tree_style = ttk.Style()
        tree_style.theme_use("clam")
        tree_style.configure("TECLA.Treeview",
                             background=_BG_CARD, foreground=_TEXT,
                             fieldbackground=_BG_CARD,
                             bordercolor=_BORDER, lightcolor=_BORDER, darkcolor=_BORDER,
                             rowheight=30, font=("", 11))
        tree_style.configure("TECLA.Treeview.Heading",
                             background=_BG_CARD2, foreground=_TEXT_MUTED,
                             relief="flat", font=("", 10, "bold"), bordercolor=_BORDER)
        tree_style.map("TECLA.Treeview",
                       background=[("selected", _SB_SECTION)],
                       foreground=[("selected", _TEXT)])
        tree_style.map("TECLA.Treeview.Heading",
                       background=[("active", _BG_CARD)])

        self._build_sidebar()
        self._build_tab_corpus()
        self._build_tab_extraccion()
        self._build_tab_evaluacion()
        self._build_tab_revision()
        self._add_next_buttons()


    # ═══════════════════════════════════════════
    # Sidebar
    # ═══════════════════════════════════════════

    def _build_sidebar(self):
        s = self._sidebar

        # ── Header ──
        header = ctk.CTkFrame(s, fg_color=_SB_BG, corner_radius=0, height=86)
        header.pack(fill="x")
        header.pack_propagate(False)

        name_row = ctk.CTkFrame(header, fg_color="transparent")
        name_row.pack(fill="x", padx=18, pady=(22, 0))
        try:
            from PIL import Image
            logo = ctk.CTkImage(Image.open(_ASSETS / "logo.png"), size=(44, 44))
            ctk.CTkLabel(name_row, text="", image=logo, width=44, height=44).pack(side="left")
        except Exception:
            ctk.CTkLabel(name_row, text="T", width=40, height=40, corner_radius=10,
                         fg_color=_ACCENT, text_color="#ffffff",
                         font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        name_txt = ctk.CTkFrame(name_row, fg_color="transparent")
        name_txt.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(name_txt, text="TECLA", height=22,
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=_SB_TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(name_txt, text="Term Extraction and Corpus\nLinguistics Application",
                     font=ctk.CTkFont(size=9), text_color=_SB_MUTED,
                     justify="left", anchor="w").pack(anchor="w")
        ctk.CTkFrame(s, height=1, fg_color=_SB_BORDER, corner_radius=0).pack(fill="x")

        # ── Opciones principales ──
        scroll = ctk.CTkScrollableFrame(s, fg_color=_SB_BG, scrollbar_button_color=_SB_SECTION)
        scroll.pack(fill="both", expand=True, pady=(6, 0))

        # CARPETA DE TRABAJO
        self._build_section(scroll, "Carpeta de trabajo")
        card = ctk.CTkFrame(scroll, fg_color=_BG_CARD, corner_radius=8,
                            border_width=1, border_color=_SB_BORDER, cursor="hand2")
        card.pack(fill="x", padx=14, pady=(2, 4))
        icon = ctk.CTkLabel(card, text="📁", font=ctk.CTkFont(size=18))
        icon.pack(side="left", padx=(10, 8), pady=8)
        card_txt = ctk.CTkFrame(card, fg_color="transparent")
        card_txt.pack(side="left", fill="x", expand=True, pady=6)
        self._folder_name = ctk.CTkLabel(card_txt, text="", height=18, anchor="w",
                                         font=ctk.CTkFont(size=12, weight="bold"),
                                         text_color=_SB_TEXT)
        self._folder_name.pack(fill="x")
        self._folder_path = ctk.CTkLabel(card_txt, text="", height=14, anchor="w",
                                         font=ctk.CTkFont(size=10), text_color=_SB_MUTED)
        self._folder_path.pack(fill="x")
        for w in (card, icon, card_txt, self._folder_name, self._folder_path):
            w.bind("<Button-1>", lambda _e: self._browse_corpus())
        self.corpus_path_var.trace_add("write", lambda *_: self._update_folder_card())
        self._update_folder_card()
        ctk.CTkLabel(scroll,
                     text="Los PDF o TXT van en una subcarpeta «corpus».",
                     font=ctk.CTkFont(size=10), text_color=_SB_MUTED,
                     justify="left", wraplength=230,
                     ).pack(anchor="w", padx=16, pady=(0, 2))
        ctk.CTkButton(scroll, text="Elegir carpeta…", height=28,
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_ACCENT,
                      text_color=_ACCENT, font=ctk.CTkFont(size=12),
                      command=self._browse_corpus,
                      ).pack(fill="x", padx=14, pady=(2, 8))

        # LENGUA
        self._build_section(scroll, "Lengua")
        _Segmented(scroll, values=["auto", "es", "en"],
                   labels={"es": "español", "en": "inglés"},
                   variable=self.language_var,
                   ).pack(fill="x", padx=14, pady=(4, 8))

        # EXTRACCIÓN (esencial)
        self._build_section(scroll, "Extracción")
        ctk.CTkCheckBox(scroll, text="Incluir candidatos monoléxicos",
                        variable=self._include_mono_var,
                        checkbox_width=18, checkbox_height=18, border_width=2,
                        border_color=_STEP_PENDING, font=ctk.CTkFont(size=12),
                        fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                        checkmark_color="#ffffff", text_color=_SB_TEXT,
                        command=self._on_filter_changed,
                        ).pack(anchor="w", padx=18, pady=(4, 4))

        self._build_section(scroll, "Perfil de puntuación")
        _Segmented(scroll, values=list(_WEIGHT_PRESETS.keys()),
                               variable=self.weight_preset,
                               fg_color=_SB_SECTION, selected_color=_SEG_SELECTED,
                               selected_hover_color=_SEG_SEL_HOV,
                               unselected_color=_SB_SECTION,
                               text_color=_SEG_TEXT,
                               text_color_disabled=_SEG_TEXT,
                               command=self._on_preset_changed,
                               ).pack(fill="x", padx=14, pady=(4, 4))
        self._preset_hint = ctk.CTkLabel(scroll, text=_PRESET_HINTS["Equilibrado"],
                                          font=ctk.CTkFont(size=11), text_color=_SB_MUTED,
                                          wraplength=240, justify="left")
        self._preset_hint.pack(fill="x", padx=18, pady=(0, 8))

        # ── AJUSTES DE EXTRACCIÓN (en una ventana aparte) ──
        self._build_section(scroll, "Ajustes de extracción")
        self._settings_summary = ctk.CTkLabel(
            scroll, text="", font=ctk.CTkFont(size=11), text_color=_SB_MUTED,
            wraplength=240, justify="left", anchor="w")
        self._settings_summary.pack(fill="x", padx=18, pady=(2, 4))
        ctk.CTkButton(scroll, text="⚙  Ajustes de extracción…", height=32,
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_ACCENT,
                      text_color=_ACCENT, font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._open_settings,
                      ).pack(fill="x", padx=14, pady=(2, 10))
        for var in (self.max_term_length_var, self._min_freq_var, self._min_score_var,
                    self._percentile_choice, self._drop_other_var, self._other_sw_var,
                    self._stoplist_var, self.grammar_path_var):
            var.trace_add("write", lambda *_: self._update_settings_summary())
        self._update_settings_summary()

        # ── Botón de extracción ──
        ctk.CTkFrame(s, height=1, fg_color=_SB_BORDER, corner_radius=0).pack(fill="x")
        btn_frame = ctk.CTkFrame(s, fg_color=_SB_BG, height=68)
        btn_frame.pack(fill="x", side="bottom")
        btn_frame.pack_propagate(False)
        self._run_btn = ctk.CTkButton(
            btn_frame, text="▶  Ejecutar",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=_ACCENT, hover_color=_ACCENT_DIM,
            text_color="#ffffff",
            height=44, corner_radius=8,
            command=self._start_extraction,
        )
        self._run_btn.pack(fill="x", padx=14, pady=12)

    def _update_settings_summary(self):
        """Resume en la barra lateral los ajustes que no están por defecto."""
        changed = []
        if self.max_term_length_var.get() != _DEFAULTS["max_len"]:
            changed.append(f"longitud máx. {self.max_term_length_var.get()}")
        if self._min_freq_var.get() != _DEFAULTS["min_freq"]:
            changed.append(f"frecuencia mín. {self._min_freq_var.get()}")
        if self._min_score_var.get() > 0:
            changed.append(f"puntuación mín. {self._min_score_var.get():.2f}")
        if self._percentile_choice.get() != "—":
            changed.append(f"percentil {self._percentile_choice.get()}")
        if self._drop_other_var.get():
            changed.append("sin párrafos en la otra lengua")
        if self._other_sw_var.get():
            changed.append("sin palabras vacías de la otra lengua")
        if self._get_extra_stoplist():
            changed.append(f"stoplist ({len(self._get_extra_stoplist())})")
        if self.grammar_path_var.get():
            changed.append("gramática propia")
        text = ("Valores por defecto." if not changed
                else "Cambiado: " + " · ".join(changed) + ".")
        self._settings_summary.configure(text=text)

    def _other_language_name(self) -> str:
        return {"es": "inglés", "en": "español"}.get(self.language_var.get(), "la otra lengua")

    def _open_settings(self):
        """Ventana de ajustes de extracción, con ayuda en cada opción."""
        if self._settings_win is not None and self._settings_win.winfo_exists():
            self._settings_win.deiconify()
            self._settings_win.lift()
            self._settings_win.focus_force()
            return

        win = ctk.CTkToplevel(self)
        self._settings_win = win
        win.title("Ajustes de extracción")
        win.geometry("500x720")
        win.minsize(440, 520)
        win.configure(fg_color=_SB_BG)
        win.transient(self)

        footer = ctk.CTkFrame(win, fg_color=_SB_BG, height=60)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        ctk.CTkFrame(win, height=1, fg_color=_SB_BORDER, corner_radius=0).pack(side="bottom", fill="x")
        ctk.CTkButton(footer, text="Cerrar", width=110, height=34,
                      fg_color=_ACCENT, hover_color=_ACCENT_DIM, text_color="#ffffff",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=win.destroy).pack(side="right", padx=16, pady=12)
        ctk.CTkButton(footer, text="Restablecer valores", width=150, height=34,
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_SB_BORDER, text_color=_SB_MUTED,
                      font=ctk.CTkFont(size=12),
                      command=self._reset_settings).pack(side="right", pady=12)

        body = ctk.CTkScrollableFrame(win, fg_color=_SB_BG, scrollbar_button_color=_SB_SECTION)
        body.pack(fill="both", expand=True)

        ctk.CTkLabel(body, text="Ajustes de extracción",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=_SB_TEXT, anchor="w").pack(fill="x", padx=18, pady=(14, 2))
        ctk.CTkLabel(body,
                     text="Los filtros se aplican al momento a la tabla de candidatos, "
                          "la evaluación y la revisión. El resto de ajustes se aplica "
                          "la próxima vez que pulses Ejecutar.",
                     font=ctk.CTkFont(size=11), text_color=_SB_MUTED,
                     wraplength=430, justify="left", anchor="w").pack(fill="x", padx=18, pady=(0, 4))

        def card(title, when):
            ctk.CTkLabel(body, text=f"{title.upper()}  ·  {when}", height=18,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=_SB_MUTED, anchor="w").pack(fill="x", padx=18, pady=(14, 4))
            frame = ctk.CTkFrame(body, fg_color=_BG_CARD, corner_radius=10,
                                 border_width=1, border_color=_SB_BORDER)
            frame.pack(fill="x", padx=14)
            return frame

        def labelled(parent, text, help_text):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)
            name = ctk.CTkFrame(row, fg_color="transparent")
            name.pack(side="left")
            ctk.CTkLabel(name, text=text, font=ctk.CTkFont(size=12),
                         text_color=_SB_TEXT).pack(side="left")
            _help_icon(name, help_text).pack(side="left", padx=(6, 0))
            return row

        # — Filtros —
        f = card("Filtros", "al momento")
        row = labelled(f, "Frecuencia mínima",
                       "Número mínimo de veces que un candidato aparece en todo el corpus. "
                       "Con 1 se incluyen también los hápax, los candidatos que aparecen "
                       "una sola vez.")
        _NumberField(row, self._min_freq_var, 1, 9999,
                     command=self._on_filter_changed).pack(side="right")
        row = labelled(f, "Puntuación mínima",
                       "Valor mínimo del índice de terminologicidad, entre 0 y 1. El índice "
                       "combina TF-IDF y NC-value según el perfil de puntuación elegido.")
        _NumberField(row, self._min_score_var, 0, 1, step=0.05, decimals=2,
                     command=self._on_filter_changed).pack(side="right")
        row = labelled(f, "Percentil mínimo",
                       "Conserva solo los candidatos con mejor puntuación: con p75, por "
                       "ejemplo, queda el 25 % superior. Con «—» no se aplica.")
        _Segmented(f, values=list(_PCT_MAP), variable=self._percentile_choice,
                   font=ctk.CTkFont(size=11),
                   command=lambda _v: self._on_filter_changed(),
                   ).pack(fill="x", padx=12, pady=(0, 10))

        # — Candidatos —
        f = card("Candidatos", "al volver a ejecutar")
        row = labelled(f, "Longitud máxima (palabras)",
                       "Número máximo de palabras de un candidato, incluidas las "
                       "preposiciones, como «de» en «anotación de corpus».")
        _NumberField(row, self.max_term_length_var, 1, 15).pack(side="right")

        # — Otra lengua —
        f = card("Otra lengua en el corpus", "al volver a ejecutar")
        ctk.CTkLabel(f, text="Para textos con partes en otra lengua, como los resúmenes "
                             "en inglés de los artículos en español.",
                     font=ctk.CTkFont(size=11), text_color=_SB_MUTED,
                     wraplength=410, justify="left", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        checks = []
        for var, help_text in (
            (self._drop_other_var,
             "Antes del análisis, se detecta la lengua de cada párrafo y se eliminan "
             "los que están claramente en la otra lengua. Los párrafos de menos de "
             "ocho palabras, como los títulos, se conservan."),
            (self._other_sw_var,
             "Descarta los candidatos que contienen palabras gramaticales de la otra "
             "lengua (the, of, and… o de, la, y…). Recoge las frases sueltas que el "
             "filtro de párrafos deja pasar."),
        ):
            row = ctk.CTkFrame(f, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)
            box = ctk.CTkCheckBox(row, text="", variable=var,
                                  checkbox_width=18, checkbox_height=18, border_width=2,
                                  border_color=_STEP_PENDING, font=ctk.CTkFont(size=12),
                                  fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                                  checkmark_color="#ffffff", text_color=_SB_TEXT)
            box.pack(side="left")
            _help_icon(row, help_text).pack(side="left", padx=(6, 0))
            checks.append(box)
        checks[-1].master.pack_configure(pady=(6, 10))

        def _name_checks(*_):
            if not win.winfo_exists():
                return
            other = self._other_language_name()
            checks[0].configure(text=f"Descartar los párrafos en {other}")
            checks[1].configure(text=f"Excluir las palabras vacías del {other}"
                                if other != "la otra lengua"
                                else "Excluir las palabras vacías de la otra lengua")
        _name_checks()
        trace = self.language_var.trace_add("write", _name_checks)
        win.bind("<Destroy>", lambda e: e.widget is win and self.language_var.trace_remove("write", trace))

        # — Stoplist —
        f = card("Stoplist adicional", "al volver a ejecutar")
        labelled(f, "Palabras que no pueden formar parte de un candidato",
                 "Palabras o expresiones separadas por comas. Ningún candidato que las "
                 "contenga llega a la tabla. Sirve para descartar vocabulario general "
                 "que se cuela en la extracción.")
        ctk.CTkEntry(f, textvariable=self._stoplist_var,
                     placeholder_text="palabra1, palabra2, …",
                     fg_color=_BG_ROOT, border_color=_SB_BORDER,
                     text_color=_SB_TEXT).pack(fill="x", padx=12, pady=(0, 4))
        ctk.CTkButton(f, text="Cargar desde archivo .txt…",
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_SB_BORDER, text_color=_SB_MUTED,
                      height=30, font=ctk.CTkFont(size=12),
                      command=self._browse_stoplist).pack(fill="x", padx=12, pady=(0, 10))

        # — Gramática —
        f = card("Gramática de patrones", "al volver a ejecutar")
        labelled(f, "Archivo de gramática (.yaml)",
                 "Por defecto se usa la gramática incluida en TECLA, con los patrones "
                 "morfosintácticos de los términos en español y en inglés. Puede "
                 "sustituirse por un archivo .yaml propio con otros patrones.")
        ctk.CTkEntry(f, textvariable=self.grammar_path_var,
                     placeholder_text="Gramática incluida en TECLA",
                     fg_color=_BG_ROOT, border_color=_SB_BORDER,
                     text_color=_SB_TEXT).pack(fill="x", padx=12, pady=(0, 4))
        ctk.CTkButton(f, text="Seleccionar gramática…",
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_SB_BORDER, text_color=_SB_MUTED,
                      height=30, font=ctk.CTkFont(size=12),
                      command=self._browse_grammar).pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkFrame(body, height=10, fg_color="transparent").pack()

    def _reset_settings(self):
        self.max_term_length_var.set(_DEFAULTS["max_len"])
        self._min_freq_var.set(_DEFAULTS["min_freq"])
        self._min_score_var.set(_DEFAULTS["min_score"])
        self._percentile_choice.set("—")
        self._drop_other_var.set(False)
        self._other_sw_var.set(False)
        self._stoplist_var.set("")
        self.grammar_path_var.set("")
        self._on_filter_changed()

    def _build_section(self, parent, label: str):
        """Cabecera de sección de la sidebar."""
        ctk.CTkLabel(parent, text=label.upper(), height=18,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_SB_MUTED, anchor="w",
                     ).pack(fill="x", padx=18, pady=(12, 2))

    def _update_folder_card(self):
        """Muestra la carpeta de trabajo por su nombre, con la ruta debajo."""
        raw = self.corpus_path_var.get().strip()
        if not raw:
            self._folder_name.configure(text="Ninguna carpeta elegida")
            self._folder_path.configure(text="Pulsa para seleccionarla")
            return
        path = Path(raw)
        parent = str(path.parent).replace(str(Path.home()), "~", 1)
        if len(parent) > 34:
            parent = "…" + parent[-33:]
        self._folder_name.configure(text=path.name or raw)
        self._folder_path.configure(text=parent)

    # ═══════════════════════════════════════════
    # Pestaña 1 — Corpus
    # ═══════════════════════════════════════════

    def _build_tab_corpus(self):
        tab = self._tabview.tab("Corpus")
        # ── Bienvenida (hasta que hay un corpus cargado) ──
        self._corpus_welcome = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=10,
                                            border_width=1, border_color=_BORDER)
        self._corpus_welcome.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(self._corpus_welcome, text="Empieza por tu corpus",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=_TEXT, anchor="w").pack(fill="x", padx=22, pady=(20, 0))
        ctk.CTkLabel(self._corpus_welcome,
                     text="TECLA recorre contigo las fases del trabajo terminográfico: "
                          "corpus, extracción, evaluación y revisión. Para comenzar:",
                     font=ctk.CTkFont(size=12), text_color=_TEXT_MUTED,
                     anchor="w", justify="left").pack(fill="x", padx=22, pady=(2, 12))
        steps = ctk.CTkFrame(self._corpus_welcome, fg_color="transparent")
        steps.pack(fill="x", padx=16, pady=(0, 20))
        for i, (title, text) in enumerate([
                ("Elige la carpeta", "Selecciona a la izquierda la carpeta de trabajo, "
                                     "con tus textos en PDF o TXT."),
                ("Indica la lengua", "Español, inglés o detección automática."),
                ("Pulsa «Ejecutar»", "TECLA procesa los textos y propone los "
                                     "candidatos a término.")]):
            steps.grid_columnconfigure(i, weight=1, uniform="inicio")
            box = ctk.CTkFrame(steps, fg_color=_BG_ROOT, corner_radius=10,
                               border_width=1, border_color=_SB_BORDER)
            box.grid(row=0, column=i, sticky="nsew", padx=6)
            ctk.CTkLabel(box, text=str(i + 1), width=28, height=28, corner_radius=14,
                         fg_color=_SB_SECTION, text_color=_ACCENT,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         ).pack(anchor="w", padx=16, pady=(16, 6))
            ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=_TEXT, anchor="w").pack(fill="x", padx=16)
            ctk.CTkLabel(box, text=text, font=ctk.CTkFont(size=12), text_color=_TEXT_MUTED,
                         anchor="w", justify="left", wraplength=230,
                         ).pack(fill="x", padx=16, pady=(2, 16))

        # El resto del paso se muestra cuando el corpus está procesado
        self._corpus_body = ctk.CTkFrame(tab, fg_color="transparent")
        tab = self._corpus_body
        _tab_header(tab, "Corpus",
                    "Documentos procesados, estadísticas lingüísticas y metadatos del corpus.")

        # ── Cifras del corpus ──
        self._corpus_cards = _stat_cards(tab, [
            ("docs", "documentos"), ("tokens", "tokens"), ("sents", "oraciones"),
            ("types", "tipos únicos"), ("ttr", "TTR"),
        ])
        self._corpus_cards.update(_stat_cards(tab, [
            ("doc_len", "tokens por documento (media)"),
            ("sent_len", "tokens por oración (media)"),
            ("hapax", "hápax (proporción de tipos)"),
            ("density", "densidad léxica"),
        ]))

        # ── Cabecera tabla ──
        hdr = ctk.CTkFrame(tab, fg_color="transparent")
        hdr.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(hdr, text="Documentos del corpus",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=_TEXT).pack(side="left")
        ctk.CTkButton(
            hdr, text="Guardar como…", width=120, height=28,
            fg_color="transparent", hover_color=_BG_CARD,
            border_width=1, border_color=_ACCENT2,
            text_color=_ACCENT2, font=ctk.CTkFont(size=11),
            command=self._export_corpus_csv,
        ).pack(side="right")
        ctk.CTkButton(
            hdr, text="Abrir tabla", width=110, height=28,
            fg_color=_ACCENT, hover_color=_ACCENT_DIM,
            text_color="#ffffff", font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_corpus_stats,
        ).pack(side="right", padx=(0, 6))
        ctk.CTkLabel(
            tab, text=f"La tabla se guarda sola, en cada ejecución, en "
                      f"{_OUTPUT_DIR}/estadisticas_corpus.csv.",
            font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 4))

        # ── Treeview de documentos ──
        corpus_wrap = tk.Frame(tab, bg=_BG_ROOT)
        corpus_wrap.pack(fill="x", padx=18, pady=(0, 0))

        self._corpus_tree = ttk.Treeview(
            corpus_wrap,
            style="TECLA.Treeview",
            columns=("num", "doc", "tokens", "sents", "types", "ttr",
                     "hapax", "dens", "slen", "autor", "año", "tema"),
            show="headings",
            selectmode="browse",
            height=8,
        )
        corpus_cols = [
            ("num",    "#",          42,  False, "e"),
            ("doc",    "Documento", 180,  True,  "w"),
            ("tokens", "Tokens",     80,  False, "e"),
            ("sents",  "Oraciones",  90,  False, "e"),
            ("types",  "Tipos",      80,  False, "e"),
            ("ttr",    "TTR",        70,  False, "e"),
            ("hapax",  "Hápax",      66,  False, "e"),
            ("dens",   "Dens. léx.", 82,  False, "e"),
            ("slen",   "Long. or.",  78,  False, "e"),
            ("autor",  "Autor",     130,  False, "w"),
            ("año",    "Año",        55,  False, "c"),
            ("tema",   "Temática",  100,  True,  "w"),
        ]
        for cid, heading, width, stretch, anchor in corpus_cols:
            self._corpus_tree.heading(cid, text=heading)
            self._corpus_tree.column(cid, width=width, stretch=stretch,
                                     anchor=anchor, minwidth=width)
        self._corpus_tree.tag_configure("odd",  background=_ROW_ODD,  foreground=_TEXT)
        self._corpus_tree.tag_configure("even", background=_ROW_EVEN, foreground=_TEXT)
        self._corpus_tree.bind("<<TreeviewSelect>>", self._on_corpus_row_selected)

        corpus_vsb = tk.Scrollbar(corpus_wrap, orient="vertical",
                                  command=self._corpus_tree.yview,
                                  bg=_BG_ROOT, troughcolor=_BG_CARD,
                                  activebackground=_BG_CARD2, width=12)
        self._corpus_tree.configure(yscrollcommand=corpus_vsb.set)
        corpus_vsb.pack(side="right", fill="y")
        self._corpus_tree.pack(side="left", fill="both", expand=True)

        # ── Separador ──
        ctk.CTkFrame(tab, height=1, fg_color=_BORDER).pack(fill="x", padx=18, pady=(8, 0))

        # ── Panel de metadatos ──
        meta_card = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=10,
                                 border_width=1, border_color=_BORDER)
        meta_card.pack(fill="both", expand=True, padx=18, pady=(6, 16))

        self._meta_doc_label = ctk.CTkLabel(
            meta_card,
            text="Selecciona un documento de la tabla para editar sus metadatos.",
            font=ctk.CTkFont(size=12), text_color=_TEXT_MUTED, anchor="w",
        )
        self._meta_doc_label.pack(anchor="w", padx=14, pady=(10, 8))

        row1 = ctk.CTkFrame(meta_card, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkLabel(row1, text="Autor:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, width=52, anchor="e").pack(side="left")
        self._meta_autor = ctk.CTkEntry(row1, width=200, fg_color=_BG_CARD2,
                                        border_color=_BORDER, text_color=_TEXT,
                                        placeholder_text="Autor o institución")
        self._meta_autor.pack(side="left", padx=(6, 16))
        ctk.CTkLabel(row1, text="Año:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, width=36, anchor="e").pack(side="left")
        self._meta_año = ctk.CTkEntry(row1, width=80, fg_color=_BG_CARD2,
                                      border_color=_BORDER, text_color=_TEXT,
                                      placeholder_text="2024")
        self._meta_año.pack(side="left", padx=(6, 16))
        ctk.CTkLabel(row1, text="Temática:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, width=44, anchor="e").pack(side="left")
        self._meta_tema = ctk.CTkEntry(row1, width=220, fg_color=_BG_CARD2,
                                       border_color=_BORDER, text_color=_TEXT,
                                       placeholder_text="Área temática")
        self._meta_tema.pack(side="left", padx=(6, 0))

        row2 = ctk.CTkFrame(meta_card, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkLabel(row2, text="Fuente:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, width=52, anchor="e").pack(side="left")
        self._meta_fuente = ctk.CTkEntry(row2, width=480, fg_color=_BG_CARD2,
                                         border_color=_BORDER, text_color=_TEXT,
                                         placeholder_text="Título, revista, URL…")
        self._meta_fuente.pack(side="left", padx=(6, 0))

        row3 = ctk.CTkFrame(meta_card, fg_color="transparent")
        row3.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(row3, text="Notas:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED, width=52, anchor="e").pack(side="left", anchor="n", pady=(4, 0))
        self._meta_notas = ctk.CTkTextbox(row3, height=55, fg_color=_BG_CARD2,
                                          border_width=1, border_color=_BORDER,
                                          text_color=_TEXT, font=ctk.CTkFont(size=11))
        self._meta_notas.pack(side="left", fill="x", expand=True, padx=(6, 0))

        ctk.CTkButton(
            meta_card, text="Guardar metadatos", height=32,
            fg_color=_ACCENT, hover_color=_ACCENT_DIM,
            text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, command=self._save_doc_metadata,
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def _render_corpus_tab(self):
        total_tok   = sum(d["tokens"]    for d in self._doc_stats)
        total_sent  = sum(d["sentences"] for d in self._doc_stats)
        total_types = self._corpus_types or sum(d["types"] for d in self._doc_stats)
        corpus_ttr  = round(total_types / total_tok, 4) if total_tok else 0.0
        for key, value in (("docs", _miles(len(self._doc_stats))), ("tokens", _miles(total_tok)),
                           ("sents", _miles(total_sent)), ("types", _miles(total_types)),
                           ("ttr", f"{corpus_ttr:.4f}")):
            self._corpus_cards[key].configure(text=value)
        summary = self._corpus_summary
        n_docs  = len(self._doc_stats)
        for key, value in (
            ("doc_len",  _miles(round(total_tok / n_docs)) if n_docs else "—"),
            ("sent_len", f"{total_tok / total_sent:.1f}" if total_sent else "—"),
            ("hapax",    f"{summary.get('hapax_ratio', 0):.3f}"),
            ("density",  f"{summary.get('lexical_density', 0):.3f}"),
        ):
            self._corpus_cards[key].configure(text=value)
        self._corpus_welcome.pack_forget()
        self._corpus_body.pack(fill="both", expand=True)
        self._tabview.mark_done("Corpus")

        self._corpus_tree.delete(*self._corpus_tree.get_children())
        for i, d in enumerate(self._doc_stats, 1):
            meta = self._corpus_metadata.get(d["doc_id"], {})
            tag  = "odd" if i % 2 == 1 else "even"
            self._corpus_tree.insert("", "end", iid=d["doc_id"], tags=(tag,),
                values=(
                    f"{i}.",
                    d["doc_id"],
                    _miles(d['tokens']),
                    _miles(d['sentences']),
                    _miles(d['types']),
                    f"{d['ttr']:.4f}",
                    f"{d.get('hapax_ratio', 0):.3f}",
                    f"{d.get('lexical_density', 0):.3f}",
                    f"{d.get('avg_sentence_length', 0):.1f}",
                    meta.get("autor", ""),
                    meta.get("año", ""),
                    meta.get("tema", ""),
                ))

    def _corpus_stats_file(self) -> Path:
        return self._output_dir() / "estadisticas_corpus.csv"

    def _open_corpus_stats(self):
        """Abre la tabla de estadísticas con la aplicación predeterminada."""
        if not self._doc_stats:
            messagebox.showwarning("Sin datos", "Ejecuta TECLA para obtener las estadísticas.")
            return
        self._write_corpus_stats(self._corpus_stats_file())
        self._open_folder(self._corpus_stats_file())

    def _export_corpus_csv(self):
        if not self._doc_stats:
            messagebox.showwarning("Sin datos", "No hay datos de corpus para exportar.")
            return
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), 
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="estadisticas_corpus.csv",
        )
        if not path:
            return
        self._write_corpus_stats(Path(path))
        messagebox.showinfo("Exportado", f"Tabla guardada en:\n{path}")

    def _write_corpus_stats(self, path: Path):
        """Tabla de estadísticas por documento, con los metadatos y el total.
        Se guarda sola en la carpeta de salida en cada ejecución."""
        total_tok   = sum(d["tokens"]    for d in self._doc_stats)
        total_sent  = sum(d["sentences"] for d in self._doc_stats)
        total_types = self._corpus_types or sum(d["types"] for d in self._doc_stats)
        corpus_ttr  = round(total_types / total_tok, 4) if total_tok else 0.0
        # utf-8-sig: Excel reconoce así las tildes al abrir el CSV
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["documento", "tokens", "oraciones", "tipos_unicos", "ttr",
                             "hapax", "densidad_lexica", "longitud_media_oracion",
                             "autor", "año", "tema", "fuente", "notas"])
            for d in self._doc_stats:
                meta = self._corpus_metadata.get(d["doc_id"], {})
                writer.writerow([
                    d["doc_id"], d["tokens"], d["sentences"], d["types"], d["ttr"],
                    d.get("hapax_ratio", ""), d.get("lexical_density", ""),
                    d.get("avg_sentence_length", ""),
                    meta.get("autor", ""), meta.get("año", ""),
                    meta.get("tema", ""), meta.get("fuente", ""), meta.get("notas", ""),
                ])
            writer.writerow([])
            summary = self._corpus_summary
            writer.writerow(["TOTAL", total_tok, total_sent, total_types, corpus_ttr,
                             summary.get("hapax_ratio", ""), summary.get("lexical_density", ""),
                             round(total_tok / total_sent, 2) if total_sent else "",
                             "", "", "", "", ""])

    # ═══════════════════════════════════════════
    # Pestaña 2 — Extracción
    # ═══════════════════════════════════════════

    def _build_tab_extraccion(self):
        tab = self._tabview.tab("Extracción")
        _tab_header(tab, "Extracción de candidatos a término",
                    "Registro del proceso y tabla de candidatos ordenados por terminologicidad.")

        # ── Cifras ──
        self._ext_cards = _stat_cards(tab, [
            ("shown", "candidatos (con los filtros)"),
            ("cands", "extraídos en total"),
            ("multi", "poliléxicos · monoléxicos"),
            ("spread", "en 2 o más documentos"),
        ])

        # ── Log ──
        log_hdr = ctk.CTkFrame(tab, fg_color="transparent")
        log_hdr.pack(fill="x", padx=18, pady=(6, 0))
        ctk.CTkLabel(log_hdr, text="Registro del proceso",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=_TEXT).pack(side="left")
        ctk.CTkButton(log_hdr, text="Limpiar", width=68, height=24,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2,
                      border_width=1, border_color=_BORDER,
                      text_color=_TEXT_MUTED,
                      font=ctk.CTkFont(size=11),
                      command=lambda: self.log_box.delete("1.0", "end"),
                      ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            tab, height=88, fg_color=_BG_LOG, text_color=_TEXT_LOG,
            font=ctk.CTkFont(size=12),
            corner_radius=8, border_width=1, border_color=_BORDER,
        )
        self.log_box.pack(fill="x", padx=18, pady=(6, 0))

        self._progress = ctk.CTkProgressBar(tab, fg_color=_BORDER, progress_color=_ACCENT,
                                             height=5, corner_radius=3)
        self._progress.pack(fill="x", padx=18, pady=(8, 0))
        self._progress.set(0)
        self._progress.configure(mode="indeterminate")

        ctk.CTkFrame(tab, height=1, fg_color=_BORDER).pack(fill="x", padx=18, pady=10)

        # ── Cabecera de resultados ──
        res_hdr = ctk.CTkFrame(tab, fg_color="transparent")
        res_hdr.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(res_hdr, text="Candidatos a término",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=_TEXT).pack(side="left")

        ctk.CTkButton(res_hdr, text="⬇  TBX", width=80, height=28,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2,
                      border_width=1, border_color=_ACCENT2,
                      text_color=_ACCENT2,
                      font=ctk.CTkFont(size=12), command=self._export_tbx,
                      ).pack(side="right", padx=(4, 0))
        ctk.CTkButton(res_hdr, text="⬇  CSV", width=80, height=28,
                      fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                      text_color="#ffffff",
                      font=ctk.CTkFont(size=12, weight="bold"), command=self._export_csv,
                      ).pack(side="right", padx=(4, 0))
        ctk.CTkButton(res_hdr, text="Ninguno", width=68, height=28,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2,
                      border_width=1, border_color=_BORDER,
                      text_color=_TEXT_MUTED,
                      font=ctk.CTkFont(size=12), command=self._deselect_all,
                      ).pack(side="right", padx=(4, 0))
        ctk.CTkButton(res_hdr, text="Todos", width=56, height=28,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2,
                      border_width=1, border_color=_BORDER,
                      text_color=_TEXT_MUTED,
                      font=ctk.CTkFont(size=12), command=self._select_all,
                      ).pack(side="right", padx=(0, 0))
        self._term_count_label = ctk.CTkLabel(res_hdr, text="",
                                               font=ctk.CTkFont(size=12), text_color=_ACCENT)
        self._term_count_label.pack(side="right", padx=(0, 14))

        # ── Barra de ordenación ──
        sort_bar = ctk.CTkFrame(tab, fg_color="transparent")
        sort_bar.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(sort_bar, text="Ordenar por:",
                     font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED,
                     ).pack(side="left", padx=(0, 6))
        _Segmented(sort_bar, values=list(_SORT_KEY_MAP.keys()),
                               variable=self._sort_key_var,
                               fg_color=_BG_CARD, selected_color=_SEG_SELECTED,
                               selected_hover_color=_SEG_SEL_HOV,
                               unselected_color=_BG_CARD,
                               text_color=_SEG_TEXT,
                               font=ctk.CTkFont(size=11),
                               command=self._on_sort_changed,
                               ).pack(side="left")
        self._sort_dir_btn = ctk.CTkButton(sort_bar, text="▼ desc", width=68, height=26,
                                            fg_color=_BG_CARD, hover_color=_BG_CARD2,
                                            border_width=1, border_color=_BORDER,
                                            text_color=_TEXT_MUTED,
                                            font=ctk.CTkFont(size=11),
                                            command=self._toggle_sort_dir)
        self._sort_dir_btn.pack(side="left", padx=(8, 0))

        # ── Columnas de la tabla: definición con anchos y visibilidad por defecto ──
        # (cid, encabezado, ancho, stretch, anchor, visible_por_defecto)
        self._RESULT_COLS = [
            ("num",      "#",          42,  False, "e", True),
            ("term",     "Candidato", 200,  True,  "w", True),
            ("var",      "Variantes", 180,  False, "w", True),
            ("pat",      "Patrón",    130,  False, "w", False),
            ("score",    "Score",      66,  False, "e", True),
            ("bar",      "",          118,  False, "w", True),
            ("tfidf",    "TF-IDF",     66,  False, "e", True),
            ("cval",     "C-val",      62,  False, "e", False),
            ("ncval",    "NC-val",     62,  False, "e", True),
            ("freq",     "Frec",       50,  False, "e", True),
            ("freq_rel", "Frec/mil",   72,  False, "e", True),
            ("docs",     "Docs",       44,  False, "e", True),
            ("authors",  "Autores",    58,  False, "e", True),
        ]

        # Toggle row
        toggle_row = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=6)
        toggle_row.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(toggle_row, text="Columnas:",
                     font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
                     ).pack(side="left", padx=(8, 4))
        for cid, heading, width, stretch, anchor, default_on in self._RESULT_COLS:
            if cid in ("num", "term", "bar"):
                continue  # siempre visibles (la barra acompaña a la columna Score)
            var = ctk.BooleanVar(value=default_on)
            self._col_visible[cid] = var
            ctk.CTkCheckBox(
                toggle_row, text=heading, variable=var,
                width=16, height=16, checkbox_width=15, checkbox_height=15,
                border_width=2, border_color=_STEP_PENDING, corner_radius=4,
                fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                checkmark_color="#ffffff",
                text_color=_TEXT_MUTED, font=ctk.CTkFont(size=10),
                command=lambda c=cid, w=width, st=stretch: self._toggle_col(c, w, st),
            ).pack(side="left", padx=(0, 8))

        # ── Qué mide cada columna ──
        legend = ctk.CTkFrame(tab, fg_color="transparent")
        legend.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(legend, text="Qué mide cada columna:",
                     font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
                     ).pack(side="left", padx=(0, 8))
        for name in ("Score", "TF-IDF", "C-val", "NC-val", "Frec", "Frec/mil", "Docs", "Autores"):
            ctk.CTkLabel(legend, text=name, font=ctk.CTkFont(size=10),
                         text_color=_TEXT).pack(side="left")
            _help_icon(legend, _METRIC_HELP[name]).pack(side="left", padx=(3, 12))

        # ── Tabla de resultados ──
        tree_wrap = tk.Frame(tab, bg=_BG_ROOT)
        tree_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        self._results_tree = ttk.Treeview(
            tree_wrap,
            style="TECLA.Treeview",
            columns=tuple(c[0] for c in self._RESULT_COLS),
            show="headings",
            selectmode="extended",
        )
        for cid, heading, width, stretch, anchor, default_on in self._RESULT_COLS:
            self._results_tree.heading(cid, text=heading)
            if default_on or cid in ("num", "term"):
                self._results_tree.column(cid, width=width, stretch=stretch,
                                          anchor=anchor, minwidth=width)
            else:
                self._results_tree.column(cid, width=0, stretch=False, minwidth=0)

        self._results_tree.tag_configure("odd",  background=_ROW_ODD,  foreground=_TEXT)
        self._results_tree.tag_configure("even", background=_ROW_EVEN, foreground=_TEXT)

        vsb = tk.Scrollbar(tree_wrap, orient="vertical",
                           command=self._results_tree.yview,
                           bg=_BG_ROOT, troughcolor=_BG_CARD,
                           activebackground=_BG_CARD2, width=12)
        self._results_tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self._results_tree.pack(side="left", fill="both", expand=True)

    def _add_next_buttons(self):
        """Botón «Siguiente» en la esquina inferior derecha de los pasos 1 a 3."""
        names = ["Corpus", "Extracción", "Evaluación", "Revisión"]
        for cur, nxt in zip(names, names[1:]):
            tab = self._tabview.tab(cur)
            bar = ctk.CTkFrame(tab, fg_color="transparent")
            ctk.CTkButton(bar, text=f"Siguiente: {nxt}   →", height=32, corner_radius=8,
                          fg_color=_ACCENT, hover_color=_ACCENT_DIM, text_color="#ffffff",
                          font=ctk.CTkFont(size=12, weight="bold"),
                          command=lambda n=nxt: self._tabview.set(n)).pack(side="right")
            kids = [k for k in tab.winfo_children() if k is not bar]
            opts = dict(side="bottom", fill="x", padx=18, pady=(0, 12))
            if kids:
                opts["before"] = kids[0]
            bar.pack(**opts)

    # ═══════════════════════════════════════════
    # Pestaña 3 — Gráficos
    # ═══════════════════════════════════════════

    def _output_dir(self) -> Path:
        """Carpeta donde TECLA guarda lo que genera, junto a la carpeta «corpus»
        (nunca dentro de ella, para que no se lea como parte del corpus)."""
        workdir = self.corpus_path_var.get()
        out = (Path(workdir) if workdir else Path.home()) / _OUTPUT_DIR
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _user_file(self, name: str, legacy: str) -> Path:
        """Archivo con trabajo del usuario en la carpeta de salida; si aún no
        existe, el que guardaba TECLA 2.0 en la carpeta de trabajo."""
        current = self._output_dir() / name
        old = Path(self.corpus_path_var.get()) / legacy
        return old if not current.exists() and old.exists() else current

    def _extraction_graphs_dir(self) -> Path:
        out = self._output_dir() / "graphs" / "extraction"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _evaluation_graphs_dir(self) -> Path:
        out = self._output_dir() / "graphs" / "evaluation"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _update_graficos(self):
        """Genera los gráficos de extracción y los guarda como PNG."""
        if not self._results:
            return

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            self._log("⚠  Instala matplotlib para generar los gráficos: pip install matplotlib")
            return

        scores  = [t["terminologicity"]    for t in self._results]
        freqs   = [t["frequency"]          for t in self._results]
        tfidf   = [t.get("tf_idf", 0)     for t in self._results]
        ncval   = [t.get("nc_value", 0)   for t in self._results]
        doc_frq = [t["doc_frequency"]   for t in self._results]
        top20   = sorted(self._results, key=lambda t: t["frequency"], reverse=True)[:20]

        out_dir = self._extraction_graphs_dir()

        def _style(ax):
            ax.set_facecolor(_BG_CARD)
            ax.tick_params(colors=_TEXT, labelsize=8)
            for sp in ax.spines.values():
                sp.set_color(_TEXT_MUTED)

        # ── Figura 1: terminologicidad + top 20 ──
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor=_BG_ROOT)
        fig1.subplots_adjust(wspace=0.35, top=0.88, bottom=0.14, left=0.07, right=0.97)
        _style(ax1); _style(ax2)

        ax1.hist(scores, bins=20, color=_ACCENT, edgecolor=_ACCENT2, alpha=0.85)
        ax1.set_title("Distribución de puntuaciones de terminologicidad", color=_TEXT, fontsize=9, weight="bold")
        ax1.set_xlabel("Puntuación de terminologicidad", color=_TEXT_MUTED, fontsize=8)
        ax1.set_ylabel("Número de candidatos terminológicos", color=_TEXT_MUTED, fontsize=8)

        terms_top = [t["lemma"][:30] for t in reversed(top20)]
        freqs_top = [t["frequency"]  for t in reversed(top20)]
        ax2.barh(terms_top, freqs_top, color=_ACCENT, alpha=0.85)
        ax2.set_title("Top 20 candidatos terminológicos por frecuencia de corpus", color=_TEXT, fontsize=9, weight="bold")
        ax2.set_xlabel("Frecuencia absoluta", color=_TEXT_MUTED, fontsize=8)
        ax2.tick_params(axis="y", labelsize=7)

        p1 = out_dir / "terminologicity_scores.png"
        fig1.savefig(p1, dpi=150, bbox_inches="tight")
        plt.close(fig1)

        # ── Figura 2: TF-IDF vs C-value + cobertura documental ──
        fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5), facecolor=_BG_ROOT)
        fig2.subplots_adjust(wspace=0.35, top=0.88, bottom=0.14, left=0.07, right=0.97)
        _style(ax3); _style(ax4)

        sc = ax3.scatter(tfidf, ncval, c=scores, cmap="Purples", alpha=0.7, s=20, edgecolors="none")
        ax3.set_title("Correlación entre TF-IDF y NC-value", color=_TEXT, fontsize=9, weight="bold")
        ax3.set_xlabel("TF-IDF", color=_TEXT_MUTED, fontsize=8)
        ax3.set_ylabel("NC-value", color=_TEXT_MUTED, fontsize=8)
        cb = fig2.colorbar(sc, ax=ax3)
        cb.set_label("Terminologicidad", color=_TEXT_MUTED, fontsize=7)

        ax4.scatter(doc_frq, freqs, c=scores, cmap="Purples", alpha=0.7, s=20, edgecolors="none")
        ax4.set_title("Frecuencia de corpus vs. cobertura documental", color=_TEXT, fontsize=9, weight="bold")
        ax4.set_xlabel("Número de documentos", color=_TEXT_MUTED, fontsize=8)
        ax4.set_ylabel("Frecuencia total", color=_TEXT_MUTED, fontsize=8)

        p2 = out_dir / "tfidf_cvalue_coverage.png"
        fig2.savefig(p2, dpi=150, bbox_inches="tight")
        plt.close(fig2)

        self._log(f"📊  Gráficos de extracción guardados en:\n   {out_dir}")

    # ═══════════════════════════════════════════
    # Pestaña 5 — Revisión
    # ═══════════════════════════════════════════

    def _build_tab_revision(self):
        tab = self._tabview.tab("Revisión")
        _tab_header(tab, "Revisión de candidatos a término",
                    "Valida manualmente cada candidato: apruébalo, recházalo o añade notas.")

        # Contador de la revisión y exportación de los términos validados
        rev_bar = ctk.CTkFrame(tab, fg_color="transparent")
        rev_bar.pack(fill="x", padx=18, pady=(0, 0))
        self._rev_counter_label = ctk.CTkLabel(rev_bar, text="", font=ctk.CTkFont(size=12),
                                               text_color=_ACCENT)
        self._rev_counter_label.pack(side="left")
        self._rev_progress = ctk.CTkProgressBar(rev_bar, width=180, height=8, corner_radius=4,
                                                fg_color=_BORDER, progress_color=_TEAL)
        self._rev_progress.set(0)
        self._rev_progress.pack(side="left", padx=(12, 6))
        self._rev_pct_label = ctk.CTkLabel(rev_bar, text="", font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color=_TEAL)
        self._rev_pct_label.pack(side="left")
        rev_bar = ctk.CTkFrame(tab, fg_color="transparent")   # fila de la exportación
        rev_bar.pack(fill="x", padx=18, pady=(4, 0))
        for fmt in ("TXT", "JSON", "CSV"):
            ctk.CTkButton(rev_bar, text=f"⬇  {fmt}", width=72, height=28,
                          fg_color=_ACCENT if fmt == "CSV" else _BG_CARD,
                          hover_color=_ACCENT_DIM if fmt == "CSV" else _BG_CARD2,
                          border_width=0 if fmt == "CSV" else 1, border_color=_ACCENT2,
                          text_color="#ffffff" if fmt == "CSV" else _ACCENT2,
                          font=ctk.CTkFont(size=12, weight="bold" if fmt == "CSV" else "normal"),
                          command=lambda f=fmt.lower(): self._export_reviewed(f),
                          ).pack(side="right", padx=(4, 0))
        self._exp_rejected_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(rev_bar, text="incluir los rechazados", variable=self._exp_rejected_var,
                        width=16, height=16, checkbox_width=15, checkbox_height=15,
                        border_width=2, border_color=_STEP_PENDING, corner_radius=4,
                        fg_color=_ACCENT, hover_color=_ACCENT_DIM, checkmark_color="#ffffff",
                        text_color=_TEXT_MUTED, font=ctk.CTkFont(size=11),
                        ).pack(side="right", padx=(10, 4))
        ctk.CTkLabel(rev_bar, text="Exportar los términos revisados:", font=ctk.CTkFont(size=11),
                     text_color=_TEXT_MUTED).pack(side="right", padx=(0, 6))

        # Layout: lista izquierda + detalle derecha
        left = ctk.CTkFrame(tab, width=260, fg_color=_BG_CARD, corner_radius=10,
                            border_width=1, border_color=_BORDER)
        left.pack(side="left", fill="y", padx=(18, 6), pady=16)
        left.pack_propagate(False)

        right = ctk.CTkScrollableFrame(tab, fg_color=_BG_CARD, corner_radius=10,
                                       border_width=1, border_color=_BORDER,
                                       scrollbar_button_color=_BG_CARD2)
        right.pack(side="right", fill="both", expand=True, padx=(0, 18), pady=16)

        # ── Lista izquierda ──
        ctk.CTkLabel(left, text="Lista de candidatos",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=_TEXT,
                     ).pack(fill="x", padx=10, pady=(12, 4))

        self._rev_filter_var = ctk.StringVar(value="Todos")
        _Segmented(left,
                               values=["Todos", "Pendiente", "Aprobado", "Rechazado"],
                               variable=self._rev_filter_var,
                               fg_color=_BG_CARD2, selected_color=_SEG_SELECTED,
                               selected_hover_color=_SEG_SEL_HOV,
                               unselected_color=_BG_CARD2,
                               text_color=_SEG_TEXT,
                               font=ctk.CTkFont(size=10),
                               command=self._render_revision_list,
                               ).pack(fill="x", padx=8, pady=(0, 6))

        self._rev_list_scroll = ctk.CTkScrollableFrame(
            left, fg_color=_BG_CARD, corner_radius=6,
            scrollbar_button_color=_BG_CARD2,
        )
        self._rev_list_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))

        # ── Panel de detalle derecho ──
        # Orden: estado y término · concordancias · datos · notas
        head = ctk.CTkFrame(right, fg_color="transparent")
        head.pack(fill="x", padx=22, pady=(18, 4))
        status_row = ctk.CTkFrame(head, fg_color="transparent")
        status_row.pack(side="right", anchor="n")
        self._rev_status_btns = {}
        for status, color in _STATUS_COLOR.items():
            btn = ctk.CTkButton(
                status_row, text=status.capitalize(), height=32, width=96,
                fg_color=_BG_CARD, hover_color=_BG_CARD2,
                border_width=2, border_color=color, text_color=color,
                font=ctk.CTkFont(size=12, weight="bold"), corner_radius=8,
                command=lambda s=status: self._set_review_status(s),
            )
            btn.pack(side="left", padx=(6, 0))
            self._rev_status_btns[status] = btn
        ctk.CTkFrame(head, width=1, height=34, fg_color=_BORDER).pack(side="right", padx=(14, 8))
        term_box = ctk.CTkFrame(head, fg_color="transparent")
        term_box.pack(side="left", fill="x", expand=True)
        self._rev_term_label = ctk.CTkLabel(term_box, text="Selecciona un término",
                                             font=ctk.CTkFont(size=17, weight="bold"),
                                             text_color=_TEXT_MUTED, anchor="w")
        self._rev_term_label.pack(fill="x")
        self._rv = {}
        self._rv["variants"] = ctk.CTkLabel(term_box, text="", font=ctk.CTkFont(size=11),
                                             text_color=_ACCENT2, anchor="w",
                                             wraplength=520, justify="left")
        self._rv["variants"].pack(fill="x")
        self._rv_forms_open = False
        self._rv["variants"].configure(cursor="hand2")
        self._rv["variants"].bind("<Button-1>", lambda _: self._toggle_forms())
        self._rv["forms"] = ctk.CTkLabel(term_box, text="", font=ctk.CTkFont(size=11),
                                          text_color=_TEXT_MUTED, anchor="w",
                                          wraplength=520, justify="left")

        self._rv["author_note"] = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11),
                                                text_color=_INFO, anchor="w",
                                                wraplength=900, justify="left")
        self._rv["author_note"].pack(fill="x", padx=22, pady=(4, 0))
        self._rev_author_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Posible uso propio de autor/es", variable=self._rev_author_var,
                        width=16, height=16, checkbox_width=15, checkbox_height=15,
                        border_width=2, border_color=_INFO, corner_radius=4,
                        fg_color=_INFO, hover_color=_INFO_DIM, checkmark_color="#ffffff",
                        text_color=_TEXT, font=ctk.CTkFont(size=11),
                        command=self._toggle_author_usage).pack(anchor="w", padx=22, pady=(6, 0))
        ctk.CTkFrame(right, height=1, fg_color=_BORDER).pack(fill="x", padx=22, pady=(8, 4))

        # ── Concordancias ──
        conc_hdr = ctk.CTkFrame(right, fg_color="transparent")
        conc_hdr.pack(fill="x", padx=22, pady=(8, 4))
        ctk.CTkLabel(conc_hdr, text="CONCORDANCIAS",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED,
                     ).pack(side="left")
        _help_icon(conc_hdr, "Apariciones del candidato en los textos del corpus, con su contexto "
                             "a izquierda y derecha y el documento de procedencia. Ayudan a decidir "
                             "si funciona como término en el uso.").pack(side="left", padx=(4, 0))
        ctk.CTkButton(conc_hdr, text="⬇  CSV", width=64, height=22,
                      fg_color="transparent", hover_color=_BG_CARD2,
                      border_width=1, border_color=_ACCENT, text_color=_ACCENT,
                      font=ctk.CTkFont(size=10), command=self._export_concordances,
                      ).pack(side="right")
        self._conc_info = ctk.CTkLabel(conc_hdr, text="", font=ctk.CTkFont(size=10),
                                       text_color=_TEXT_MUTED)
        self._conc_info.pack(side="right", padx=(0, 10))
        conc_ctrl = ctk.CTkFrame(right, fg_color="transparent")
        conc_ctrl.pack(fill="x", padx=22, pady=(0, 4))
        self._conc_sort_var = ctk.StringVar(value="aparición")   # orden de aparición
        self._conc_doc_var = ctk.StringVar(value="Todos los documentos")
        self._conc_doc_menu = ctk.CTkOptionMenu(
            conc_ctrl, variable=self._conc_doc_var, values=["Todos los documentos"],
            width=230, height=24, font=ctk.CTkFont(size=10), dropdown_font=ctk.CTkFont(size=11),
            fg_color=_BG_CARD2, button_color=_ACCENT, button_hover_color=_ACCENT_DIM,
            text_color=_TEXT, command=lambda _: self._refresh_concordances())
        self._conc_doc_menu.pack(side="left")
        conc_wrap = tk.Frame(right, bg=_BORDER, bd=0)
        conc_wrap.pack(fill="x", padx=22, pady=(0, 4))
        self._conc_text = tk.Text(conc_wrap, height=11, wrap="none", relief="flat",
                                  bg=_BG_CARD, fg=_TEXT, font=("Menlo", 11),
                                  padx=8, pady=6, highlightthickness=0, cursor="hand2")
        conc_x = tk.Scrollbar(conc_wrap, orient="horizontal", command=self._conc_text.xview,
                              bg=_BG_ROOT, troughcolor=_BG_CARD, width=10)
        self._conc_text.configure(xscrollcommand=conc_x.set)
        self._conc_text.pack(fill="x", padx=1, pady=(1, 0))
        conc_x.pack(fill="x", padx=1, pady=(0, 1))
        self._conc_text.tag_configure("even", background=_ROW_EVEN)
        self._conc_text.tag_configure("sel_line", background=_SB_SECTION)
        self._conc_text.tag_configure("kw", foreground=_ACCENT, font=("Menlo", 11, "bold"))
        self._conc_text.tag_configure("doc", foreground=_TEXT_MUTED)
        self._conc_text.tag_raise("kw")
        self._conc_text.bind("<Button-1>", self._on_concordance_click)
        self._conc_text.configure(state="disabled")
        self._conc_shown = []   # concordancias en pantalla, por línea
        # Oración completa de la línea elegida
        self._conc_detail = tk.Text(right, height=4, wrap="word", relief="flat",
                                    bg=_BG_CARD2, fg=_TEXT, font=("Helvetica", 12),
                                    padx=10, pady=8, highlightthickness=0)
        self._conc_detail.tag_configure("kw", foreground=_ACCENT, font=("Helvetica", 12, "bold"))
        self._conc_detail.tag_configure("doc", foreground=_TEXT_MUTED, font=("Helvetica", 11))
        self._conc_detail.pack(fill="x", padx=22, pady=(0, 10))
        self._set_concordance_detail(None)

        # ── Datos de la extracción (tabla) ──
        data_hdr = ctk.CTkFrame(right, fg_color="transparent")
        data_hdr.pack(fill="x", padx=22, pady=(8, 4))
        ctk.CTkLabel(data_hdr, text="DATOS DE LA EXTRACCIÓN",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED,
                     ).pack(side="left")
        _help_icon(data_hdr, "\n\n".join(f"{k}: {v}" for k, v in _METRIC_HELP.items())
                   ).pack(side="left", padx=(4, 0))
        data_wrap = tk.Frame(right, bg=_BG_CARD)
        data_wrap.pack(fill="x", padx=22, pady=(0, 10))
        self._rev_data_cols = [("score", "Score", 70), ("tfidf", "TF-IDF", 70),
                               ("cval", "C-val", 70), ("ncval", "NC-val", 70),
                               ("freq", "Frec", 60), ("freqrel", "Frec/mil", 70),
                               ("docs", "Docs", 50), ("authors", "Autores", 60),
                               ("pattern", "Patrón", 160)]
        self._rev_data_tree = ttk.Treeview(data_wrap, style="TECLA.Treeview",
                                           columns=[c for c, _, _ in self._rev_data_cols],
                                           show="headings", selectmode="none", height=1)
        for cid, heading, width in self._rev_data_cols:
            self._rev_data_tree.heading(cid, text=heading)
            self._rev_data_tree.column(cid, width=width, minwidth=width,
                                       stretch=cid == "pattern",
                                       anchor="w" if cid == "pattern" else "e")
        self._rev_data_tree.pack(fill="x")

        # ── Notas ──
        ctk.CTkLabel(right, text="NOTAS",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED, anchor="w",
                     ).pack(fill="x", padx=22, pady=(8, 4))
        self._rev_notes = ctk.CTkTextbox(right, height=80,
                                          fg_color=_BG_CARD, text_color=_TEXT,
                                          border_width=1, border_color=_BORDER,
                                          font=ctk.CTkFont(size=12), corner_radius=6)
        self._rev_notes.pack(fill="x", padx=22, pady=(0, 8))
        ctk.CTkButton(right, text="💾  Guardar notas", height=32,
                      fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                      text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, command=self._save_review_notes,
                      ).pack(anchor="w", padx=22, pady=(0, 16))

    def _render_revision_list(self, _=None):
        for w in self._rev_term_btns.values():
            w.destroy()
        self._rev_term_btns = {}

        filter_val = self._rev_filter_var.get().lower()
        max_rows   = 300   # la lista se limita para que la interfaz no se bloquee
        omitted    = 0

        for t in self._results:
            term  = t["lemma"]
            entry = self._review_data.get(term, {"status": "pendiente", "notes": ""})
            if filter_val != "todos" and entry["status"] != filter_val:
                continue
            if len(self._rev_term_btns) >= max_rows:
                omitted += 1
                continue

            color = _STATUS_COLOR[entry["status"]]
            btn = ctk.CTkButton(
                self._rev_list_scroll,
                text=f"●  {display_form(t)}" + ("   · uso de autor/es" if entry.get("author_usage") else ""),
                anchor="w", height=28,
                fg_color="transparent",
                hover_color=_BG_CARD,
                text_color=color,
                font=ctk.CTkFont(size=11),
                command=lambda term=term: self._select_revision_term(term),
            )
            btn.pack(fill="x", pady=1)
            self._rev_term_btns[term] = btn

        if self._rev_more_label is not None:
            self._rev_more_label.destroy()
            self._rev_more_label = None
        if omitted:
            self._rev_more_label = ctk.CTkLabel(
                self._rev_list_scroll,
                text=f"Se muestran los {max_rows} primeros.\nQuedan {_miles(omitted)} más: usa el filtro.",
                text_color=_TEXT_MUTED, font=ctk.CTkFont(size=10), justify="left")
            self._rev_more_label.pack(anchor="w", padx=8, pady=8)

        self._update_review_counter()
        if not self._rev_term_btns:
            ctk.CTkLabel(self._rev_list_scroll, text="Sin términos.",
                         text_color=_TEXT_MUTED, font=ctk.CTkFont(size=11),
                         ).pack(pady=20)

    def _select_revision_term(self, term: str):
        self._rev_selected = term
        entry = self._review_data.setdefault(term, {"status": "pendiente", "notes": ""})

        t_shown = next((t for t in self._all_results if t["lemma"] == term), None)
        self._rev_term_label.configure(text=display_form(t_shown) if t_shown else term, text_color=_TEXT)

        # Resaltar botón de estado activo
        for s, btn in self._rev_status_btns.items():
            active = (s == entry["status"])
            btn.configure(
                fg_color=_STATUS_COLOR[s] if active else _BG_CARD2,
                text_color="#ffffff" if active else _STATUS_COLOR[s],
            )

        self._rev_author_var.set(bool(entry.get("author_usage")))

        # Notas
        self._rev_notes.delete("1.0", "end")
        self._rev_notes.insert("1.0", entry.get("notes", ""))

        # Datos del término
        t_data = next((t for t in self._all_results if t["lemma"] == term), None)
        self._rev_data_tree.delete(*self._rev_data_tree.get_children())
        if t_data:
            self._rev_data_tree.insert("", "end", values=(
                f"{t_data['terminologicity']:.4f}", f"{t_data.get('tf_idf', 0):.1f}",
                f"{t_data.get('c_value', 0):.2f}", f"{t_data.get('nc_value', 0):.2f}",
                t_data["frequency"], f"{t_data.get('freq_rel', 0):.2f}",
                t_data["doc_frequency"], len(self._authors_of(t_data)[0]) or "—",
                " / ".join(t_data.get("patterns", [])) or "—"))
            self._show_author_note(t_data)
            self._rv_forms_open = False
            self._render_forms(t_data)
            self._show_concordances(term, t_data)

    def _set_review_status(self, status: str):
        if not self._rev_selected:
            return
        self._review_data.setdefault(self._rev_selected, {"status": "pendiente", "notes": ""})
        self._review_data[self._rev_selected]["status"] = status

        for s, btn in self._rev_status_btns.items():
            active = (s == status)
            btn.configure(
                fg_color=_STATUS_COLOR[s] if active else _BG_CARD2,
                text_color="#ffffff" if active else _STATUS_COLOR[s],
            )

        # Actualizar color en la lista
        if self._rev_selected in self._rev_term_btns:
            self._rev_term_btns[self._rev_selected].configure(
                text_color=_STATUS_COLOR[status]
            )

        self._save_review_data()
        self._update_review_counter()

    def _render_forms(self, t_data):
        shown = display_form(t_data)
        forms = [f for f in surface_forms(t_data) if f != shown]
        lbl = self._rv["forms"]
        summary = variants_summary(t_data)
        if not forms:
            self._rv["variants"].configure(text=summary)
            lbl.pack_forget()
            return
        self._rv["variants"].configure(text=f"{summary}  {'▴' if self._rv_forms_open else '▾'}")
        if self._rv_forms_open:
            names = {"otra": "otra forma", "ortográfica": "otra grafía"}
            lbl.configure(text="\n".join(
                f"{f}   ({', '.join(names.get(k, k) for k in classify_variant(shown, f).split('+'))})"
                for f in forms))
            lbl.pack(fill="x", pady=(2, 0))
        else:
            lbl.pack_forget()

    def _toggle_forms(self):
        t_data = next((t for t in self._all_results if t["lemma"] == self._rev_selected), None)
        if t_data:
            self._rv_forms_open = not self._rv_forms_open
            self._render_forms(t_data)

    def _toggle_author_usage(self):
        if not self._rev_selected:
            self._rev_author_var.set(False)
            return
        entry = self._review_data.setdefault(self._rev_selected, {"status": "pendiente", "notes": ""})
        if self._rev_author_var.get():
            entry["author_usage"] = True
        else:
            entry.pop("author_usage", None)
        btn = self._rev_term_btns.get(self._rev_selected)
        if btn is not None:
            t_sel = next((t for t in self._all_results if t["lemma"] == self._rev_selected), None)
            btn.configure(text=f"●  {display_form(t_sel) if t_sel else self._rev_selected}"
                               + ("   · uso de autor/es" if entry.get("author_usage") else ""))
        self._save_review_data()
        self._update_review_counter()

    def _update_review_counter(self):
        terms = [t["lemma"] for t in self._results]
        status = [self._review_data.get(t, {}).get("status", "pendiente") for t in terms]
        done = sum(s != "pendiente" for s in status)
        n_author = sum(1 for t in terms if self._review_data.get(t, {}).get("author_usage"))
        frac = done / len(terms) if terms else 0
        self._rev_progress.set(frac)
        pct = 100 * frac
        self._rev_pct_label.configure(
            text=(f"{pct:.0f} %" if pct >= 1 or done == 0 else "< 1 %") if terms else "")
        self._rev_counter_label.configure(
            text=(f"Revisados: {_miles(done)} de {_miles(len(terms))}   ·   "
                  f"aprobados {_miles(status.count('aprobado'))}   ·   "
                  f"rechazados {_miles(status.count('rechazado'))}"
                  + (f"   ·   uso de autor/es {_miles(n_author)}" if n_author else "")) if terms else "")

    def _export_reviewed(self, fmt: str):
        wanted = {"aprobado", "rechazado"} if self._exp_rejected_var.get() else {"aprobado"}
        status_of = lambda t: self._review_data.get(t["lemma"], {}).get("status", "pendiente")
        approved = [t for t in self._all_results if status_of(t) in wanted]
        approved.sort(key=lambda t: status_of(t) != "aprobado")   # primero los aprobados
        if not approved:
            messagebox.showwarning("TECLA", "Todavía no hay candidatos aprobados." if wanted == {"aprobado"}
                                   else "Todavía no hay candidatos revisados.")
            return
        with_status = len(wanted) > 1
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), title="Exportar los términos revisados",
                                            defaultextension=f".{fmt}",
                                            filetypes=[(fmt.upper(), f"*.{fmt}")],
                                            initialfile=f"terminos_{'revisados' if with_status else 'aprobados'}.{fmt}")
        if not path:
            return
        fields = ["term", "lemma", "variants", "patterns", "terminologicity", "tf_idf",
                  "c_value", "nc_value", "frequency", "freq_rel", "doc_frequency"]
        def row(t):
            r = {k: t.get(k, "") for k in fields}
            r["term"] = display_form(t)
            r["variants"] = [f for f in surface_forms(t) if f != r["term"]]
            r["patterns"] = t.get("patterns", [])
            r["status"] = status_of(t)
            r["author_usage"] = bool(self._review_data.get(t["lemma"], {}).get("author_usage"))
            r["notes"] = self._review_data.get(t["lemma"], {}).get("notes", "")
            return r
        try:
            if fmt == "txt":
                Path(path).write_text("\n".join(
                    display_form(t) + (f"\t{status_of(t)}" if with_status else "")
                    for t in approved) + "\n", encoding="utf-8")
            elif fmt == "json":
                Path(path).write_text(json.dumps([row(t) for t in approved], ensure_ascii=False,
                                                 indent=2, default=float), encoding="utf-8")
            else:
                with open(path, "w", encoding="utf-8-sig", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=fields + ["status", "author_usage", "notes"])
                    w.writeheader()
                    for t in approved:
                        r = row(t)
                        r["variants"] = "; ".join(r["variants"])
                        r["patterns"] = "; ".join(r["patterns"])
                        r["author_usage"] = "sí" if r["author_usage"] else ""
                        w.writerow(r)
            n_ok = sum(status_of(t) == "aprobado" for t in approved)
            detail = (f"{n_ok} aprobados y {len(approved) - n_ok} rechazados" if with_status
                      else f"{n_ok} términos aprobados")
            messagebox.showinfo("TECLA", f"Exportados {detail} a:\n{path}")
        except Exception as e:
            messagebox.showerror("TECLA", f"Error al exportar:\n{e}")

    # ── Concordancias ──

    def _texts_folder(self):
        if self._clean_folder and Path(self._clean_folder).exists():
            return Path(self._clean_folder)
        base = Path(self.corpus_path_var.get() or ".") / _OUTPUT_DIR / "textos"
        clean = base / "clean"
        return clean if clean.exists() else base

    def _load_conc_texts(self):
        texts = {}
        try:
            for p in sorted(self._texts_folder().rglob("*.txt")):
                texts[p.stem] = re.sub(r"\s+", " ", p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
        self._conc_texts, self._conc_loading = texts, False
        self.after(0, lambda: self._rev_selected and self._select_revision_term(self._rev_selected))

    def _doc_label(self, doc_id: str) -> str:
        """Forma corta del documento: «Casas Gómez (2023)», a partir de los metadatos
        o, si no los hay, del nombre del archivo («Autor_Año_Título»)."""
        meta = self._corpus_metadata.get(doc_id, {})
        author, year = (meta.get("autor") or "").strip(), (meta.get("año") or "").strip()
        if not author:
            parts = doc_id.split("_")
            author = parts[0] if parts else doc_id
            year = year or (parts[1] if len(parts) > 1 and parts[1][:4].isdigit() else "")
        author = re.sub(r"\s*\((coords?|eds?|dirs?)\.?\)", "", author)
        people = [p.strip() for p in re.split(r"\s+y\s+|\s*;\s*|\s+and\s+|\s*&\s*", author) if p.strip()]
        surnames = [p.split(",")[0].strip() for p in people]
        short = f"{surnames[0]} et al." if len(surnames) > 2 else (" y ".join(surnames) or doc_id)
        return f"{short} ({year})" if year and year.lower() != "xxx" else short

    def _doc_authors(self, doc_id: str) -> list:
        """Apellidos de los autores de un documento (metadatos o nombre de archivo)."""
        meta = self._corpus_metadata.get(doc_id, {})
        author = (meta.get("autor") or "").strip() or doc_id.split("_")[0]
        author = re.sub(r"\s*\((coords?|eds?|dirs?)\.?\)", "", author)
        people = [p.strip() for p in re.split(r"\s+y\s+|\s*;\s*|\s+and\s+|\s*&\s*", author) if p.strip()]
        return [p.split(",")[0].strip() for p in people if p.split(",")[0].strip()]

    def _authors_of(self, t) -> tuple:
        """(autores que lo emplean, autores presentes en todos sus documentos).
        Cuenta los documentos de la extracción y, si ya se han buscado, también
        aquellos en que aparece cualquier forma del término en las concordancias."""
        docs = set((t.get("per_doc") or {}).keys())
        docs |= {name for name, _, _ in self._conc_cache.get(t.get("lemma"), [])}
        sets = [set(self._doc_authors(d)) for d in docs]
        sets = [x for x in sets if x]
        if not sets:
            return set(), set()
        return set().union(*sets), set.intersection(*sets)

    def _show_author_note(self, t):
        authors, shared = self._authors_of(t)
        ndocs = len(set((t.get("per_doc") or {}).keys())
                    | {n for n, _, _ in self._conc_cache.get(t.get("lemma"), [])})
        note = ""
        who = " y ".join(sorted(shared))
        whose = "de ese autor" if len(shared) == 1 else "de esos autores"
        if shared and ndocs == 1:
            note = f"!  Solo aparece en un documento, de {who}: puede ser un uso propio {whose}."
        elif shared and len(authors) <= len(shared) + 1:
            note = (f"!  Todas sus apariciones están en textos de {who}: "
                    f"puede ser un uso propio {whose}.")
        self._rv["author_note"].configure(text=note)

    def _show_concordances(self, term, t_data):
        if self._conc_texts is None:
            if not self._conc_loading:
                self._conc_loading = True
                threading.Thread(target=self._load_conc_texts, daemon=True).start()
            self._conc_shown = []
            self._write_concordances([], "Cargando los textos del corpus…")
            return
        if term not in self._conc_cache:
            forms = {term, *surface_forms(t_data)}
            forms = sorted({f.strip() for f in forms if f and f.strip()}, key=len, reverse=True)
            pat = re.compile(r"(?<!\w)(" + "|".join(re.escape(f) for f in forms) + r")(?!\w)", re.I)
            self._conc_cache[term] = [(name, m.start(), m.end())
                                      for name, text in self._conc_texts.items()
                                      for m in pat.finditer(text)]
        hits = self._conc_cache[term]
        docs = Counter(name for name, _, _ in hits)
        self._conc_doc_map = {f"{self._doc_label(d)} · {n}": d for d, n in docs.items()}
        self._conc_doc_menu.configure(
            values=["Todos los documentos"] + [f"{self._doc_label(d)} · {n}" for d, n in docs.most_common()])
        self._conc_doc_var.set("Todos los documentos")
        self._set_concordance_detail(None)
        self._refresh_concordances()
        self._show_author_note(t_data)

    def _context(self, name, start, end, width=70):
        """Contexto izquierdo y derecho sin cortar palabras."""
        text = self._conc_texts[name]
        left = text[max(0, start - width):start]
        if start - width > 0 and " " in left:
            left = "… " + left.split(" ", 1)[1]
        right = text[end:end + width]
        if end + width < len(text) and " " in right:
            right = right.rsplit(" ", 1)[0] + " …"
        return left, text[start:end], right

    def _refresh_concordances(self):
        term = self._rev_selected
        if not term or self._conc_texts is None or term not in self._conc_cache:
            return
        all_hits = self._conc_cache[term]
        doc = self._conc_doc_map.get(self._conc_doc_var.get())
        hits = [h for h in all_hits if h[0] == doc] if doc else list(all_hits)
        words = lambda s: re.findall(r"\w+", s.lower())
        order = self._conc_sort_var.get()
        if order == "anterior":
            hits.sort(key=lambda h: words(self._conc_texts[h[0]][max(0, h[1] - 80):h[1]])[::-1])
        elif order == "siguiente":
            hits.sort(key=lambda h: words(self._conc_texts[h[0]][h[2]:h[2] + 80]))
        shown = hits[:_CONC_MAX]
        ndocs = len({h[0] for h in all_hits})
        if not all_hits:
            info = "Sin apariciones en los textos"
        else:
            info = f"{_miles(len(all_hits))} apariciones en {ndocs} documento{'s' if ndocs != 1 else ''}"
            if doc:
                info += f" · {len(hits)} en este"
            if len(hits) > len(shown):
                info += f" · se muestran {len(shown)}"
        self._conc_shown = shown
        self._write_concordances([(*self._context(*h), h[0]) for h in shown], info)

    def _export_concordances(self):
        term = self._rev_selected
        if not term or self._conc_texts is None:
            messagebox.showwarning("TECLA", "Selecciona primero un candidato.")
            return
        t_data = next((t for t in self._all_results if t["lemma"] == term), {"term": term})
        forms = {term, *surface_forms(t_data)}
        forms = sorted({f.strip() for f in forms if f and f.strip()}, key=len, reverse=True)
        pat = re.compile(r"(?<!\w)(" + "|".join(re.escape(f) for f in forms) + r")(?!\w)", re.I)
        rows = [(self._doc_label(name), name,
                 *(c.strip(" …") for c in self._context(name, m.start(), m.end(), 120)))
                for name, text in self._conc_texts.items() for m in pat.finditer(text)]
        if not rows:
            messagebox.showwarning("TECLA", "Este candidato no tiene apariciones en los textos.")
            return
        safe = re.sub(r"[^\w-]+", "_", term).strip("_") or "termino"
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), title="Exportar concordancias",
                                            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile=f"concordancias_{safe}.csv")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["documento", "archivo", "contexto_izquierdo", "forma", "contexto_derecho"])
                w.writerows(rows)
            messagebox.showinfo("TECLA", f"Exportadas {len(rows)} concordancias a:\n{path}")
        except Exception as e:
            messagebox.showerror("TECLA", f"Error al exportar:\n{e}")

    def _write_concordances(self, lines, info):
        self._conc_info.configure(text=info)
        txt = self._conc_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        for i, (left, kw, right, doc) in enumerate(lines):
            start = txt.index("end-1c")
            txt.insert("end", f"{left:>72} ")
            txt.insert("end", kw, "kw")
            txt.insert("end", f" {right:<72}   ")
            txt.insert("end", self._doc_label(doc) + "\n", "doc")
            if i % 2:
                txt.tag_add("even", start, txt.index("end-1c"))
        txt.configure(state="disabled")

    def _on_concordance_click(self, event):
        if self._conc_texts is None:
            return
        line = int(self._conc_text.index(f"@{event.x},{event.y}").split(".")[0]) - 1
        if not (0 <= line < len(self._conc_shown)):
            return
        self._conc_text.tag_remove("sel_line", "1.0", "end")
        self._conc_text.tag_add("sel_line", f"{line + 1}.0", f"{line + 2}.0")
        name, start, end = self._conc_shown[line]
        text = self._conc_texts[name]
        a = max(text.rfind(". ", 0, start), text.rfind("? ", 0, start), text.rfind("! ", 0, start))
        a = a + 2 if a >= 0 and start - a < 600 else max(0, start - 300)
        ends = [i for i in (text.find(". ", end), text.find("? ", end), text.find("! ", end)) if i >= 0]
        b = min(ends) + 1 if ends and min(ends) - end < 600 else min(len(text), end + 300)
        self._set_concordance_detail((text[a:start], text[start:end], text[end:b], name))

    def _set_concordance_detail(self, data):
        box = self._conc_detail
        box.configure(state="normal")
        box.delete("1.0", "end")
        if data is None:
            box.insert("end", "Pulsa una línea para ver la oración completa.", "doc")
        else:
            left, kw, right, name = data
            box.insert("end", f"{self._doc_label(name)}   ", "doc")
            box.insert("end", left)
            box.insert("end", kw, "kw")
            box.insert("end", right)
        box.configure(state="disabled")

    # ── Revisión guardada ──

    def _candidates_path(self):
        workdir = self.corpus_path_var.get()
        return Path(workdir) / _OUTPUT_DIR / "candidatos.json" if workdir else None

    def _corpus_signature(self):
        folder = Path(self.corpus_path_var.get()) / "corpus"
        try:
            return sorted(f"{p.name}|{p.stat().st_size}" for p in folder.iterdir()
                          if p.is_file() and not p.name.startswith("."))
        except OSError:
            return []

    def _save_candidates(self, results):
        try:
            data = {"version": 1, "saved_at": datetime.now().isoformat(timespec="minutes"),
                    "language": self.language_var.get(), "corpus": self._corpus_signature(),
                    "results": results}
            (self._output_dir() / "candidatos.json").write_text(
                json.dumps(data, ensure_ascii=False, default=float), encoding="utf-8")
        except Exception as e:
            self._log(f"⚠  No se pudieron guardar los candidatos: {e}")

    def _offer_resume(self):
        f = self._candidates_path()
        if self._all_results or self._running or not f or not f.exists():
            return
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results = data.get("results") or []
        except Exception:
            return
        if not results:
            return
        self._load_review_data()
        status = [self._review_data.get(t["lemma"], {}).get("status", "pendiente") for t in results]
        done = sum(s != "pendiente" for s in status)
        try:
            saved = datetime.fromisoformat(data.get("saved_at", "")).strftime("%d/%m/%Y, %H:%M")
        except ValueError:
            saved = "—"
        changed = data.get("corpus") and data.get("corpus") != self._corpus_signature()

        win = ctk.CTkToplevel(self)
        win.title("TECLA")
        win.configure(fg_color=_BG_CARD)
        win.resizable(False, False)
        win.transient(self)
        ctk.CTkLabel(win, text="Hay una revisión en curso en esta carpeta",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=_TEXT,
                     ).pack(anchor="w", padx=24, pady=(20, 6))
        pl = lambda n, w: f"{_miles(n)} {w}{'' if n == 1 else 's'}"
        ctk.CTkLabel(win, text=(f"Llevas {pl(done, 'candidato')} revisado{'' if done == 1 else 's'} "
                                f"({pl(status.count('aprobado'), 'aprobado')}, "
                                f"{pl(status.count('rechazado'), 'rechazado')}).\n"
                                f"Extracción guardada el {saved}."),
                     font=ctk.CTkFont(size=12), text_color=_TEXT, justify="left",
                     ).pack(anchor="w", padx=24)
        if changed:
            ctk.CTkLabel(win, text=("⚠  El corpus ha cambiado desde entonces (hay documentos nuevos, "
                                    "eliminados o modificados). Puedes continuar, pero conviene volver "
                                    "a ejecutar la extracción: tus decisiones se conservan."),
                         font=ctk.CTkFont(size=11), text_color="#b45309", justify="left",
                         wraplength=440).pack(anchor="w", padx=24, pady=(10, 0))
        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(18, 20))

        def resume():
            win.destroy()
            self._restore_results(results)

        def restart():
            if not messagebox.askyesno(
                    "TECLA", "¿Quieres archivar la revisión guardada y empezar una nueva?\n\n"
                             "No se borra nada: se guarda una copia en la carpeta _tecla_output.",
                    parent=win):
                return
            stamp = datetime.now().strftime("%Y%m%d-%H%M")
            out = f.parent
            for name in ("revision.json", "candidatos.json"):
                p = out / name
                if p.exists():
                    p.rename(out / f"{p.stem}_archivada_{stamp}.json")
            self._review_data = {}
            win.destroy()

        ctk.CTkButton(btns, text="Continuar la revisión", height=34, corner_radius=8,
                      fg_color=_ACCENT, hover_color=_ACCENT_DIM, text_color="#ffffff",
                      font=ctk.CTkFont(size=12, weight="bold"), command=resume,
                      ).pack(side="right")
        ctk.CTkButton(btns, text="Empezar de nuevo", height=34, corner_radius=8,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2, border_width=1,
                      border_color=_BORDER, text_color=_TEXT_MUTED,
                      font=ctk.CTkFont(size=12), command=restart,
                      ).pack(side="right", padx=(0, 8))
        win.after(50, win.grab_set)

    def _restore_results(self, results):
        self._all_results = results
        self._eval_done = False
        self._conc_texts, self._conc_cache = None, {}
        self._load_review_data()
        try:
            self._load_corpus_metadata()
        except Exception:
            pass
        self._apply_filters(notify=False)
        self._render_revision_list()
        self._tabview.mark_done("Extracción", True)
        self._tabview.set("Revisión")
        self._log("Revisión retomada con la extracción guardada. Para evaluar el corpus, "
                  "vuelve a ejecutar la extracción.")

    def _save_review_notes(self):
        if not self._rev_selected:
            return
        notes = self._rev_notes.get("1.0", "end").strip()
        self._review_data.setdefault(self._rev_selected, {"status": "pendiente", "notes": ""})
        self._review_data[self._rev_selected]["notes"] = notes
        self._save_review_data()

    # ═══════════════════════════════════════════
    # Pestaña 5 — Evaluación
    # ═══════════════════════════════════════════

    def _build_tab_evaluacion(self):
        tab = self._tabview.tab("Evaluación")
        _tab_header(tab, "Evaluación del corpus",
                    "Métricas de representatividad: ¿es el corpus suficientemente rico y equilibrado?")

        # ── BLOQUE SUPERIOR: gráficos (ancho completo) ──
        self._eval_graph_frame = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=8,
                                              border_width=1, border_color=_BORDER)
        self._eval_graph_frame.pack(fill="x", padx=18, pady=(4, 8))
        _placeholder(self._eval_graph_frame,
                     "Realiza una extracción para ver la evaluación del corpus.")

        # ── BLOQUE INFERIOR: métricas en 3 columnas ──
        metrics_row = ctk.CTkFrame(tab, fg_color="transparent")
        metrics_row.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        # Columna izquierda: puntuación IRT + bootstrap (ancho fijo)
        left_col = ctk.CTkFrame(metrics_row, fg_color="transparent", width=300)
        left_col.pack(side="left", fill="y", padx=(0, 8))
        left_col.pack_propagate(False)

        # Columna central: tabla DP (flexible)
        mid_col = ctk.CTkFrame(metrics_row, fg_color="transparent")
        mid_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Columna derecha: keyness (flexible)
        right_col = ctk.CTkFrame(metrics_row, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # ── Tarjeta de puntuación ──
        score_card = ctk.CTkFrame(left_col, fg_color=_BG_CARD, corner_radius=10,
                                  border_width=1, border_color=_BORDER)
        score_card.pack(fill="x", pady=(0, 8))

        score_inner = ctk.CTkFrame(score_card, fg_color="transparent")
        score_inner.pack(fill="x", padx=14, pady=12)

        # Fila: etiqueta "Índice IRT" con (?)
        itr_row = ctk.CTkFrame(score_inner, fg_color="transparent")
        itr_row.pack(anchor="w")
        ctk.CTkLabel(itr_row, text="Representatividad terminológica",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_TEXT_MUTED).pack(side="left")
        _help_icon(itr_row,
                   "Índice de representatividad terminológica (IRT).\n\n"
                   "Puntuación de 0 a 100 que resume la calidad del corpus para extraer "
                   "terminología. Es la media de la saturación léxica (Heaps), la proporción "
                   "de hápax, la dispersión de los candidatos entre documentos y, si se calcula, "
                   "la estabilidad bootstrap.\n\n"
                   "≥ 75: muy representativo\n"
                   "60–74: representativo\n"
                   "40–59: moderadamente representativo\n"
                   "25–39: poco representativo\n"
                   "< 25: escasamente representativo"
                   ).pack(side="left", padx=(4, 0))

        # Número grande + "/100" en la misma fila
        num_row = ctk.CTkFrame(score_inner, fg_color="transparent")
        num_row.pack(anchor="w")
        self._eval_score_num = ctk.CTkLabel(
            num_row, text="—",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color=_TEXT_MUTED,
        )
        self._eval_score_num.pack(side="left")
        ctk.CTkLabel(num_row, text=" / 100",
                     font=ctk.CTkFont(size=14),
                     text_color=_TEXT_MUTED).pack(side="left", pady=(12, 0))

        self._eval_score_label = ctk.CTkLabel(
            score_inner, text="Realiza una extracción",
            font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED, wraplength=280, justify="left",
        )
        self._eval_score_label.pack(anchor="w", pady=(2, 0))

        self._eval_description = ctk.CTkLabel(
            score_inner, text="",
            font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
            wraplength=280, justify="left", anchor="w",
        )
        self._eval_description.pack(fill="x", pady=(4, 0))

        # Escala visual (canvas)
        scale_row = ctk.CTkFrame(score_inner, fg_color="transparent")
        scale_row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(scale_row, text="escasamente",
                     font=ctk.CTkFont(size=9), text_color=_TEXT_MUTED,
                     ).pack(side="left")
        self._eval_scale_canvas = tk.Canvas(scale_row, height=14, bg=_BG_CARD,
                                            highlightthickness=0)
        self._eval_scale_canvas.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkLabel(scale_row, text="muy representativo",
                     font=ctk.CTkFont(size=9), text_color="#16a34a",
                     ).pack(side="left")

        self._eval_components_label = ctk.CTkLabel(
            score_inner, text="",
            font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
            anchor="w", justify="left",
        )
        self._eval_components_label.pack(fill="x", pady=(4, 0))

        # Botón calcular representatividad (fast eval + bootstrap)
        btn_row = ctk.CTkFrame(score_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 10))
        self._eval_btn = ctk.CTkButton(
            btn_row, text="Calcular representatividad",
            width=240, height=28,
            fg_color=_ACCENT, hover_color=_ACCENT_DIM,
            text_color="#ffffff", font=ctk.CTkFont(size=11, weight="bold"),
            state="disabled",
            command=self._start_full_eval,
        )
        self._eval_btn.pack(side="left")
        self._eval_stability_label = ctk.CTkLabel(
            btn_row, text="",
            font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED,
        )
        self._eval_stability_label.pack(side="left", padx=(12, 0))

        # ── Tabla de resultados por prueba ──
        tests_card = ctk.CTkFrame(left_col, fg_color=_BG_CARD, corner_radius=10,
                                  border_width=1, border_color=_BORDER)
        tests_card.pack(fill="x", pady=(0, 8))
        tests_hdr = ctk.CTkFrame(tests_card, fg_color="transparent")
        tests_hdr.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(tests_hdr, text="Resultados por prueba",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_TEXT_MUTED).pack(side="left")
        _help_icon(tests_hdr, _EVAL_TESTS_HELP).pack(side="left", padx=(4, 0))
        self._eval_csv_btn = ctk.CTkButton(
            tests_hdr, text="⬇  CSV", width=64, height=22,
            fg_color="transparent", hover_color=_BG_CARD2,
            border_width=1, border_color=_ACCENT, text_color=_ACCENT,
            font=ctk.CTkFont(size=10), state="disabled",
            command=self._export_eval_csv)
        self._eval_csv_btn.pack(side="right")
        tests_wrap = tk.Frame(tests_card, bg=_BG_CARD)
        tests_wrap.pack(fill="x", padx=10, pady=(0, 10))
        self._eval_tests_tree = ttk.Treeview(
            tests_wrap, style="TECLA.Treeview", columns=("prueba", "valor", "puntos"),
            show="headings", selectmode="none", height=4)
        for cid, heading, width, anchor in [("prueba", "Prueba", 92, "w"),
                                            ("valor", "Valor", 120, "w"),
                                            ("puntos", "Puntos", 50, "e")]:
            self._eval_tests_tree.heading(cid, text=heading)
            self._eval_tests_tree.column(cid, width=width, minwidth=width, stretch=False,
                                         anchor=anchor)
        self._eval_tests_tree.tag_configure("odd", background=_ROW_ODD, foreground=_TEXT)
        self._eval_tests_tree.tag_configure("even", background=_ROW_EVEN, foreground=_TEXT)
        self._eval_tests_tree.pack(fill="x")

        # ── Tarjeta de cobertura externa ──────────────────────────────────
        cov_card = ctk.CTkFrame(left_col, fg_color=_BG_CARD, corner_radius=10,
                                border_width=1, border_color=_BORDER)
        cov_card.pack(fill="x", pady=(0, 8))

        cov_inner = ctk.CTkFrame(cov_card, fg_color="transparent")
        cov_inner.pack(fill="x", padx=14, pady=(10, 4))

        cov_hdr = ctk.CTkFrame(cov_inner, fg_color="transparent")
        cov_hdr.pack(anchor="w")
        ctk.CTkLabel(cov_hdr, text="Cobertura vs. lista de referencia",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_TEXT_MUTED).pack(side="left")
        _help_icon(cov_hdr,
                   "Lista de referencia terminológica (opcional)\n\n"
                   "Carga un CSV con columna 'term' que contenga los términos\n"
                   "esenciales del dominio (glosario, IATE, terminología publicada…).\n\n"
                   "TECLA calculará qué porcentaje de esos términos aparece\n"
                   "en los candidatos extraídos del corpus (recall).\n\n"
                   "Un recall alto indica que el corpus cubre el vocabulario\n"
                   "nuclear del dominio. Es completamente opcional: sin lista\n"
                   "cargada el IRT se calcula igualmente con las otras métricas."
                   ).pack(side="left", padx=(4, 0))

        self._cov_status_label = ctk.CTkLabel(
            cov_inner, text="Sin lista cargada",
            font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
            anchor="w",
        )
        self._cov_status_label.pack(fill="x", pady=(6, 0))

        cov_btn_row = ctk.CTkFrame(cov_inner, fg_color="transparent")
        cov_btn_row.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(
            cov_btn_row, text="Cargar lista…",
            width=120, height=24,
            fg_color="transparent", hover_color=_BG_CARD2,
            border_width=1, border_color=_ACCENT,
            text_color=_ACCENT, font=ctk.CTkFont(size=10),
            command=self._load_gold_list,
        ).pack(side="left")
        self._cov_clear_btn = ctk.CTkButton(
            cov_btn_row, text="Quitar",
            width=60, height=24,
            fg_color="transparent", hover_color=_BG_CARD2,
            border_width=1, border_color=_BORDER,
            text_color=_TEXT_MUTED, font=ctk.CTkFont(size=10),
            command=self._clear_gold_list,
            state="disabled",
        )
        self._cov_clear_btn.pack(side="left", padx=(6, 0))

        self._cov_result_label = ctk.CTkLabel(
            cov_inner, text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=_TEXT_MUTED, anchor="w",
        )
        self._cov_result_label.pack(fill="x", pady=(6, 0))

        self._cov_detail_label = ctk.CTkLabel(
            cov_inner, text="",
            font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
            anchor="w", justify="left", wraplength=265,
        )
        self._cov_detail_label.pack(fill="x", pady=(2, 8))

        # ── Columna central: tabla DP ──
        dp_card = ctk.CTkFrame(mid_col, fg_color=_BG_CARD, corner_radius=8,
                               border_width=1, border_color=_BORDER)
        dp_card.pack(fill="both", expand=True)

        dp_hdr = ctk.CTkFrame(dp_card, fg_color="transparent")
        dp_hdr.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(dp_hdr, text="Candidatos — dispersión (DP de Gries)",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=_TEXT,
                     ).pack(side="left")
        _help_icon(dp_hdr,
                   "Dispersión de Gries (DP)\n\n"
                   "Mide cómo de repartido está un candidato entre los documentos del corpus. "
                   "Va de 0 a 1:\n\n"
                   "DP ≈ 0 → el candidato aparece de forma uniforme en todos los documentos "
                   "(bien representado, fiable).\n"
                   "DP ≈ 1 → el candidato está concentrado en uno o pocos documentos "
                   "(puede ser ruido o jerga de un solo autor).\n\n"
                   "Se muestran los 50 candidatos con mayor terminologicidad."
                   ).pack(side="left", padx=(4, 0))

        dp_wrap = tk.Frame(dp_card, bg=_BG_ROOT)
        dp_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._eval_dp_tree = ttk.Treeview(
            dp_wrap,
            style="TECLA.Treeview",
            columns=("num", "term", "freq", "docs", "dp"),
            show="headings",
            selectmode="none",
            height=7,
        )
        for cid, heading, width, stretch, anchor in [
            ("num",  "#",        40,  False, "e"),
            ("term", "Candidato", 200,  True,  "w"),
            ("freq", "Frec",     60,  False, "e"),
            ("docs", "Docs",     50,  False, "e"),
            ("dp",   "DP",       60,  False, "e"),
        ]:
            self._eval_dp_tree.heading(cid, text=heading)
            self._eval_dp_tree.column(cid, width=width, stretch=stretch,
                                      anchor=anchor, minwidth=width)
        self._eval_dp_tree.tag_configure("odd",  background=_ROW_ODD,  foreground=_TEXT)
        self._eval_dp_tree.tag_configure("even", background=_ROW_EVEN, foreground=_TEXT)
        dp_vsb = tk.Scrollbar(dp_wrap, orient="vertical", command=self._eval_dp_tree.yview,
                              bg=_BG_ROOT, troughcolor=_BG_CARD, width=10)
        self._eval_dp_tree.configure(yscrollcommand=dp_vsb.set)
        dp_vsb.pack(side="right", fill="y")
        self._eval_dp_tree.pack(side="left", fill="both", expand=True)

        # ── Columna derecha: keyness ──
        kn_card = ctk.CTkFrame(right_col, fg_color=_BG_CARD, corner_radius=8,
                               border_width=1, border_color=_BORDER)
        kn_card.pack(fill="both", expand=True)

        kn_hdr = ctk.CTkFrame(kn_card, fg_color="transparent")
        kn_hdr.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(kn_hdr, text="Keyness (G²) vs corpus de referencia",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=_TEXT,
                     ).pack(side="left")
        ctk.CTkButton(
            kn_hdr, text="Cargar referencia…", width=130, height=24,
            fg_color="transparent", hover_color=_BG_CARD2,
            border_width=1, border_color=_ACCENT,
            text_color=_ACCENT, font=ctk.CTkFont(size=10),
            command=self._load_reference_corpus,
        ).pack(side="right")

        kn_wrap = tk.Frame(kn_card, bg=_BG_ROOT)
        kn_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._eval_kn_tree = ttk.Treeview(
            kn_wrap,
            style="TECLA.Treeview",
            columns=("num", "term", "freq", "fref", "g2", "lr", "dir"),
            show="headings",
            selectmode="none",
            height=7,
        )
        for cid, heading, width, stretch, anchor in [
            ("num",  "#",       40,  False, "e"),
            ("term", "Término",180,  True,  "w"),
            ("freq", "Frec",    55,  False, "e"),
            ("fref", "Ref",     55,  False, "e"),
            ("g2",   "G²",      65,  False, "e"),
            ("lr",   "LogRat",  60,  False, "e"),
            ("dir",  "Dir",     32,  False, "c"),
        ]:
            self._eval_kn_tree.heading(cid, text=heading)
            self._eval_kn_tree.column(cid, width=width, stretch=stretch,
                                      anchor=anchor, minwidth=width)
        self._eval_kn_tree.tag_configure("odd",  background=_ROW_ODD,  foreground=_TEXT)
        self._eval_kn_tree.tag_configure("even", background=_ROW_EVEN, foreground=_TEXT)
        kn_vsb = tk.Scrollbar(kn_wrap, orient="vertical", command=self._eval_kn_tree.yview,
                              bg=_BG_ROOT, troughcolor=_BG_CARD, width=10)
        self._eval_kn_tree.configure(yscrollcommand=kn_vsb.set)
        kn_vsb.pack(side="right", fill="y")
        self._eval_kn_tree.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(kn_card, text="Carga un CSV con columnas 'lemma' y 'frequency'.",
                     font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
                     ).pack(padx=10, pady=(0, 6))

    # ── Evaluación completa (bajo demanda) ──

    def _start_full_eval(self):
        if self._eval_running or not self._results or not self._doc_stats:
            return
        self._eval_running = True
        self._eval_btn.configure(state="disabled", text="Calculando métricas…")
        self._eval_stability_label.configure(text="")
        threading.Thread(target=self._full_eval_thread, daemon=True).start()

    def _full_eval_thread(self):
        try:
            from tecla.evaluation.corpus_metrics import (
                compute_bootstrap_stability,
                compute_heaps, compute_hapax_ratio,
                compute_dp, dp_stats,
                compute_representativity_score,
            )

            # ── Fase 1: métricas rápidas ──────────────────────────────────
            heaps     = compute_heaps(self._documents)
            hapax     = compute_hapax_ratio(self._documents)
            dp_scores = compute_dp(self._results, self._doc_stats)
            dp_sum    = dp_stats(dp_scores, self._results)
            rep_fast  = compute_representativity_score(heaps, hapax, dp_sum)
            self._eval_raw = {"heaps": heaps, "hapax": hapax, "dp": dp_sum}
            self.after(0, self._render_eval_fast, heaps, dp_scores, rep_fast)
            self.after(0, lambda: self._eval_btn.configure(
                text="Calculando estabilidad (bootstrap)…"))

            # ── Fase 2: bootstrap (más lento) ─────────────────────────────
            stability = compute_bootstrap_stability(self._results, self._doc_stats)
            rep = compute_representativity_score(heaps, hapax, dp_sum, stability=stability)
            self.after(0, self._render_bootstrap_results, stability, rep)

            # ── Fase 3: cobertura externa (solo si hay lista cargada) ──────
            if self._gold_terms:
                self.after(0, self._compute_and_render_coverage)

        except Exception as exc:
            self.after(0, self._log, f"[Evaluación] {exc}")
        finally:
            self._eval_running = False
            self.after(0, lambda: self._eval_btn.configure(
                state="normal", text="Recalcular representatividad"))

    def _render_eval_fast(self, heaps, dp_scores, rep):
        self._eval_done = True
        self._tabview.mark_done("Evaluación")
        score = rep["score"]
        label = rep["label"]
        color = rep["color"]

        # Score card
        self._eval_score_num.configure(text=f"{score}", text_color=color)
        self._eval_score_label.configure(
            text=f"El corpus es {label}",
            text_color=color,
        )
        self._eval_description.configure(
            text=rep.get("description", ""), text_color=_TEXT,
        )

        # Componentes: en la tabla de resultados por prueba
        self._eval_rep = rep
        self._update_eval_table()

        # Barra de escala
        self._draw_eval_scale(score, color)

        # DP scores guardados para bootstrap
        self._eval_dp_scores = dp_scores

        # Tabla DP — top 50 términos, ordenados por terminologicidad
        self._eval_dp_tree.delete(*self._eval_dp_tree.get_children())
        top_terms = sorted(self._results,
                           key=lambda t: t["terminologicity"], reverse=True)[:50]
        for i, t in enumerate(top_terms, 1):
            dp_val = dp_scores.get(t["lemma"], None)
            dp_str = f"{dp_val:.3f}" if dp_val is not None else "—"
            tag = "odd" if i % 2 else "even"
            self._eval_dp_tree.insert("", "end", tags=(tag,), values=(
                f"{i}.", t["lemma"], t["frequency"], t["doc_frequency"], dp_str,
            ))

        # Gráficos
        self._render_eval_graphs(heaps, dp_scores)

    def _eval_rows(self):
        """Filas de la tabla de resultados por prueba: (prueba, valor, puntos, qué indica)."""
        num = lambda x, nd=2: f"{x:.{nd}f}".replace(".", ",")
        comp = (self._eval_rep or {}).get("components", {})
        heaps, hapax, dp = (self._eval_raw.get(k) or {} for k in ("heaps", "hapax", "dp"))
        stab = (self._eval_stab or {}).get("stability_index")
        rows = []
        if heaps.get("beta") is not None:
            rows.append(("Saturación", f"β de Heaps = {num(heaps['beta'])}", comp.get("saturación"),
                         "Velocidad a la que crece el vocabulario al añadir textos"))
        if hapax:
            rows.append(("Hápax", f"{num(100 * hapax.get('ratio', 0), 1)} % de los tipos",
                         comp.get("hápax léxico"), "Palabras distintas que aparecen una sola vez"))
        if dp:
            rows.append(("Dispersión", f"DP medio = {num(dp.get('mean', 0))}", comp.get("dispersión"),
                         "Reparto de los candidatos entre los documentos"))
        rows.append(("Estabilidad", f"{round(100 * stab)} % (remuestreo)" if stab is not None
                     else "calculando…" if self._eval_running else "—",
                     comp.get("estabilidad"), "Candidatos principales que se mantienen al remuestrear"))
        return rows

    def _update_eval_table(self):
        tree = self._eval_tests_tree
        tree.delete(*tree.get_children())
        for i, (name, value, pts, _) in enumerate(self._eval_rows(), 1):
            tree.insert("", "end", tags=("odd" if i % 2 else "even",),
                        values=(name, value, "—" if pts is None else pts))
        self._eval_csv_btn.configure(state="normal" if self._eval_rep else "disabled")

    def _export_eval_csv(self):
        if not self._eval_rep:
            return
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), title="Exportar la evaluación del corpus",
                                            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="evaluacion_corpus.csv")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["prueba", "valor", "puntuacion_0_100", "que_indica"])
                for name, value, pts, what in self._eval_rows():
                    w.writerow([name, value, "" if pts is None else pts, what])
                w.writerow(["Índice de representatividad terminológica", self._eval_rep.get("label", ""),
                            self._eval_rep.get("score", ""), "Media de las pruebas anteriores"])
            messagebox.showinfo("TECLA", f"Evaluación exportada a:\n{path}")
        except Exception as e:
            messagebox.showerror("TECLA", f"Error al exportar:\n{e}")

    def _draw_eval_scale(self, score: int, color: str):
        c = self._eval_scale_canvas
        c.update_idletasks()
        w = c.winfo_width() or 300
        h = 14
        # Gradiente de 5 bloques
        segments = [
            (0,   35,  "#dc2626"),
            (35,  50,  "#ea580c"),
            (50,  65,  "#d97706"),
            (65,  80,  "#65a30d"),
            (80,  100, "#16a34a"),
        ]
        c.delete("all")
        for lo, hi, seg_col in segments:
            x0 = int(lo / 100 * w)
            x1 = int(hi / 100 * w)
            c.create_rectangle(x0, 2, x1, h - 2, fill=seg_col, outline="")
        # Marcador
        mx = int(score / 100 * w)
        c.create_polygon(mx - 5, 0, mx + 5, 0, mx, h, fill=color, outline="white", width=1)

    def _render_eval_graphs(self, heaps, dp_scores):
        for w in self._eval_graph_frame.winfo_children():
            w.destroy()

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            _placeholder(self._eval_graph_frame,
                         "Instala matplotlib para generar los gráficos:\npip install matplotlib")
            return

        out_dir = self._evaluation_graphs_dir()
        has_entropy = False

        def _style(ax):
            ax.set_facecolor(_BG_CARD)
            ax.tick_params(colors=_TEXT, labelsize=8)
            for sp in ax.spines.values():
                sp.set_color(_BORDER)

        saved_files = []

        # ────────────────────────────────────────────────────────────
        # 1. LEY DE HEAPS — saturación del vocabulario
        # ────────────────────────────────────────────────────────────
        fig1, ax1 = plt.subplots(figsize=(7, 4.5), facecolor=_BG_ROOT)
        fig1.subplots_adjust(top=0.88, bottom=0.14, left=0.10, right=0.97)
        _style(ax1)
        if heaps.get("tokens"):
            ax1.plot(heaps["tokens"], heaps["types"],
                     color=_ACCENT, linewidth=1.6, label="observado", zorder=3)
            if heaps.get("predicted"):
                ax1.plot(heaps["tokens"], heaps["predicted"],
                         color=_ACCENT2, linewidth=1, linestyle="--", alpha=0.8,
                         label=f"Heaps β={heaps.get('beta', '?')}", zorder=2)
            ax1.legend(fontsize=8, framealpha=0.6, loc="lower right")
            beta = heaps.get("beta")
            if beta is not None:
                interp = heaps.get("interpretation", "")
                ax1.annotate(interp, xy=(0.03, 0.97), xycoords="axes fraction",
                             fontsize=7.5, color=_TEXT_MUTED, va="top",
                             bbox=dict(boxstyle="round,pad=0.2", fc=_BG_ROOT,
                                       ec="none", alpha=0.8))
        ax1.set_title("Ley de Heaps: saturación del vocabulario",
                      color=_TEXT, fontsize=10, weight="bold", pad=6)
        ax1.set_xlabel("Tokens procesados", color=_TEXT_MUTED, fontsize=8.5)
        ax1.set_ylabel("Tipos léxicos únicos", color=_TEXT_MUTED, fontsize=8.5)
        p1 = out_dir / "heaps_law.png"
        fig1.savefig(p1, dpi=150, bbox_inches="tight")
        plt.close(fig1)
        saved_files.append(p1)

        # ────────────────────────────────────────────────────────────
        # 2. DISPERSIÓN (DP de Gries) — top 20 CT
        # ────────────────────────────────────────────────────────────
        fig2, ax2 = plt.subplots(figsize=(7, 5.5), facecolor=_BG_ROOT)
        fig2.subplots_adjust(top=0.88, bottom=0.12, left=0.28, right=0.97)
        _style(ax2)
        if dp_scores and self._results:
            top20 = sorted(self._results,
                           key=lambda t: t["terminologicity"], reverse=True)[:20]
            top20 = [t for t in top20 if t["lemma"] in dp_scores]
            top20_sorted = sorted(top20, key=lambda t: dp_scores[t["lemma"]])
            labels_dp  = [t["lemma"][:28] for t in top20_sorted]
            values_dp  = [dp_scores[t["lemma"]] for t in top20_sorted]
            cmap = matplotlib.colormaps.get_cmap("RdYlGn_r")
            bar_colors = [cmap(v) for v in values_dp]
            ax2.barh(labels_dp, values_dp, color=bar_colors, alpha=0.9, height=0.7)
            ax2.axvline(0.4, color=_TEXT_MUTED, linewidth=0.8, linestyle=":",
                        label="umbral 0,4")
            ax2.set_xlim(0, 1)
            ax2.legend(fontsize=8, framealpha=0.6)
            ax2.tick_params(axis="y", labelsize=8)
        ax2.set_title("Dispersión de candidatos terminológicos (DP de Gries)",
                      color=_TEXT, fontsize=10, weight="bold", pad=6)
        ax2.set_xlabel("DP de Gries  (0 = disperso · 1 = concentrado)",
                       color=_TEXT_MUTED, fontsize=8.5)
        p2 = out_dir / "term_dispersion.png"
        fig2.savefig(p2, dpi=150, bbox_inches="tight")
        plt.close(fig2)
        saved_files.append(p2)

        # ────────────────────────────────────────────────────────────
        # 3. DISTRIBUCIÓN DE FRECUENCIAS
        # ────────────────────────────────────────────────────────────
        fig3, ax3 = plt.subplots(figsize=(6, 4.5), facecolor=_BG_ROOT)
        fig3.subplots_adjust(top=0.88, bottom=0.14, left=0.13, right=0.97)
        _style(ax3)
        if self._results:
            freqs = [t["frequency"] for t in self._results]
            buckets = {
                "Hápax\n(f = 1)":    sum(1 for f in freqs if f == 1),
                "Baja\n(f 2–5)":     sum(1 for f in freqs if 2 <= f <= 5),
                "Media\n(f 6–20)":   sum(1 for f in freqs if 6 <= f <= 20),
                "Alta\n(f > 20)":    sum(1 for f in freqs if f > 20),
            }
            bcolors = ["#ef4444", "#f59e0b", "#65a30d", "#16a34a"]
            bvals   = list(buckets.values())
            blbls   = list(buckets.keys())
            rects   = ax3.bar(blbls, bvals, color=bcolors, alpha=0.85, width=0.55)
            for rect, val in zip(rects, bvals):
                ax3.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.5,
                         str(val), ha="center", va="bottom",
                         fontsize=9, color=_TEXT, weight="bold")
            ax3.set_ylim(0, max(bvals) * 1.18 if bvals else 1)
        ax3.set_title("Distribución de frecuencias de candidatos terminológicos",
                      color=_TEXT, fontsize=10, weight="bold", pad=6)
        ax3.set_ylabel("Número de candidatos terminológicos",
                       color=_TEXT_MUTED, fontsize=8.5)
        p3 = out_dir / "frequency_distribution.png"
        fig3.savefig(p3, dpi=150, bbox_inches="tight")
        plt.close(fig3)
        saved_files.append(p3)

        # ────────────────────────────────────────────────────────────
        # 4. DIVERSIDAD TEMÁTICA (solo si hay metadatos de 'tema')
        # ────────────────────────────────────────────────────────────
        if has_entropy:
            fig4, ax4 = plt.subplots(figsize=(6, 5), facecolor=_BG_ROOT)
            fig4.subplots_adjust(top=0.88, bottom=0.08, left=0.05, right=0.95)
            _style(ax4)
            pass
            p4 = out_dir / "thematic_diversity.png"
            fig4.savefig(p4, dpi=150, bbox_inches="tight")
            plt.close(fig4)
            saved_files.append(p4)

        # ── Panel de resultado en la GUI ──
        ctk.CTkLabel(
            self._eval_graph_frame,
            text="Gráficos de evaluación guardados en:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=_TEXT,
        ).pack(anchor="w", padx=12, pady=(16, 2))
        ctk.CTkLabel(
            self._eval_graph_frame,
            text=str(out_dir),
            font=ctk.CTkFont(size=10), text_color=_ACCENT,
        ).pack(anchor="w", padx=12, pady=(0, 6))

        for saved_path in saved_files:
            row = ctk.CTkFrame(self._eval_graph_frame, fg_color="transparent")
            row.pack(anchor="w", padx=12, pady=(1, 1))
            ctk.CTkLabel(
                row,
                text=f"• {saved_path.name}",
                font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
                width=230, anchor="w",
            ).pack(side="left")
            ctk.CTkButton(
                row,
                text="Ver",
                width=50, height=22,
                fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                text_color="#ffffff", font=ctk.CTkFont(size=10),
                command=lambda p=saved_path: self._show_graph_fullscreen(p),
            ).pack(side="left", padx=(6, 0))

        ctk.CTkButton(
            self._eval_graph_frame,
            text="Abrir carpeta",
            width=130, height=28,
            fg_color="transparent", hover_color=_BG_CARD2,
            border_width=1, border_color=_ACCENT,
            text_color=_ACCENT, font=ctk.CTkFont(size=11),
            command=lambda p=out_dir: self._open_folder(p),
        ).pack(anchor="w", padx=12, pady=(10, 0))

    def _show_graph_fullscreen(self, path: Path):
        """Abre el gráfico guardado en una ventana ampliada."""
        try:
            from PIL import Image, ImageTk
        except ImportError:
            messagebox.showwarning(
                "TECLA",
                "Instala Pillow para ver los gráficos:\npip install Pillow",
            )
            return

        if not path.exists():
            messagebox.showwarning("TECLA", f"No se encontró el archivo:\n{path}")
            return

        win = ctk.CTkToplevel(self)
        win.title("Evaluación del corpus — gráficos")
        win.geometry("1400x860")
        win.configure(fg_color=_BG_ROOT)
        win.focus_force()

        img_orig = Image.open(path)

        canvas = tk.Canvas(win, bg=_BG_ROOT, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def _redraw(*_):
            w, h = canvas.winfo_width(), canvas.winfo_height()
            if w < 10 or h < 10:
                return
            resized = img_orig.copy()
            resized.thumbnail((w, h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            canvas._photo = photo  # evita que el GC lo elimine
            canvas.delete("all")
            canvas.create_image(w // 2, h // 2, anchor="center", image=photo)

        canvas.bind("<Configure>", lambda _: _redraw())
        win.after(80, _redraw)


    def _render_bootstrap_results(self, stability, rep):
        self._eval_rep, self._eval_stab = rep, stability
        self._update_eval_table()
        idx = stability.get("stability_index")
        if idx is not None:
            pct = round(idx * 100)
            self._eval_stability_label.configure(
                text=f"Estabilidad: {pct}%  ({stability['n_bootstrap']} iteraciones)",
                text_color=("#16a34a" if pct >= 70 else "#d97706" if pct >= 50 else "#dc2626"),
            )
        # Update score card
        score = rep["score"]
        color = rep["color"]
        self._eval_score_num.configure(text=f"{score}", text_color=color)
        self._eval_score_label.configure(text=f"El corpus es {rep['label']}", text_color=color)
        self._eval_description.configure(text=rep.get("description", ""), text_color=_TEXT)
        comp = rep.get("components", {})
        parts = [f"{k.capitalize()}: {v}" for k, v in comp.items()]
        self._eval_components_label.configure(text="   ·   ".join(parts))
        self._draw_eval_scale(score, color)

    # ── Keyness ──

    def _load_reference_corpus(self):
        if not self._results:
            messagebox.showinfo("TECLA", "Realiza una extracción primero.")
            return
        path = filedialog.askopenfilename(
            title="Seleccionar corpus de referencia (CSV)",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            from tecla.evaluation.corpus_metrics import load_reference_corpus, compute_keyness
            reference, ref_size = load_reference_corpus(path)
            corpus_size = sum(d["tokens"] for d in self._doc_stats)
            rows = compute_keyness(self._results, reference, corpus_size, ref_size)
            self._render_keyness(rows)
        except Exception as exc:
            messagebox.showerror("TECLA", f"Error cargando referencia:\n{exc}")

    def _render_keyness(self, rows):
        self._eval_kn_tree.delete(*self._eval_kn_tree.get_children())
        for i, r in enumerate(rows[:100], 1):
            tag = "odd" if i % 2 else "even"
            self._eval_kn_tree.insert("", "end", tags=(tag,), values=(
                f"{i}.", r["lemma"],
                r["freq_corp"], r["freq_ref"],
                f"{r['g2']:.1f}", f"{r['log_ratio']:.2f}", r["direction"],
            ))

    # ── Lista de referencia (cobertura externa) ──────────────────────────────

    def _load_gold_list(self):
        path = filedialog.askopenfilename(
            title="Seleccionar lista de referencia terminológica (CSV)",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
        )
        if not path:
            return
        self._apply_gold_list(Path(path))

    def _apply_gold_list(self, path: Path):
        import csv as _csv
        try:
            with open(path, encoding="utf-8") as f:
                rows = list(_csv.DictReader(f))
            col = next((c for c in (rows[0].keys() if rows else [])
                        if c.strip().lower() == "term"), None)
            if col is None:
                messagebox.showerror(
                    "TECLA",
                    f"El CSV no tiene columna 'term'.\nColumnas encontradas: "
                    f"{', '.join(rows[0].keys()) if rows else '(vacío)'}"
                )
                return
            self._gold_terms = [r[col].strip().lower() for r in rows if r.get(col, "").strip()]
            self._gold_path  = path
            n = len(self._gold_terms)
            self._cov_status_label.configure(
                text=f"{path.name}  ·  {n} término{'s' if n != 1 else ''}",
                text_color=_TEXT,
            )
            self._cov_clear_btn.configure(state="normal")
            self._cov_result_label.configure(text="")
            self._cov_detail_label.configure(text="Ejecuta la evaluación para calcular la cobertura.")
            if self._results:
                self._compute_and_render_coverage()
        except Exception as exc:
            messagebox.showerror("TECLA", f"Error leyendo la lista:\n{exc}")

    def _clear_gold_list(self):
        self._gold_terms = []
        self._gold_path  = None
        self._cov_status_label.configure(text="Sin lista cargada", text_color=_TEXT_MUTED)
        self._cov_clear_btn.configure(state="disabled")
        self._cov_result_label.configure(text="")
        self._cov_detail_label.configure(text="")

    def _autodetect_gold(self, corpus_path: Path):
        """Detecta automáticamente un gold.csv en la carpeta del corpus."""
        lang = getattr(self, "_corpus_language", "")
        candidates = [
            corpus_path / f"gold_{lang}.csv",
            corpus_path / "gold.csv",
            corpus_path / "lista_referencia.csv",
        ]
        for p in candidates:
            if p.exists():
                self._apply_gold_list(p)
                return

    def _compute_and_render_coverage(self):
        if not self._gold_terms or not self._results:
            return
        from tecla.evaluation.term_eval import evaluate_extraction
        result = evaluate_extraction(self._results, self._gold_terms, mode="exact")
        recall    = result["recall"]
        tp        = result["tp"]
        total_ref = tp + result["fn"]
        missing   = result["false_negatives"]

        color = "#16a34a" if recall >= 0.70 else ("#d97706" if recall >= 0.40 else "#dc2626")
        self._cov_result_label.configure(
            text=f"Recall  {recall:.1%}   ({tp} / {total_ref} términos)",
            text_color=color,
        )
        if missing:
            preview = ", ".join(sorted(missing)[:12])
            suffix  = f"… (+{len(missing) - 12} más)" if len(missing) > 12 else ""
            self._cov_detail_label.configure(
                text=f"No encontrados ({len(missing)}): {preview}{suffix}",
                text_color=_TEXT_MUTED,
            )
        else:
            self._cov_detail_label.configure(
                text="Todos los términos de referencia están cubiertos.",
                text_color="#16a34a",
            )

    def _save_review_data(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        try:
            out = self._output_dir() / "revision.json"
            out.write_text(
                json.dumps({"version": 1, "terms": self._review_data}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _load_review_data(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        f = self._user_file("revision.json", "_tecla_revision.json")
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                self._review_data = data.get("terms", {})
            except Exception:
                self._review_data = {}
            self._remap_review_keys()

    def _remap_review_keys(self):
        """Traslada las decisiones guardadas con un lema que ya no existe al
        candidato que ahora agrupa sus formas (p. ej., tras unir lemas)."""
        if not self._all_results or not self._review_data:
            return
        lang = getattr(self, "_corpus_language", None) or self.language_var.get()
        lang = lang if lang in ("es", "en") else "es"
        current = {t["lemma"] for t in self._all_results}
        by_key = {lemma_key(l, lang): l for l in current}
        rank = {"aprobado": 2, "rechazado": 1, "pendiente": 0}
        moved = False
        for old in [k for k in self._review_data if k not in current]:
            new = by_key.get(lemma_key(old, lang))
            if not new:
                continue
            entry, prev = self._review_data.pop(old), self._review_data.get(new)
            if prev is None or rank.get(entry.get("status"), 0) > rank.get(prev.get("status"), 0):
                merged = dict(entry)
                if prev:
                    merged["notes"] = "\n".join(n for n in (prev.get("notes"), entry.get("notes")) if n)
                    merged["author_usage"] = prev.get("author_usage") or entry.get("author_usage")
                self._review_data[new] = merged
            moved = True
        if moved:
            self._save_review_data()

    # ═══════════════════════════════════════════
    # Metadatos del corpus
    # ═══════════════════════════════════════════

    def _load_corpus_metadata(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        f = self._user_file("metadatos_documentos.json", "_tecla_metadata.json")
        if f.exists():
            try:
                self._corpus_metadata = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                self._corpus_metadata = {}
        else:
            self._corpus_metadata = {}

        # Los documentos sin metadatos guardados se completan con los que TECLA
        # deduce del nombre del archivo (_tecla_output/metadata.csv).
        inferred = self._output_dir() / "metadata.csv"
        if inferred.exists():
            try:
                with open(inferred, encoding="utf-8", newline="") as fh:
                    for row in csv.DictReader(fh):
                        doc_id = Path(row.get("file", "")).name
                        if doc_id.lower().endswith(".txt") or doc_id.lower().endswith(".pdf"):
                            doc_id = doc_id[:-4]
                        if doc_id and doc_id not in self._corpus_metadata:
                            self._corpus_metadata[doc_id] = {
                                "autor":  (row.get("author") or "").strip(),
                                "año":    (row.get("year") or "").strip(),
                                "tema":   "",
                                "fuente": (row.get("title") or row.get("source") or "").strip(),
                                "notas":  "",
                            }
            except Exception:
                pass

    def _save_corpus_metadata(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        try:
            out = self._output_dir() / "metadatos_documentos.json"
            out.write_text(
                json.dumps(self._corpus_metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _on_corpus_row_selected(self, _=None):
        sel = self._corpus_tree.selection()
        if not sel:
            return
        doc_id = sel[0]
        self._meta_selected_doc = doc_id
        self._meta_doc_label.configure(
            text=f"Metadatos de: {doc_id}", text_color=_TEXT,
        )
        meta = self._corpus_metadata.get(doc_id, {})
        # Rellenar campos
        self._meta_autor.delete(0, "end")
        self._meta_autor.insert(0, meta.get("autor", ""))
        self._meta_año.delete(0, "end")
        self._meta_año.insert(0, meta.get("año", ""))
        self._meta_tema.delete(0, "end")
        self._meta_tema.insert(0, meta.get("tema", ""))
        self._meta_fuente.delete(0, "end")
        self._meta_fuente.insert(0, meta.get("fuente", ""))
        self._meta_notas.delete("1.0", "end")
        self._meta_notas.insert("1.0", meta.get("notas", ""))

    def _save_doc_metadata(self):
        if not self._meta_selected_doc:
            messagebox.showwarning("TECLA", "Selecciona un documento primero.")
            return
        doc_id = self._meta_selected_doc
        self._corpus_metadata[doc_id] = {
            "autor":  self._meta_autor.get().strip(),
            "año":    self._meta_año.get().strip(),
            "tema":   self._meta_tema.get().strip(),
            "fuente": self._meta_fuente.get().strip(),
            "notas":  self._meta_notas.get("1.0", "end").strip(),
        }
        self._save_corpus_metadata()
        try:
            self._write_corpus_stats(self._corpus_stats_file())
        except OSError:
            pass
        # Actualizar la celda en el Treeview
        meta = self._corpus_metadata[doc_id]
        try:
            vals = list(self._corpus_tree.item(doc_id, "values"))
            vals[9]  = meta["autor"]
            vals[10] = meta["año"]
            vals[11] = meta["tema"]
            self._corpus_tree.item(doc_id, values=vals)
        except Exception:
            pass

    # ═══════════════════════════════════════════
    # Callbacks del sidebar
    # ═══════════════════════════════════════════

    def _on_preset_changed(self, value: str):
        self._preset_hint.configure(text=_PRESET_HINTS.get(value, ""))

    def _browse_corpus(self):
        folder = filedialog.askdirectory(title="Seleccionar directorio de trabajo")
        if folder:
            self.corpus_path_var.set(folder)
            self._clear_results()
            self.after(150, self._offer_resume)

    def _open_folder(self, path: Path):
        import subprocess, sys
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            elif sys.platform == "win32":
                subprocess.Popen(["explorer", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception:
            pass

    def _browse_grammar(self):
        path = filedialog.askopenfilename(
            title="Seleccionar gramática POS",
            filetypes=[("YAML", "*.yaml *.yml"), ("Todos", "*.*")],
        )
        if path:
            self.grammar_path_var.set(path)

    def _browse_stoplist(self):
        path = filedialog.askopenfilename(
            title="Seleccionar stoplist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            words = [w.strip() for w in Path(path).read_text(encoding="utf-8").splitlines() if w.strip()]
            self._stoplist_var.set(", ".join(words))
        except Exception as e:
            messagebox.showerror("TECLA", f"No se pudo leer el archivo:\n{e}")

    def _get_extra_stoplist(self) -> list:
        raw = self._stoplist_var.get().strip()
        return [w.strip() for w in raw.split(",") if w.strip()] if raw else []

    # ═══════════════════════════════════════════
    # Filtro y ordenación (pestaña Extracción)
    # ═══════════════════════════════════════════

    def _on_filter_changed(self, _=None):
        if self._all_results:
            self._apply_filters()

    def _on_sort_changed(self, _=None):
        if self._all_results:
            self._apply_filters()

    def _toggle_sort_dir(self):
        self._sort_reverse = not self._sort_reverse
        self._sort_dir_btn.configure(text="▼ desc" if self._sort_reverse else "▲ asc")
        if self._all_results:
            self._apply_filters()

    def _apply_filters(self, notify: bool = True):
        """Aplica los filtros: los CTs que los pasan son el resultado que usan
        la tabla, la exportación, la evaluación y la revisión."""
        min_freq  = self._min_freq_var.get()
        min_score = self._min_score_var.get()

        # Percentile threshold: compute score cutoff from all results
        pct = _PCT_MAP.get(self._percentile_choice.get(), 0)
        if pct > 0 and self._all_results:
            all_scores = sorted(t["terminologicity"] for t in self._all_results)
            idx = int(len(all_scores) * pct / 100)
            pct_threshold = all_scores[min(idx, len(all_scores) - 1)]
        else:
            pct_threshold = 0.0

        effective_min_score = max(min_score, pct_threshold)

        include_mono  = self._include_mono_var.get()

        filtered = [
            t for t in self._all_results
            if t["frequency"] >= min_freq
            and t["terminologicity"] >= effective_min_score
            and not (not include_mono and len(t["lemma"].split()) == 1)
        ]
        changed = [t["lemma"] for t in filtered] != [t["lemma"] for t in self._results]
        self._results = filtered
        filtered = list(filtered)
        sort_field = _SORT_KEY_MAP[self._sort_key_var.get()]
        reverse    = self._sort_reverse
        if sort_field == "term":
            reverse = not reverse
        filtered.sort(key=lambda t: t.get(sort_field) or 0, reverse=reverse)
        self._render_results(filtered)
        if changed and notify:
            if self._results_job is not None:
                self.after_cancel(self._results_job)
            self._results_job = self.after(400, self._on_results_changed)

    def _on_results_changed(self):
        """Lleva el resultado filtrado a la revisión, los gráficos y la evaluación."""
        self._results_job = None
        self._render_revision_list()
        self._update_graficos()
        if self._gold_terms:
            self._compute_and_render_coverage()
        if self._eval_done and not self._eval_running:
            self._tabview.mark_done("Evaluación", False)
            self._eval_btn.configure(text="Recalcular con los filtros actuales")

    def _toggle_col(self, col_id: str, orig_width: int, stretch: bool):
        visible = self._col_visible[col_id].get()
        if visible:
            self._results_tree.column(col_id, width=orig_width,
                                      stretch=stretch, minwidth=orig_width)
        else:
            self._results_tree.column(col_id, width=0, stretch=False, minwidth=0)
        if col_id == "score":
            self._results_tree.column("bar", width=118 if visible else 0, stretch=False,
                                      minwidth=118 if visible else 0)

    def _select_all(self):
        self._results_tree.selection_set(self._results_tree.get_children())

    def _deselect_all(self):
        self._results_tree.selection_remove(self._results_tree.get_children())

    # ═══════════════════════════════════════════
    # Exportación
    # ═══════════════════════════════════════════

    def _export_csv(self):
        if not self._results_data:
            messagebox.showwarning("TECLA", "No hay términos para exportar.")
            return
        iids = self._results_tree.selection() or self._results_tree.get_children()
        selected = [self._results_data[int(iid)] for iid in iids]
        if not selected:
            messagebox.showwarning("TECLA", "No hay ningún término seleccionado.")
            return
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), title="Exportar términos",
                                            defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        fieldnames = ["term", "lemma", "variants", "patterns", "terminologicity",
                      "tf_idf", "c_value", "nc_value", "frequency", "freq_rel", "doc_frequency"]
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for t in selected:
                    row = {k: t.get(k, "") for k in fieldnames}
                    row["patterns"] = ";".join(t.get("patterns", []))
                    row["variants"] = ";".join(t.get("variants", []))
                    w.writerow(row)
            messagebox.showinfo("TECLA", f"Exportados {len(selected)} términos a:\n{path}")
        except Exception as e:
            messagebox.showerror("TECLA", f"Error al exportar:\n{e}")

    def _export_tbx(self):
        if not self._results_data:
            messagebox.showwarning("TECLA", "No hay términos para exportar.")
            return
        iids = self._results_tree.selection() or self._results_tree.get_children()
        selected = [self._results_data[int(iid)] for iid in iids]
        if not selected:
            messagebox.showwarning("TECLA", "No hay ningún término seleccionado.")
            return
        path = filedialog.asksaveasfilename(parent=self, initialdir=str(self._output_dir()), title="Exportar TBX",
                                            defaultextension=".tbx",
                                            filetypes=[("TBX", "*.tbx"), ("XML", "*.xml")])
        if not path:
            return
        try:
            from tecla.extractor.tbx_export import export_tbx
            export_tbx(selected, Path(path), language=self.language_var.get())
            messagebox.showinfo("TECLA", f"Exportados {len(selected)} términos a:\n{path}")
        except Exception as e:
            messagebox.showerror("TECLA", f"Error al exportar TBX:\n{e}")

    # ═══════════════════════════════════════════
    # Extracción
    # ═══════════════════════════════════════════

    def _start_extraction(self):
        if not self.corpus_path_var.get():
            messagebox.showwarning("TECLA", "Selecciona una carpeta de corpus.")
            return
        if self._running:
            return

        self._running = True
        self.log_box.delete("1.0", "end")
        self._clear_results()
        self._term_count_label.configure(text="")
        self._run_btn.configure(state="disabled", text="Extrayendo…")
        self._progress.start()
        self._tabview.set("Extracción")

        threading.Thread(target=self._run_thread, daemon=True).start()

    def _run_thread(self):
        self._save_session()
        try:
            workdir     = Path(self.corpus_path_var.get())
            corpus_path = workdir / "corpus"
            if not corpus_path.exists():
                self.after(0, self._log,
                           f"❌  No se encontró la carpeta 'corpus' en:\n   {workdir}\n"
                           "   Crea la subcarpeta 'corpus/' y coloca tus archivos PDF o TXT dentro.")
                return

            lang = self.language_var.get()
            results = run_tecla_pipeline(
                corpus_path=corpus_path,
                language=None if lang == "auto" else lang,
                cleaning_options={
                    "structure": True,
                    "remove_bibliography_flag": True,
                    "remove_captions_flag": True,
                    "remove_section_headers_flag": True,
                },
                extraction_options={
                    "multiword_only": not self._include_mono_var.get(),
                    "max_term_length": self.max_term_length_var.get(),
                    "max_span_tokens": max(6, self.max_term_length_var.get()),
                    # Se extraen todos los candidatos; la frecuencia mínima
                    # se aplica como filtro, al momento
                    "min_freq": 1,
                    "drop_other_language": self._drop_other_var.get(),
                    "other_language_stopwords": self._other_sw_var.get(),
                    "weights": _WEIGHT_PRESETS[self.weight_preset.get()],
                    "grammar_path": self.grammar_path_var.get() or None,
                    "extra_stop_terms": self._get_extra_stoplist() or None,
                },
                on_progress=lambda msg: self.after(0, self._log, msg),
                on_corpus_ready=lambda docs, folder, lang: self.after(
                    0, self._on_corpus_ready, docs, folder, lang
                ),
            )
            self.after(0, self._show_results, results)

        except Exception as exc:
            self.after(0, self._log, f"❌  {exc}")
            self.after(0, messagebox.showerror, "TECLA – Error", str(exc))
        finally:
            self.after(0, self._extraction_done)

    def _extraction_done(self):
        self._progress.stop()
        self._progress.set(1)
        self._run_btn.configure(state="normal", text="▶  Ejecutar")
        self._running = False

    def _on_corpus_ready(self, documents: list, clean_folder: str, language: str):
        self._clean_folder    = clean_folder
        self._conc_texts, self._conc_cache = None, {}
        self._corpus_language = language
        self._documents       = documents
        self._doc_stats    = []

        try:
            from tecla.corpus.cleaning import get_language_stopwords
            stopwords = get_language_stopwords(language)
        except Exception:
            stopwords = set()

        for doc in documents:
            doc_id   = doc["doc_id"]
            tokens   = doc["tokens"]
            sents    = doc.get("sentences", [])
            lemmas   = Counter(t["lemma"] for t in tokens)
            types    = len(lemmas)
            n_tokens = len(tokens)
            ttr      = round(types / n_tokens, 4) if n_tokens else 0.0
            # Hápax: proporción de tipos que aparecen una sola vez en el documento
            hapax    = sum(1 for n in lemmas.values() if n == 1)
            # Densidad léxica: palabras de contenido entre las palabras del documento
            words    = [t["text"].lower() for t in tokens if t["text"].isalpha()]
            content  = sum(1 for w in words if w not in stopwords)
            self._doc_stats.append({
                "doc_id":    doc_id,
                "tokens":    n_tokens,
                "sentences": len(sents),
                "types":     types,
                "ttr":       ttr,
                "hapax_ratio":         round(hapax / types, 4) if types else 0.0,
                "lexical_density":     round(content / len(words), 4) if words else 0.0,
                "avg_sentence_length": round(n_tokens / len(sents), 2) if sents else 0.0,
            })

        # Tipos del corpus completo (no la suma de los tipos de cada documento)
        corpus_lemmas = Counter(t["lemma"] for doc in documents for t in doc["tokens"])
        self._corpus_types = len(corpus_lemmas)
        corpus_words = [t["text"].lower() for doc in documents for t in doc["tokens"]
                        if t["text"].isalpha()]
        self._corpus_summary = {
            "hapax_ratio": round(sum(1 for n in corpus_lemmas.values() if n == 1)
                                 / len(corpus_lemmas), 4) if corpus_lemmas else 0.0,
            "lexical_density": round(sum(1 for w in corpus_words if w not in stopwords)
                                     / len(corpus_words), 4) if corpus_words else 0.0,
        }

        self._load_corpus_metadata()
        self._render_corpus_tab()
        try:
            self._write_corpus_stats(self._corpus_stats_file())
        except OSError:
            pass

        # Auto-detectar lista de referencia si no hay una cargada
        if not self._gold_terms:
            corpus_root = Path(self.corpus_path_var.get())
            if corpus_root.exists():
                self._autodetect_gold(corpus_root)

    # ═══════════════════════════════════════════
    # Display — pestaña Extracción
    # ═══════════════════════════════════════════

    def _show_results(self, results):
        self._all_results = results
        self._conc_cache = {}
        self._save_candidates(results)
        self._eval_done = False
        self._load_review_data()
        self._apply_filters(notify=False)
        self._render_revision_list()
        self._tabview.mark_done("Extracción", bool(results))
        self._update_graficos()
        if self._eval_btn is not None:
            self._eval_btn.configure(state="normal")

    def _clear_results(self):
        self._results_tree.delete(*self._results_tree.get_children())
        self._results_data = []
        self._all_results  = []
        self._results      = []
        self._term_count_label.configure(text="")
        for card in self._ext_cards.values():
            card.configure(text="—")
        self._tabview.mark_done("Extracción", False)
        self._tabview.mark_done("Evaluación", False)

    def _render_results(self, results):
        self._results_tree.delete(*self._results_tree.get_children())
        self._results_data = results

        n     = len(results)
        total = len(self._all_results)
        self._term_count_label.configure(
            text=f"{_miles(n)} candidato{'s' if n != 1 else ''}" if n == total
            else f"{_miles(n)} de {_miles(total)} candidatos"
        )

        self._ext_cards["cands"].configure(text=_miles(total) if total else "—")
        self._ext_cards["shown"].configure(text=_miles(n) if total else "—")
        multi  = sum(1 for t in results if len(t["lemma"].split()) > 1)
        spread = sum(1 for t in results if t["doc_frequency"] >= 2)
        self._ext_cards["multi"].configure(
            text=f"{_miles(multi)} · {_miles(n - multi)}" if n else "—")
        self._ext_cards["spread"].configure(
            text=f"{100 * spread / n:.0f} %" if n else "—")

        if not results:
            return

        top = max((r["terminologicity"] for r in self._all_results), default=0) or 1
        for i, t in enumerate(results, 1):
            filled = max(0, min(10, round(10 * t["terminologicity"] / top)))
            pats     = "/".join(t.get("patterns", []))
            var_str  = variants_summary(t).replace("También ", "") or "—"
            tag      = "odd" if i % 2 == 1 else "even"
            self._results_tree.insert("", "end", iid=str(i - 1),
                values=(
                    f"{i}.",
                    display_form(t),
                    var_str,
                    pats,
                    f"{t['terminologicity']:.4f}",
                    "▰" * filled + "▱" * (10 - filled),
                    f"{t.get('tf_idf', 0):.4f}",
                    f"{t.get('c_value', 0):.4f}",
                    f"{t.get('nc_value', 0):.4f}",
                    t["frequency"],
                    f"{t.get('freq_rel', 0):.2f}",
                    t["doc_frequency"],
                    len(self._authors_of(t)[0]) or "—",
                ),
                tags=(tag,),
            )
        # Seleccionar todos por defecto
        self._results_tree.selection_set(self._results_tree.get_children())

    def _log(self, text: str):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    # ═══════════════════════════════════════════
    # Sesión
    # ═══════════════════════════════════════════

    def _load_session(self):
        try:
            if _SESSION_FILE.exists():
                data = json.loads(_SESSION_FILE.read_text(encoding="utf-8"))
                path = data.get("corpus_path", "")
                if path and Path(path).exists():
                    self.corpus_path_var.set(path)
        except Exception:
            pass

    def _save_session(self):
        try:
            _SESSION_FILE.write_text(
                json.dumps({"corpus_path": self.corpus_path_var.get()}),
                encoding="utf-8",
            )
        except Exception:
            pass


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = TeclaApp()
    app.mainloop()
