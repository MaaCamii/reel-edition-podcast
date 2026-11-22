import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import type { Palette } from "./palette";
import type { Word } from "./data";

type Line = { words: Word[]; startS: number; endS: number };

const norm = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^\w]/g, "");

function chunk(words: Word[], maxWords = 3, maxChars = 22): Line[] {
  const lines: Line[] = [];
  let cur: Word[] = [];
  let chars = 0;
  for (const w of words) {
    const wlen = w.text.length + 1;
    const corte = /[.?!]$/.test(w.text);
    if (cur.length && (cur.length >= maxWords || chars + wlen > maxChars)) {
      lines.push({ words: cur, startS: cur[0].startS, endS: cur[cur.length - 1].endS });
      cur = [];
      chars = 0;
    }
    cur.push(w);
    chars += wlen;
    if (corte) {
      lines.push({ words: cur, startS: cur[0].startS, endS: cur[cur.length - 1].endS });
      cur = [];
      chars = 0;
    }
  }
  if (cur.length)
    lines.push({ words: cur, startS: cur[0].startS, endS: cur[cur.length - 1].endS });
  return lines;
}

export const Captions: React.FC<{
  words: Word[];
  paleta: Palette;
  keywords: string[];
  banda: "baja" | "centro";
}> = ({ words, paleta, keywords, banda }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const kw = useMemo(() => new Set(keywords.map(norm)), [keywords]);
  const lines = useMemo(() => chunk(words || []), [words]);
  if (!lines.length) return null;

  let active = lines[0];
  let activeIdx = 0;
  lines.forEach((ln, i) => {
    if (ln.startS <= t + 0.06) {
      active = ln;
      activeIdx = i;
    }
  });

  // Rebote de entrada de la línea (spring) al aparecer.
  const lineStartFrame = Math.round(active.startS * fps);
  const pop = spring({
    frame: frame - lineStartFrame,
    fps,
    config: { damping: 14, stiffness: 180, mass: 0.6 },
  });
  const scale = interpolate(pop, [0, 1], [0.82, 1]);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: banda === "baja" ? "14%" : undefined,
        top: banda === "centro" ? "42%" : undefined,
        display: "flex",
        justifyContent: "center",
        padding: "0 70px",
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "6px 16px",
          maxWidth: 940,
          background: paleta.franja,
          borderRadius: 30,
          padding: "20px 34px",
          transform: `scale(${scale})`,
        }}
      >
        {active.words.map((w, i) => {
          const spoken = t >= w.endS - 0.02;
          const current = t >= w.startS - 0.04 && t < w.endS - 0.02;
          const isKw = kw.has(norm(w.text));
          let color: string = paleta.texto;
          if (current) color = paleta.primario;
          else if (isKw) color = paleta.acento;
          else if (!spoken) color = "rgba(255,255,255,0.55)";
          return (
            <span
              key={`${activeIdx}-${i}`}
              style={{
                color,
                fontSize: 78,
                fontWeight: 900,
                letterSpacing: "-0.5px",
                lineHeight: 1.1,
                textTransform: "none",
                textShadow: `0 4px 14px ${paleta.sombra}`,
                transform: current ? "translateY(-3px)" : "none",
                fontFamily:
                  "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};
