export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      siteOrigin: 'https://aiplaygrounds-org.github.io',
    },
  },
  // Obsidian's presentation plugin uses port 3000.
  // Use 3100 here so localhost opens the site instead of Obsidian.
  devServer: { port: 3100 },
  app: {
    // GitHub Pages supplies a repository subpath through the deploy workflow.
    // Local development uses the domain root.
    baseURL: process.env.PAGES_BASE_URL || '/',
    head: {
      htmlAttrs: { lang: 'es' },
    },
  },
  nitro: {
    prerender: {
      routes: ['/sitemap.xml', '/robots.txt'],
    },
  },
})
