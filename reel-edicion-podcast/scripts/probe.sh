#!/usr/bin/env bash
# probe.sh — Inspecciona un archivo de video/audio y reporta lo que importa
# para decidir el corte y el reencuadre.
#
# Uso: ./probe.sh <archivo>
set -euo pipefail

IN="${1:?Uso: probe.sh <archivo de video o audio>}"
[ -f "$IN" ] || { echo "No existe el archivo: $IN" >&2; exit 1; }

echo "== $IN =="
ffprobe -v error -show_entries format=duration,size,bit_rate \
  -of default=noprint_wrappers=1 "$IN"

echo "-- video --"
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate \
  -of default=noprint_wrappers=1 "$IN" 2>/dev/null || echo "(sin pista de video)"

echo "-- audio --"
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,channels,sample_rate \
  -of default=noprint_wrappers=1 "$IN" 2>/dev/null || echo "(sin pista de audio)"

# Relación de aspecto / orientación
read -r W H < <(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=p=0:s=' ' "$IN" 2>/dev/null || echo "0 0")
if [ "${W:-0}" -gt 0 ] && [ "${H:-0}" -gt 0 ]; then
  if [ "$W" -gt "$H" ]; then ORIENT="horizontal (16:9 aprox) -> hay que reencuadrar a 9:16";
  elif [ "$H" -gt "$W" ]; then ORIENT="vertical -> quizá ya sirve 9:16";
  else ORIENT="cuadrado"; fi
  echo "-- orientación: ${W}x${H} -> $ORIENT"
fi
