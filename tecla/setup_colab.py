"""
Full plug-and-play setup utility for TECLA in Google Colab.

Automatically:
- Adds TECLA to sys.path
- Installs required Python packages
- Downloads spaCy models
- Downloads NLTK stopwords and punkt
- Cleans cached modules
- Confirms TECLA importability
"""

import sys
import os
import importlib
import subprocess


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
    """Install all core dependencies for TECLA."""
    deps = [
        "pdfminer.six",
        "spacy",
        "nltk",
        "langid",
    ]
    print("📌 Installing dependencies...")
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
    print("📌 Ensuring spaCy models...")
    import spacy
    import spacy.cli

    for lang, model in SPACY_MODELS.items():
        try:
            spacy.load(model)
            print(f"   🔄 Model already present: {model}")
        except OSError:
            print(f"   ⬇️ Downloading model: {model}")
            try:
                spacy.cli.download(model)
                print(f"   ✓ Installed: {model}")
            except Exception as e:
                print(f"   ⚠️ Could not download {model}. Using blank fallback.")


# ---------------------------------------------------------------------
# NLTK resources installer
# ---------------------------------------------------------------------

def _download_nltk_resources():
    """Install stopwords + punkt for NLTK automatically."""
    print("📌 Ensuring NLTK resources...")
    try:
        import nltk
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        print("   ✓ NLTK resources installed")
    except Exception as e:
        print(f"   ⚠️ Could not download NLTK data: {e}")
        print("   → TECLA will use only spaCy stopwords.")


# ---------------------------------------------------------------------
# MAIN SETUP
# ---------------------------------------------------------------------

def setup_tecla(path="/content/TECLA_v2"):
    """
    Run full TECLA setup automatically in Google Colab.
    """

    print("🚀 Setting up TECLA...")

    if not os.path.isdir(path):
        raise ValueError(f"Directory not found: {path}")

    # Add repo to path
    if path not in sys.path:
        sys.path.append(path)
        print(f"📂 Added TECLA path: {path}")

    # Install deps & resources
    _install_dependencies()
    _ensure_spacy_models()
    _download_nltk_resources()

    # Clear cached modules
    removed = [m for m in sys.modules if m.startswith("tecla")]
    for m in removed:
        del sys.modules[m]
    print(f"🧹 Cleared {len(removed)} cached modules")

    # Validate import
    try:
        importlib.import_module("tecla")
        print("✅ TECLA successfully imported!")
    except Exception as e:
        raise ImportError(f"❌ TECLA could not be imported: {e}")

    print("🎉 TECLA setup completed — ready to use!")
    return True
