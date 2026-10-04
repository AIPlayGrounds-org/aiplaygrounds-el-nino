import { configuredSiteUrl } from '../utils/site'

export default defineEventHandler((event) => {
  setResponseHeader(event, 'content-type', 'text/plain; charset=utf-8')
  return `User-agent: *\nAllow: /\nSitemap: ${configuredSiteUrl('/sitemap.xml')}\n`
})
