"""
Text cleaning and linguistic normalisation utilities for the TECLA corpus module.

This module offers (all optional, activated by flag):

Structural noise
    rejoin_hyphens_flag             Reúne palabras partidas por guión al final de línea.
    structure                       Elimina números de página y líneas muy cortas.

Document metadata
    remove_section_headers_flag     Elimina líneas que son solo un título de sección
                                    (Introduction, Metodología, Conclusiones…).
    remove_keyword_lines_flag       Elimina líneas "Keywords: …" / "Palabras clave: …".
    remove_captions_flag            Elimina pies de figura y tabla (Figure 1, Tabla 3…).
    remove_urls_flag                Elimina líneas que son solo URL, DOI o email.
    remove_publication_metadata_flag Elimina copyright, licencias CC, fechas de recepción.
    remove_journal_metadata_flag    Elimina líneas de volumen/número/páginas de revista.
    remove_inline_citations_flag    Elimina marcadores de cita numérica [1], [2,3].
    remove_statistical_lines_flag   Elimina líneas mayoritariamente numéricas (tablas, stats).
    remove_bibliography_flag        Elimina la sección de referencias/bibliografía.

Lexical filtering
    remove_stopwords_flag           Elimina palabras vacías (spaCy + NLTK + lista extra).
    stoplist                        Stoplist personalizada (lista o ruta a .txt).
    lemmatize_flag                  Lematiza el texto con spaCy.

QA (no modifica el texto, solo informa)
    flag_discourse_noise(text, language)  Devuelve líneas que son solo marcadores
                                          de discurso genérico.

Design principles:
- Nothing is applied implicitly.
- Every operation is explicit, controlled by flags.
- Always fails gracefully (never breaks corpus building).
"""

import re
from pathlib import Path
import spacy
from .utils import load_stoplist

_RESOURCES_DIR = Path(__file__).resolve().parent.parent / "extractor" / "resources"

# ---------------------------------------------------------------------------
# SECTION HEADERS
# Títulos estructurales de sección que, si aparecen solos en una línea,
# son ruido estructural (no cuerpo del texto).
# ---------------------------------------------------------------------------

_SECTION_HEADERS: dict[str, frozenset] = {
    "en": frozenset({
        "abstract", "introduction", "background", "related work",
        "methodology", "methods", "method", "materials", "materials and methods",
        "results", "discussion", "conclusion", "conclusions",
        "limitations", "acknowledgements", "acknowledgments",
        "references", "bibliography", "appendix", "supplementary material",
        "keywords", "key words", "funding", "conflict of interest",
        "author contributions", "data availability",
    }),
    "es": frozenset({
        "resumen", "introducción", "antecedentes", "trabajo relacionado",
        "metodología", "métodos", "método", "materiales", "materiales y métodos",
        "resultados", "discusión", "conclusión", "conclusiones",
        "limitaciones", "agradecimientos", "agradecimiento",
        "referencias", "bibliografía", "apéndice", "material suplementario",
        "palabras clave", "financiación", "conflicto de intereses",
        "contribución de los autores", "disponibilidad de datos",
    }),
}

# Prefijos de líneas de metadatos de palabras clave
_KEYWORD_PREFIXES = re.compile(
    r"^\s*(?:keywords?|key\s*words?|palabras?\s*claves?|mots[\s\-]clés?"
    r"|paraules?\s*claus?|palavras?\s*[\-]?chave)\s*[:\-]",
    re.IGNORECASE,
)

# Patrón de número de sección al inicio de línea (ej: "1.", "2.3", "IV.")
_SECTION_NUM = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s*|[IVXLCDM]+\.?\s*)")

# ---------------------------------------------------------------------------
# STOPWORD MANAGEMENT (spaCy + NLTK + user)
# ---------------------------------------------------------------------------

import nltk
from nltk.corpus import stopwords as nltk_stopwords

NLTK_LANG_MAP = {
    "es": "spanish",
    "en": "english",
    "fr": "french",
    "de": "german",
    "pt": "portuguese",
    "it": "italian",
}


