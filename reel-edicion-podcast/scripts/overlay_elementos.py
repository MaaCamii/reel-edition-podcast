#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
overlay_elementos.py — Superpone elementos complementarios (PNG/imagen con
transparencia, o un clip de b-roll) sobre el reel en momentos concretos, con
aparición/desaparición suave. Construye un filter_complex de ffmpeg a partir de
una lista de "cues".

Uso:
  python3 overlay_elementos.py BASE.mp4 -o SALIDA.mp4 --cues cues.json

Formato de cues.json:
  [
    { "archivo":"overlays/dato.png", "inicio":4.0, "fin":7.0,
      "pos":"centro", "escala":0.6, "fade":0.25 },
    { "archivo":"overlays/logo.png", "inicio":0.0, "fin":99,
      "pos":"sup-der", "escala":0.18, "fade":0.0 }
  ]
  pos: centro | sup | inf | sup-izq | sup-der | inf-izq | inf-der
  escala: fracción del ancho del reel (1080). 0.6 = 60% del ancho.
  fade: segundos de fundido de entrada/salida (0 = sin fundido).

Solo imágenes estáticas (PNG/JPG). Para b-roll en video, ver references/ffmpeg-recetas.md.
"""
import argparse, json, subprocess, sys, os

W, Hh = 1080, 1920

def pos_xy(pos):
    m = 48  # margen
    return {
        "centro":  ("(W-w)/2", "(H-h)/2"),
        "sup":     ("(W-w)/2", str(m+120)),
        "inf":     ("(W-w)/2", "H-h-%d" % (m+260)),
        "sup-izq": (str(m), str(m+120)),
        "sup-der": ("W-w-%d" % m, str(m+120)),
        "inf-izq": (str(m), "H-h-%d" % (m+260)),
        "inf-der": ("W-w-%d" % m, "H-h-%d" % (m+260)),
    }.get(pos, ("(W-w)/2", "(H-h)/2"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("-o","--salida", required=True)
    ap.add_argument("--cues", required=True)
    a = ap.parse_args()

    with open(a.cues, encoding="utf-8") as f:
        cues = json.load(f)
    if not cues:
        sys.exit("cues.json está vacío.")

    inputs = ["-i", a.base]
    for c in cues:
        if not os.path.isfile(c["archivo"]):
            sys.exit("No existe el overlay: %s" % c["archivo"])
        inputs += ["-i", c["archivo"]]

    chain = []
    last = "[0:v]"
    for i, c in enumerate(cues, start=1):
        w_px = int(W * float(c.get("escala", 0.5)))
        ini, fin = float(c["inicio"]), float(c["fin"])
        fade = float(c.get("fade", 0.2))
        x, y = pos_xy(c.get("pos", "centro"))
        pre = "[%d:v]scale=%d:-1" % (i, w_px)
        if fade > 0:
            dur = max(0.01, fin - ini)
            pre += ",format=rgba,fade=t=in:st=%s:d=%s:alpha=1,fade=t=out:st=%s:d=%s:alpha=1" % (
                ini, fade, max(ini, fin - fade), fade)
        pre += "[ov%d];" % i
        out = "[tmp%d]" % i if i < len(cues) else "[v]"
        chain.append(pre)
        chain.append("%s[ov%d]overlay=%s:%s:enable='between(t,%s,%s)'%s;" % (
            last, i, x, y, ini, fin, out))
        last = out

    fc = "".join(chain).rstrip(";")
    cmd = ["ffmpeg","-y"] + inputs + ["-filter_complex", fc,
           "-map","[v]","-map","0:a?",
           "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
           "-c:a","copy","-movflags","+faststart", a.salida]
    subprocess.run(cmd, check=True)
    print("OK overlays -> %s" % a.salida)

if __name__ == "__main__":
    main()
