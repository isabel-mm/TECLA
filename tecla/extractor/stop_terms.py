"""
TECLA – Stop-term lists
-----------------------

Phrases that look like terminological candidates (they pass POS filters)
but are generic academic or methodological language rather than domain terms.

Entries are compared against the **lemmatized, lowercase** form stored in
each term's ``lemma`` field.  Add new entries in lowercase.

Two types of entries are supported:
  - Exact strings  → matched against ``term["lemma"]``
  - Prefix/suffix patterns  → matched via _STOP_PATTERNS (compiled once)

Keep the lists conservative: only exclude what is clearly *not* a term in
any specialised domain.  Domain-specific stop-terms (e.g. "present corpus"
in corpus linguistics) can be passed at runtime via the ``extra`` parameter
of ``is_stop_term()``.
"""

from __future__ import annotations
import re
import unicodedata
from pathlib import Path
from typing import Set

_RESOURCES_DIR = Path(__file__).parent / "resources"


def _fold(text: str) -> str:
    """Lowercase and strip diacritics, so that "análisis" matches the
    accent-free lemma "analisis" produced by the lemma normaliser."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


def _load_txt_list(filename: str) -> frozenset:
    """Load a plain-text word/phrase list (one entry per line) from resources/."""
    path = _RESOURCES_DIR / filename
    if not path.exists():
        return frozenset()
    with open(path, encoding="utf-8") as f:
        return frozenset(
            _fold(line)
            for line in f
            if line.strip() and not line.startswith("#")
        )


# ── English stop-terms (exact lemma match) ────────────────────────────────────
_EN_CORE: frozenset[str] = frozenset({
    # Self-references to the paper / study
    "present study", "present paper", "present article", "present work",
    "current study", "current paper", "current work", "current article",
    "previous study", "previous work", "previous research", "previous paper",
    "recent study", "recent work", "recent research", "recent paper",
    "future study", "future work", "future research",
    "following section", "previous section", "next section",

    # Generic research-process phrases
    "research question", "research method", "research design",
    "research context", "research process", "research objective",
    "research finding", "research result", "main result", "key result",
    "main finding", "key finding", "main contribution",
    "data collection", "data analysis", "data set", "data point",
    "sample size", "effect size", "response rate",
    "statistical analysis", "quantitative analysis", "qualitative analysis",
    "content analysis", "discourse analysis",
    "analytical framework", "theoretical framework", "conceptual framework",
    "methodological framework",
    "literature review", "systematic review",
    "significant difference", "significant effect", "significant result",
    "independent variable", "dependent variable", "control variable",
    "experimental group", "control group",
    "mean score", "standard deviation", "confidence interval",
    "null hypothesis", "alternative hypothesis",
    "positive correlation", "negative correlation",
    "first author", "second author", "corresponding author",
    "native speaker", "non-native speaker",
    "spoken language", "written language",
    "large corpus", "small corpus", "large sample", "small sample",
    "high frequency", "low frequency", "medium frequency",
    "first language", "second language", "target language", "source language",
    "language learner", "language learning", "language teaching",
})

_EN: frozenset[str] = (
    _EN_CORE
    | _load_txt_list("stop_en.txt")
    | _load_txt_list("en_academic_discourse.txt")
    | _load_txt_list("en_academic_collocations.txt")
    | _load_txt_list("BAWE_blacklist_verbs.txt")
)

# ── Spanish stop-terms (exact lemma match) ────────────────────────────────────
_ES_CORE: frozenset[str] = frozenset({
    # Autorreferencias al artículo / estudio
    "presente estudio", "presente trabajo", "presente artículo",
    "presente investigación", "presente análisis",
    "estudio previo", "trabajo previo", "investigación previa",
    "estudio anterior", "trabajo anterior", "investigación anterior",
    "estudio reciente", "trabajo reciente", "investigación reciente",
    "trabajo futuro", "investigación futura", "estudio futuro",
    "sección siguiente", "sección anterior", "siguiente sección",
    "apartado siguiente", "apartado anterior",

    # Proceso de investigación genérico
    "pregunta de investigación", "objetivo de investigación",
    "hipótesis de investigación", "método de investigación",
    "diseño de investigación", "proceso de investigación",
    "resultado principal", "resultado clave", "resultado significativo",
    "hallazgo principal", "hallazgo clave",
    "contribución principal", "contribución clave",
    "recogida de dato", "análisis de dato", "conjunto de dato",
    "tamaño de muestra", "tasa de respuesta",
    "análisis estadístico", "análisis cuantitativo", "análisis cualitativo",
    "análisis de contenido",
    "marco teórico", "marco conceptual", "marco metodológico",
    "marco analítico",
    "revisión bibliográfico", "revisión de literatura",
    "diferencia significativo", "efecto significativo", "resultado significativo",
    "variable dependiente", "variable independiente", "variable control",
    "grupo experimental", "grupo control",
    "desviación típico", "desviación estándar",
    "intervalo de confianza",
    "primer autor", "segundo autor",
    "hablante nativo", "hablante no nativo",
    "lengua hablado", "lengua escrito",
    "corpus grande", "corpus pequeño", "muestra grande", "muestra pequeño",
    "alta frecuencia", "baja frecuencia", "frecuencia alto", "frecuencia bajo",
    "primera lengua", "segunda lengua", "lengua meta", "lengua origen",
    "aprendiz de lengua", "aprendizaje de lengua", "enseñanza de lengua",
})

_ES: frozenset[str] = frozenset(_fold(e) for e in _ES_CORE) | _load_txt_list("stop_es.txt")

_BY_LANG: dict[str, frozenset[str]] = {
    "en": _EN,
    "es": _ES,
}

# ── Regex patterns (language-independent) ────────────────────────────────────
# Match lemmas that *start* or *end* with highly generic heads.
_STOP_PREFIX_RE = re.compile(
    r"^(?:figure|table|appendix|annex|section|chapter|example|note|footnote"
    r"|figura|tabla|apendice|anexo|seccion|capitulo|ejemplo|nota)\b",
    re.IGNORECASE,
)


def is_stop_term(
    lemma: str,
    language: str,
    extra: Set[str] | None = None,
) -> bool:
    """
    Return True if *lemma* is a stop-term for the given language.

    Parameters
    ----------
    lemma    : lowercased lemma string as stored in term["lemma"]
    language : ISO 639-1 code ("en" / "es")
    extra    : optional caller-supplied set of additional stop-terms
    """
    lemma = _fold(lemma)
    lang_set = _BY_LANG.get(language, frozenset())
    if lemma in lang_set:
        return True
    if extra and lemma in {_fold(e) for e in extra}:
        return True
    if _STOP_PREFIX_RE.match(lemma):
        return True
    return False
