# Flujo detallado y checklist de QC

## Estructura de la carpeta de proyecto
```
<proyecto>/
  origen/            video/audio fuente
  transcripcion/     transcripción de la fuente y de cada clip (JSON {words})
  clips/             cortes intermedios y finales de cada reel
  subtitulos/        .ass (solo ruta ligera)
  overlays/          PNG/imágenes para superponer
  export/            reels finales listos para publicar
  reel.json          plan de todos los reels del lote
```

## Nombres sugeridos por reel (id = r01, r02, ...)
```
clips/r01_corte.mp4     # segmento crudo
clips/r01_vert.mp4      # reencuadrado 9:16
clips/r01_base.mp4      # audio normalizado (+ jump-cuts) -> ESTE va a Remotion
clips/r01_edit.json     # edit.json para Remotion
clips/r01_remotion/     # proyecto Remotion montado
export/r01_reel_final.mp4
```

## Orden de operaciones (por qué este orden)
1. **Cortar** primero: trabajas sobre segundos, no sobre todo el episodio.
2. **Reencuadrar** antes del audio: el video queda en su forma final 9:16.
3. **Normalizar audio** sobre el clip ya cortado.
4. **Jump-cuts** al final del pre-proceso (cambia la duración → re-transcribe el clip después).
5. **Transcribir el clip final** (`r01_base.mp4`) → tiempos relativos a 0 → `edit.json`.
6. **Remotion** pone subtítulos/título/overlays. Último paso.

> Si vas a aplicar jump-cuts, hazlo ANTES de transcribir el clip, porque mueve
> los tiempos. Transcribe siempre la versión final del `base.mp4`.

## Checklist de QC (antes de entregar)
- [ ] Dura entre 15 y 60 s (ideal 20–45 s para retención).
- [ ] El **primer segundo** tiene gancho (frase o imagen que frena el scroll).
- [ ] Se entiende **en mute** (subtítulos correctos y legibles).
- [ ] El hablante no queda cortado por el reencuadre (revisa `crop`; usa `blur` si dudas).
- [ ] Audio parejo, sin picos ni saltos bruscos en los jump-cuts.
- [ ] Los subtítulos **coinciden** con lo que se dice (sin inventar).
- [ ] El corte **no distorsiona** el sentido de lo dicho.
- [ ] Safe area: nada importante en el 12% inferior (tapa la UI de la app) ni pegado a los bordes.
- [ ] Copy + hashtags listos (skill `agora-social-content`).

## Rendimiento
- El primer `preparar_remotion.sh` instala Node deps + Chromium headless (minutos).
- Reutiliza `node_modules`: para el 2º reel, copia la carpeta `r01_remotion`
  (con su `node_modules`) y solo cambia `public/base.mp4` + `public/edit.json`,
  o reusa el mismo proyecto cambiando esos dos archivos y volviendo a `npm run render`.
- Render con `--concurrency=1` es lo más estable en Mac; súbelo si tu CPU aguanta.
