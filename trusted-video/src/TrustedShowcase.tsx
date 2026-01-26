import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";

// Intro Scene
const IntroScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleY = interpolate(
    spring({ frame, fps, config: { damping: 200 } }),
    [0, 1],
    [100, 0]
  );

  const titleOpacity = interpolate(frame, [0, fps], [0, 1], {
    extrapolateRight: "clamp",
  });

  const subtitleOpacity = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <h1
          style={{
            fontSize: 80,
            color: "#fff",
            fontFamily: "Arial, sans-serif",
            fontWeight: "bold",
            margin: 0,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
          }}
        >
          /trusted Landing Page
        </h1>
        <p
          style={{
            fontSize: 36,
            color: "#4285f4",
            fontFamily: "Arial, sans-serif",
            marginTop: 20,
            opacity: subtitleOpacity,
          }}
        >
          Development Showcase
        </p>
      </div>
    </AbsoluteFill>
  );
};

// Landing Page Scene
const LandingPageScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pageScale = spring({
    frame,
    fps,
    config: { damping: 200 },
  });

  const badgeY = interpolate(
    spring({ frame: frame - fps, fps, config: { damping: 15 } }),
    [0, 1],
    [50, 0]
  );

  const badgeOpacity = interpolate(frame, [fps, fps * 1.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Mock landing page card */}
      <div
        style={{
          background: "#fff",
          borderRadius: 20,
          padding: 60,
          width: 700,
          boxShadow: "0 25px 80px rgba(0,0,0,0.3)",
          transform: `scale(${pageScale})`,
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: 24,
            color: "#666",
            marginBottom: 20,
          }}
        >
          EGuideSearches
        </div>

        <h2
          style={{
            fontSize: 42,
            color: "#333",
            fontFamily: "Arial, sans-serif",
            margin: "20px 0",
          }}
        >
          Free Download From Microsoft
        </h2>

        <p
          style={{
            fontSize: 18,
            color: "#666",
            lineHeight: 1.6,
          }}
        >
          Download the trusted stocks app to manage your portfolio
        </p>

        {/* CTA Button */}
        <div
          style={{
            background: "#4285f4",
            color: "#fff",
            padding: "18px 50px",
            borderRadius: 10,
            fontSize: 22,
            fontWeight: "bold",
            margin: "30px auto",
            display: "inline-block",
          }}
        >
          Continue
        </div>

        {/* Microsoft Badge */}
        <div
          style={{
            marginTop: 30,
            opacity: badgeOpacity,
            transform: `translateY(${badgeY}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              background: "#f5f5f5",
              padding: "12px 24px",
              borderRadius: 8,
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 3,
                width: 24,
                height: 24,
              }}
            >
              <div style={{ background: "#f25022", borderRadius: 2 }} />
              <div style={{ background: "#7fba00", borderRadius: 2 }} />
              <div style={{ background: "#00a4ef", borderRadius: 2 }} />
              <div style={{ background: "#ffb900", borderRadius: 2 }} />
            </div>
            <span style={{ fontSize: 16, color: "#333" }}>
              Get it from Microsoft
            </span>
          </div>
        </div>
      </div>

      {/* Label */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          left: 60,
          background: "rgba(0,0,0,0.7)",
          color: "#fff",
          padding: "12px 24px",
          borderRadius: 8,
          fontSize: 20,
        }}
      >
        Microsoft Store Badge Integration
      </div>
    </AbsoluteFill>
  );
};

// Download Flow Scene
const DownloadFlowScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const arrowProgress = interpolate(frame, [0, fps * 2], [0, 1], {
    extrapolateRight: "clamp",
  });

  const cursorX = interpolate(arrowProgress, [0, 0.3, 0.6, 1], [960, 960, 1700, 1700]);
  const cursorY = interpolate(arrowProgress, [0, 0.3, 0.6, 1], [500, 500, 80, 80]);

  const clickRipple = frame > fps * 2 ?
    interpolate(frame - fps * 2, [0, fps * 0.5], [0, 1], {
      extrapolateRight: "clamp",
    }) : 0;

  return (
    <AbsoluteFill
      style={{
        background: "#1a1a2e",
        justifyContent: "flex-start",
        alignItems: "center",
      }}
    >
      {/* Browser mockup */}
      <div
        style={{
          width: "90%",
          height: "85%",
          marginTop: 50,
          background: "#fff",
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
        }}
      >
        {/* Browser toolbar */}
        <div
          style={{
            height: 50,
            background: "#f1f3f4",
            display: "flex",
            alignItems: "center",
            padding: "0 15px",
            gap: 10,
          }}
        >
          <div style={{ display: "flex", gap: 8 }}>
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#ff5f57",
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#febc2e",
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#28c840",
              }}
            />
          </div>

          <div
            style={{
              flex: 1,
              background: "#fff",
              padding: "8px 15px",
              borderRadius: 20,
              fontSize: 14,
              color: "#666",
              marginLeft: 20,
            }}
          >
            eguidesearches.com/trusted
          </div>

          {/* Download icon area */}
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              background: arrowProgress > 0.6 ? "#e8f0fe" : "transparent",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginLeft: "auto",
              position: "relative",
            }}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#4285f4"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>

            {/* Click ripple effect */}
            {clickRipple > 0 && (
              <div
                style={{
                  position: "absolute",
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  border: "3px solid #4285f4",
                  opacity: 1 - clickRipple,
                  transform: `scale(${0.5 + clickRipple})`,
                }}
              />
            )}
          </div>
        </div>

        {/* Page content placeholder */}
        <div
          style={{
            padding: 60,
            textAlign: "center",
          }}
        >
          <h2 style={{ fontSize: 36, color: "#333" }}>
            Click Continue to Download
          </h2>
          <div
            style={{
              background: "#4285f4",
              color: "#fff",
              padding: "15px 40px",
              borderRadius: 8,
              fontSize: 20,
              display: "inline-block",
              marginTop: 30,
            }}
          >
            Continue
          </div>
        </div>
      </div>

      {/* Animated cursor */}
      <svg
        width="32"
        height="32"
        viewBox="0 0 24 24"
        style={{
          position: "absolute",
          left: cursorX,
          top: cursorY,
          filter: "drop-shadow(2px 2px 4px rgba(0,0,0,0.3))",
        }}
      >
        <path
          d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 0 1 .35-.15h6.87c.48 0 .72-.58.38-.92L6.35 2.91a.5.5 0 0 0-.85.3z"
          fill="#fff"
          stroke="#000"
          strokeWidth="1"
        />
      </svg>

      {/* Label */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 60,
          background: "rgba(0,0,0,0.7)",
          color: "#fff",
          padding: "12px 24px",
          borderRadius: 8,
          fontSize: 20,
        }}
      >
        User clicks Continue - Download starts
      </div>
    </AbsoluteFill>
  );
};

// Small Tooltip Helper Scene
const TooltipHelperScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bounceY = interpolate(
    frame % (fps * 0.75),
    [0, fps * 0.375, fps * 0.75],
    [0, -15, 0]
  );

  const helperOpacity = interpolate(frame, [fps * 0.5, fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "#1a1a2e",
      }}
    >
      {/* Browser mockup header only */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 50,
          background: "#f1f3f4",
          display: "flex",
          alignItems: "center",
          padding: "0 15px",
        }}
      >
        <div style={{ display: "flex", gap: 8 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              background: "#ff5f57",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              background: "#febc2e",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              background: "#28c840",
            }}
          />
        </div>

        <div
          style={{
            flex: 1,
            background: "#fff",
            padding: "8px 15px",
            borderRadius: 20,
            fontSize: 14,
            color: "#666",
            marginLeft: 20,
          }}
        >
          eguidesearches.com/trusted
        </div>

        {/* Download icon */}
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            background: "#e8f0fe",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginRight: 15,
          }}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#4285f4"
            strokeWidth="2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
        </div>
      </div>

      {/* Bouncing tooltip helper */}
      <div
        style={{
          position: "absolute",
          top: 100,
          right: 30,
          opacity: helperOpacity,
          transform: `translateY(${bounceY}px)`,
        }}
      >
        <div
          style={{
            background: "#4285f4",
            color: "#fff",
            padding: "20px 28px",
            borderRadius: 14,
            boxShadow: "0 8px 32px rgba(66, 133, 244, 0.4)",
            position: "relative",
          }}
        >
          {/* Close button */}
          <div
            style={{
              position: "absolute",
              top: 8,
              right: 12,
              fontSize: 20,
              opacity: 0.8,
            }}
          >
            x
          </div>

          <div
            style={{
              fontSize: 24,
              fontWeight: "bold",
              marginBottom: 8,
            }}
          >
            Click <span style={{ fontSize: 28 }}>↓</span> above
          </div>

          <div
            style={{
              fontSize: 16,
              opacity: 0.9,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span
              style={{
                background: "rgba(255,255,255,0.2)",
                padding: "4px 8px",
                borderRadius: 4,
                fontSize: 14,
              }}
            >
              MSIX
            </span>
            <span>Then click trusted-stocks.Msix</span>
          </div>

          {/* Arrow pointing up */}
          <div
            style={{
              position: "absolute",
              top: -10,
              right: 50,
              width: 0,
              height: 0,
              borderLeft: "10px solid transparent",
              borderRight: "10px solid transparent",
              borderBottom: "10px solid #4285f4",
            }}
          />
        </div>
      </div>

      {/* Label */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          left: 60,
          background: "rgba(0,0,0,0.7)",
          color: "#fff",
          padding: "12px 24px",
          borderRadius: 8,
          fontSize: 20,
        }}
      >
        Small Bouncing Tooltip Helper - Guides user to downloads
      </div>
    </AbsoluteFill>
  );
};

// Big Modal Helper Scene
const BigModalScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const modalScale = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const progressWidth = interpolate(frame, [fps, fps * 3], [0, 85], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cursorBounceY = interpolate(
    frame % fps,
    [0, fps * 0.5, fps],
    [0, -10, 0]
  );

  const rippleScale = interpolate(
    (frame % (fps * 0.8)),
    [0, fps * 0.8],
    [0.5, 2.5]
  );

  const rippleOpacity = interpolate(
    (frame % (fps * 0.8)),
    [0, fps * 0.8],
    [1, 0]
  );

  const glowPulse = interpolate(
    (frame % (fps * 2)),
    [0, fps, fps * 2],
    [0.3, 0.8, 0.3]
  );

  return (
    <AbsoluteFill
      style={{
        background: "rgba(0, 0, 0, 0.75)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Big modal card */}
      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          padding: "30px 35px",
          maxWidth: 750,
          width: "90%",
          boxShadow: "0 25px 80px rgba(0,0,0,0.5)",
          transform: `scale(${modalScale})`,
        }}
      >
        {/* Progress section */}
        <h2
          style={{
            fontSize: 28,
            color: "#333",
            margin: "0 0 24px 0",
            textAlign: "center",
          }}
        >
          Last step left
        </h2>

        {/* Progress bar */}
        <div
          style={{
            width: "100%",
            height: 24,
            background: "#E0E7FF",
            borderRadius: 4,
            marginBottom: 20,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${progressWidth}%`,
              height: "100%",
              background: "#708EFF",
              borderRadius: 4,
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              paddingRight: 10,
            }}
          >
            <span style={{ fontSize: 12, color: "#333", fontWeight: "bold" }}>
              {Math.round(progressWidth)}%
            </span>
          </div>
        </div>

        {/* Instructions section */}
        <div
          style={{
            background: "#F0F3FF",
            borderRadius: 16,
            padding: 24,
            display: "flex",
            gap: 30,
          }}
        >
          {/* Text instructions */}
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: 24 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 8,
                }}
              >
                <span
                  style={{
                    background: "#4285f4",
                    color: "#fff",
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    fontSize: 14,
                  }}
                >
                  1
                </span>
                <span style={{ fontSize: 18, fontWeight: 600 }}>
                  Click the download icon
                </span>
              </div>
              <p style={{ color: "#666", marginLeft: 40, fontSize: 14 }}>
                Find and click the download icon in your browser toolbar
              </p>
            </div>

            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 8,
                }}
              >
                <span
                  style={{
                    background: "#4285f4",
                    color: "#fff",
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    fontSize: 14,
                  }}
                >
                  2
                </span>
                <span style={{ fontSize: 18, fontWeight: 600 }}>
                  Click trusted-stocks.Msix
                </span>
              </div>
              <p style={{ color: "#666", marginLeft: 40, fontSize: 14 }}>
                Open the downloaded file to install
              </p>
            </div>
          </div>

          {/* Browser mockup with cursor */}
          <div
            style={{
              width: 280,
              background: "#fff",
              borderRadius: 8,
              overflow: "hidden",
              boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
              position: "relative",
            }}
          >
            {/* Mini toolbar */}
            <div
              style={{
                height: 32,
                background: "#f1f3f4",
                display: "flex",
                alignItems: "center",
                padding: "0 10px",
                gap: 6,
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "#ff5f57",
                }}
              />
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "#febc2e",
                }}
              />
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "#28c840",
                }}
              />

              <div style={{ flex: 1 }} />

              {/* Download icon with glow */}
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: "#e8f0fe",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                }}
              >
                {/* Green glow */}
                <div
                  style={{
                    position: "absolute",
                    inset: -8,
                    background: `radial-gradient(circle, rgba(145, 219, 61, ${glowPulse}) 0%, transparent 70%)`,
                    borderRadius: "50%",
                  }}
                />
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#4285f4"
                  strokeWidth="2"
                  style={{ position: "relative", zIndex: 1 }}
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
              </div>
            </div>

            {/* Animated cursor */}
            <div
              style={{
                position: "absolute",
                right: 30,
                top: 45 + cursorBounceY,
                zIndex: 10,
              }}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                style={{
                  filter: "drop-shadow(1px 1px 2px rgba(0,0,0,0.3))",
                  transform: "rotate(-15deg)",
                }}
              >
                <path
                  d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 0 1 .35-.15h6.87c.48 0 .72-.58.38-.92L6.35 2.91a.5.5 0 0 0-.85.3z"
                  fill="#fff"
                  stroke="#000"
                  strokeWidth="1"
                />
              </svg>

              {/* Click ripple */}
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: 20,
                  height: 20,
                  borderRadius: "50%",
                  border: "2px solid #4285f4",
                  transform: `scale(${rippleScale})`,
                  opacity: rippleOpacity,
                }}
              />
            </div>

            {/* Placeholder content */}
            <div style={{ padding: 15, color: "#999", fontSize: 12 }}>
              Page content area
            </div>
          </div>
        </div>

        {/* Got it button */}
        <div style={{ textAlign: "center", marginTop: 24 }}>
          <div
            style={{
              background: "#4285f4",
              color: "#fff",
              padding: "12px 32px",
              borderRadius: 8,
              fontSize: 18,
              fontWeight: "bold",
              display: "inline-block",
            }}
          >
            Got it!
          </div>
        </div>
      </div>

      {/* Label */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 60,
          background: "rgba(255,255,255,0.9)",
          color: "#333",
          padding: "12px 24px",
          borderRadius: 8,
          fontSize: 20,
        }}
      >
        Big Modal Helper - Animated cursor & progress bar
      </div>
    </AbsoluteFill>
  );
};

