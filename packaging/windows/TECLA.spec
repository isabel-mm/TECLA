# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import importlib.util

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    copy_metadata,
)


PROJECT_ROOT = Path.cwd()

datas = []
binaries = []
hiddenimports = []

for package in ("tecla", "pipeline", "customtkinter", "langid", "spacy"):
    datas += collect_data_files(package)

datas += [(str(PROJECT_ROOT / "gui" / "assets"), "gui/assets")]

for package in ("spacy", "numpy"):
    binaries += collect_dynamic_libs(package)

# Include models that are installed in the build environment. Without them,
# TECLA can still use its blank spaCy fallback (with lower linguistic quality).
for model_name in ("es_core_news_md", "en_core_web_lg"):
    if importlib.util.find_spec(model_name):
        datas += collect_data_files(model_name)
        binaries += collect_dynamic_libs(model_name)
        hiddenimports.append(model_name)

for package_name in (
    "spacy", "thinc", "srsly", "catalogue", "preshed", "cymem",
    "murmurhash", "blis", "numpy", "pandas", "matplotlib", "langid",
    "customtkinter",
):
    try:
        datas += copy_metadata(package_name)
    except Exception:
        pass

hiddenimports += [
    "PIL.Image",
    "PIL.ImageTk",
    "matplotlib.backends.backend_agg",
    "matplotlib.backends.backend_tkagg",
]

a = Analysis(
    [str(PROJECT_ROOT / "gui" / "tecla_gui.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=sorted(set(hiddenimports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "IPython", "jupyter_client", "jupyter_core", "pytest", "sphinx",
        "torch", "tensorflow", "sklearn", "scipy", "numba", "pyarrow",
        "openpyxl",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TECLA",
    icon=str(PROJECT_ROOT / "gui" / "assets" / "tecla.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
