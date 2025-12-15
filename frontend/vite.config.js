import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        // 开发环境：使用 localhost（通过 Vite 代理）
        // 生产环境：前端会直接请求配置的 API 地址（不经过代理）
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  // 生产环境构建配置
  build: {
    // 确保不会在构建时暴露敏感信息
    sourcemap: false, // 生产环境建议关闭 sourcemap
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除 console.log
        drop_debugger: true
      }
    }
  }
})