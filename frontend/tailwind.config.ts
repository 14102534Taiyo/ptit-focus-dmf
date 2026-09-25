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
        sovereign: {
          void: "#070C18",
          dark: "#0A1128",
          navy: "#0A192F",
          slate: "#0F172A",
          surface: "#1E293B",
          border: "#334155",
          muted: "#64748B",
        },
        gold: {
          50: "#FFFBEB",
          100: "#FEF3C7",
          300: "#FCD34D",
          500: "#F59E0B",
          600: "#D97706",
          700: "#B45309",
          champagne: "#C5A059",
        },
        petro: {
          gas: "#06B6D4",
          gasDark: "#0891B2",
          cond: "#8B5CF6",
          condDark: "#7C3AED",
          crude: "#F59E0B",
          crudeDark: "#D97706",
          boed: "#10B981",
          boedDark: "#059669",
        }
      },
      fontFamily: {
        display: ["var(--font-display)", "Manrope", "Prompt", "sans-serif"],
        body: ["var(--font-body)", "Inter", "Sarabun", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(10, 25, 47, 0.08), 0 2px 6px 0 rgba(0, 0, 0, 0.03)",
        "glass-hover": "0 16px 40px 0 rgba(10, 25, 47, 0.14), 0 4px 12px 0 rgba(0, 0, 0, 0.05)",
        "gold-glow": "0 0 20px rgba(197, 160, 89, 0.35)",
        "blue-glow": "0 0 24px rgba(2, 132, 199, 0.30)",
      }
    },
  },
  plugins: [],
};

export default config;
