/** Static Tailwind build config — mirrors the former cdn.tailwindcss.com runtime config. */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './guides/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        zinc: {
          950: '#09090B',
          900: '#18181B',
          850: '#1F1F23',
          800: '#27272A'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace']
      }
    }
  },
  corePlugins: {
    preflight: true
  },
  plugins: []
};
