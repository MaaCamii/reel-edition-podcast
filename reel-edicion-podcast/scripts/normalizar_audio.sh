#!/usr/bin/env bash
# normalizar_audio.sh — Normaliza loudness a -14 LUFS (estándar para redes) y
# limpia un poco el audio hablado. Deja el video intacto (-c:v copy).
#
# Uso: ./normalizar_audio.sh <entrada.mp4> <salida.mp4>
set -euo pipefail

IN="${1:?entrada}"; OUT="${2:?salida}"
mkdir -p "$(dirname "$OUT")"

# highpass quita retumbe; loudnorm estandariza volumen percibido.
ffmpeg -y -i "$IN" \
  -c:v copy \
  -af "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"

echo "OK -> $OUT (loudness -14 LUFS)"
