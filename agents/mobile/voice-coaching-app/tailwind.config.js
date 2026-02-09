/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#4F46E5", // Indigo 600
          light: "#818CF8", // Indigo 400
          dark: "#3730A3", // Indigo 800
        },
        secondary: {
          DEFAULT: "#EC4899", // Pink 500
          light: "#F472B6", // Pink 400
          dark: "#DB2777", // Pink 600
        },
        background: "#0F172A", // Slate 900
        surface: "#1E293B", // Slate 800
        text: {
          primary: "#F8FAFC", // Slate 50
          secondary: "#94A3B8", // Slate 400
          muted: "#64748B", // Slate 500
        },
        accent: "#22D3EE", // Cyan 400
      },
      fontFamily: {
        sans: ["System"], // Use system font for now, can add custom fonts later
      },
    },
  },
  plugins: [],
}
