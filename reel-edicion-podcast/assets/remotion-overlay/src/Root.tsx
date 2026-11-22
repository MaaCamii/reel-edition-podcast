import React from "react";
import { Composition } from "remotion";
import { ReelEdit } from "./ReelEdit";
import { loadEditData } from "./data";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ReelEdit"
      component={ReelEdit as any}
      durationInFrames={1500}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ data: null } as any}
      calculateMetadata={async ({ props }) => {
        const data = await loadEditData();
        const fps = data.fps ?? 30;
        return {
          durationInFrames: Math.max(1, Math.round(data.durationS * fps)),
          fps,
          width: 1080,
          height: 1920,
          props: { ...props, data },
        };
      }}
    />
  );
};
