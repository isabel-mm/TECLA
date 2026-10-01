import csv
import json
import sys
import threading
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from pipeline.pipeline import run_tecla_pipeline

# ─────────────────────────────────────────────
# Tema y constantes
# ─────────────────────────────────────────────

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── Paleta índigo/pizarra (profesional, sin verde) ──
_ACCENT        = "#4361ee"   # índigo azul (resalte principal, botones con texto blanco)
_ACCENT_DIM    = "#3451c7"   # índigo oscuro (hover)
_ACCENT2       = "#7c3aed"   # violeta (resalte secundario, botones con texto blanco)
_BG_ROOT       = "#f7f8fc"   # fondo general
_BG_CARD       = "#ffffff"   # tarjetas
_BG_CARD2      = "#eef0f8"   # cabeceras / filas alternas
_BG_LOG        = "#1e2240"   # log (terminal oscuro)
_BORDER        = "#dde1ef"   # bordes suaves
_TEXT          = "#1a1d35"   # texto principal
_TEXT_MUTED    = "#6b7280"   # texto atenuado
_SEG_TEXT      = "#1a1d35"   # texto en botones segmentados (oscuro sobre fondos claros)
_SEG_SELECTED  = "#a5b4fc"   # fondo seleccionado en botones/pestañas (índigo suave)
_SEG_SEL_HOV   = "#818cf8"   # hover del estado seleccionado (índigo medio)
_TEXT_LOG      = "#818cf8"   # texto del log
_ROW_ODD       = "#ffffff"
_ROW_EVEN      = "#f7f8fc"
_STATUS_COLOR  = {"pendiente": "#6b7280", "aprobado": "#16a34a", "rechazado": "#dc2626"}

# ── Sidebar (panel lateral claro, diferenciado) ──
_SB_BG         = "#eef0fa"   # fondo sidebar (lavanda suave)
_SB_SECTION    = "#dde2f5"   # bandas de sección
_SB_TEXT       = "#1a1d35"   # texto sidebar (oscuro sobre claro)
_SB_MUTED      = "#6b7280"   # texto atenuado sidebar
_SB_BORDER     = "#c8d0e8"   # bordes sidebar

_SESSION_FILE  = Path.home() / ".tecla_session.json"

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


# ─────────────────────────────────────────────
# Aplicación
# ─────────────────────────────────────────────

class TeclaApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("TECLA")
        self.geometry("1420x800")
        self.minsize(1100, 640)
        self.configure(fg_color=_BG_ROOT)

        # ── Config extracción ──
        self.corpus_path_var    = ctk.StringVar(value="")   # directorio de trabajo
        self.grammar_path_var   = ctk.StringVar(value="")
        self.language_var       = ctk.StringVar(value="es")
        self._include_mono_var  = ctk.BooleanVar(value=False)

        self._percentile_var    = tk.IntVar(value=0)
        self.weight_preset      = ctk.StringVar(value="Equilibrado")
        self.max_term_length_var = ctk.IntVar(value=5)
        self._running         = False
        self._advanced_open   = False   # progressive disclosure sidebar

        # ── Datos post-extracción ──
        self._all_results    = []     # CTs completos del pipeline
        self._results_data   = []     # filtrados+ordenados (para display)
        self._doc_stats      = []     # [{doc_id, tokens, sentences, types}]
        self._documents      = []     # documentos enriquecidos (para evaluación)
        self._clean_folder   = ""

        # ── Evaluación ──
        self._eval_running   = False
        self._eval_dp_scores = {}     # lemma → DP score
        self._eval_btn       = None   # se asigna al construir el tab

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

        self._build_ui()
        self._load_session()

    # ═══════════════════════════════════════════
    # Layout principal
    # ═══════════════════════════════════════════

    def _build_ui(self):
        self._sidebar = ctk.CTkFrame(self, width=290, fg_color=_SB_BG, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Línea separadora entre sidebar y contenido
        ctk.CTkFrame(self, width=1, fg_color=_BORDER, corner_radius=0).pack(side="left", fill="y")

        self._tabview = ctk.CTkTabview(
            self, fg_color=_BG_ROOT,
            segmented_button_fg_color=_BG_CARD2,
            segmented_button_selected_color=_SEG_SELECTED,
            segmented_button_selected_hover_color=_SEG_SEL_HOV,
            segmented_button_unselected_color=_BG_CARD2,
            segmented_button_unselected_hover_color=_BG_CARD,
            text_color=_SEG_TEXT,
            text_color_disabled=_SEG_TEXT,
        )
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
                             rowheight=28, font=("", 11))
        tree_style.configure("TECLA.Treeview.Heading",
                             background=_BG_CARD2, foreground=_TEXT_MUTED,
                             relief="flat", font=("", 11), bordercolor=_BORDER)
        tree_style.map("TECLA.Treeview",
                       background=[("selected", "#e8eaf0")],
                       foreground=[("selected", _TEXT)])
        tree_style.map("TECLA.Treeview.Heading",
                       background=[("active", _BG_CARD)])

        self._build_sidebar()
        self._build_tab_corpus()
        self._build_tab_extraccion()
        self._build_tab_evaluacion()
        self._build_tab_revision()


    # ═══════════════════════════════════════════
    # Sidebar
    # ═══════════════════════════════════════════

    def _build_sidebar(self):
        s = self._sidebar

        # ── Header ──
        header = ctk.CTkFrame(s, fg_color=_SB_BG, corner_radius=0, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkFrame(header, fg_color=_ACCENT, height=3, corner_radius=0).pack(fill="x", side="top")

        name_row = ctk.CTkFrame(header, fg_color="transparent")
        name_row.place(relx=0.5, rely=0.52, anchor="center")

        ctk.CTkLabel(name_row, text="TECLA",
                     font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=_SB_TEXT).pack(side="left")

        ctk.CTkLabel(header, text="Term Extraction and Corpus Linguistics Application",
                     font=ctk.CTkFont(size=9), text_color=_SB_MUTED,
                     wraplength=220, justify="center",
                     ).place(relx=0.5, rely=0.82, anchor="center")

        # ── Opciones principales ──
        scroll = ctk.CTkScrollableFrame(s, fg_color=_SB_BG, scrollbar_button_color=_SB_SECTION)
        scroll.pack(fill="both", expand=True, pady=(6, 0))

        # DIRECTORIO DE TRABAJO
        self._build_section(scroll, "Directorio de trabajo")
        ctk.CTkLabel(scroll,
                     text="Los archivos PDF o TXT deben estar\nen una subcarpeta llamada  corpus/",
                     font=ctk.CTkFont(size=9), text_color=_SB_MUTED,
                     justify="left",
                     ).pack(anchor="w", padx=18, pady=(4, 2))
        ctk.CTkEntry(scroll, textvariable=self.corpus_path_var,
                     placeholder_text="Ruta al directorio de trabajo…",
                     fg_color=_SB_SECTION, border_color=_SB_BORDER,
                     text_color=_SB_TEXT,
                     ).pack(fill="x", padx=14, pady=(2, 4))
        ctk.CTkButton(scroll, text="Seleccionar directorio…",
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_ACCENT,
                      text_color=_ACCENT,
                      command=self._browse_corpus,
                      ).pack(fill="x", padx=14, pady=(0, 8))

        # LENGUA
        self._build_section(scroll, "Lengua")
        ctk.CTkSegmentedButton(scroll, values=["auto", "es", "en"],
                               variable=self.language_var,
                               fg_color=_SB_SECTION, selected_color=_SEG_SELECTED,
                               selected_hover_color=_SEG_SEL_HOV,
                               unselected_color=_SB_SECTION,
                               text_color=_SEG_TEXT,
                               text_color_disabled=_SEG_TEXT,
                               ).pack(fill="x", padx=14, pady=(4, 8))

        # EXTRACCIÓN (esencial)
        self._build_section(scroll, "Extracción")
        ctk.CTkCheckBox(scroll, text="Incluir candidatos monoléxicos",
                        variable=self._include_mono_var,
                        fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                        checkmark_color=_SB_BG, text_color=_SB_TEXT,
                        ).pack(anchor="w", padx=18, pady=(4, 4))

        self._build_section(scroll, "Perfil de puntuación")
        ctk.CTkSegmentedButton(scroll, values=list(_WEIGHT_PRESETS.keys()),
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

        # ── OPCIONES AVANZADAS (progressive disclosure) ──
        self._adv_toggle_btn = ctk.CTkButton(
            scroll,
            text="▸  Opciones avanzadas",
            fg_color="transparent", hover_color=_SB_SECTION,
            text_color=_SB_MUTED, font=ctk.CTkFont(size=11),
            anchor="w", height=26,
            command=self._toggle_advanced,
        )
        self._adv_toggle_btn.pack(fill="x", padx=10, pady=(4, 0))

        self._adv_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        # starts hidden; _toggle_advanced will pack/forget it

        # — Stoplist adicional —
        self._build_section(self._adv_frame, "Stoplist adicional")
        self._stoplist_entry = ctk.CTkEntry(self._adv_frame,
                                            placeholder_text="palabra1, palabra2, …",
                                            fg_color=_SB_SECTION, border_color=_SB_BORDER,
                                            text_color=_SB_TEXT)
        self._stoplist_entry.pack(fill="x", padx=14, pady=(4, 4))
        ctk.CTkButton(self._adv_frame, text="Cargar desde archivo .txt…",
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_SB_BORDER,
                      text_color=_SB_MUTED,
                      height=30, font=ctk.CTkFont(size=12),
                      command=self._browse_stoplist,
                      ).pack(fill="x", padx=14, pady=(0, 8))

        # — Gramática personalizada —
        self._build_section(self._adv_frame, "Gramática POS personalizada")
        ctk.CTkLabel(self._adv_frame,
                     text="Por defecto se usa la gramática incorporada.\n"
                          "Puedes proporcionar tu propia gramática .yaml.",
                     font=ctk.CTkFont(size=10), text_color=_SB_MUTED,
                     wraplength=240, justify="left",
                     ).pack(fill="x", padx=14, pady=(4, 4))
        ctk.CTkEntry(self._adv_frame, textvariable=self.grammar_path_var,
                     placeholder_text="grammar.yaml (opcional)",
                     fg_color=_SB_SECTION, border_color=_SB_BORDER,
                     text_color=_SB_TEXT,
                     ).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self._adv_frame, text="Seleccionar gramática…",
                      fg_color="transparent", hover_color=_SB_SECTION,
                      border_width=1, border_color=_SB_BORDER,
                      text_color=_SB_MUTED,
                      height=30, font=ctk.CTkFont(size=12),
                      command=self._browse_grammar,
                      ).pack(fill="x", padx=14, pady=(0, 8))

        # — Longitud máxima de CT —
        self._build_section(self._adv_frame, "Longitud máxima de los candidatos")
        self._max_len_label = ctk.CTkLabel(self._adv_frame, text="Tokens máx. por candidato: 5",
                                            font=ctk.CTkFont(size=11), text_color=_SB_MUTED, anchor="w")
        self._max_len_label.pack(fill="x", padx=18, pady=(4, 0))
        self._max_len_slider = ctk.CTkSlider(self._adv_frame, from_=1, to=15, number_of_steps=14,
                                              fg_color=_SB_BORDER, progress_color=_ACCENT,
                                              button_color=_ACCENT, button_hover_color=_ACCENT_DIM,
                                              command=self._on_max_len_changed)
        self._max_len_slider.set(5)
        self._max_len_slider.pack(fill="x", padx=18, pady=(2, 8))

        # — Filtrar resultados —
        self._build_section(self._adv_frame, "Filtrar candidatos")
        self._min_freq_label = ctk.CTkLabel(self._adv_frame, text="Frecuencia mínima: 1",
                                             font=ctk.CTkFont(size=11), text_color=_SB_MUTED, anchor="w")
        self._min_freq_label.pack(fill="x", padx=18, pady=(4, 0))
        self._min_freq_slider = ctk.CTkSlider(self._adv_frame, from_=1, to=50, number_of_steps=49,
                                               fg_color=_SB_BORDER, progress_color=_ACCENT,
                                               button_color=_ACCENT, button_hover_color=_ACCENT_DIM,
                                               command=self._on_filter_changed)
        self._min_freq_slider.set(1)
        self._min_freq_slider.pack(fill="x", padx=18, pady=(2, 4))

        self._exclude_hapax_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._adv_frame,
            text="Excluir hápax (frecuencia = 1)",
            variable=self._exclude_hapax_var,
            font=ctk.CTkFont(size=11), text_color=_SB_MUTED,
            fg_color=_ACCENT, hover_color=_ACCENT_DIM,
            checkmark_color="#ffffff",
            command=self._on_filter_changed,
        ).pack(anchor="w", padx=18, pady=(0, 6))


        ctk.CTkLabel(
            self._adv_frame, text="Percentil mínimo",
            font=ctk.CTkFont(size=11), text_color=_SB_MUTED, anchor="w",
        ).pack(fill="x", padx=18, pady=(4, 2))
        self._percentile_seg = ctk.CTkSegmentedButton(
            self._adv_frame,
            values=["—", "p25", "p50", "p75", "p90"],
            fg_color=_SB_SECTION, selected_color=_SEG_SELECTED,
            selected_hover_color=_SEG_SEL_HOV, unselected_color=_SB_SECTION,
            text_color=_SEG_TEXT, text_color_disabled=_SB_TEXT,
            font=ctk.CTkFont(size=11),
            command=self._on_percentile_changed,
        )
        self._percentile_seg.set("—")
        self._percentile_seg.pack(fill="x", padx=18, pady=(0, 8))

        self._min_score_label = ctk.CTkLabel(self._adv_frame, text="Score mínimo: 0.00",
                                              font=ctk.CTkFont(size=11), text_color=_SB_MUTED, anchor="w")
        self._min_score_label.pack(fill="x", padx=18)
        self._min_score_slider = ctk.CTkSlider(self._adv_frame, from_=0, to=1, number_of_steps=100,
                                                fg_color=_SB_BORDER, progress_color=_ACCENT,
                                                button_color=_ACCENT, button_hover_color=_ACCENT_DIM,
                                                command=self._on_filter_changed)
        self._min_score_slider.set(0)
        self._min_score_slider.pack(fill="x", padx=18, pady=(2, 10))

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

    def _build_section(self, parent, label: str):
        """Cabecera de sección en la sidebar oscura."""
        band = ctk.CTkFrame(parent, fg_color=_SB_SECTION, corner_radius=4, height=22)
        band.pack(fill="x", padx=10, pady=(8, 2))
        band.pack_propagate(False)
        inner = ctk.CTkFrame(band, fg_color="transparent")
        inner.pack(fill="both", expand=True)
        ctk.CTkFrame(inner, width=3, fg_color=_ACCENT, corner_radius=2,
                     ).pack(side="left", fill="y", padx=(4, 6), pady=3)
        ctk.CTkLabel(inner, text=label.upper(),
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_SB_MUTED, anchor="w",
                     ).pack(side="left", fill="both", expand=True)

    # ═══════════════════════════════════════════
    # Pestaña 1 — Corpus
    # ═══════════════════════════════════════════

    def _build_tab_corpus(self):
        tab = self._tabview.tab("Corpus")
        _tab_header(tab, "Corpus",
                    "Documentos procesados, estadísticas lingüísticas y metadatos del corpus.")

        # ── Tarjeta de resumen ──
        summary = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=10,
                               border_width=1, border_color=_BORDER)
        summary.pack(fill="x", padx=18, pady=(18, 8))
        self._corpus_summary_label = ctk.CTkLabel(
            summary, text="Sin corpus cargado. Realiza una extracción primero.",
            font=ctk.CTkFont(size=12), text_color=_TEXT_MUTED,
        )
        self._corpus_summary_label.pack(pady=12)

        # ── Cabecera tabla ──
        hdr = ctk.CTkFrame(tab, fg_color="transparent")
        hdr.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(hdr, text="Documentos del corpus",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=_TEXT).pack(side="left")
        ctk.CTkButton(
            hdr, text="Exportar CSV", width=120, height=28,
            fg_color="transparent", hover_color=_BG_CARD,
            border_width=1, border_color=_ACCENT2,
            text_color=_ACCENT2, font=ctk.CTkFont(size=11),
            command=self._export_corpus_csv,
        ).pack(side="right")

        # ── Treeview de documentos ──
        corpus_wrap = tk.Frame(tab, bg=_BG_ROOT)
        corpus_wrap.pack(fill="x", padx=18, pady=(0, 0))

        self._corpus_tree = ttk.Treeview(
            corpus_wrap,
            style="TECLA.Treeview",
            columns=("num", "doc", "tokens", "sents", "types", "ttr", "autor", "año", "tema"),
            show="headings",
            selectmode="browse",
            height=8,
        )
        corpus_cols = [
            ("num",    "#",          42,  False, "e"),
            ("doc",    "Documento", 200,  True,  "w"),
            ("tokens", "Tokens",     80,  False, "e"),
            ("sents",  "Oraciones",  90,  False, "e"),
            ("types",  "Tipos",      80,  False, "e"),
            ("ttr",    "TTR",        70,  False, "e"),
            ("autor",  "Autor",     120,  False, "w"),
            ("año",    "Año",        55,  False, "c"),
            ("tema",   "Tema",      160,  True,  "w"),
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
        ctk.CTkLabel(row1, text="Tema:", font=ctk.CTkFont(size=11),
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
        total_types = sum(d["types"]     for d in self._doc_stats)
        corpus_ttr  = round(total_types / total_tok, 4) if total_tok else 0.0
        self._corpus_summary_label.configure(
            text=(f"  {len(self._doc_stats)} documentos   ·   {total_tok:,} tokens"
                  f"   ·   {total_sent:,} oraciones   ·   {total_types:,} tipos únicos"
                  f"   ·   TTR {corpus_ttr:.4f}  "),
            text_color=_ACCENT,
        )

        self._corpus_tree.delete(*self._corpus_tree.get_children())
        for i, d in enumerate(self._doc_stats, 1):
            meta = self._corpus_metadata.get(d["doc_id"], {})
            tag  = "odd" if i % 2 == 1 else "even"
            self._corpus_tree.insert("", "end", iid=d["doc_id"], tags=(tag,),
                values=(
                    f"{i}.",
                    d["doc_id"],
                    f"{d['tokens']:,}",
                    f"{d['sentences']:,}",
                    f"{d['types']:,}",
                    f"{d['ttr']:.4f}",
                    meta.get("autor", ""),
                    meta.get("año", ""),
                    meta.get("tema", ""),
                ))

    def _export_corpus_csv(self):
        if not self._doc_stats:
            messagebox.showwarning("Sin datos", "No hay datos de corpus para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="estadisticas_corpus.csv",
        )
        if not path:
            return
        total_tok   = sum(d["tokens"]    for d in self._doc_stats)
        total_sent  = sum(d["sentences"] for d in self._doc_stats)
        total_types = sum(d["types"]     for d in self._doc_stats)
        corpus_ttr  = round(total_types / total_tok, 4) if total_tok else 0.0
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["documento", "tokens", "oraciones", "tipos_unicos", "ttr",
                             "autor", "año", "tema", "fuente", "notas"])
            for d in self._doc_stats:
                meta = self._corpus_metadata.get(d["doc_id"], {})
                writer.writerow([
                    d["doc_id"], d["tokens"], d["sentences"], d["types"], d["ttr"],
                    meta.get("autor", ""), meta.get("año", ""),
                    meta.get("tema", ""), meta.get("fuente", ""), meta.get("notas", ""),
                ])
            writer.writerow([])
            writer.writerow(["TOTAL", total_tok, total_sent, total_types, corpus_ttr,
                             "", "", "", "", ""])
        messagebox.showinfo("Exportado", f"Tabla guardada en:\n{path}")

    # ═══════════════════════════════════════════
    # Pestaña 2 — Extracción
    # ═══════════════════════════════════════════

    def _build_tab_extraccion(self):
        tab = self._tabview.tab("Extracción")
        _tab_header(tab, "Extracción de candidatos a término",
                    "Registro del proceso y tabla de candidatos ordenados por terminologicidad.")

        # ── Log ──
        log_hdr = ctk.CTkFrame(tab, fg_color="transparent")
        log_hdr.pack(fill="x", padx=18, pady=(16, 0))
        ctk.CTkLabel(log_hdr, text="Registro del proceso",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkButton(log_hdr, text="Limpiar", width=68, height=24,
                      fg_color=_BG_CARD, hover_color=_BG_CARD2,
                      border_width=1, border_color=_BORDER,
                      text_color=_TEXT_MUTED,
                      font=ctk.CTkFont(size=11),
                      command=lambda: self.log_box.delete("1.0", "end"),
                      ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            tab, height=130, fg_color=_BG_LOG, text_color=_TEXT_LOG,
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
        ctk.CTkLabel(res_hdr, text="Términos extraídos",
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
        ctk.CTkSegmentedButton(sort_bar, values=list(_SORT_KEY_MAP.keys()),
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
            ("tfidf",    "TF-IDF",     66,  False, "e", True),
            ("cval",     "C-val",      62,  False, "e", False),
            ("ncval",    "NC-val",     62,  False, "e", True),
            ("freq",     "Frec",       50,  False, "e", True),
            ("freq_rel", "Frec/mil",   72,  False, "e", True),
            ("docs",     "Docs",       44,  False, "e", True),
        ]

        # Toggle row
        toggle_row = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=6)
        toggle_row.pack(fill="x", padx=18, pady=(0, 4))
        ctk.CTkLabel(toggle_row, text="Columnas:",
                     font=ctk.CTkFont(size=10), text_color=_TEXT_MUTED,
                     ).pack(side="left", padx=(8, 4))
        for cid, heading, width, stretch, anchor, default_on in self._RESULT_COLS:
            if cid in ("num", "term"):
                continue  # siempre visibles, no se togglean
            var = ctk.BooleanVar(value=default_on)
            self._col_visible[cid] = var
            ctk.CTkCheckBox(
                toggle_row, text=heading, variable=var,
                width=16, height=16,
                fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                checkmark_color="#ffffff",
                text_color=_TEXT_MUTED, font=ctk.CTkFont(size=10),
                command=lambda c=cid, w=width, st=stretch: self._toggle_col(c, w, st),
            ).pack(side="left", padx=(0, 8))

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

    # ═══════════════════════════════════════════
    # Pestaña 3 — Gráficos
    # ═══════════════════════════════════════════

    def _extraction_graphs_dir(self) -> Path:
        workdir = self.corpus_path_var.get()
        base = Path(workdir) if workdir else Path.home()
        out = base / "_tecla_output" / "graphs" / "extraction"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _evaluation_graphs_dir(self) -> Path:
        workdir = self.corpus_path_var.get()
        base = Path(workdir) if workdir else Path.home()
        out = base / "_tecla_output" / "graphs" / "evaluation"
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _update_graficos(self):
        """Genera los gráficos de extracción y los guarda como PNG."""
        if not self._all_results:
            return

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            self._log("⚠  Instala matplotlib para generar los gráficos: pip install matplotlib")
            return

        scores  = [t["terminologicity"]    for t in self._all_results]
        freqs   = [t["frequency"]          for t in self._all_results]
        tfidf   = [t.get("tf_idf", 0)     for t in self._all_results]
        ncval   = [t.get("nc_value", 0)   for t in self._all_results]
        doc_frq = [t["doc_frequency"]   for t in self._all_results]
        top20   = sorted(self._all_results, key=lambda t: t["frequency"], reverse=True)[:20]

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

        sc = ax3.scatter(tfidf, ncval, c=scores, cmap="YlGn", alpha=0.7, s=20, edgecolors="none")
        ax3.set_title("Correlación entre TF-IDF y NC-value", color=_TEXT, fontsize=9, weight="bold")
        ax3.set_xlabel("TF-IDF", color=_TEXT_MUTED, fontsize=8)
        ax3.set_ylabel("NC-value", color=_TEXT_MUTED, fontsize=8)
        cb = fig2.colorbar(sc, ax=ax3)
        cb.set_label("Terminologicidad", color=_TEXT_MUTED, fontsize=7)

        ax4.scatter(doc_frq, freqs, c=scores, cmap="YlGn", alpha=0.7, s=20, edgecolors="none")
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

        # Layout: lista izquierda + detalle derecha
        left = ctk.CTkFrame(tab, width=260, fg_color=_BG_CARD, corner_radius=10,
                            border_width=1, border_color=_BORDER)
        left.pack(side="left", fill="y", padx=(18, 6), pady=16)
        left.pack_propagate(False)

        right = ctk.CTkFrame(tab, fg_color=_BG_CARD, corner_radius=10,
                             border_width=1, border_color=_BORDER)
        right.pack(side="right", fill="both", expand=True, padx=(0, 18), pady=16)

        # ── Lista izquierda ──
        ctk.CTkLabel(left, text="Lista de candidatos",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=_TEXT,
                     ).pack(fill="x", padx=10, pady=(12, 4))

        self._rev_filter_var = ctk.StringVar(value="Todos")
        ctk.CTkSegmentedButton(left,
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
        self._rev_term_label = ctk.CTkLabel(right, text="Selecciona un término",
                                             font=ctk.CTkFont(size=17, weight="bold"),
                                             text_color=_TEXT_MUTED)
        self._rev_term_label.pack(fill="x", padx=22, pady=(20, 2))

        ctk.CTkFrame(right, height=1, fg_color=_BORDER).pack(fill="x", padx=22, pady=(6, 10))

        ctk.CTkLabel(right, text="ESTADO",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED, anchor="w",
                     ).pack(fill="x", padx=22, pady=(0, 4))

        status_row = ctk.CTkFrame(right, fg_color="transparent")
        status_row.pack(fill="x", padx=22, pady=(0, 14))
        self._rev_status_btns = {}
        for status, color in _STATUS_COLOR.items():
            btn = ctk.CTkButton(
                status_row, text=status.capitalize(), height=34,
                fg_color=_BG_CARD, hover_color=_BG_CARD2,
                border_width=2, border_color=color,
                text_color=color,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda s=status: self._set_review_status(s),
            )
            btn.pack(side="left", padx=(0, 8))
            self._rev_status_btns[status] = btn

        ctk.CTkFrame(right, height=1, fg_color=_BORDER).pack(fill="x", padx=22, pady=4)

        ctk.CTkLabel(right, text="NOTAS",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED, anchor="w",
                     ).pack(fill="x", padx=22, pady=(10, 4))
        self._rev_notes = ctk.CTkTextbox(right, height=160,
                                          fg_color=_BG_CARD, text_color=_TEXT,
                                          border_width=1, border_color=_BORDER,
                                          font=ctk.CTkFont(size=12),
                                          corner_radius=6)
        self._rev_notes.pack(fill="x", padx=22, pady=(0, 10))

        ctk.CTkButton(right, text="💾  Guardar notas", height=34,
                      fg_color=_ACCENT, hover_color=_ACCENT_DIM,
                      text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8,
                      command=self._save_review_notes,
                      ).pack(anchor="w", padx=22, pady=(0, 16))

        ctk.CTkFrame(right, height=1, fg_color=_BORDER).pack(fill="x", padx=22, pady=4)

        # ── Estadísticas del término ──
        ctk.CTkLabel(right, text="DATOS DE LA EXTRACCIÓN",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=_TEXT_MUTED, anchor="w",
                     ).pack(fill="x", padx=22, pady=(10, 4))

        self._rev_stats_frame = ctk.CTkFrame(right, fg_color=_BG_CARD2, corner_radius=8)
        self._rev_stats_frame.pack(fill="x", padx=22, pady=(0, 8))

        self._rv: dict = {}  # value-label references

        # Row 1: Score · TF-IDF · C-val · NC-val
        _r1 = ctk.CTkFrame(self._rev_stats_frame, fg_color="transparent")
        _r1.pack(fill="x", padx=10, pady=(10, 4))
        for key, lbl in [("score", "Score"), ("tfidf", "TF-IDF"),
                          ("cval", "C-val"), ("ncval", "NC-val")]:
            _cell = ctk.CTkFrame(_r1, fg_color="transparent")
            _cell.pack(side="left", expand=True)
            ctk.CTkLabel(_cell, text=lbl,
                         font=ctk.CTkFont(size=9), text_color=_TEXT_MUTED).pack()
            self._rv[key] = ctk.CTkLabel(_cell, text="—",
                                         font=ctk.CTkFont(size=12, weight="bold"),
                                         text_color=_TEXT)
            self._rv[key].pack()

        ctk.CTkFrame(self._rev_stats_frame, height=1,
                     fg_color=_BORDER).pack(fill="x", padx=10, pady=2)

        # Row 2: Frecuencia · Frec/mil · Docs
        _r2 = ctk.CTkFrame(self._rev_stats_frame, fg_color="transparent")
        _r2.pack(fill="x", padx=10, pady=(4, 4))
        for key, lbl in [("freq", "Frecuencia"), ("freqrel", "Frec/mil"), ("docs", "Docs")]:
            _cell = ctk.CTkFrame(_r2, fg_color="transparent")
            _cell.pack(side="left", expand=True)
            ctk.CTkLabel(_cell, text=lbl,
                         font=ctk.CTkFont(size=9), text_color=_TEXT_MUTED).pack()
            self._rv[key] = ctk.CTkLabel(_cell, text="—",
                                         font=ctk.CTkFont(size=12), text_color=_TEXT)
            self._rv[key].pack()

        ctk.CTkFrame(self._rev_stats_frame, height=1,
                     fg_color=_BORDER).pack(fill="x", padx=10, pady=2)

        # Row 3: Patrón
        _r3 = ctk.CTkFrame(self._rev_stats_frame, fg_color="transparent")
        _r3.pack(fill="x", padx=10, pady=(4, 4))
        ctk.CTkLabel(_r3, text="Patrón",
                     font=ctk.CTkFont(size=9), text_color=_TEXT_MUTED).pack(anchor="w")
        self._rv["pattern"] = ctk.CTkLabel(_r3, text="—",
                                            font=ctk.CTkFont(size=10),
                                            text_color=_TEXT, anchor="w",
                                            wraplength=380, justify="left")
        self._rv["pattern"].pack(fill="x")

        # Row 4: Variantes (oculto cuando vacío)
        self._rv["variants"] = ctk.CTkLabel(self._rev_stats_frame, text="",
                                             font=ctk.CTkFont(size=10),
                                             text_color=_ACCENT2, anchor="w",
                                             wraplength=380, justify="left")
        self._rv["variants"].pack(fill="x", padx=10, pady=(0, 8))

    def _render_revision_list(self, _=None):
        for w in self._rev_term_btns.values():
            w.destroy()
        self._rev_term_btns = {}

        filter_val = self._rev_filter_var.get().lower()

        for t in self._all_results:
            term  = t["lemma"]
            entry = self._review_data.get(term, {"status": "pendiente", "notes": ""})
            if filter_val != "todos" and entry["status"] != filter_val:
                continue

            color = _STATUS_COLOR[entry["status"]]
            btn = ctk.CTkButton(
                self._rev_list_scroll,
                text=f"●  {term}",
                anchor="w", height=28,
                fg_color="transparent",
                hover_color=_BG_CARD,
                text_color=color,
                font=ctk.CTkFont(size=11),
                command=lambda term=term: self._select_revision_term(term),
            )
            btn.pack(fill="x", pady=1)
            self._rev_term_btns[term] = btn

        if not self._rev_term_btns:
            ctk.CTkLabel(self._rev_list_scroll, text="Sin términos.",
                         text_color=_TEXT_MUTED, font=ctk.CTkFont(size=11),
                         ).pack(pady=20)

    def _select_revision_term(self, term: str):
        self._rev_selected = term
        entry = self._review_data.setdefault(term, {"status": "pendiente", "notes": ""})

        self._rev_term_label.configure(text=term, text_color=_TEXT)

        # Resaltar botón de estado activo
        for s, btn in self._rev_status_btns.items():
            active = (s == entry["status"])
            btn.configure(
                fg_color=_STATUS_COLOR[s] if active else _BG_CARD2,
                text_color="#ffffff" if active else _STATUS_COLOR[s],
            )

        # Notas
        self._rev_notes.delete("1.0", "end")
        self._rev_notes.insert("1.0", entry.get("notes", ""))

        # Estadísticas del término
        t_data = next((t for t in self._all_results if t["lemma"] == term), None)
        if t_data:
            self._rv["score"].configure(text=f"{t_data['terminologicity']:.4f}")
            self._rv["tfidf"].configure(text=f"{t_data.get('tf_idf', 0):.1f}")
            self._rv["cval"].configure(text=f"{t_data.get('c_value', 0):.2f}")
            self._rv["ncval"].configure(text=f"{t_data.get('nc_value', 0):.2f}")
            self._rv["freq"].configure(text=str(t_data["frequency"]))
            self._rv["freqrel"].configure(text=f"{t_data.get('freq_rel', 0):.2f}")
            self._rv["docs"].configure(text=str(t_data["doc_frequency"]))
            self._rv["pattern"].configure(
                text=" / ".join(t_data.get("patterns", [])) or "—"
            )
            variants = t_data.get("variants", [])
            self._rv["variants"].configure(
                text="Variantes: " + " · ".join(variants) if variants else ""
            )

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
            fg_color=_ACCENT, hover_color=_ACCENT2,
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
        if self._eval_running or not self._all_results or not self._doc_stats:
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
            dp_scores = compute_dp(self._all_results, self._doc_stats)
            dp_sum    = dp_stats(dp_scores, self._all_results)
            rep_fast  = compute_representativity_score(heaps, hapax, dp_sum)
            self.after(0, self._render_eval_fast, heaps, dp_scores, rep_fast)
            self.after(0, self._eval_btn.configure,
                       {"text": "Calculando estabilidad (bootstrap)…"})

            # ── Fase 2: bootstrap (más lento) ─────────────────────────────
            stability = compute_bootstrap_stability(self._all_results, self._doc_stats)
            rep = compute_representativity_score(heaps, hapax, dp_sum, stability=stability)
            self.after(0, self._render_bootstrap_results, stability, rep)

            # ── Fase 3: cobertura externa (solo si hay lista cargada) ──────
            if self._gold_terms:
                self.after(0, self._compute_and_render_coverage)

        except Exception as exc:
            self.after(0, self._log, f"[Evaluación] {exc}")
        finally:
            self._eval_running = False
            self.after(0, self._eval_btn.configure,
                       {"state": "normal", "text": "Recalcular representatividad"})

    def _render_eval_fast(self, heaps, dp_scores, rep):
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

        # Componentes
        comp = rep.get("components", {})
        parts = [f"{k.capitalize()}: {v}" for k, v in comp.items()]
        self._eval_components_label.configure(text="   ·   ".join(parts))

        # Barra de escala
        self._draw_eval_scale(score, color)

        # DP scores guardados para bootstrap
        self._eval_dp_scores = dp_scores

        # Tabla DP — top 50 términos, ordenados por terminologicidad
        self._eval_dp_tree.delete(*self._eval_dp_tree.get_children())
        top_terms = sorted(self._all_results,
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
        if dp_scores and self._all_results:
            top20 = sorted(self._all_results,
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
        if self._all_results:
            freqs = [t["frequency"] for t in self._all_results]
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
        if not self._all_results:
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
            rows = compute_keyness(self._all_results, reference, corpus_size, ref_size)
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
            if self._all_results:
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
        if not self._gold_terms or not self._all_results:
            return
        from tecla.evaluation.term_eval import evaluate_extraction
        result = evaluate_extraction(self._all_results, self._gold_terms, mode="exact")
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
            out = Path(path) / "_tecla_revision.json"
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
        f = Path(path) / "_tecla_revision.json"
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                self._review_data = data.get("terms", {})
            except Exception:
                self._review_data = {}

    # ═══════════════════════════════════════════
    # Metadatos del corpus
    # ═══════════════════════════════════════════

    def _load_corpus_metadata(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        f = Path(path) / "_tecla_metadata.json"
        if f.exists():
            try:
                self._corpus_metadata = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                self._corpus_metadata = {}
        else:
            self._corpus_metadata = {}

    def _save_corpus_metadata(self):
        path = self.corpus_path_var.get()
        if not path:
            return
        try:
            out = Path(path) / "_tecla_metadata.json"
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
        # Actualizar la celda en el Treeview
        meta = self._corpus_metadata[doc_id]
        try:
            vals = list(self._corpus_tree.item(doc_id, "values"))
            vals[6] = meta["autor"]
            vals[7] = meta["año"]
            vals[8] = meta["tema"]
            self._corpus_tree.item(doc_id, values=vals)
        except Exception:
            pass

    # ═══════════════════════════════════════════
    # Callbacks del sidebar
    # ═══════════════════════════════════════════

    def _toggle_advanced(self):
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self._adv_frame.pack(fill="x")
            self._adv_toggle_btn.configure(text="▾  Opciones avanzadas")
        else:
            self._adv_frame.pack_forget()
            self._adv_toggle_btn.configure(text="▸  Opciones avanzadas")

    def _on_preset_changed(self, value: str):
        self._preset_hint.configure(text=_PRESET_HINTS.get(value, ""))

    def _on_max_len_changed(self, _=None):
        val = int(round(self._max_len_slider.get()))
        self.max_term_length_var.set(val)
        self._max_len_label.configure(text=f"Tokens máx. por candidato: {val}")

    def _browse_corpus(self):
        folder = filedialog.askdirectory(title="Seleccionar directorio de trabajo")
        if folder:
            self.corpus_path_var.set(folder)

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
            self._stoplist_entry.delete(0, "end")
            self._stoplist_entry.insert(0, ", ".join(words))
        except Exception as e:
            messagebox.showerror("TECLA", f"No se pudo leer el archivo:\n{e}")

    def _get_extra_stoplist(self) -> list:
        raw = self._stoplist_entry.get().strip()
        return [w.strip() for w in raw.split(",") if w.strip()] if raw else []

    # ═══════════════════════════════════════════
    # Filtro y ordenación (pestaña Extracción)
    # ═══════════════════════════════════════════

    def _on_filter_changed(self, _=None):
        freq_val  = int(round(self._min_freq_slider.get()))
        score_val = self._min_score_slider.get()
        self._min_freq_label.configure(text=f"Frecuencia mínima: {freq_val}")
        self._min_score_label.configure(text=f"Score mínimo: {score_val:.2f}")
        if self._all_results:
            self._apply_filters()

    def _on_percentile_changed(self, value=None):
        _PCT_MAP = {"—": 0, "p25": 25, "p50": 50, "p75": 75, "p90": 90}
        pct = _PCT_MAP.get(value or self._percentile_seg.get(), 0)
        self._percentile_var.set(pct)
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

    def _apply_filters(self):
        min_freq  = int(round(self._min_freq_slider.get()))
        min_score = self._min_score_slider.get()

        # Percentile threshold: compute score cutoff from all results
        pct = self._percentile_var.get()
        if pct > 0 and self._all_results:
            all_scores = sorted(t["terminologicity"] for t in self._all_results)
            idx = int(len(all_scores) * pct / 100)
            pct_threshold = all_scores[min(idx, len(all_scores) - 1)]
        else:
            pct_threshold = 0.0

        effective_min_score = max(min_score, pct_threshold)

        exclude_hapax = self._exclude_hapax_var.get()
        include_mono  = self._include_mono_var.get()

        filtered = [
            t for t in self._all_results
            if t["frequency"] >= min_freq
            and t["terminologicity"] >= effective_min_score
            and not (exclude_hapax and t["frequency"] == 1)
            and not (not include_mono and len(t["lemma"].split()) == 1)
        ]
        sort_field = _SORT_KEY_MAP[self._sort_key_var.get()]
        reverse    = self._sort_reverse
        if sort_field == "term":
            reverse = not reverse
        filtered.sort(key=lambda t: t.get(sort_field) or 0, reverse=reverse)
        self._render_results(filtered)

    def _toggle_col(self, col_id: str, orig_width: int, stretch: bool):
        visible = self._col_visible[col_id].get()
        if visible:
            self._results_tree.column(col_id, width=orig_width,
                                      stretch=stretch, minwidth=orig_width)
        else:
            self._results_tree.column(col_id, width=0, stretch=False, minwidth=0)

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
        path = filedialog.asksaveasfilename(title="Exportar términos",
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
        path = filedialog.asksaveasfilename(title="Exportar TBX",
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
                    "extra_stoplist": self._get_extra_stoplist() or None,
                },
                extraction_options={
                    "multiword_only": not self._include_mono_var.get(),
                    "max_term_length": self.max_term_length_var.get(),
                    "weights": _WEIGHT_PRESETS[self.weight_preset.get()],
                    "grammar_path": self.grammar_path_var.get() or None,
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
        self._corpus_language = language
        self._documents       = documents
        self._doc_stats    = []

        for doc in documents:
            doc_id   = doc["doc_id"]
            tokens   = doc["tokens"]
            sents    = doc.get("sentences", [])
            types    = len({t["lemma"] for t in tokens})
            n_tokens = len(tokens)
            ttr      = round(types / n_tokens, 4) if n_tokens else 0.0
            self._doc_stats.append({
                "doc_id":    doc_id,
                "tokens":    n_tokens,
                "sentences": len(sents),
                "types":     types,
                "ttr":       ttr,
            })

        self._load_corpus_metadata()
        self._render_corpus_tab()

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
        self._load_review_data()
        self._render_revision_list()

        # Resetear filtros
        self._min_freq_slider.set(1)
        self._min_score_slider.set(0)
        self._min_freq_label.configure(text="Frecuencia mínima: 1")
        self._min_score_label.configure(text="Score mínimo: 0.00")
        self._exclude_hapax_var.set(False)

        self._percentile_var.set(0)
        self._percentile_seg.set("—")

        self._apply_filters()
        self._update_graficos()
        if self._eval_btn is not None:
            self._eval_btn.configure(state="normal")

    def _clear_results(self):
        self._results_tree.delete(*self._results_tree.get_children())
        self._results_data = []
        self._all_results  = []
        self._term_count_label.configure(text="")

    def _render_results(self, results):
        self._results_tree.delete(*self._results_tree.get_children())
        self._results_data = results

        n     = len(results)
        total = len(self._all_results)
        self._term_count_label.configure(
            text=f"{n} término{'s' if n != 1 else ''}" if n == total
            else f"{n} de {total} términos"
        )

        if not results:
            return

        for i, t in enumerate(results, 1):
            pats     = "/".join(t.get("patterns", []))
            variants = t.get("variants", [])
            var_str  = " · ".join(variants) if variants else "—"
            tag      = "odd" if i % 2 == 1 else "even"
            self._results_tree.insert("", "end", iid=str(i - 1),
                values=(
                    f"{i}.",
                    t["lemma"],
                    var_str,
                    pats,
                    f"{t['terminologicity']:.4f}",
                    f"{t.get('tf_idf', 0):.4f}",
                    f"{t.get('c_value', 0):.4f}",
                    f"{t.get('nc_value', 0):.4f}",
                    t["frequency"],
                    f"{t.get('freq_rel', 0):.2f}",
                    t["doc_frequency"],
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
