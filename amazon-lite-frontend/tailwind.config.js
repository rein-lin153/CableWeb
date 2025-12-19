/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ff9900', // 亚马逊经典橙色，或者你可以改成小米的 #ff6700
        secondary: '#232f3e', // 深色背景
      }
    },
  },
  plugins: [],
}