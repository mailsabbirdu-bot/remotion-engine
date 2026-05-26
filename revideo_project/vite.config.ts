import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';
import path from 'path';

export default defineConfig({
  plugins: [
    (motionCanvas as any).default({
        project: [
            './src/project.ts',
        ]
    }),
  ],
  resolve: {
    dedupe: [
        '@motion-canvas/core',
        '@motion-canvas/2d',
    ],
  },
  build: {
    rollupOptions: {
      input: {
        index: path.resolve(__dirname, 'index.html'),
      },
    },
  },
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
});
