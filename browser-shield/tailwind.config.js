/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./entrypoints/**/*.{html,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0a0d14",
        surface: "#0c0f17",
        border: "#1e293b",
        primary: "#3b82f6",
        danger: "#ef4444",
        warning: "#f59e0b",
        success: "#10b981"
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}