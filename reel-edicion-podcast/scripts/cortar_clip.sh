#!/usr/bin/env bash
# cortar_clip.sh — Extrae un segmento [inicio, fin] del video fuente con corte
# preciso al frame (re-encodea). Mantiene la resolución original; el reencuadre
# a 9:16 lo hace vertical.sh en el siguiente paso.
#
# Uso: ./cortar_clip.sh <fuente> <inicio> <fin> <salida.mp4>
#   inicio/fin en HH:MM:SS.mmm o en segundos (ej. 00:12:40.000  o  760.0)
set -euo pipefail

IN="${1:?fuente}"; START="${2:?inicio}"; END="${3:?fin}"; OUT="${4:?salida.mp4}"
mkdir -p "$(dirname "$OUT")"

# -ss/-to DESPUÉS de -i = corte preciso al frame (más lento pero exacto).
ffmpeg -y -i "$IN" -ss "$START" -to "$END" \
  -map 0:v:0 -map 0:a:0? \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$OUT"

echo "OK -> $OUT"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT" \
  | awk '{printf "duración: %.2fs\n", $1}'
