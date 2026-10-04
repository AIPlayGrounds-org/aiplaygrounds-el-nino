import { resolve } from 'node:path'
import { normalizeBasePath } from '../shared/site'

type RouteBudget = {
  payloadBytes: number
  entryJsBytes: number
}

type Budget = {
  margin: number
  routes: Record<string, RouteBudget>
}

const root = resolve(import.meta.dir, '../.output/public')
const basePath = normalizeBasePath(process.env.PAGES_BASE_URL || '/')
const budget = (await Bun.file(
  resolve(import.meta.dir, '../performance-budget.json'),
).json()) as Budget

function routeDirectory(route: string): string {
  return route === '/' ? root : resolve(root, route.slice(1))
}

async function size(path: string): Promise<number> {
  const file = Bun.file(path)
  if (!(await file.exists())) throw new Error(`Missing generated file: ${path}`)
  return file.size
}

async function entryJsBytes(html: string): Promise<number> {
  const sources = [...html.matchAll(/<script\b[^>]*\s+src\s*=\s*["']([^"']+)["']/gi)].map(
    (match) => match[1]!,
  )
  const files = new Set<string>()
  for (const source of sources) {
    const assetPath = new URL(source, 'https://wawapacha.invalid').pathname
    if (!assetPath.startsWith(basePath)) {
      throw new Error(`Generated asset is outside PAGES_BASE_URL: ${source}`)
    }
    const relativePath = assetPath.slice(basePath.length)
    const file = resolve(root, relativePath)
    if (!(await Bun.file(file).exists())) {
      throw new Error(`Missing generated JavaScript asset referenced by HTML: ${source}`)
    }
    files.add(file)
  }
  return (await Promise.all([...files].map(size))).reduce((total, bytes) => total + bytes, 0)
}

let failed = false
for (const [route, expected] of Object.entries(budget.routes)) {
  const directory = routeDirectory(route)
  const htmlPath = resolve(directory, 'index.html')
  const html = await Bun.file(htmlPath).text()
  const payloadBytes = await size(resolve(directory, '_payload.json'))
  const jsBytes = await entryJsBytes(html)
  const payloadLimit = Math.ceil(expected.payloadBytes * (1 + budget.margin))
  const jsLimit = Math.ceil(expected.entryJsBytes * (1 + budget.margin))
  const payloadStatus = payloadBytes <= payloadLimit ? 'ok' : 'FAIL'
  const jsStatus = jsBytes <= jsLimit ? 'ok' : 'FAIL'
  console.log(
    `${route} payload=${payloadBytes}/${payloadLimit} ${payloadStatus} entry-js=${jsBytes}/${jsLimit} ${jsStatus}`,
  )
  if (payloadStatus === 'FAIL' || jsStatus === 'FAIL') failed = true
}

if (failed) process.exit(1)
