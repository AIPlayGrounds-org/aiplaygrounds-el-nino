import { resolve } from 'node:path'
import { normalizeBasePath, publicRoutes } from '../shared/site'

const output = resolve(import.meta.dir, '../.output/public')
const basePath = normalizeBasePath(process.env.PAGES_BASE_URL || '/')
const htmlPath = (route: string) =>
  resolve(output, route === '/' ? 'index.html' : `${route.slice(1)}/index.html`)

function attribute(html: string, pattern: RegExp, label: string, route: string): string {
  const value = pattern.exec(html)?.[1]
  if (!value) throw new Error(`${route}: missing ${label}`)
  return value
}

function routePath(route: string): string {
  return `${basePath}${route === '/' ? '' : route.slice(1)}`
}

function urlPath(value: string, label: string): string {
  try {
    return new URL(value).pathname
  } catch {
    throw new Error(`Invalid ${label} URL: ${value}`)
  }
}

function assertEqual(actual: string, expected: string, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${expected}, got ${actual}`)
}

for (const asset of ['og-image.svg', 'sitemap.xml', 'robots.txt']) {
  if (!(await Bun.file(resolve(output, asset)).exists())) {
    throw new Error(`Missing generated static SEO asset: ${asset}`)
  }
}

const sitemap = await Bun.file(resolve(output, 'sitemap.xml')).text()
const sitemapPaths = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) =>
  urlPath(match[1]!, 'sitemap location'),
)
assertEqual(
  JSON.stringify(sitemapPaths),
  JSON.stringify(publicRoutes.map(routePath)),
  'sitemap routes',
)

const robots = await Bun.file(resolve(output, 'robots.txt')).text()
const robotsSitemap = robots.match(/^Sitemap: (.+)$/m)?.[1]
if (!robotsSitemap) throw new Error('robots.txt: missing Sitemap directive')
assertEqual(
  urlPath(robotsSitemap, 'robots sitemap'),
  routePath('/sitemap.xml'),
  'robots sitemap path',
)

for (const route of publicRoutes) {
  const html = await Bun.file(htmlPath(route)).text()
  const language = attribute(html, /<html[^>]+lang="([^"]+)"/, 'lang=es', route)
  assertEqual(language, 'es', `${route} lang`)
  attribute(html, /<title>([^<]+)<\/title>/, 'title', route)
  attribute(html, /<meta name="description" content="([^"]+)"/, 'description', route)
  attribute(html, /<meta property="og:title" content="([^"]+)"/, 'Open Graph title', route)
  attribute(
    html,
    /<meta property="og:description" content="([^"]+)"/,
    'Open Graph description',
    route,
  )
  const image = attribute(
    html,
    /<meta property="og:image" content="([^"]+)"/,
    'Open Graph image',
    route,
  )
  assertEqual(
    urlPath(image, 'Open Graph image'),
    routePath('/og-image.svg'),
    `${route} Open Graph image path`,
  )
  attribute(html, /<meta name="twitter:card" content="([^"]+)"/, 'Twitter card', route)
  attribute(html, /<meta name="twitter:title" content="([^"]+)"/, 'Twitter title', route)
  attribute(
    html,
    /<meta name="twitter:description" content="([^"]+)"/,
    'Twitter description',
    route,
  )
  attribute(html, /<meta name="twitter:image" content="([^"]+)"/, 'Twitter image', route)
  const canonical = attribute(html, /<link rel="canonical" href="([^"]+)"/, 'canonical URL', route)
  assertEqual(urlPath(canonical, 'canonical'), routePath(route), `${route} canonical path`)
  console.log(`${route} SEO metadata ok`)
}
