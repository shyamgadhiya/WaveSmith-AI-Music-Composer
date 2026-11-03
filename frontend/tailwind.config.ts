import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8F9FE",
        card: "#FFFFFF",
        primary: {
          DEFAULT: "#4F46E5",
          hover: "#4338CA",
          gradientFrom: "#4F46E5",
          gradientTo: "#7C3AED",
        },
        brand: {
          dark: "#0F172A",
          purple: "#6366F1",
          violet: "#7C3AED",
          soft: "#EEF2FF",
        },
      },
      boxShadow: {
        card: "0 10px 30px -5px rgba(99, 102, 241, 0.06), 0 2px 8px -2px rgba(15, 23, 42, 0.04)",
        cardHover: "0 20px 40px -10px rgba(99, 102, 241, 0.12), 0 4px 12px -2px rgba(15, 23, 42, 0.06)",
        glow: "0 4px 20px -2px rgba(99, 102, 241, 0.35)",
        pill: "0 2px 10px rgba(79, 70, 229, 0.2)",
      },
      keyframes: {
        floatNote: {
          "0%, 100%": { transform: "translateY(0px) rotate(0deg)", opacity: "0.4" },
          "50%": { transform: "translateY(-14px) rotate(8deg)", opacity: "0.85" },
        },
        waveRibbon: {
          "0%": { transform: "translateX(0%)" },
          "50%": { transform: "translateX(-2%) scaleY(1.03)" },
          "100%": { transform: "translateX(0%)" },
        },
        equalizerPulse: {
          "0%, 100%": { height: "4px" },
          "50%": { height: "20px" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        floatNote: "floatNote 4s ease-in-out infinite",
        floatNoteSlow: "floatNote 6s ease-in-out infinite",
        waveRibbon: "waveRibbon 12s ease-in-out infinite",
        equalizer: "equalizerPulse 1s ease-in-out infinite",
        shimmer: "shimmer 2.5s infinite linear",
      },
    },
  },
  plugins: [],
};

export default config;
