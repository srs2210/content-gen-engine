/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-sans)'],
      },
      colors: {
        primary: 'var(--color-primaryColor)',
        secondary: 'var(--color-secondaryColor)',
        alert: 'var(--color-alertColor)',
        warning: 'var(--color-warningColor)',
      },
    },
  },
  plugins: [],
};
