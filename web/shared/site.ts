export const publicRoutes = [
  '/',
  '/territorio',
  '/historico',
  '/rios',
  '/aprende',
  '/metodologia',
] as const

export const socialImagePath = '/og-image.png'

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
