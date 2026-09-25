/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        crimson: {
          DEFAULT: "#B03052",
          dark: "#8C2440",
        },
        indigo: {
          DEFAULT: "#0F3D68",
        },
        paper: "#FAF8F5",
        ink: "#1E1B18",
        rise: "#1E8E5A",
        fall: "#C13B3B",
      },
      fontFamily: {
        sans: ["-apple-system", "Segoe UI", "Roboto", "Helvetica", "Arial", "sans-serif"],
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(30,27,24,0.06), 0 4px 14px rgba(30,27,24,0.06)",
      },
    },
  },
  plugins: [],
};
