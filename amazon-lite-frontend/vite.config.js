import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'
import { fileURLToPath, URL } from 'node:url' // <--- 1. 引入这个

export default defineConfig({
  plugins: [vue(), basicSsl()],
  
  // 2. 添加 resolve 配置
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  server: {
    host: '0.0.0.0',
    port: 5173,
    https: true,
    proxy: {
      '/api': {
        target: 'https://192.168.1.76:8000',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'https://192.168.1.76:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})