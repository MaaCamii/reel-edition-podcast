---
name: reel-edicion-podcast
description: >
  Edita video profesional en formato reel/short vertical a partir de material
  AUDIOVISUAL GRABADO POR UNA PERSONA (podcast, entrevista, charla, cámara,
  clase) — NO contenido generado con IA. La IA se usa para EDITAR: transcribe el
  material largo, detecta los mejores momentos autocontenidos, los corta, los
  reencuadra a 9:16, limpia el audio, quita silencios (jump-cuts), y añade una
  capa de pulido profesional con subtítulos interactivos (palabra activa estilo
  TikTok/Reels), títulos resaltados, keywords con color de acento y elementos
  complementarios en pantalla (imágenes, emojis, b-roll, barra de progreso).
  Trabaja 100% con código (FFmpeg + Remotion), sin depender de CapCut ni de APIs
  externas de edición. Úsalo SIEMPRE que el usuario quiera "sacar clips/reels de
  un podcast o video", "editar este episodio para redes", "convertir esta
  grabación en shorts", "hacer un reel con subtítulos de esta entrevista",
  "cortar los mejores momentos", "reencuadrar a vertical", o "editar video
  profesional para Instagram/TikTok/YouTube Shorts" a partir de un archivo que
  ellos aportan. Actívate aunque no diga "skill", "FFmpeg" ni "Remotion".
  NO uses esta skill cuando el video se genera desde cero con IA a partir de un
  guión (para eso está reel-educativo-ia): esta parte de grabación humana real.
---

# Reel Edición Podcast — de la grabación larga al reel con pulido profesional

Esta skill **edita contenido grabado por una persona** (podcast, entrevista,
charla) y extrae **reels verticales 1080×1920 listos para publicar**, con corte,
reencuadre 9:16, audio limpio y una capa de pulido (subtítulos interactivos,
títulos, overlays). Todo con **código reproducible**: FFmpeg para el video y
Remotion para el texto/animaciones. **No usa CapCut** ni APIs de terceros.

> Hermana de `reel-educativo-ia`: aquella **genera** el video con IA desde un
> guión; **esta edita** material real ya grabado. Si el usuario aporta un
> archivo de video/audio para sacar clips, es esta.

## Restricción de entorno (leer una vez)

El FFmpeg de este Mac **no trae `libass`/`drawtext`**, así que **no puede quemar
texto**. Por eso los subtítulos y títulos se renderizan con **Remotion** (motor
propio, independiente de libass) — que además da mejores efectos. Corre primero:

```
scripts/preflight.sh
```

- Si dice que `ass` **NO** está disponible → usa la **ruta Remotion** (por
  defecto en esta skill).
- Si algún día instalas un ffmpeg con libass → también existe una **ruta ligera
  ASS** (ver `references/subtitulos-y-overlays.md`), más rápida pero con menos
  efectos.

## Lo que produce

Por cada reel aprobado: un `reel_final.mp4` vertical (1080×1920, ~15–60 s) con
hasta cinco capas sobre la grabación original:
1. **Video reencuadrado** 9:16 (fondo borroso o recorte con foco en el hablante).
2. **Audio normalizado** a −14 LUFS y sin pausas muertas (jump-cuts opcionales).
3. **Subtítulos interactivos** — pocas palabras a la vez, palabra activa resaltada.
4. **Título + keywords** resaltadas con color de acento.
5. **Elementos complementarios** — imágenes/datos, emojis, b-roll, barra de progreso.

Y, para publicar: **copy + hashtags** (apóyate en la skill `agora-social-content`).

## Flujo de trabajo (sigue estos pasos)

### 0. Intake
Pide/confirma: el **archivo fuente**, la **plataforma** (Reels/TikTok/Shorts),
**cuántos reels** quieres y el **tema/ángulo**. Luego inspecciona el archivo:
```
scripts/probe.sh <fuente>
```
Crea la carpeta de trabajo:
```
scripts/nuevo_proyecto.sh <nombre> [carpeta_base]
```
Copia el video a `origen/` y trabaja sobre `reel.json`.

### 1. Transcribir el material completo
Transcribe la fuente para poder leerla y ubicar momentos. Dos opciones:
- **MCP de ElevenLabs** (`creative_transcribe_audio`) — sin instalar nada.
- O cualquier transcriptor que dé **tiempos por palabra**.

Normaliza el resultado a `{ "words": [ {"text","start","end"}, ... ] }` y
guárdalo en `transcripcion/`. (El loader también acepta formato Whisper
`segments[].words`.) Ver `references/transcripcion.md`.

