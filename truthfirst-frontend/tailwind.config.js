/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#64B5F6',
          DEFAULT: '#2185D0',
          dark: '#1976D2',
        },
        success: '#4CAF50',
        warning: '#FF9800',
        danger: '#F44336',
        neutral: '#757575',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderRadius: {
        card: '10px',
      },
    },
  },
  plugins: [],
}