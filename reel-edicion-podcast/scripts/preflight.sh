#!/usr/bin/env bash
# preflight.sh — Verifica qué herramientas hay y qué ruta de subtítulos usar.
set -uo pipefail
ok(){ printf "  \033[32m✓\033[0m %s\n" "$1"; }
no(){ printf "  \033[31m✗\033[0m %s\n" "$1"; }

echo "== Dependencias =="
command -v ffmpeg  >/dev/null && ok "ffmpeg: $(ffmpeg -version | head -1 | awk '{print $3}')" || no "ffmpeg (brew install ffmpeg)"
command -v ffprobe >/dev/null && ok "ffprobe" || no "ffprobe"
command -v node    >/dev/null && ok "node: $(node --version)" || no "node (brew install node)"
command -v npm     >/dev/null && ok "npm" || no "npm"
command -v python3 >/dev/null && ok "python3: $(python3 --version 2>&1 | awk '{print $2}')" || no "python3"

echo "== Capacidad de texto en ffmpeg =="
FILT="$(ffmpeg -hide_banner -filters 2>/dev/null)"
HAS_ASS=0
echo "$FILT" | grep -qiE '\bass\b'       && { ok "filtro 'ass' (libass) disponible"; HAS_ASS=1; } || no "filtro 'ass' (libass) NO disponible"
echo "$FILT" | grep -qiE '\bdrawtext\b'  && ok "filtro 'drawtext'" || no "filtro 'drawtext' NO disponible"

echo "== Ruta de subtítulos recomendada =="
if [ "$HAS_ASS" = "1" ]; then
  echo "  -> Puedes usar la ruta LIGERA (ASS): construir_subtitulos.py + quemar_subtitulos.sh"
  echo "  -> La ruta Remotion (más efectos) también funciona."
else
  echo "  -> Tu ffmpeg NO quema texto. Usa la ruta REMOTION para subtítulos/títulos:"
  echo "     construir_edit_json.py + preparar_remotion.sh"
  echo "  -> (Opcional) Para habilitar la ruta ligera ASS, instala un ffmpeg con libass."
fi
