import { siteUrl } from '#shared/site'
import { useRuntimeConfig } from '#imports'

export function configuredSiteUrl(path: string): string {
  const config = useRuntimeConfig()
  const publicConfig = config.public as { siteOrigin?: string }
  const appConfig = config.app as { baseURL?: string }
  if (!publicConfig.siteOrigin) {
    throw new Error('runtimeConfig.public.siteOrigin is required')
  }
  return siteUrl(publicConfig.siteOrigin, appConfig.baseURL || '/', path)
}
