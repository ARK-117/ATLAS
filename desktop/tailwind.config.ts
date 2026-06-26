import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        atlas: {
          void: "#05070A",
          deck: "#0B0F14",
          panel: "#111820",
          panelSoft: "#15151B",
          line: "#273241",
          cyan: "#30D5E8",
          blue: "#3B82F6",
          violet: "#8B5CF6",
          amber: "#F5B84B",
          green: "#36D399",
          red: "#F05C5C",
          text: "#E6EDF3",
          muted: "#8D99A6"
        }
      },
      fontFamily: {
        sans: ["Inter", "Sora", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Cascadia Mono", "Consolas", "monospace"]
      },
      boxShadow: {
        glow: "0 0 24px rgba(48, 213, 232, 0.16)"
      }
    }
  },
  plugins: []
} satisfies Config;
