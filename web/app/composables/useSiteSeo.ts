import { resolveSiteConfig, siteUrl, socialImagePath } from '#shared/site'
import { useHead, useRoute, useRuntimeConfig, useSeoMeta } from '#imports'

type SiteSeo = {
  title: string
  description: string
  ogDescription?: string
}

export function useSiteSeo({ title, description, ogDescription = description }: SiteSeo) {
  const route = useRoute()
  const { origin, baseURL } = resolveSiteConfig(useRuntimeConfig())
  const canonical = siteUrl(origin, baseURL, route.path)
  const image = siteUrl(origin, baseURL, socialImagePath)

  useSeoMeta({
    title,
    description,
    ogTitle: title,
    ogDescription,
    ogType: 'website',
    ogUrl: canonical,
    ogImage: image,
    twitterCard: 'summary_large_image',
    twitterTitle: title,
    twitterDescription: ogDescription,
    twitterImage: image,
  })
  useHead({
    link: [{ rel: 'canonical', href: canonical }],
  })
}
