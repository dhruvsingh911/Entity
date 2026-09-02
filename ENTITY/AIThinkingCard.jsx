import React, { useEffect, useRef } from "react";

const COLORS = [
  "#ff8a5c",
  "#ffb38a",
  "#ffd0b8",
  "#a78bfa",
  "#7aa7ff",
];

export default function AIThinkingCard() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    let animationFrame;
    let time = 0;

    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;

      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resizeCanvas();

    const observer = new ResizeObserver(resizeCanvas);
    observer.observe(canvas);

    const getNodes = () => {
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;

      return [
        { x: width * 0.12, y: height * 0.20 },
        { x: width * 0.28, y: height * 0.13 },
        { x: width * 0.48, y: height * 0.23 },
        { x: width * 0.70, y: height * 0.15 },
        { x: width * 0.88, y: height * 0.27 },

        { x: width * 0.08, y: height * 0.50 },
        { x: width * 0.25, y: height * 0.62 },
        { x: width * 0.42, y: height * 0.55 },
        { x: width * 0.64, y: height * 0.66 },
        { x: width * 0.87, y: height * 0.55 },

        { x: width * 0.18, y: height * 0.83 },
        { x: width * 0.43, y: height * 0.82 },
        { x: width * 0.68, y: height * 0.84 },
        { x: width * 0.90, y: height * 0.78 },
      ];
    };

    const connections = [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],

      [0, 5],
      [0, 6],
      [1, 6],
      [1, 7],
      [2, 7],
      [2, 8],
      [3, 8],
      [3, 9],
      [4, 9],

      [5, 6],
      [6, 7],
      [7, 8],
      [8, 9],

      [5, 10],
      [6, 10],
      [6, 11],
      [7, 11],
      [7, 12],
      [8, 12],
      [9, 13],

      [10, 11],
      [11, 12],
      [12, 13],

      [2, 6],
      [2, 9],
      [7, 3],
      [8, 4],
    ];

    const particles = Array.from({ length: 70 }, () => ({
      connection:
        connections[Math.floor(Math.random() * connections.length)],
      progress: Math.random(),
      speed: 0.002 + Math.random() * 0.005,
      size: 1.5 + Math.random() * 2.5,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
    }));

    const draw = () => {
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;

      ctx.clearRect(0, 0, width, height);

      const nodes = getNodes();

      // Background glow
      const backgroundGlow = ctx.createRadialGradient(
        width * 0.5,
        height * 0.48,
        20,
        width * 0.5,
        height * 0.48,
        width * 0.75
      );

      backgroundGlow.addColorStop(
        0,
        "rgba(255, 138, 92, 0.12)"
      );

      backgroundGlow.addColorStop(
        0.45,
        "rgba(139, 92, 246, 0.08)"
      );

      backgroundGlow.addColorStop(
        1,
        "rgba(0, 0, 0, 0)"
      );

      ctx.fillStyle = backgroundGlow;
      ctx.fillRect(0, 0, width, height);

      // Network connections
      connections.forEach(([a, b], index) => {
        const start = nodes[a];
        const end = nodes[b];

        const color =
          COLORS[index % COLORS.length];

        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);

        ctx.strokeStyle = `${color}80`;
        ctx.lineWidth = 1.4;

        ctx.shadowBlur = 8;
        ctx.shadowColor = color;

        ctx.stroke();

        ctx.shadowBlur = 0;
      });

      // Moving particles
      particles.forEach((particle) => {
        particle.progress += particle.speed;

        if (particle.progress >= 1) {
          particle.progress = 0;

          particle.connection =
            connections[
              Math.floor(
                Math.random() *
                  connections.length
              )
            ];

          particle.color =
            COLORS[
              Math.floor(
                Math.random() *
                  COLORS.length
              )
            ];
        }

        const [a, b] = particle.connection;

        const start = nodes[a];
        const end = nodes[b];

        const x =
          start.x +
          (end.x - start.x) *
            particle.progress;

        const y =
          start.y +
          (end.y - start.y) *
            particle.progress;

        ctx.beginPath();

        ctx.arc(
          x,
          y,
          particle.size,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = particle.color;

        ctx.shadowBlur = 16;
        ctx.shadowColor = particle.color;

        ctx.fill();

        ctx.shadowBlur = 0;
      });

      // Neural nodes
      nodes.forEach((node, index) => {
        const color =
          COLORS[index % COLORS.length];

        const pulse =
          1 +
          Math.sin(
            time * 0.002 +
              index * 0.9
          ) *
            0.18;

        // Outer glow
        ctx.beginPath();

        ctx.arc(
          node.x,
          node.y,
          12 * pulse,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = `${color}25`;
        ctx.fill();

        // Bright node
        ctx.beginPath();

        ctx.arc(
          node.x,
          node.y,
          4.5 * pulse,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = color;

        ctx.shadowBlur = 20;
        ctx.shadowColor = color;

        ctx.fill();

        ctx.shadowBlur = 0;
      });

      // Central AI core
      const coreX = width * 0.5;
      const coreY = height * 0.48;

      const corePulse =
        1 +
        Math.sin(time * 0.003) * 0.06;

      // Orbit rings
      for (let ring = 3; ring > 0; ring--) {
        ctx.beginPath();

        ctx.arc(
          coreX,
          coreY,
          (42 + ring * 34) *
            corePulse,
          0,
          Math.PI * 2
        );

        ctx.strokeStyle =
          ring === 3
            ? "rgba(122, 167, 255, 0.25)"
            : ring === 2
            ? "rgba(167, 139, 250, 0.35)"
            : "rgba(255, 138, 92, 0.45)";

        ctx.lineWidth = 1.2;
        ctx.stroke();
      }

      // Core
      const coreGradient =
        ctx.createRadialGradient(
          coreX - 10,
          coreY - 10,
          2,
          coreX,
          coreY,
          55 * corePulse
        );

      coreGradient.addColorStop(
        0,
        "#ffffff"
      );

      coreGradient.addColorStop(
        0.2,
        "#ffd6c4"
      );

      coreGradient.addColorStop(
        0.5,
        "#ff8a5c"
      );

      coreGradient.addColorStop(
        0.8,
        "#7a3d2a"
      );

      coreGradient.addColorStop(
        1,
        "rgba(20, 10, 10, 0)"
      );

      ctx.beginPath();

      ctx.arc(
        coreX,
        coreY,
        55 * corePulse,
        0,
        Math.PI * 2
      );

      ctx.fillStyle = coreGradient;

      ctx.shadowBlur = 40;
      ctx.shadowColor =
        "rgba(255, 138, 92, 0.7)";

      ctx.fill();

      ctx.shadowBlur = 0;

      time += 16;

      animationFrame =
        requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrame);
      observer.disconnect();
    };
  }, []);

  return (
    <div className="react-ai-thinking-card">
      <canvas
        ref={canvasRef}
        className="ai-thinking-canvas"
      />

      <div className="ai-card-overlay">
        <span>ENTITY THINKING</span>
      </div>
    </div>
  );
}