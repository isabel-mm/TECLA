#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export MPLCONFIGDIR="${ROOT_DIR}/.tmp/matplotlib"
mkdir -p "$MPLCONFIGDIR"

python3 -m PyInstaller \
  --noconfirm \
  --clean \
  packaging/macos/TECLA.spec

echo
echo "App generated at:"
echo "  ${ROOT_DIR}/dist/TECLA.app"
