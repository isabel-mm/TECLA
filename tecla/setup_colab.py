"""
Utility to auto-configure TECLA inside Google Colab.

This script:
- Ensures TECLA is importable by adding the repo path to sys.path
- Clears Colab's aggressive module caching for the "tecla" namespace
- Installs Python dependencies (spacy, nltk, pdfminer, etc.)
- Downloads necessary spaCy models automatically
- Downloads NLTK resources (stopwords, punkt)
- Confirms TECLA loads successfully

This gives TECLA true plug-and-play behaviour in Google Colab.
"""

import sys
import os
import importlib
import subprocess


# ---------------------------------------------------------------------
# Dependency installer
# ---------------------------------------------------------------------

def _pip_install(package):
    """Install a package via pip inside Colab."""
    try:
        print(f"📦 Installing: {package} …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"⚠️ Could not install {package}: {e}")


def _install_dependencies():
    """Install core libraries needed by TECLA."""
    deps = [
        "pdfminer.six",
        "spacy",
        "nltk",
        "langid",
    ]
    for pkg in deps:
        _pip_install(pkg)


# ---------------------------------------------------------------------
# spaCy model installer
# ---------------------------------------------------------------------

SPACY_MODELS = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}

def _ensure_spacy_models():
    """Download spaCy models if missing."""
    import spacy
    import spacy.cli

    for lang, model in SPACY_MODELS.items():
        try:
            spacy.load(model)
            print(f"🔄 spaCy model already present: {model}")
        except Exception:
            print(f"⬇️ Downloading spaCy model: {model}")
            try:
                spacy.cli.download(model)
                print(f"   ✓ {model} installed")
            except Exception as e:
                print(f"   ⚠️ Failed to download {model}: {e}")


# ---------------------------------------------------------------------
# NLTK resource installer
# ---------------------------------------------------------------------

def _download_nltk_resources():
    """Download NLTK stopwords and punkt."""
    try:
        import nltk
        print("⬇️ Downloading NLTK stopwords & punkt...")
        nltk.download("stopwords")
        nltk.download("punkt")
        print("   ✓ NLTK resources installed")
    except Exception as e:
        print(f"⚠️ Could not download NLTK resources: {e}")


# ---------------------------------------------------------------------
# Main TECLA setup
# ---------------------------------------------------------------------

def setup_tecla(path="/content/TECLA_v2"):
    """
    Configure TECLA after git clone in Colab.

    Steps:
    1. Add TECLA to sys.path
    2. Install dependencies
    3. Download spaCy + NLTK resources
    4. Clear Colab cached modules
    5. Import TECLA to confirm installation

    Returns:
        True if setup completed successfully.
    """
    print("🚀 Setting up TECLA in Google Colab...")

    # 1. Ensure folder exists
    if not os.path.isdir(path):
        raise ValueError(f"Directory not found: {path}")

    # 2. Add to sys.path
    if path not in sys.path:
        sys.path.append(path)
        print(f"📌 Added TECLA path: {path}")

    # 3. Install required packages
    _install_dependencies()

    # 4. Download spaCy models
    _ensure_spacy_models()

    # 5. Download NLTK data
    _download_nltk_resources()

    # 6. Clear cached "tecla" modules
    removed = [
        m for m in list(sys.modules.keys())
        if m.startswith("tecla")
    ]
    for m in removed:
        del sys.modules[m]
    print(f"🧹 Cleared {len(removed)} cached TECLA modules")

    # 7. Validate import works
    try:
        importlib.import_module("tecla")
        print("✅ TECLA imported successfully!")
    except Exception as e:
        raise ImportError(f"❌ TECLA could not be imported: {e}")

    print("🎉 TECLA setup completed")
    return True
