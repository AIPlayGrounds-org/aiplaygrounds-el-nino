export type AssetReferences = {
  js: string[]
  css: string[]
}

type ManifestEntry = {
  resourceType?: string
  file?: string
  imports?: string[]
  dynamicImports?: string[]
}

export type ClientManifest = Record<string, ManifestEntry>

export function manifestPageKey(route: string): string {
  return route === '/' ? 'pages/index.vue' : `pages${route}.vue`
}

function attribute(tag: string, name: string): string | undefined {
  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return tag.match(new RegExp(`(?:^|\\s)${escapedName}\\s*=\\s*["']([^"']*)["']`, 'i'))?.[1]
}

export function htmlAssetReferences(html: string): AssetReferences {
  const js = new Set<string>()
  const css = new Set<string>()

  for (const match of html.matchAll(/<(script|link)\b[^>]*>/gi)) {
    const tag = match[0]!
    const element = match[1]!.toLowerCase()
    if (element === 'script') {
      const source = attribute(tag, 'src')
      if (source) js.add(source)
      continue
    }

    const rel = attribute(tag, 'rel')?.toLowerCase().split(/\s+/) ?? []
    const href = attribute(tag, 'href')
    if (!href) continue
    if (rel.includes('stylesheet')) css.add(href)
    const as = attribute(tag, 'as')?.toLowerCase()
    const isModulePreload = rel.includes('modulepreload')
    const isScriptPrefetch =
      rel.includes('prefetch') && (as === 'script' || (!as && /\.(?:js|mjs)(?:[?#]|$)/i.test(href)))
    if (isModulePreload || isScriptPrefetch) {
      js.add(href)
    }
  }

  return { js: [...js], css: [...css] }
}

export function manifestJavaScriptFiles(route: string, manifest: ClientManifest): string[] {
  const page = manifestPageKey(route)
  const files = new Set<string>()
  const visited = new Set<string>()

  function visit(key: string): void {
    if (visited.has(key)) return
    visited.add(key)
    const entry = manifest[key]
    if (!entry) throw new Error(`Build manifest is missing ${key}`)
    if (entry.resourceType === 'script' && entry.file) files.add(entry.file)
    for (const imported of [...(entry.imports ?? []), ...(entry.dynamicImports ?? [])]) {
      visit(imported)
    }
  }

  visit(page)
  return [...files]
}

export type RouteBudget = {
  payloadBytes: number
  entryJsBytes: number
  cssBytes: number
}

export type Budget = {
  margin: number
  routes: Record<string, RouteBudget>
}

export type RouteCheck = {
  limits: RouteBudget
  failures: (keyof RouteBudget)[]
}

/** Return the inclusive size limits and the measured fields that exceed them. */
export function routeCheck(
  measured: RouteBudget,
  budgeted: RouteBudget,
  margin: number,
): RouteCheck {
  const keys = Object.keys(budgeted) as (keyof RouteBudget)[]
  const limits = Object.fromEntries(
    keys.map((key) => [key, Math.ceil(budgeted[key] * (1 + margin))]),
  ) as RouteBudget
  return { limits, failures: keys.filter((key) => measured[key] > limits[key]) }
}

/** Return a budget whose routes contain the latest measured sizes. */
export function updatedBudget(budget: Budget, measured: Record<string, RouteBudget>): Budget {
  return { margin: budget.margin, routes: measured }
}
