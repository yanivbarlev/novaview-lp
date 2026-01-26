import { Composition } from "remotion";
import { TrustedShowcase } from "./TrustedShowcase";

export const RemotionRoot = () => {
  return (
    <Composition
      id="TrustedShowcase"
      component={TrustedShowcase}
      durationInFrames={600}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
