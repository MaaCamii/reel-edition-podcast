#!/usr/bin/env bash
# nuevo_proyecto.sh — Crea la carpeta de trabajo de un lote de reels.
#
# Uso: ./nuevo_proyecto.sh <nombre-proyecto> [directorio-base]
# Crea:  <base>/<nombre>/{origen,transcripcion,clips,subtitulos,overlays,export,reel.json}
set -euo pipefail

NAME="${1:?Uso: nuevo_proyecto.sh <nombre> [base]}"
BASE="${2:-$PWD}"
DIR="$BASE/$NAME"

mkdir -p "$DIR"/{origen,transcripcion,clips,subtitulos,overlays,export}

cat > "$DIR/reel.json" <<'JSON'
{
  "fuente": "origen/NOMBRE_DEL_VIDEO.mp4",
  "plataforma": "instagram_reels",
  "voz_marca": "agora",
  "reels": [
    {
      "id": "r01",
      "titulo": "Título corto y claro del reel",
      "gancho": "Primera frase que detiene el scroll",
      "inicio": "00:12:40.000",
      "fin": "00:13:28.500",
      "por_que_funciona": "Idea autocontenida + tensión/revelación",
      "reencuadre": "blur",
      "quitar_silencios": true,
      "keywords": ["palabra", "clave", "a", "resaltar"],
      "title_cards": [
        { "t": "0.0", "dur": "2.5", "texto": "TÍTULO EN PANTALLA" }
      ],
      "overlays": [
        { "inicio": "4.0", "fin": "7.0", "archivo": "overlays/grafico.png", "pos": "centro", "escala": "0.6" }
      ],
      "copy": {
        "caption": "",
        "hashtags": []
      }
    }
  ]
}
JSON

echo "Proyecto creado en: $DIR"
echo "1) Copia tu video a:  $DIR/origen/"
echo "2) Edita:             $DIR/reel.json"
find "$DIR" -maxdepth 1 -mindepth 1 | sort
