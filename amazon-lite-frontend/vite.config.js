import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig({
  plugins: [vue(), basicSsl()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: true,
    proxy: {
      // 1. 原有的 API 代理
      '/api': {
        target: 'https://192.168.1.76:8000', // 注意：如果你后端开了HTTPS，这里要是 https
        changeOrigin: true,
        secure: false, // 关键：如果是自签名证书，必须设为 false
      },
      // 2. 【新增】静态资源代理
      '/static': {
        target: 'https://192.168.1.76:8000', // 指向后端地址
        changeOrigin: true,
        secure: false, // 关键：允许自签名证书
      }
    }
  }
})