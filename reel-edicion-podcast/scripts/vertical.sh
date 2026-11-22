#!/usr/bin/env bash
# vertical.sh — Reencuadra un clip a 1080x1920 (9:16) para reel.
#
# Uso: ./vertical.sh <entrada.mp4> <salida.mp4> [modo] [foco]
#   modo:
#     blur   (por defecto) -> video completo centrado sobre fondo borroso. No recorta.
#     crop                 -> recorte central 9:16 (llena pantalla, pierde los bordes).
#     crop_left / crop_right -> recorte 9:16 desplazado (útil si el hablante no está centrado).
#   foco: solo para crop desplazado, 0.0 (izq) .. 1.0 (der). Default 0.5.
set -euo pipefail

IN="${1:?entrada}"; OUT="${2:?salida}"; MODE="${3:-blur}"; FOCUS="${4:-0.5}"
mkdir -p "$(dirname "$OUT")"
W=1080; H=1920

case "$MODE" in
  blur)
    VF="[0:v]split=2[bg][fg];\
[bg]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},gblur=sigma=24,eq=brightness=-0.06[bgb];\
[fg]scale=${W}:-2:flags=lanczos[fgs];\
[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]"
    ;;
  crop)
    VF="[0:v]crop=ih*9/16:ih,scale=${W}:${H}:flags=lanczos,setsar=1,format=yuv420p[v]"
    ;;
  crop_left|crop_right|crop_focus)
    # x del recorte = (ancho_sobrante) * foco
    VF="[0:v]crop=w=ih*9/16:h=ih:x='(iw-ih*9/16)*${FOCUS}':y=0,scale=${W}:${H}:flags=lanczos,setsar=1,format=yuv420p[v]"
    ;;
  *) echo "Modo desconocido: $MODE (usa blur|crop|crop_focus)" >&2; exit 1;;
esac

ffmpeg -y -i "$IN" -filter_complex "$VF" -map "[v]" -map 0:a:0? \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"

echo "OK ($MODE) -> $OUT (1080x1920)"
