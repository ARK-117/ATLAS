import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        atlas: {
          void: "#080A0D",
          deck: "#0D1117",
          panel: "#11161D",
          panelSoft: "#171D26",
          line: "#29313D",
          cyan: "#5BA7C8",
          blue: "#4F7FB8",
          violet: "#6F6A8F",
          amber: "#C99945",
          green: "#5BAE78",
          red: "#D35F5F",
          text: "#E7ECF2",
          muted: "#9AA4B2"
        }
      },
      fontFamily: {
        sans: ["Inter", "Sora", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Cascadia Mono", "Consolas", "monospace"]
      },
      boxShadow: {
        glow: "0 10px 28px rgba(0, 0, 0, 0.24)"
      }
    }
  },
  plugins: []
} satisfies Config;
