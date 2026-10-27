/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // PitStop vibrant racing orange
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
        workshop: {
          bg: '#0b0f17',
          card: '#131b2a',
          surface: '#1b2538',
          border: '#26344d',
          accent: '#38bdf8', // Neon electric blue
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
          purple: '#a855f7',
        }
      },
      boxShadow: {
        'glow-brand': '0 0 25px -5px rgba(249, 115, 22, 0.4)',
        'glow-accent': '0 0 25px -5px rgba(56, 189, 248, 0.4)',
      }
    },
  },
  plugins: [],
};
