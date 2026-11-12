/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        smartflow: {
          dark: '#0f172a',      // Slate 900
          navy: '#1e293b',      // Slate 800
          card: '#1e293b',
          blue: '#2563eb',      // Royal Blue 600
          accent: '#38bdf8',    // Sky 400
          dmart: '#15803d',     // DMart Forest Green 700
          amazon: '#f59e0b',    // Amazon Amber/Gold 500
          danger: '#ef4444',    // Rose Red
          warning: '#f59e0b',
          success: '#10b981'
        }
      }
    },
  },
  plugins: [],
}
