#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construir_edit_json.py — Convierte la transcripción de un CLIP ya cortado en el
edit.json que consume la plantilla Remotion (assets/remotion-overlay).

IMPORTANTE: transcribe el clip YA cortado (no el video fuente), así los tiempos
de las palabras ya son relativos a 0.

Uso:
  python3 construir_edit_json.py TRANSCRIPCION_CLIP.json -o edit.json \
      --video-path CLIP.mp4 --titulo "..." --keywords "a,b,c"

Opciones:
  --video base.mp4        Nombre del archivo de video dentro de public/ (default base.mp4).
  --video-path CLIP.mp4   Ruta real al clip para medir su duración con ffprobe.
  --dur 48.5              Duración en s (si no das --video-path).
  --fps 30
  --titulo "TEXTO"        Título que aparece arriba al inicio.
  --titulo-dur 2.5
  --keywords a,b,c        Keywords que se pintan con color de acento.
  --banda baja|centro     Posición de los subtítulos (default baja).
  --sin-progreso          Oculta la barra de progreso.
  --primario FFD54A  --acento 4ADE80  --texto FFFFFF   (colores hex RRGGBB)
  --overlays overlays.json  Lista JSON de overlays (ver reel.json / references).
"""
import argparse, json, subprocess, sys

def cargar_palabras(data):
    if isinstance(data, dict) and isinstance(data.get("words"), list):
        src = data["words"]
    elif isinstance(data, dict) and isinstance(data.get("segments"), list):
        src = []
        for seg in data["segments"]:
            src.extend(seg.get("words", []))
    elif isinstance(data, list):
        src = data
    else:
        sys.exit("No encuentro palabras con tiempos en la transcripción.")
    out = []
    for w in src:
        if not isinstance(w, dict):
            continue
        txt = w.get("text", w.get("word", ""))
        st = w.get("start", w.get("start_time"))
        en = w.get("end", w.get("end_time"))
        if txt is None or st is None or en is None:
            continue
        txt = str(txt).strip()
        if not txt:
            continue
        out.append({"text": txt, "startS": round(float(st), 3), "endS": round(float(en), 3)})
    if not out:
        sys.exit("La transcripción no trae tiempos por palabra.")
    return out

def ffprobe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return round(float(out.stdout.strip()), 3)
    except ValueError:
        sys.exit("No pude medir la duración de %s" % path)

def hx(h):
    h = h.strip().lstrip("#")
    return "#" + h.upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripcion")
    ap.add_argument("-o", "--salida", required=True)
    ap.add_argument("--video", default="base.mp4")
    ap.add_argument("--video-path", dest="vpath")
    ap.add_argument("--dur", type=float)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--titulo", default="")
    ap.add_argument("--titulo-dur", dest="tdur", type=float, default=2.5)
    ap.add_argument("--keywords", default="")
    ap.add_argument("--banda", choices=["baja", "centro"], default="baja")
    ap.add_argument("--sin-progreso", dest="sinprog", action="store_true")
    ap.add_argument("--primario", default="FFD54A")
    ap.add_argument("--acento", default="4ADE80")
    ap.add_argument("--texto", default="FFFFFF")
    ap.add_argument("--overlays")
    a = ap.parse_args()

    with open(a.transcripcion, encoding="utf-8") as f:
        words = cargar_palabras(json.load(f))

    if a.dur:
        dur = a.dur
    elif a.vpath:
        dur = ffprobe_dur(a.vpath)
    else:
        dur = round(words[-1]["endS"] + 0.5, 3)

    overlays = []
    if a.overlays:
        with open(a.overlays, encoding="utf-8") as f:
            overlays = json.load(f)

    edit = {
        "video": a.video,
        "fps": a.fps,
        "durationS": dur,
        "paleta": {"texto": hx(a.texto), "primario": hx(a.primario), "acento": hx(a.acento)},
        "titulo": a.titulo,
        "tituloDur": a.tdur,
        "keywords": [k.strip() for k in a.keywords.split(",") if k.strip()],
        "banda": a.banda,
        "progreso": not a.sinprog,
        "words": words,
        "overlays": overlays,
    }
    with open(a.salida, "w", encoding="utf-8") as f:
        json.dump(edit, f, ensure_ascii=False, indent=2)
    print("OK -> %s  (%d palabras, dur %.2fs)" % (a.salida, len(words), dur))

if __name__ == "__main__":
    main()
