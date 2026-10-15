#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export MPLCONFIGDIR="${ROOT_DIR}/.tmp/matplotlib"
mkdir -p "$MPLCONFIGDIR"

# NLTK stopword lists: bundled into the app
python3 -c "import nltk; nltk.download('stopwords', quiet=True)"

python3 -m PyInstaller \
  --noconfirm \
  --clean \
  packaging/macos/TECLA.spec

# Disk image for distribution: the app next to a shortcut to Applications
# No version in the name: the website links to releases/latest/download/
DMG_PATH="dist/TECLA-instalador-macos-$(uname -m).dmg"
STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT

ditto dist/TECLA.app "$STAGING_DIR/TECLA.app"
ln -s /Applications "$STAGING_DIR/Applications"

hdiutil create \
  -volname "TECLA" \
  -srcfolder "$STAGING_DIR" \
  -format UDZO \
  -ov \
  "$DMG_PATH"

echo
echo "App generated at:"
echo "  ${ROOT_DIR}/dist/TECLA.app"
echo "Disk image generated at:"
echo "  ${ROOT_DIR}/${DMG_PATH}"
