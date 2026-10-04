import { publicRoutes } from '#shared/site'
import { configuredSiteUrl } from '../utils/site'

export default defineEventHandler((event) => {
  const urls = publicRoutes
    .map((route) => `  <url><loc>${configuredSiteUrl(route)}</loc></url>`)
    .join('\n')
  setResponseHeader(event, 'content-type', 'application/xml; charset=utf-8')
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`
})
