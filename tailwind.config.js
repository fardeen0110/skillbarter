/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#eef4ff",
        peach: "#ffedd5",
        mint: "#dcfce7",
        coral: "#fb7185",
        sky: "#38bdf8",
        gold: "#f59e0b",
      },
      boxShadow: {
        glow: "0 25px 60px rgba(15, 23, 42, 0.14)",
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["Manrope", "sans-serif"],
      },
      backgroundImage: {
        mesh: "radial-gradient(circle at top left, rgba(56,189,248,0.24), transparent 30%), radial-gradient(circle at top right, rgba(251,113,133,0.2), transparent 32%), radial-gradient(circle at bottom center, rgba(245,158,11,0.18), transparent 28%)",
      },
    },
  },
  plugins: [],
};
