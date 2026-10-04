import { siteUrl, socialImagePath } from '#shared/site'
import { useHead, useRoute, useRuntimeConfig, useSeoMeta } from '#imports'

type SiteSeo = {
  title: string
  description: string
}

export function useSiteSeo({ title, description }: SiteSeo) {
  const route = useRoute()
  const config = useRuntimeConfig()
  const publicConfig = config.public as { siteOrigin?: string }
  const appConfig = config.app as { baseURL?: string }
  const origin = publicConfig.siteOrigin || 'https://aiplaygrounds-org.github.io'
  const baseURL = appConfig.baseURL || '/'
  const canonical = siteUrl(origin, baseURL, route.path)
  const image = siteUrl(origin, baseURL, socialImagePath)

  useSeoMeta({
    title,
    description,
    ogTitle: title,
    ogDescription: description,
    ogType: 'website',
    ogUrl: canonical,
    ogImage: image,
    twitterCard: 'summary_large_image',
    twitterTitle: title,
    twitterDescription: description,
    twitterImage: image,
  })
  useHead({
    link: [{ rel: 'canonical', href: canonical }],
  })
}