// Outro Scene
const OutroScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const items = [
    "Microsoft Store Badge",
    "Custom Download URL with clickid",
    "Small Bouncing Tooltip Helper",
    "Big Modal with Animated Cursor",
    "Progress Bar Animation",
    "Green Pulsing Glow Effect",
  ];

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <h1
          style={{
            fontSize: 60,
            color: "#fff",
            fontFamily: "Arial, sans-serif",
            marginBottom: 40,
          }}
        >
          Features Implemented
        </h1>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 15,
            alignItems: "center",
          }}
        >
          {items.map((item, index) => {
            const itemOpacity = interpolate(
              frame,
              [index * 8, index * 8 + 15],
              [0, 1],
              {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }
            );

            const itemX = interpolate(
              frame,
              [index * 8, index * 8 + 15],
              [-50, 0],
              {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }
            );

            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 15,
                  opacity: itemOpacity,
                  transform: `translateX(${itemX}px)`,
                }}
              >
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: "#4285f4",
                  }}
                />
                <span
                  style={{
                    fontSize: 28,
                    color: "#fff",
                    fontFamily: "Arial, sans-serif",
                  }}
                >
                  {item}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Main composition
export const TrustedShowcase = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={90}>
        <IntroScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={120}>
        <LandingPageScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: 20 })}
      />

      <TransitionSeries.Sequence durationInFrames={120}>
        <DownloadFlowScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={90}>
        <TooltipHelperScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-bottom" })}
        timing={linearTiming({ durationInFrames: 20 })}
      />

      <TransitionSeries.Sequence durationInFrames={150}>
        <BigModalScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={120}>
        <OutroScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
