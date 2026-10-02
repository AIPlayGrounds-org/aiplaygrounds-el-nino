// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  // El 3000 lo usa el plugin de presentaciones de Obsidian; con el mismo puerto, localhost abre Obsidian.
  devServer: { port: 3100 },
  app: {
    // En GitHub Pages la web vive en /<nombre-del-repo>/; el workflow de deploy pasa esa ruta. En local, la raíz.
    baseURL: process.env.PAGES_BASE_URL || '/',
    head: {
      htmlAttrs: { lang: 'es' },
    },
  },
})
