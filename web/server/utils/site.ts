import { resolveSiteConfig, siteUrl } from '#shared/site'
import { useRuntimeConfig } from '#imports'

export function configuredSiteUrl(path: string): string {
  const { origin, baseURL } = resolveSiteConfig(useRuntimeConfig())
  return siteUrl(origin, baseURL, path)
}
