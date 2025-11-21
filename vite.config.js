import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import basicSsl from '@vitejs/plugin-basic-ssl';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), basicSsl()],
  server: {
    port: 5173,
    https: true,
    host: true,
    proxy: {
      '/api': {
        target: 'https://192.168.2.96:5000',  // Mudança para HTTPS
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        retry: 3
      }
    },
  },
});