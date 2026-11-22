#!/usr/bin/env bash
# preparar_remotion.sh — Monta la capa de pulido Remotion para un clip y la
# renderiza. Copia la plantilla, coloca el clip base + edit.json en public/,
# instala dependencias (una sola vez) y renderiza el MP4 final.
#
# Uso:
#   ./preparar_remotion.sh <dir_remotion> <clip_base.mp4> <edit.json> [dir_overlays]
#
#   dir_remotion : carpeta destino (se crea). Ej: proyecto/r01/remotion
#   clip_base    : clip 1080x1920 ya cortado/reencuadrado/normalizado
#   edit.json    : generado con construir_edit_json.py (video debe ser "base.mp4")
#   dir_overlays : opcional, carpeta con PNG/imágenes referenciadas en overlays
#
# Requiere Node + npm. La primera vez instala node_modules (puede tardar).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$HERE/../assets/remotion-overlay"

DEST="${1:?dir_remotion}"; CLIP="${2:?clip_base.mp4}"; EDIT="${3:?edit.json}"; OVDIR="${4:-}"
[ -f "$CLIP" ] || { echo "No existe el clip: $CLIP" >&2; exit 1; }
[ -f "$EDIT" ] || { echo "No existe edit.json: $EDIT" >&2; exit 1; }
command -v npm >/dev/null || { echo "Falta npm (instala Node)." >&2; exit 1; }

mkdir -p "$DEST"
# Copia la plantilla (sin node_modules/out) si el destino aún no la tiene.
if [ ! -f "$DEST/package.json" ]; then
  echo "Copiando plantilla Remotion..."
  rsync -a --exclude node_modules --exclude out "$TEMPLATE"/ "$DEST"/
fi
mkdir -p "$DEST/public"
cp "$CLIP" "$DEST/public/base.mp4"
cp "$EDIT" "$DEST/public/edit.json"
if [ -n "$OVDIR" ] && [ -d "$OVDIR" ]; then
  cp -R "$OVDIR"/. "$DEST/public/" 2>/dev/null || true
fi

cd "$DEST"
if [ ! -d node_modules ]; then
  echo "Instalando dependencias (una sola vez)..."
  npm install --silent
fi

echo "Renderizando..."
npm run render --silent
echo "OK -> $DEST/out/reel_final.mp4"
