import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { viteSingleFile } from 'vite-plugin-singlefile'

// GitHub Pages публикует сайт по адресу https://<user>.github.io/<repo>/
const base = process.env.APP_BASE ?? '/lazer/'

// Сборка в один HTML-файл: открывается с диска, без сервера и Service Worker.
const singleFile = process.env.SINGLE_FILE === '1'

export default defineConfig({
  base: singleFile ? './' : base,
  build: singleFile
    ? {
        outDir: 'dist-single',
        assetsInlineLimit: 100_000_000,
        cssCodeSplit: false,
        // iife вместо ES-модуля: браузер выполняет скрипт даже при открытии файла с диска.
        rollupOptions: { output: { format: 'iife', inlineDynamicImports: true } },
      }
    : {},
  plugins: [
    react(),
    VitePWA({
      disable: singleFile,
      registerType: 'autoUpdate',
      includeAssets: ['icons/apple-touch-icon.png', 'icons/favicon.svg'],
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        cleanupOutdatedCaches: true,
      },
      manifest: {
        name: 'Ninja AF400EU — кулинарная книга Натальи',
        short_name: 'Ninja Наталья',
        description:
          'Инструкция, таблицы приготовления и рецепты для аэрогриля Ninja Foodi MAX Dual Zone AF400EU на русском языке',
        lang: 'ru',
        dir: 'ltr',
        start_url: base,
        scope: base,
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#fdf7f0',
        theme_color: '#b3541e',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          {
            src: 'icons/icon-512-maskable.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
    }),
    ...(singleFile
      ? [
          viteSingleFile(),
          {
            name: 'strip-module-type',
            enforce: 'post' as const,
            transformIndexHtml(html: string) {
              return html
                .replace(/<script type="module"/g, '<script')
                .replace(/\s*<link rel="[^"]*icon[^"]*"[^>]*>/g, '')
            },
          },
        ]
      : []),
  ],
})
