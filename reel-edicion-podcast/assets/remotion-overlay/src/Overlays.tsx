import React from "react";
import {
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import type { Overlay } from "./data";

function posStyle(pos?: string): React.CSSProperties {
  const m = 56;
  switch (pos) {
    case "sup":
      return { top: m + 150, left: 0, right: 0, justifyContent: "center" };
    case "inf":
      return { bottom: m + 320, left: 0, right: 0, justifyContent: "center" };
    case "sup-izq":
      return { top: m + 150, left: m, justifyContent: "flex-start" };
    case "sup-der":
      return { top: m + 150, right: m, justifyContent: "flex-end" };
    case "inf-izq":
      return { bottom: m + 320, left: m, justifyContent: "flex-start" };
    case "inf-der":
      return { bottom: m + 320, right: m, justifyContent: "flex-end" };
    default:
      return {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        justifyContent: "center",
        alignItems: "center",
      };
  }
}

const OverlayItem: React.FC<{ ov: Overlay }> = ({ ov }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durF = Math.max(1, Math.round((ov.finS - ov.inicioS) * fps));
  const fadeF = Math.max(1, Math.round((ov.fade ?? 0.25) * fps));
  const opacity = interpolate(
    frame,
    [0, fadeF, durF - fadeF, durF],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const box: React.CSSProperties = {
    position: "absolute",
    display: "flex",
    opacity,
    ...posStyle(ov.pos),
  };
  if (ov.tipo === "emoji") {
    return (
      <div style={box}>
        <span style={{ fontSize: 180 * (ov.escala ?? 1) }}>{ov.valor}</span>
      </div>
    );
  }
  return (
    <div style={box}>
      <Img
        src={staticFile(ov.valor)}
        style={{ width: 1080 * (ov.escala ?? 0.35), height: "auto" }}
      />
    </div>
  );
};

export const Overlays: React.FC<{ overlays: Overlay[] }> = ({ overlays }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {overlays.map((ov, i) => (
        <Sequence
          key={i}
          from={Math.round(ov.inicioS * fps)}
          durationInFrames={Math.max(1, Math.round((ov.finS - ov.inicioS) * fps))}
          name={`ov-${i}`}
        >
          <OverlayItem ov={ov} />
        </Sequence>
      ))}
    </>
  );
};