def get_language_stopwords(language, extra_stoplist=None):
    """
    Returns a unified stopword set combining:
    - spaCy's default stopwords
    - NLTK stopwords (if available)
    - optional extra stoplist provided by user

    Always returns a Python set().
    """

    lang = language.lower()
    combined = set()

    # ------------------------------- spaCy STOPWORDS ---------------------------
    try:
        nlp = _get_spacy_model(lang)
        combined |= {w.lower() for w in nlp.Defaults.stop_words}
    except Exception:
        print(f"⚠️ Could not load spaCy stopwords for '{lang}'.")

    # ------------------------------- NLTK STOPWORDS ----------------------------
    nltk_lang = NLTK_LANG_MAP.get(lang)
    if nltk_lang:
        try:
            nltk_sw = nltk_stopwords.words(nltk_lang)
        except LookupError:
            print(f"📥 Downloading NLTK stopwords for '{nltk_lang}'...")
            nltk.download("stopwords")
            nltk_sw = nltk_stopwords.words(nltk_lang)
        except Exception:
            print(f"⚠️ Error loading NLTK stopwords for '{lang}'.")
            nltk_sw = []
        combined |= {w.lower() for w in nltk_sw}

    # ------------------------------- EXTRA STOPLIST ----------------------------
    if extra_stoplist:
        if isinstance(extra_stoplist, list):
            combined |= {w.lower() for w in extra_stoplist}

        elif isinstance(extra_stoplist, str):  # path to .txt file
            try:
                extra = load_stoplist(extra_stoplist)
                combined |= {w.lower() for w in extra}
            except Exception:
                print(f"⚠️ Could not load extra stoplist file '{extra_stoplist}'. Skipping.")

    return combined


# ---------------------------------------------------------------------------
# SPACY MODELS
# ---------------------------------------------------------------------------

SPACY_MODEL_TABLE = {
    "en": "en_core_web_lg",
    "es": "es_core_news_md",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}

_SPACY_MODELS = {}


def _get_spacy_model(language):
    """
    Robust spaCy model loader:

    1. Try to load installed model.
    2. If not installed, download it.
    3. If download fails, fallback to spacy.blank(language).

    Always returns an NLP object.
    """

    import spacy.cli

    lang = language.lower()
    model_name = SPACY_MODEL_TABLE.get(lang)

    # Unsupported language -> blank model
    if not model_name:
        if lang not in _SPACY_MODELS:
            nlp = spacy.blank(lang)
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            _SPACY_MODELS[lang] = nlp
            print(f"✅ spaCy blank model initialised for language '{language}'")
        return _SPACY_MODELS[lang]

    # Cached model
    if model_name in _SPACY_MODELS:
        return _SPACY_MODELS[model_name]

    # Try loading installed model
    try:
        nlp = spacy.load(model_name)
        _SPACY_MODELS[model_name] = nlp
        print(f"✅ spaCy model '{model_name}' loaded successfully")
        return nlp

    except OSError:
        try:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
            _SPACY_MODELS[model_name] = nlp
            print(f"✅ spaCy model '{model_name}' downloaded and loaded successfully")
            return nlp

        except Exception:
            nlp = spacy.blank(lang)
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            _SPACY_MODELS[model_name] = nlp
            print(
                f"⚠️ spaCy model '{model_name}' unavailable. "
                f"Using blank model for '{language}'."
            )
            return nlp


# ---------------------------------------------------------------------------
# STRUCTURAL CLEANING
# ---------------------------------------------------------------------------

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$")


def clean_structure(text, remove_short_lines=True, remove_page_numbers=True):
    """Remove page numbers and extremely short lines."""
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if remove_page_numbers and PAGE_NUMBER_LINE.fullmatch(stripped):
            continue

        if remove_short_lines and len(stripped.split()) < 3:
            continue

        cleaned.append(stripped)

    return "\n".join(cleaned)


def remove_numeric_only_lines(text):
    """Remove lines containing only numbers or numeric markers."""
    pattern = r'^\s*[\(\[\{\-–—\*•●"]*\s*\d+\s*[\)\]\}\-–—\*•●"."]*\s*$'
    return "\n".join(
        line for line in text.splitlines()
        if not re.fullmatch(pattern, line)
    )


# ---------------------------------------------------------------------------
# BIBLIOGRAPHY REMOVAL
# ---------------------------------------------------------------------------

