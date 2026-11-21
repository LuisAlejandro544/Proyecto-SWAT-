#!/usr/bin/env bash
# export-godot.sh
# Compila e importa el proyecto Godot 4.7.2-stable en modo headless y genera los archivos WebAssembly en public/godot/.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT_BIN="$ROOT_DIR/tools/godot/Godot_v4.7.2-stable_linux.x86_64"
PROJECT_DIR="$ROOT_DIR/godot-project"
OUTPUT_DIR="$ROOT_DIR/public/godot"

if [ ! -x "$GODOT_BIN" ]; then
  echo "Error: No se encontró el binario de Godot en $GODOT_BIN" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Primer paso: importar recursos en modo headless para generar .godot/ correctamente.
"$GODOT_BIN" --headless --path "$PROJECT_DIR" --import --quit || true

# Segundo paso: exportar el preset "Web" en modo release hacia public/godot/index.html.
"$GODOT_BIN" --headless --path "$PROJECT_DIR" --export-release "Web" "$OUTPUT_DIR/index.html"

echo "Exportación Web de Godot completada en $OUTPUT_DIR"
