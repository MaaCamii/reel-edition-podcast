#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_silencios.py — Detecta silencios con ffmpeg y produce un video con
jump-cuts (quita las pausas muertas, estilo "talking head" ágil de redes).

Uso:
  python3 detectar_silencios.py ENTRADA.mp4 [opciones]

Opciones:
  --render SALIDA.mp4   Renderiza el video recortado. Sin esto, solo imprime JSON.
  --ruido -30           Umbral de silencio en dB (default -30; más negativo = más estricto).
  --min-silencio 0.45   Duración mínima de un silencio para cortarlo, en s (default 0.45).
  --margen 0.08         Margen que se conserva alrededor del habla, en s (default 0.08).
  --json segmentos.json Guarda los segmentos de habla detectados.

Depende solo de ffmpeg/ffprobe + stdlib. Pensado para Python 3.9+.
"""
import argparse, json, re, subprocess, sys, os

def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        sys.exit("No pude leer la duración de %s" % path)

def detectar(path, ruido, min_sil):
    proc = subprocess.run(
        ["ffmpeg","-i",path,"-af",
         "silencedetect=noise=%sdB:d=%s" % (ruido, min_sil),
         "-f","null","-"],
        capture_output=True, text=True)
    log = proc.stderr
    starts = [float(m) for m in re.findall(r"silence_start:\s*([0-9.]+)", log)]
    ends   = [float(m) for m in re.findall(r"silence_end:\s*([0-9.]+)", log)]
    sil = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        sil.append((s, e))
    return sil

def habla_desde_silencios(sil, dur, margen):
    # Complemento de los silencios = segmentos de habla, con margen y merge.
    segs = []
    cursor = 0.0
    for s, e in sil:
        ini = cursor
        fin = s + margen
        if fin - ini > 0.05:
            segs.append([max(0.0, ini - 0), min(dur, fin)])
        cursor = (e - margen) if e is not None else dur
        cursor = max(0.0, cursor)
    if cursor < dur:
        segs.append([max(0.0, cursor), dur])
    # merge solapados
    merged = []
    for a, b in segs:
        if merged and a <= merged[-1][1] + 0.02:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(round(a,3), round(b,3)) for a,b in merged if b - a > 0.08]

def render(path, segs, out):
    if not segs:
        sys.exit("No hay segmentos de habla; nada que renderizar.")
    parts_v, parts_a, labels = [], [], []
    for i,(a,b) in enumerate(segs):
        parts_v.append("[0:v]trim=start=%s:end=%s,setpts=PTS-STARTPTS[v%d];" % (a,b,i))
        parts_a.append("[0:a]atrim=start=%s:end=%s,asetpts=PTS-STARTPTS[a%d];" % (a,b,i))
        labels.append("[v%d][a%d]" % (i,i))
    fc = "".join(parts_v) + "".join(parts_a) + \
         "".join(labels) + "concat=n=%d:v=1:a=1[v][a]" % len(segs)
    cmd = ["ffmpeg","-y","-i",path,"-filter_complex",fc,
           "-map","[v]","-map","[a]",
           "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
           "-c:a","aac","-b:a","192k","-movflags","+faststart", out]
    subprocess.run(cmd, check=True)
    print("OK jump-cuts -> %s" % out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("--render")
    ap.add_argument("--ruido", default="-30")
    ap.add_argument("--min-silencio", dest="minsil", default="0.45")
    ap.add_argument("--margen", type=float, default=0.08)
    ap.add_argument("--json")
    a = ap.parse_args()

    dur = ffprobe_duration(a.entrada)
    sil = detectar(a.entrada, a.ruido, a.minsil)
    segs = habla_desde_silencios(sil, dur, a.margen)

    dur_final = round(sum(b-x for x,b in segs), 2)
    info = {"duracion_original": round(dur,2),
            "duracion_tras_cortes": dur_final,
            "segmentos_habla": [{"inicio":x,"fin":b} for x,b in segs]}
    if a.json:
        with open(a.json,"w") as f: json.dump(info,f,ensure_ascii=False,indent=2)
    print(json.dumps(info, ensure_ascii=False, indent=2))

    if a.render:
        render(a.entrada, segs, a.render)

if __name__ == "__main__":
    main()
