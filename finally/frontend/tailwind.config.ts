import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          background: '#0d1117',
          foreground: '#e6edf3',
        },
      },
    },
  },
  darkMode: 'class',
};

export default config;