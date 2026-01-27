import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#fff5f7',
        surface: '#ffffff',
        border: '#fce7f3',
        accent: '#ec4899',
        'accent-light': '#f472b6',
        'pink-soft': '#fce7f3',
        green: '#10b981',
        amber: '#f59e0b',
      },
    },
  },
  plugins: [],
};

export default config;
