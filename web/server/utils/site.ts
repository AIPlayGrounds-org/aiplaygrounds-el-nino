import { normalizeBasePath, publicRoutes, siteUrl, socialImagePath } from '#shared/site'
import { useRuntimeConfig } from '#imports'

export { normalizeBasePath, publicRoutes, siteUrl, socialImagePath }

export function configuredSiteUrl(path: string): string {
  const config = useRuntimeConfig()
  const publicConfig = config.public as { siteOrigin?: string }
  const appConfig = config.app as { baseURL?: string }
  return siteUrl(
    publicConfig.siteOrigin || 'https://aiplaygrounds-org.github.io',
    appConfig.baseURL || '/',
    path,
  )
}
