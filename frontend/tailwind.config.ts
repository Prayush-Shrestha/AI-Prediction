import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B1220",
        card: "#111827",
        surface: "#172033",
        accent: "#3B82F6",
        up: "#22C55E",
        down: "#EF4444",
        body: "#F8FAFC",
        muted: "#94A3B8",
        line: "#243044",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
