import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
// PWA 비활성화 — 나중에 다시 활성화 가능
// import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 3002,
    proxy: {
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        cookiePathRewrite: '/'
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
