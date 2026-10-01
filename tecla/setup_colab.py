"""
Full plug-and-play setup utility for TECLA in Google Colab.

Features:
- Instala todas las dependencias de TECLA
- El usuario selecciona las lenguas (modelos spaCy)
- Descarga recursos NLTK automáticamente
- Limpia módulos cacheados para evitar conflictos en Colab
- TECLA queda importable de inmediato
"""

import sys
import os
import importlib
import subprocess


# ---------------------------------------------------------------------
# Tabla de modelos spaCy
# ---------------------------------------------------------------------

SPACY_MODELS = {
    "en": "en_core_web_lg",
    "es": "es_core_news_md",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}

# Dependencias Python de TECLA
_DEPENDENCIES = [
    "pdfminer.six",
    "spacy>=3.0",
    "nltk",
    "langid",
    "pandas",
    "tqdm",
    "pyyaml",
]


# ---------------------------------------------------------------------
# Instalador pip
# ---------------------------------------------------------------------

def _pip_install(package: str) -> None:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", package]
        )
        print(f"   ✓ {package}")
    except Exception as e:
        print(f"   ⚠️  No se pudo instalar {package}: {e}")


def _install_dependencies() -> None:
    print("📦 Instalando dependencias de TECLA…")
    for pkg in _DEPENDENCIES:
        _pip_install(pkg)
    print("   Listo.\n")


# ---------------------------------------------------------------------
# Instalador de modelos spaCy
# ---------------------------------------------------------------------

def _ensure_spacy_models(languages: list) -> None:
    import spacy
    import spacy.cli

    print("🔤 Comprobando modelos spaCy para:", languages)

    for lang in languages:
        if lang not in SPACY_MODELS:
            print(f"   ⚠️  Lengua '{lang}' no admitida. Se omite.")
            continue

        model = SPACY_MODELS[lang]
        try:
            spacy.load(model)
            print(f"   ✓ Ya instalado: {model}")
        except OSError:
            print(f"   ⬇️  Descargando: {model}")
            try:
                spacy.cli.download(model)
                print(f"   ✓ Instalado: {model}")
            except Exception as e:
                print(f"   ⚠️  No se pudo descargar {model}: {e}")
                print(f"      → Se usará modelo en blanco en tiempo de ejecución.")
    print()


# ---------------------------------------------------------------------
# Recursos NLTK
# ---------------------------------------------------------------------

def _download_nltk_resources() -> None:
    import nltk

    print("📚 Descargando recursos NLTK…")
    for resource in ("stopwords", "punkt", "punkt_tab"):
        try:
            nltk.download(resource, quiet=True)
            print(f"   ✓ {resource}")
        except Exception as e:
            print(f"   ⚠️  No se pudo descargar {resource}: {e}")
    print()


# ---------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------

def setup_tecla(path: str = "/content/TECLA", languages: list | str = ["es", "en"]) -> bool:
    """
    Configura TECLA en Google Colab de forma completa.

    Parámetros
    ----------
    path : str
        Ruta al repositorio de TECLA clonado en Colab.
        Por defecto: "/content/TECLA"
    languages : list o "all"
        Lenguas para las que instalar modelos spaCy.
        Ejemplo: ["es", "en"] — admite "all" para instalar todos.

    Uso
    ---
    >>> from tecla.setup_colab import setup_tecla
    >>> setup_tecla(path="/content/TECLA", languages=["es", "en"])
    """

    print("🚀 Iniciando configuración de TECLA…\n")

    # Validar lenguas
    if languages == "all":
        languages = list(SPACY_MODELS.keys())
    elif isinstance(languages, str):
        languages = [languages]

    if not isinstance(languages, list):
        raise ValueError("languages debe ser una lista como ['es','en'] o 'all'.")

    # Añadir TECLA al path
    if not os.path.isdir(path):
        raise ValueError(
            f"Directorio no encontrado: {path}\n"
            f"Asegúrate de haber clonado el repositorio con:\n"
            f"  !git clone https://github.com/tu-usuario/TECLA {path}"
        )

    if path not in sys.path:
        sys.path.insert(0, path)
        print(f"📂 Ruta añadida al path: {path}\n")

    # Instalación
    _install_dependencies()
    _ensure_spacy_models(languages)
    _download_nltk_resources()

    # Limpiar módulos cacheados (necesario si se reinstala en Colab)
    removed = [m for m in list(sys.modules) if m.startswith("tecla")]
    for m in removed:
        del sys.modules[m]
    if removed:
        print(f"🧹 Módulos cacheados limpiados: {len(removed)}\n")

    # Validar importación
    try:
        importlib.import_module("tecla")
        print("✅ TECLA importado correctamente.")
    except Exception as e:
        raise ImportError(
            f"❌ TECLA no se pudo importar: {e}\n"
            f"Comprueba que la ruta '{path}' contiene el paquete 'tecla/'."
        )

    print("\n🎉 ¡Configuración completa! TECLA está listo para usar.")
    return True
