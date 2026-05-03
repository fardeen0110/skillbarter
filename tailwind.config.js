/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#6366F1",
        accent: "#10B981",
        ink: "#0F172A",
        canvas: "#F8FAFC",
        panel: "#FFFFFF",
        mist: "#EEF2FF",
        peach: "#FEF3C7",
        mint: "#D1FAE5",
        coral: "#FCA5A5",
        sky: "#BAE6FD",
        gold: "#FDE68A",
      },
      boxShadow: {
        glow: "0 25px 60px rgba(15, 23, 42, 0.14)",
        premium: "0 20px 60px rgba(15, 23, 42, 0.10)",
        float: "0 28px 80px rgba(15, 23, 42, 0.18)",
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["Manrope", "sans-serif"],
      },
      backgroundImage: {
        aurora:
          "radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 28%), radial-gradient(circle at top right, rgba(16,185,129,0.16), transparent 32%), radial-gradient(circle at bottom center, rgba(14,165,233,0.12), transparent 30%)",
        spotlight:
          "linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(255,255,255,0) 45%), linear-gradient(225deg, rgba(16,185,129,0.14) 0%, rgba(255,255,255,0) 45%)",
      },
    },
  },
  plugins: [],
};
