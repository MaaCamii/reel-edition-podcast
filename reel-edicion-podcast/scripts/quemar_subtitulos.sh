#!/usr/bin/env bash
# quemar_subtitulos.sh — Incrusta (quema) un .ass sobre el clip vertical.
#
# Uso: ./quemar_subtitulos.sh <clip.mp4> <subs.ass> <salida.mp4> [dir_de_fuentes]
#   dir_de_fuentes: opcional, carpeta con .ttf/.otf si usas una fuente de marca
#                   que no está instalada en el sistema.
set -euo pipefail

IN="${1:?clip}"; ASS="${2:?subs.ass}"; OUT="${3:?salida}"; FONTS="${4:-}"
mkdir -p "$(dirname "$OUT")"

if [ -n "$FONTS" ]; then
  VF="ass=filename=${ASS}:fontsdir=${FONTS}"
else
  VF="ass=filename=${ASS}"
fi

ffmpeg -y -i "$IN" -vf "$VF" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart "$OUT"

echo "OK subtítulos quemados -> $OUT"