### 2. Elegir los mejores momentos (aquí decide la IA)
Lee la transcripción y propón **N reels candidatos**. Para cada uno: `inicio`,
`fin`, **gancho** (primera frase), **título**, por qué funciona, **keywords** a
resaltar y sugerencias de overlays. Criterios en
`references/seleccion-momentos.md`. **Presenta la lista y espera aprobación**
antes de renderizar — no gastes render en cortes no validados. Escribe lo
aprobado en `reel.json`.

### 3. Cortar + reencuadrar + limpiar (FFmpeg — funciona ya)
Por cada reel:
```
scripts/cortar_clip.sh    origen/<fuente> <inicio> <fin> clips/r01_corte.mp4
scripts/vertical.sh       clips/r01_corte.mp4 clips/r01_vert.mp4 blur
scripts/normalizar_audio.sh clips/r01_vert.mp4 clips/r01_base.mp4
# Opcional, estilo ágil:
scripts/detectar_silencios.py clips/r01_base.mp4 --render clips/r01_base.mp4
```
`vertical.sh` tiene modos `blur` (no recorta), `crop` (recorte central) y
`crop_focus` con foco 0..1 si el hablante no está centrado.

### 4. Pulido profesional (Remotion — subtítulos/títulos/overlays)
**Transcribe el CLIP ya cortado** (no la fuente) para tener tiempos relativos a
0, normalízalo a `{"words":[...]}`, y genera `edit.json`:
```
scripts/construir_edit_json.py transcripcion/r01_clip.json -o clips/r01_edit.json \
  --video-path clips/r01_base.mp4 --titulo "TÍTULO" --keywords "palabra1,palabra2"
```
Coloca las imágenes de overlay en una carpeta (`overlays/`) y referéncialas en
`edit.json` → `overlays`. Luego monta y renderiza:
```
scripts/preparar_remotion.sh clips/r01_remotion clips/r01_base.mp4 clips/r01_edit.json overlays/
```
Sale `clips/r01_remotion/out/reel_final.mp4`. La **primera vez** instala
dependencias y descarga el render de Chromium (tarda unos minutos); después es
rápido. Para previsualizar y ajustar en vivo: `cd` a esa carpeta y `npm run preview`.

### 5. Entregar
Copia los `reel_final.mp4` a `export/`, muéstraselos al usuario y acompáñalos de
**copy + hashtags** por plataforma (usa `agora-social-content`). Verifica el
checklist de QC en `references/flujo.md`.

## Mapa de scripts
| Script | Hace |
|---|---|
| `preflight.sh` | Verifica ffmpeg/node y qué ruta de subtítulos usar |
| `probe.sh` | Inspecciona el archivo fuente |
| `nuevo_proyecto.sh` | Crea la carpeta de trabajo + `reel.json` |
| `cortar_clip.sh` | Extrae un segmento preciso al frame |
| `vertical.sh` | Reencuadra a 1080×1920 (blur / crop / crop_focus) |
| `normalizar_audio.sh` | Loudness −14 LUFS + highpass |
| `detectar_silencios.py` | Jump-cuts automáticos (quita pausas) |
| `construir_edit_json.py` | Transcripción del clip → `edit.json` de Remotion |
| `preparar_remotion.sh` | Monta la plantilla, instala y renderiza el reel final |
| `construir_subtitulos.py` | (Ruta ligera) Transcripción → `.ass` |
| `quemar_subtitulos.sh` | (Ruta ligera, requiere libass) Quema `.ass` en el clip |
| `overlay_elementos.py` | Superpone imágenes/b-roll vía FFmpeg (sin texto) |

## Referencias
- `references/flujo.md` — pipeline detallado + checklist de QC.
- `references/seleccion-momentos.md` — cómo elegir clips que funcionan.
- `references/ffmpeg-recetas.md` — recetas de corte, reencuadre, zoom, b-roll.
- `references/subtitulos-y-overlays.md` — rutas Remotion y ASS, esquema `edit.json`.
- `references/transcripcion.md` — cómo transcribir y normalizar.
- `references/estilo-agora.md` — colores, tipografía y tono de marca.

## Principios
- **El contenido es humano; la IA solo edita.** No inventa frases ni pone en boca
  del hablante algo que no dijo. Los subtítulos transcriben lo dicho.
- **Fidelidad:** no recortes de forma que cambie el sentido de lo que se dijo.
- **Legible en mute:** el 80% ve sin sonido; los subtítulos son obligatorios.
- **Menos es más:** un reel = una idea. Si no se sostiene sola, no es reel.
