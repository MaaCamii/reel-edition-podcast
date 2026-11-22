#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construir_subtitulos.py — Convierte una transcripción con tiempos por palabra en
un archivo .ass con subtítulos "interactivos": se muestran pocas palabras a la
vez y la palabra que se está diciendo se resalta (estilo TikTok/Reels). Las
keywords de marca se pintan con color de acento. Opcionalmente añade un título
fijo arriba durante los primeros segundos.

Uso:
  python3 construir_subtitulos.py TRANSCRIPCION.json -o SALIDA.ass [opciones]

La transcripción puede venir en varios formatos; el script busca palabras con
tiempos. Formato canónico recomendado:
  { "words": [ {"text":"Hola","start":0.12,"end":0.44}, ... ] }
También acepta Whisper ({"segments":[{"words":[{"word","start","end"}]}]}) y
listas sueltas de palabras.

Opciones:
  --max-palabras 3      Palabras por grupo en pantalla (default 3).
  --max-dur 1.6         Duración máx. de un grupo en s (default 1.6).
  --fuente "Arial"      Nombre de fuente (usa una Bold; default Arial).
  --tam 92              Tamaño de fuente en px sobre lienzo 1080x1920 (default 92).
  --base FFFFFF         Color del texto normal (hex RRGGBB).
  --activa FFD400       Color de la palabra activa (hex RRGGBB).
  --acento 19C37D       Color de las keywords (hex RRGGBB).
  --banda baja|centro   Posición vertical de los subtítulos (default baja).
  --keywords a,b,c      Lista de keywords a resaltar (separadas por coma).
  --titulo "TEXTO"      Título fijo arriba.
  --titulo-dur 2.5      Segundos que dura el título (default 2.5).
  --offset 0.0          Resta este tiempo a todas las marcas (si recortaste el clip).
"""
import argparse, json, re, sys, unicodedata

W, Hh = 1080, 1920  # lienzo

def hex_to_ass(h):
    h = h.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError("Color inválido: %s (usa RRGGBB)" % h)
    r, g, b = h[0:2], h[2:4], h[4:6]
    return "&H00%s%s%s" % (b.upper(), g.upper(), r.upper())  # AABBGGRR

def t_ass(sec):
    if sec < 0: sec = 0.0
    cs = int(round(sec * 100))
    h = cs // 360000; cs -= h*360000
    m = cs // 6000;   cs -= m*6000
    s = cs // 100;    cs -= s*100
    return "%d:%02d:%02d.%02d" % (h, m, s, cs)

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]", "", w)

def cargar_palabras(data):
    """Extrae [{'text','start','end'}] de formatos variados."""
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
        if not isinstance(w, dict): continue
        txt = w.get("text", w.get("word", ""))
        st  = w.get("start", w.get("start_time"))
        en  = w.get("end", w.get("end_time"))
        if txt is None or st is None or en is None: continue
        txt = str(txt).strip()
        if not txt: continue
        out.append({"text": txt, "start": float(st), "end": float(en)})
    if not out:
        sys.exit("La transcripción no trae tiempos por palabra.")
    return out

def agrupar(words, max_pal, max_dur, offset):
    grupos, cur = [], []
    for w in words:
        w = {"text": w["text"],
             "start": max(0.0, w["start"] - offset),
             "end":   max(0.0, w["end"] - offset)}
        if not cur:
            cur = [w]; continue
        dur = w["end"] - cur[0]["start"]
        if len(cur) >= max_pal or dur > max_dur or w["text"][0:1] in ".?!":
            grupos.append(cur); cur = [w]
        else:
            cur.append(w)
        if cur and cur[-1]["text"][-1:] in ".?!":
            grupos.append(cur); cur = []
    if cur: grupos.append(cur)
    # cerrar huecos: cada palabra activa hasta el inicio de la siguiente
    for g in grupos:
        for i in range(len(g)-1):
            g[i]["end"] = max(g[i]["end"], g[i+1]["start"])
    return grupos

def construir(grupos, kws, c_base, c_act, c_acc, fuente, tam, banda, titulo, tdur):
    margen_v = 230 if banda == "baja" else 780
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {Hh}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{fuente},{tam},{c_base},{c_act},&H00101010,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,{margen_v},1
Style: Title,{fuente},74,{c_act},&H00000000,&H00101010,&H78000000,-1,0,0,0,100,100,0,0,1,5,0,8,80,80,150,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if titulo:
        lines.append("Dialogue: 0,%s,%s,Title,,0,0,0,,{\\fad(200,200)}%s" %
                     (t_ass(0.0), t_ass(tdur), titulo.upper().replace("\n","\\N")))

    for g in grupos:
        for i, w in enumerate(g):
            partes = []
            for j, ww in enumerate(g):
                token = ww["text"].replace("{","(").replace("}",")")
                if j == i:
                    col = c_act
                elif norm(ww["text"]) in kws:
                    col = c_acc
                else:
                    col = c_base
                if col == c_base:
                    partes.append(token)
                else:
                    partes.append("{\\c%s&}%s{\\c%s&}" % (col, token, c_base))
            texto = " ".join(partes)
            fx = "{\\fad(40,0)}" if i == 0 else ""
            lines.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,%s%s" %
                         (t_ass(w["start"]), t_ass(w["end"]), fx, texto))
    return head + "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripcion")
    ap.add_argument("-o","--salida", required=True)
    ap.add_argument("--max-palabras", dest="maxpal", type=int, default=3)
    ap.add_argument("--max-dur", dest="maxdur", type=float, default=1.6)
    ap.add_argument("--fuente", default="Arial")
    ap.add_argument("--tam", type=int, default=92)
    ap.add_argument("--base", default="FFFFFF")
    ap.add_argument("--activa", default="FFD400")
    ap.add_argument("--acento", default="19C37D")
    ap.add_argument("--banda", choices=["baja","centro"], default="baja")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--titulo-dur", dest="tdur", type=float, default=2.5)
    ap.add_argument("--offset", type=float, default=0.0)
    a = ap.parse_args()

    with open(a.transcripcion, encoding="utf-8") as f:
        data = json.load(f)
    words = cargar_palabras(data)
    grupos = agrupar(words, a.maxpal, a.maxdur, a.offset)
    kws = set(norm(k) for k in a.keywords.split(",") if k.strip())

    ass = construir(grupos, kws,
                    hex_to_ass(a.base), hex_to_ass(a.activa), hex_to_ass(a.acento),
                    a.fuente, a.tam, a.banda, a.titulo, a.tdur)
    with open(a.salida, "w", encoding="utf-8") as f:
        f.write(ass)
    print("OK -> %s  (%d palabras, %d grupos)" % (a.salida, len(words), len(grupos)))

if __name__ == "__main__":
    main()