def _remove_bibliography_generic(text, section_titles, ref_patterns, min_position=0.7):
    """Internal helper for bibliography section deletion.

    [FIX 2026-07-16/17] Two safeguards, added after diagnosing catastrophic
    truncation of books and papers:

    1. HEADING-ONLY matching: the section title must constitute a line by
       itself (optionally preceded by a section number and followed by a
       colon). Without this, the lowercase word "references" in running prose
       ("...references to children...") triggered the cut.
    2. POSITIONAL safeguard: the heading must appear in the final portion of
       the document (beyond `min_position`). Real bibliographies live at the
       end; earlier headings are tables of contents or per-chapter reference
       lists in books, and cutting there amputates entire chapters.
    """
    n = len(text)
    title_res = [
        re.compile(
            r"^\s*(?:\d+(?:\.\d+)*\.?\s*|[IVXLCDM]+\.?\s+)?(?:" + title + r")\s*:?\s*$",
            re.IGNORECASE,
        )
        for title in section_titles
    ]
    # Variante "fusionada" (artefacto de PDF): el encabezado y la primera
    # referencia caen en la misma línea ("References Stefanowitsch, Anatol.").
    # Se exige apellido capitalizado seguido de coma para no confundir con prosa.
    title_res += [
        re.compile(r"^\s*(?:" + title + r")\s+[A-ZÀ-Þ][a-zà-ÿ]+,\s", re.IGNORECASE)
        for title in section_titles
    ]
    candidates = []
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and len(stripped) < 60:
            for tre in title_res:
                if tre.match(stripped):
                    if offset >= n * min_position:
                        tail = text[offset:]
                        if any(re.search(patt, tail) for patt in ref_patterns):
                            candidates.append(offset)
                    break
        offset += len(line)
    if candidates:
        return text[:min(candidates)].strip()
    return text


