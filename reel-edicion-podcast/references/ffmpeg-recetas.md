# Recetas FFmpeg (lo que SÍ funciona sin libass)

Este ffmpeg (Homebrew 9.0.2) **no trae libass/drawtext** → no quema texto. Pero
sí hace todo lo demás. El texto lo pone Remotion. Recetas útiles:

## Corte preciso al frame
```
ffmpeg -y -i in.mp4 -ss 00:12:40.0 -to 00:13:25.0 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k out.mp4
```
`-ss/-to` **después** de `-i` = exacto (re-encodea). Antes de `-i` = rápido pero
salta al keyframe más cercano.

## Reencuadre 9:16 — fondo borroso (no recorta, recomendado)
```
ffmpeg -y -i in.mp4 -filter_complex \
"[0:v]split=2[bg][fg];\
 [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=24[bgb];\
 [fg]scale=1080:-2[fgs];\
 [bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" \
 -map "[v]" -map 0:a? out.mp4
```

## Reencuadre 9:16 — recorte central (llena pantalla, pierde bordes)
```
ffmpeg -y -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920,setsar=1" out.mp4
```
Recorte con foco (si el hablante está a un lado), `x` = fracción 0..1:
```
-vf "crop=w=ih*9/16:h=ih:x='(iw-ih*9/16)*0.33':y=0,scale=1080:1920,setsar=1"
```

## Zoom lento (efecto Ken Burns) para dar dinamismo
```
ffmpeg -y -i in.mp4 -vf \
"scale=2160:3840,zoompan=z='min(zoom+0.0005,1.15)':d=1:s=1080x1920:fps=30" \
 -c:a copy out.mp4
```

## Normalizar audio a -14 LUFS (estándar redes)
```
ffmpeg -y -i in.mp4 -c:v copy -af "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k out.mp4
```

## Superponer una imagen (lower-third, dato) en un rango
```
ffmpeg -y -i base.mp4 -i dato.png -filter_complex \
"[1]scale=640:-1[o];[0][o]overlay=x=(W-w)/2:y=H-h-360:enable='between(t,4,7)'" \
 -c:a copy out.mp4
```

## Superponer B-ROLL en video (picture-in-picture o pantalla completa temporal)
```
ffmpeg -y -i base.mp4 -i broll.mp4 -filter_complex \
"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setpts=PTS-STARTPTS[b];\
 [0:v][b]overlay=0:0:enable='between(t,8,12)'[v]" \
 -map "[v]" -map 0:a? -c:a aac out.mp4
```
(El audio del b-roll se ignora; se mantiene el del base. Para mezclarlo, usa `amix`.)

## Exportar fotograma / portada
```
ffmpeg -y -ss 2.0 -i reel_final.mp4 -frames:v 1 portada.png
```

## Formato de salida recomendado para redes
- Contenedor MP4, `-movflags +faststart`, video H.264 `yuv420p`, audio AAC 192k.
- 1080×1920, 30 fps (sube a 60 solo si la fuente es 60 y hay mucho movimiento).
