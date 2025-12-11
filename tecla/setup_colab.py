"""
Utility to auto-configure TECLA inside Google Colab.

- Adds TECLA root directory to sys.path
- Forces module reload to avoid Colab caching issues
- Makes TECLA importable immediately after git clone
"""

import sys
import os
import importlib

def setup_tecla(path="/content/TECLA_v2"):
    # Ensure path exists
    if not os.path.isdir(path):
        raise ValueError(f"Directory not found: {path}")

    # Add to sys.path if missing
    if path not in sys.path:
        sys.path.append(path)

    # Clear previous cached imports (Colab caches aggressively)
    for module in list(sys.modules.keys()):
        if module.startswith("tecla"):
            del sys.modules[module]

    # Try import to confirm everything is correct
    try:
        importlib.import_module("tecla")
    except Exception as e:
        raise ImportError(f"TECLA could not be imported after setup: {e}")

    return True
