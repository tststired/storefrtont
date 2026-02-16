import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8002,
    host: '0.0.0.0',
    allowedHosts: [
      'jimmysbigpads.jlkys.com',
      'localhost',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
