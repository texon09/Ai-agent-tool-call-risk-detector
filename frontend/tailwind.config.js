/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: {
          DEFAULT: "var(--surface)",
          2: "var(--surface-2)",
          3: "var(--surface-3)",
        },
        border: {
          DEFAULT: "var(--border)",
          str: "var(--border-str)",
        },
        text: {
          DEFAULT: "var(--text)",
          muted: "var(--text-muted)",
          dim: "var(--text-dim)",
        },
        allow: {
          DEFAULT: "var(--allow)",
          bg: "var(--allow-bg)",
        },
        confirm: {
          DEFAULT: "var(--confirm)",
          bg: "var(--confirm-bg)",
        },
        revise: {
          DEFAULT: "var(--revise)",
          bg: "var(--revise-bg)",
        },
        block: {
          DEFAULT: "var(--block)",
          bg: "var(--block-bg)",
        },
        brand: {
          DEFAULT: "var(--brand)",
          hover: "var(--brand-hover)",
          glow: "var(--brand-glow)",
          text: "var(--brand-text)",
        },
        panel: {
          accent: "var(--panel-accent)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
