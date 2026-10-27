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

datas += collect_data_files("tecla")
datas += collect_data_files("pipeline")
datas += collect_data_files("customtkinter")
datas += collect_data_files("langid")
datas += collect_data_files("spacy")

datas += [(str(PROJECT_ROOT / "gui" / "assets"), "gui/assets")]

binaries += collect_dynamic_libs("spacy")
binaries += collect_dynamic_libs("numpy")

for model_name in ("es_core_news_md", "en_core_web_lg"):
    if importlib.util.find_spec(model_name):
        datas += collect_data_files(model_name)
        binaries += collect_dynamic_libs(model_name)
        # spacy.load() looks the model up through its package metadata
        datas += copy_metadata(model_name)
        hiddenimports.append(model_name)

for package_name in (
    "spacy",
    "thinc",
    "srsly",
    "catalogue",
    "preshed",
    "cymem",
    "murmurhash",
    "blis",
    "numpy",
    "pandas",
    "matplotlib",
    "langid",
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
        "IPython",
        "jupyter_client",
        "jupyter_core",
        "pytest",
        "sphinx",
        "torch",
        "tensorflow",
        "sklearn",
        "scipy",
        "numba",
        "pyarrow",
        "openpyxl",
    ],
    noarchive=False,
    optimize=0,
)

# The nltk hook bundles every NLTK resource found on the build machine.
# TECLA only needs the stopword lists.
a.datas = [
    entry for entry in a.datas
    if not entry[0].startswith("nltk_data/")
    or entry[0].startswith("nltk_data/corpora/stopwords")
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TECLA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TECLA",
)

app = BUNDLE(
    coll,
    name="TECLA.app",
    icon=str(PROJECT_ROOT / "gui" / "assets" / "tecla.icns"),
    bundle_identifier="com.tecla.app",
    version="2.1.1",
    info_plist={"NSHighResolutionCapable": True},
)