def remove_bibliography(text, language="en"):
    lang = language.lower()
    mapping = {
        "es": ([
            r'\bREFERENCIAS?\s+BIBLIOGR[ÁA]FICAS?\b',
            r'\bBIBLIOGRAF[ÍI]A\b'
        ], [r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s']),
        "en": ([
            r'\bREFERENCES\b',
            r'\bBIBLIOGRAPHY\b',
            r'\bWORKS\s+CITED\b'
        ], [r'\[\d+\]', r'\(\d{4}\)', r'https?://', r'\d+\.\s']),
        "fr": ([
            r'\bRÉFÉRENCES\b',
            r'\bBIBLIOGRAPHIE\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "de": ([
            r'\bLITERATUR\b',
            r'\bBIBLIOGRAPHIE\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "it": ([
            r'\bBIBLIOGRAFIA\b'
        ], [r'\(\d{4}\)', r'https?://']),
        "pt": ([
            r'\bREFERÊNCIAS\b',
            r'\bBIBLIOGRAFIA\b'
        ], [r'\(\d{4}\)', r'https?://']),
    }

    if lang not in mapping:
        return text

    sec_titles, ref_patts = mapping[lang]
    return _remove_bibliography_generic(text, sec_titles, ref_patts)


# ---------------------------------------------------------------------------
# STOPWORDS & LEMMATISATION
# ---------------------------------------------------------------------------

def remove_stopwords(text, stopwords):
    return " ".join(t for t in text.split() if t.lower() not in stopwords)


def apply_user_stoplist(text, stoplist):
    stopset = {w.lower() for w in stoplist}
    return " ".join(t for t in text.split() if t.lower() not in stopset)


def lemmatize_text(text, language="en"):
    nlp = _get_spacy_model(language)
    doc = nlp(text)
    return " ".join(token.lemma_ if token.lemma_ else token.text for token in doc)


# ---------------------------------------------------------------------------
# SECTION HEADER LINE REMOVAL
# Elimina líneas que son solo un título de sección (Introduction, Metodología…)
# posiblemente precedido por un número de sección.
# ---------------------------------------------------------------------------

def remove_section_header_lines(text: str, language: str = "en") -> str:
    """
    Elimina líneas que consisten únicamente en un título de sección estructural,
    opcionalmente precedido por un número (ej: "1. Introduction", "3.2 Resultados").

    Solo actúa sobre líneas cortas aisladas (< 80 caracteres) para evitar
    borrar frases legítimas que empiecen por la misma palabra.
    """
    lang = language.lower()
    headers = _SECTION_HEADERS.get(lang, frozenset())
    if not headers:
        return text

    cleaned = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) >= 80:
            cleaned.append(line)
            continue

        # Quitar número de sección inicial si lo hay
        core = _SECTION_NUM.sub("", stripped).strip().rstrip(":").strip().lower()

        if core in headers:
            continue  # línea de cabecera → descartar

        cleaned.append(line)

    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# KEYWORD METADATA LINE REMOVAL
# Elimina líneas del tipo "Keywords: corpus, NLP, annotation"
# ---------------------------------------------------------------------------

def remove_keyword_lines(text: str) -> str:
    """
    Elimina líneas que son listas de palabras clave (metadatos de artículos).
    Detecta prefijos en inglés, español, francés, catalán y portugués.
    """
    return "\n".join(
        line for line in text.splitlines()
        if not _KEYWORD_PREFIXES.match(line)
    )


# ---------------------------------------------------------------------------
# DISCOURSE NOISE DETECTION (QA)
# Devuelve líneas que consisten únicamente en marcadores de discurso
# genérico, sin contenido léxico sustantivo.
# ---------------------------------------------------------------------------

def _load_discourse_markers(language: str) -> frozenset:
    """Carga marcadores de discurso genérico desde las stoplists de TECLA."""
    filename = f"stop_{language}.txt"
    path = _RESOURCES_DIR / filename
    if not path.exists():
        return frozenset()
    with open(path, encoding="utf-8") as f:
        return frozenset(
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        )


def flag_discourse_noise(text: str, language: str = "en") -> list[str]:
    """
    Devuelve una lista de líneas del texto que consisten únicamente
    en marcadores de discurso genérico (sin contenido léxico real).

    Útil para revisión QA: estas líneas son candidatas a ser ruido
    estructural (headers sueltos, pies de página, etc.).

    No modifica el texto; solo informa.
    """
    markers = _load_discourse_markers(language)
    if not markers:
        return []

    suspicious = []
    for line in text.splitlines():
        stripped = line.strip().lower()
        if not stripped:
            continue
        # Línea corta que coincide exactamente con un marcador
        if stripped in markers and len(stripped.split()) <= 6:
            suspicious.append(line.strip())

    return suspicious


# ---------------------------------------------------------------------------
# HYPHENATION REJOINING
# Reúne palabras partidas por guión a final de línea (artefacto de PDF/OCR).
# "termi-\nnología" → "terminología"
# ---------------------------------------------------------------------------

def rejoin_hyphenated_words(text: str) -> str:
    """
    Reúne palabras divididas por guión al final de línea.
    Solo actúa cuando el guión está pegado a una letra en ambos lados,
    para no afectar a listas con guión o guiones largos estructurales.
    """
    return re.sub(r"([a-záéíóúüñA-ZÁÉÍÓÚÜÑ\w])-\n([a-záéíóúüñA-ZÁÉÍÓÚÜÑ\w])", r"\1\2", text)


# ---------------------------------------------------------------------------
# FIGURE / TABLE CAPTION REMOVAL
# Elimina líneas que son pie de figura o tabla (no son cuerpo del texto).
# ---------------------------------------------------------------------------

_CAPTION_LINE = re.compile(
    r"^\s*(?:fig(?:ure|ura)?s?\.?|tab(?:le|la)s?\.?|gr[aá]fico?s?\.?|cuadros?\.?|image?n?s?\.?|chart?s?\.?)"
    r"\s*\d+[\.\-:]?",
    re.IGNORECASE,
)


def remove_caption_lines(text: str) -> str:
    """
    Elimina líneas que empiezan con "Figure X", "Table X", "Fig. X",
    "Figura X", "Tabla X", "Gráfico X", etc.
    Solo actúa en líneas relativamente cortas (< 200 chars) para no
    borrar párrafos que citan figuras en medio de una frase.
    """
    cleaned = []
    for line in text.splitlines():
        stripped = line.strip()
        if _CAPTION_LINE.match(stripped) and len(stripped) < 200:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# URL / DOI / EMAIL LINE REMOVAL
# ---------------------------------------------------------------------------

_URL_LINE = re.compile(
    r"^\s*(?:https?://|www\.|ftp://|doi\s*:\s*10\.|https?://doi\.org/)\S+\s*$",
    re.IGNORECASE,
)
_EMAIL_LINE = re.compile(
    r"^\s*[\w.+\-]+@[\w\-]+\.[a-z]{2,}\s*$",
    re.IGNORECASE,
)
_DOI_LINE = re.compile(
    r"^\s*(?:doi|DOI)\s*[:\s]\s*10\.\d{4,}/\S+\s*$",
    re.IGNORECASE,
)


def remove_url_doi_email_lines(text: str) -> str:
    """
    Elimina líneas que son exclusivamente una URL, un DOI o una dirección
    de correo electrónico. No toca líneas de texto normal que contengan
    URLs en medio de una oración.
    """
    cleaned = []
    for line in text.splitlines():
        if _URL_LINE.match(line) or _EMAIL_LINE.match(line) or _DOI_LINE.match(line):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# PUBLICATION METADATA LINE REMOVAL
# Elimina líneas de copyright, licencia y fechas de recepción/aceptación.
# ---------------------------------------------------------------------------

_PUBLICATION_METADATA = re.compile(
    r"^\s*(?:"
    r"©|copyright\s|\(c\)\s*\d{4}"                          # copyright
    r"|creative\s+commons|cc\s+by"                           # licencias
    r"|this\s+(?:work|article|paper)\s+is\s+licensed"
    r"|este\s+(?:trabajo|art[íi]culo)\s+est[aá]\s+(?:bajo|publicado)"
    r"|received\s*:|recibido\s*:|re[çc]u\s*:"               # fechas
    r"|accepted\s*:|aceptado\s*:|accept[eé]\s*:"
    r"|published\s*:|publicado\s*:|publi[eé]\s*:"
    r"|available\s+online|disponible\s+en\s+l[íi]nea"
    r"|issn\s*[\:\-]|e-?issn\s*[\:\-]"                     # ISSN
    r")",
    re.IGNORECASE,
)


def remove_publication_metadata_lines(text: str) -> str:
    """
    Elimina líneas de metadatos de publicación: copyright, licencias CC,
    fechas de recepción/aceptación, ISSN.
    Solo actúa en líneas cortas (< 180 chars).
    """
    cleaned = []
    for line in text.splitlines():
        if _PUBLICATION_METADATA.match(line) and len(line.strip()) < 180:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# INLINE CITATION MARKER REMOVAL
# Elimina marcadores de cita numérica [1], [1,2,3], [1-4] dentro del texto.
# No toca citas autor-año (Smith, 2023) para no romper texto legítimo.
# ---------------------------------------------------------------------------

_INLINE_CITATION = re.compile(
    r"\[\s*\d+(?:\s*[,\-–]\s*\d+)*\s*\]"
)


def remove_inline_citations(text: str) -> str:
    """
    Elimina marcadores de cita numérica entre corchetes: [1], [2,3], [1-4].
    Deja intactas las citas autor-año entre paréntesis.
    """
    return _INLINE_CITATION.sub("", text)


# ---------------------------------------------------------------------------
# JOURNAL / VOLUME METADATA LINE REMOVAL
# Elimina líneas del tipo "Linguistics 12(3): 45–67" o "Vol. 14, No. 2, 2023"
# ---------------------------------------------------------------------------

_JOURNAL_METADATA = re.compile(
    r"^\s*(?:"
    r"vol(?:ume|umen)?\.?\s*\d+"                            # Vol. 14
    r"|n[oú]?(?:mero|\.?)?\s*\d+"                          # No. 3 / Número 2
    r"|\d+\s*\(\s*\d+\s*\)\s*[:\-–]\s*\d"                 # 12(3): 45
    r"|pp?\.?\s*\d+\s*[–\-]\s*\d+"                        # pp. 45-67
    r"|p[aá]g(?:inas?)?\.?\s*\d+"                          # pág. 45
    r")",
    re.IGNORECASE,
)


def remove_journal_metadata_lines(text: str) -> str:
    """
    Elimina líneas de metadatos de revista: volumen, número, páginas.
    Solo en líneas cortas (< 120 chars) para no afectar texto normal.
    """
    cleaned = []
    for line in text.splitlines():
        if _JOURNAL_METADATA.match(line) and len(line.strip()) < 120:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# MOSTLY-NUMERIC LINE REMOVAL
# Elimina líneas estadísticas o de tabla (coordenadas, p-valores, IDs…)
# que no aportan terminología.
# ---------------------------------------------------------------------------

_NON_NUMERIC = re.compile(r"[^\d\s\.\,\-\+\(\)\[\]%=/]")


def remove_statistical_lines(text: str, threshold: float = 0.75) -> str:
    """
    Elimina líneas en las que la proporción de caracteres numéricos y
    símbolos matemáticos supera `threshold` (por defecto 75%).

    Evita borrar años o fechas sueltas: solo actúa en líneas con
    al menos 6 caracteres.
    """
    cleaned = []
    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) < 6:
            cleaned.append(line)
            continue
        non_num_chars = len(_NON_NUMERIC.findall(stripped))
        ratio_numeric = 1 - (non_num_chars / len(stripped))
        if ratio_numeric >= threshold:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# MASTER CLEANING FUNCTION
