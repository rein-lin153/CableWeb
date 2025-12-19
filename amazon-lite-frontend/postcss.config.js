// postcss.config.js
export default {
  plugins: {
    // 1. 必须放在 tailwindcss 之前
    'tailwindcss/nesting': {}, 
    
    // 2. Tailwind 插件
    tailwindcss: {},
    
    // 3. 自动添加浏览器前缀
    autoprefixer: {},
  },
}