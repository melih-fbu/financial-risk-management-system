/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        gold: '#d4a017',
        silver: '#8f9bb3',
        mist: '#eef4ff',
      },
      boxShadow: {
        soft: '0 24px 60px rgba(15, 23, 42, 0.12)',
      },
      backgroundImage: {
        halo:
          'radial-gradient(circle at top left, rgba(212, 160, 23, 0.18), transparent 34%), radial-gradient(circle at top right, rgba(143, 155, 179, 0.18), transparent 28%), linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%)',
      },
    },
  },
  plugins: [],
}