# ---------------------------------------------------------------------------

def clean_text(
    text,
    structure=False,
    remove_stopwords_flag=False,
    stoplist=None,
    extra_stoplist=None,
    lemmatize_flag=False,
    remove_bibliography_flag=False,
    remove_section_headers_flag=False,
    remove_keyword_lines_flag=False,
    rejoin_hyphens_flag=False,
    remove_captions_flag=False,
    remove_urls_flag=False,
    remove_publication_metadata_flag=False,
    remove_inline_citations_flag=False,
    remove_journal_metadata_flag=False,
    remove_statistical_lines_flag=False,
    language="en",
):
    """
    Main public cleaning function.
    Fully modular: the user decide cada componente.

    Flags disponibles
    -----------------
    rejoin_hyphens_flag             : Reúne palabras partidas por guión al final de línea.
    remove_captions_flag            : Elimina pies de figura y tabla (Figure 1, Tabla 3…).
    remove_urls_flag                : Elimina líneas que son solo URL, DOI o email.
    remove_publication_metadata_flag: Elimina copyright, licencias CC, fechas de recepción.
    remove_inline_citations_flag    : Elimina marcadores de cita numérica [1], [2,3].
    remove_journal_metadata_flag    : Elimina líneas de volumen/número/páginas de revista.
    remove_statistical_lines_flag   : Elimina líneas mayoritariamente numéricas (tablas, stats).
    remove_section_headers_flag     : Elimina líneas que son solo un título de sección.
    remove_keyword_lines_flag       : Elimina líneas "Keywords: …" / "Palabras clave: …".
    remove_bibliography_flag        : Elimina la sección de referencias/bibliografía.
    structure                       : Elimina números de página y líneas muy cortas.
    """

    cleaned = text

    # 1. Reunir guiones de fin de línea (antes de cualquier otra operación)
    if rejoin_hyphens_flag:
        cleaned = rejoin_hyphenated_words(cleaned)

    # 2. Eliminar marcadores de cita inline [1], [2,3]
    if remove_inline_citations_flag:
        cleaned = remove_inline_citations(cleaned)

    # 3. Bibliografía
    if remove_bibliography_flag:
        cleaned = remove_bibliography(cleaned, language)
        cleaned = remove_numeric_only_lines(cleaned)

    # 4. Cabeceras de sección
    if remove_section_headers_flag:
        cleaned = remove_section_header_lines(cleaned, language)

    # 5. Líneas de palabras clave
    if remove_keyword_lines_flag:
        cleaned = remove_keyword_lines(cleaned)

    # 6. Pies de figura/tabla
    if remove_captions_flag:
        cleaned = remove_caption_lines(cleaned)

    # 7. URLs, DOIs, emails
    if remove_urls_flag:
        cleaned = remove_url_doi_email_lines(cleaned)

    # 8. Metadatos de publicación (copyright, fechas, ISSN)
    if remove_publication_metadata_flag:
        cleaned = remove_publication_metadata_lines(cleaned)

    # 9. Metadatos de revista (Vol., No., pp.)
    if remove_journal_metadata_flag:
        cleaned = remove_journal_metadata_lines(cleaned)

    # 10. Líneas estadísticas/numéricas
    if remove_statistical_lines_flag:
        cleaned = remove_statistical_lines(cleaned)

    # 11. Limpieza estructural
    if structure:
        cleaned = clean_structure(cleaned)

    # 12. Stopwords combinadas
    if remove_stopwords_flag:
        sw = get_language_stopwords(language, extra_stoplist)
        if sw:
            cleaned = remove_stopwords(cleaned, sw)
        else:
            print(f"⚠️ No stopwords available for language '{language}'.")

    # 13. Stoplist de usuario
    if stoplist:
        if isinstance(stoplist, str):
            try:
                user_stop = load_stoplist(stoplist)
                cleaned = apply_user_stoplist(cleaned, user_stop)
            except Exception:
                print(f"⚠️ Invalid stoplist file '{stoplist}'. Skipping.")
        elif isinstance(stoplist, list):
            cleaned = apply_user_stoplist(cleaned, stoplist)
        else:
            print(f"⚠️ Ignoring invalid stoplist value: must be list or file path.")

    # 14. Lematización
    if lemmatize_flag:
        cleaned = lemmatize_text(cleaned, language)

    return cleaned
