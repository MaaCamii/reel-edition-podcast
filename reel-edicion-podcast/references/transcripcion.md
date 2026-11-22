# Transcripción con tiempos por palabra

Los scripts de subtítulos necesitan **tiempos por palabra**. El formato canónico
que consumen es:
```json
{ "words": [ { "text": "Hola", "start": 0.12, "end": 0.40 }, ... ] }
```
`start`/`end` en **segundos**. Los loaders también aceptan:
- Whisper: `{ "segments": [ { "words": [ { "word", "start", "end" } ] } ] }`
- Lista suelta: `[ { "text", "start", "end" }, ... ]`

> Para la capa Remotion, transcribe el **clip ya cortado** (`r01_base.mp4`), no
> la fuente: así los tiempos ya son relativos a 0 y no hay que desplazarlos.

## Opción 1 — MCP de ElevenLabs (sin instalar nada)
Usa la tool `creative_transcribe_audio`. Flujo típico:
1. Extrae el audio del clip si hace falta:
   ```
   ffmpeg -y -i clips/r01_base.mp4 -vn -ac 1 -ar 16000 transcripcion/r01.wav
   ```
2. Sube el audio y transcríbelo con la tool (ver instrucciones del conector
   ElevenLabs: `creative_upload_flow_reference` → `creative_transcribe_audio`
   con ese `node_id` como `connect_from`).
3. Toma el resultado y **normalízalo** al formato `{words}` de arriba
   (mapea los campos de palabra/tiempo a `text/start/end` en segundos). Guarda
   el JSON en `transcripcion/`.

## Opción 2 — Whisper local (si prefieres offline)
No está instalado en este Mac. Si lo quieres:
```
# faster-whisper (rápido, timestamps por palabra):
pipx install faster-whisper   # o pip
# o whisper.cpp:  brew install whisper-cpp   (modelo aparte)
```
Con openai-whisper / faster-whisper pide **word timestamps** y exporta JSON; con
whisper.cpp usa `--output-json-full`. Luego normaliza a `{words}`.

## Normalización (pauta)
Cualquiera sea la fuente, produce un JSON con:
- una entrada por palabra,
- `text` sin espacios extra,
- `start`/`end` numéricos en segundos,
- en orden temporal.
Descarta tokens vacíos. Si el transcriptor da tiempos por segmento pero no por
palabra, repártelos proporcionalmente (peor karaoke, pero funciona).

## Idioma
El material de Ágora es en español. Indica el idioma al transcriptor para mejorar
la precisión de nombres propios y términos cívicos (Constitución, veeduría, etc.).
Revisa a ojo los subtítulos: **no deben inventar ni corregir** lo que se dijo,
solo transcribirlo (puedes arreglar puntuación y mayúsculas).
