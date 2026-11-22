# Subtítulos y overlays: ruta Remotion (default) y ruta ligera ASS

## Ruta A — Remotion (default en este Mac, da más efectos)

Renderiza el texto con Chromium (no necesita libass). Más control de animación,
cualquier fuente, degradados, springs.

### Esquema de `edit.json`
```json
{
  "video": "base.mp4",
  "fps": 30,
  "durationS": 42.5,
  "paleta": { "texto": "#FFFFFF", "primario": "#FFD54A", "acento": "#4ADE80" },
  "titulo": "LO QUE NADIE TE DICE DEL VOTO",
  "tituloDur": 2.5,
  "keywords": ["democracia", "voto", "participar"],
  "banda": "baja",
  "progreso": true,
  "words": [ { "text": "Hola", "startS": 0.12, "endS": 0.40 } ],
  "overlays": [
    { "tipo": "img",   "valor": "dato.png", "inicioS": 5, "finS": 9, "pos": "centro",  "escala": 0.7, "fade": 0.3 },
    { "tipo": "emoji", "valor": "🔥",        "inicioS": 2, "finS": 4, "pos": "sup-der", "escala": 1.2 },
    { "tipo": "img",   "valor": "logo.png", "inicioS": 0, "finS": 99, "pos": "sup-izq", "escala": 0.16 }
  ]
}
```
- `words`: lo escupe `construir_edit_json.py` desde la transcripción del clip.
- `keywords`: se pintan con `acento`. La palabra que se dice ahora usa `primario`.
- `banda`: `baja` (tercio inferior) o `centro`.
- `pos`: `centro | sup | inf | sup-izq | sup-der | inf-izq | inf-der`.
- `escala` en `img` = fracción del ancho (0.7 = 70% de 1080). En `emoji` = múltiplo.
- Las imágenes de `overlays` deben copiarse a `public/` (lo hace `preparar_remotion.sh`
  si le pasas la carpeta `overlays/`).

### Generar y renderizar
```
python3 scripts/construir_edit_json.py transcripcion/r01_clip.json -o clips/r01_edit.json \
   --video-path clips/r01_base.mp4 --titulo "TÍTULO" --keywords "voto,democracia" \
   --primario FFD54A --acento 4ADE80 --overlays clips/r01_overlays.json
scripts/preparar_remotion.sh clips/r01_remotion clips/r01_base.mp4 clips/r01_edit.json overlays/
```
Previsualizar/ajustar en vivo: `cd clips/r01_remotion && npm run preview`.

### Tocar el estilo
Edita `assets/remotion-overlay/src/`:
- `Captions.tsx` — tamaño, agrupación (palabras/línea), colores, rebote.
- `ReelEdit.tsx` — estilo del título, barra de progreso.
- `Overlays.tsx` — posiciones y animación de los elementos.
- `palette.ts` — colores por defecto.
Para usar una fuente de marca, pon el `.ttf` y cárgala con `@remotion/fonts` o un
`@font-face` en un CSS importado (ver docs de Remotion).

## Ruta B — ASS por FFmpeg (ligera, SOLO si tu ffmpeg tiene libass)
Corre `scripts/preflight.sh`; si muestra el filtro `ass` disponible, puedes usar:
```
python3 scripts/construir_subtitulos.py transcripcion/r01_clip.json -o subtitulos/r01.ass \
   --keywords "voto,democracia" --titulo "TÍTULO" --fuente "Montserrat" --tam 92
scripts/quemar_subtitulos.sh clips/r01_base.mp4 subtitulos/r01.ass export/r01_reel_final.mp4
```
`construir_subtitulos.py` ya hace palabra-activa resaltada + keywords + título.
Para una fuente no instalada, pásale la carpeta de fuentes como 4º argumento a
`quemar_subtitulos.sh`.

### Habilitar libass (opcional)
La fórmula de ffmpeg instalada no incluye libass. Para la ruta ligera se
necesita un ffmpeg compilado con `--enable-libass --enable-libfreetype`
(p. ej. otra fórmula/tap de Homebrew, o una build estática de evermeet.cx).
No es necesario si usas Remotion.

## Overlays sin texto por FFmpeg (alternativa a Remotion para imágenes/b-roll)
`scripts/overlay_elementos.py` superpone PNG/imágenes en tiempos dados **sin
necesitar libass** (usa el filtro `overlay`). Útil si solo quieres pegar un
gráfico o logo y no subtítulos. Ver `ffmpeg-recetas.md` para b-roll en video.
