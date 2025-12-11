"""
Full plug-and-play setup utility for TECLA in Google Colab.

Features:
- User selects which languages to install (spaCy models)
- Dependencies auto-installed
- NLTK stopwords auto-downloaded
- Cleans cached modules
- TECLA becomes importable immediately
"""

import sys
import os
import importlib
import subprocess


# ---------------------------------------------------------------------
# spaCy model table
# ---------------------------------------------------------------------

SPACY_MODELS = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}


# ---------------------------------------------------------------------
# Helper: pip installer
# ---------------------------------------------------------------------

def _pip_install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"📦 Installed: {package}")
    except Exception as e:
        print(f"⚠️ Could not install {package}: {e}")


def _install_dependencies():
    """Install core TECLA dependencies."""
    deps = ["pdfminer.six", "spacy", "nltk", "langid"]
    print("📌 Installing dependencies...")
    for pkg in deps:
        _pip_install(pkg)


# ---------------------------------------------------------------------
# spaCy model installer (only selected languages)
# ---------------------------------------------------------------------

def _ensure_spacy_models(languages):
    import spacy
    import spacy.cli

    print("📌 Ensuring spaCy models for:", languages)

    for lang in languages:
        if lang not in SPACY_MODELS:
            print(f"⚠️ Language '{lang}' not supported. Skipping.")
            continue

        model = SPACY_MODELS[lang]

        try:
            spacy.load(model)
            print(f"   🔄 Model already installed: {model}")
        except OSError:
            print(f"   ⬇️ Downloading: {model}")
            try:
                spacy.cli.download(model)
                print(f"   ✓ Installed: {model}")
            except Exception as e:
                print(f"   ⚠️ Could not download {model}: {e}")
                print(f"   → Will fallback to blank model at runtime.")


# ---------------------------------------------------------------------
# NLTK stopwords installer
# ---------------------------------------------------------------------

def _download_nltk_resources():
    import nltk

    print("📌 Ensuring NLTK resources...")

    try:
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        print("   ✓ NLTK resources installed")
    except Exception as e:
        print(f"   ⚠️ Could not install NLTK resources: {e}")


# ---------------------------------------------------------------------
# MAIN SETUP FUNCTION
# ---------------------------------------------------------------------

def setup_tecla(path="/content/TECLA_v2", languages=["es", "en"]):
    """
    Run full TECLA setup in Google Colab.

    Parameters:
    - path (str): Path to TECLA repo
    - languages (list or "all"): spaCy languages to install
    """

    print("🚀 Setting up TECLA...")

    # Validate languages
    if languages == "all":
        languages = list(SPACY_MODELS.keys())
    elif isinstance(languages, str):
        languages = [languages]

    # Ensure valid list
    if not isinstance(languages, list):
        raise ValueError("languages must be a list like ['es','en'] or 'all'.")

    # Add TECLA to path
    if not os.path.isdir(path):
        raise ValueError(f"Directory not found: {path}")

    if path not in sys.path:
        sys.path.append(path)
        print(f"📂 Added TECLA path: {path}")

    # Install Python packages
    _install_dependencies()

    # Install spaCy models only for selected languages
    _ensure_spacy_models(languages)

    # NLTK resources
    _download_nltk_resources()

    # Clear cached modules (important in Colab)
    removed = [m for m in sys.modules if m.startswith("tecla")]
    for m in removed:
        del sys.modules[m]
    print(f"🧹 Cleared {len(removed)} cached TECLA modules")

    # Validate import
    try:
        importlib.import_module("tecla")
        print("✅ TECLA successfully imported!")
    except Exception as e:
        raise ImportError(f"❌ TECLA could not be imported: {e}")

    print("🎉 TECLA setup completed — ready to use!")
    return True
