import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { mergePalette } from "./palette";
import { Captions } from "./Captions";
import { Overlays } from "./Overlays";
import type { EditData } from "./data";

const TitleCard: React.FC<{ texto: string; paleta: any }> = ({ texto, paleta }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 16, stiffness: 160 } });
  const y = interpolate(pop, [0, 1], [-40, 0]);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start" }}>
      <div
        style={{
          marginTop: 170,
          transform: `translateY(${y}px)`,
          opacity: pop,
          background: paleta.primario,
          color: "#0B1020",
          fontWeight: 900,
          fontSize: 62,
          lineHeight: 1.05,
          padding: "20px 34px",
          borderRadius: 22,
          maxWidth: 900,
          textAlign: "center",
          boxShadow: "0 12px 40px rgba(0,0,0,0.35)",
          fontFamily:
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        }}
      >
        {texto}
      </div>
    </AbsoluteFill>
  );
};

const ProgressBar: React.FC<{ paleta: any }> = ({ paleta }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pct = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        height: 10,
        width: `${pct}%`,
        background: paleta.acento,
      }}
    />
  );
};

export const ReelEdit: React.FC<{ data: EditData }> = ({ data }) => {
  const { fps } = useVideoConfig();
  const paleta = mergePalette(data.paleta as any);
  const tituloDur = data.tituloDur ?? 2.5;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Video grabado (ya reencuadrado 1080x1920) */}
      <OffthreadVideo
        src={staticFile(data.video)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />

      {/* Overlays de imágenes / emojis */}
      <Overlays overlays={data.overlays || []} />

      {/* Subtítulos interactivos */}
      <Captions
        words={data.words}
        paleta={paleta}
        keywords={data.keywords || []}
        banda={data.banda || "baja"}
      />

      {/* Título fijo al inicio */}
      {data.titulo ? (
        <Sequence from={0} durationInFrames={Math.round(tituloDur * fps)} name="titulo">
          <TitleCard texto={data.titulo} paleta={paleta} />
        </Sequence>
      ) : null}

      {/* Barra de progreso */}
      {data.progreso !== false ? <ProgressBar paleta={paleta} /> : null}
    </AbsoluteFill>
  );
};
