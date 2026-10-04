import { resolve } from 'node:path'
import { publicRoutes, siteUrl } from '../shared/site'

const output = resolve(import.meta.dir, '../.output/public')
const origin = process.env.SITE_ORIGIN || 'https://aiplaygrounds-org.github.io'
const baseURL = process.env.PAGES_BASE_URL || '/'
const htmlPath = (route: string) =>
  resolve(output, route === '/' ? 'index.html' : `${route.slice(1)}/index.html`)

function has(html: string, pattern: RegExp, label: string, route: string) {
  if (!pattern.test(html)) throw new Error(`${route}: missing ${label}`)
}

if (!(await Bun.file(resolve(output, 'og-image.svg')).exists())) {
  throw new Error('Missing generated static social image: og-image.svg')
}

for (const route of publicRoutes) {
  const html = await Bun.file(htmlPath(route)).text()
  has(html, /<html[^>]+lang="es"/, 'lang=es', route)
  has(html, /<title>[^<]+<\/title>/, 'title', route)
  has(html, /<meta name="description" content="[^"]+"/, 'description', route)
  has(html, /<meta property="og:title" content="[^"]+"/, 'Open Graph title', route)
  has(html, /<meta property="og:description" content="[^"]+"/, 'Open Graph description', route)
  has(html, /<meta property="og:image" content="[^"]+og-image\.svg"/, 'Open Graph image', route)
  has(html, /<meta name="twitter:card" content="summary_large_image"/, 'Twitter card', route)
  has(html, /<meta name="twitter:title" content="[^"]+"/, 'Twitter title', route)
  has(html, /<meta name="twitter:description" content="[^"]+"/, 'Twitter description', route)
  has(html, /<meta name="twitter:image" content="[^"]+og-image\.svg"/, 'Twitter image', route)
  has(
    html,
    new RegExp(`<link rel="canonical" href="${siteUrl(origin, baseURL, route)}"`),
    'canonical URL',
    route,
  )
  console.log(`${route} SEO metadata ok`)
}
