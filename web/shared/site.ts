export const publicRoutes = [
  '/',
  '/territorio',
  '/historico',
  '/rios',
  '/aprende',
  '/metodologia',
] as const

export const socialImagePath = '/og-image.png'

type RuntimeSiteConfig = {
  public?: { siteOrigin?: string }
  app?: { baseURL?: string }
}

export function resolveSiteConfig(config: RuntimeSiteConfig): {
  origin: string
  baseURL: string
} {
  const origin = config.public?.siteOrigin
  if (!origin) throw new Error('runtimeConfig.public.siteOrigin is required')
  return { origin, baseURL: config.app?.baseURL || '/' }
}

export function normalizeBasePath(baseURL: string): string {
  if (!baseURL || baseURL === '/') return '/'
  const path = baseURL.startsWith('/') ? baseURL : `/${baseURL}`
  return `/${path.replace(/^\/+|\/+$/g, '')}/`
}

export function siteUrl(origin: string, baseURL: string, path: string): string {
  const basePath = normalizeBasePath(baseURL)
  const route = path === '/' ? '' : path.replace(/^\/+/, '')
  return `${origin.replace(/\/$/, '')}${basePath}${route}`
}
