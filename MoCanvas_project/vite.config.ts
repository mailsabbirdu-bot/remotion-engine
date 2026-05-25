import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';

export default defineConfig({
  plugins: [
    (motionCanvas as any).default(),
  ],
  base: './',
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true,
  },
  build: {
    rollupOptions: {
        input: 'index.html',
    }
  }
});
