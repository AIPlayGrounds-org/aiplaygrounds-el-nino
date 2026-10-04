import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { normalizeBasePath } from '../shared/site'
import {
  htmlAssetReferences,
  manifestJavaScriptFiles,
  manifestPageKey,
  type ClientManifest,
} from './budget-assets'

type RouteBudget = {
  payloadBytes: number
  entryJsBytes: number
  cssBytes: number
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

async function manifestPath(): Promise<string> {
  const candidates = [
    resolve(import.meta.dir, '../node_modules/.cache/nuxt/.nuxt/dist/server/client.manifest.mjs'),
    resolve(import.meta.dir, '../.nuxt/dist/server/client.manifest.mjs'),
  ]
  for (const candidate of candidates) {
    if (await Bun.file(candidate).exists()) return candidate
  }
  throw new Error('Nuxt client manifest is missing; run bun run generate first')
}

const clientManifest = (await import(pathToFileURL(await manifestPath()).href))
  .default as ClientManifest

function outputPath(source: string): string {
  const assetPath = new URL(source, 'https://wawapacha.invalid').pathname
  if (!assetPath.startsWith(basePath)) {
    throw new Error(`Generated asset is outside PAGES_BASE_URL: ${source}`)
  }
  const relativePath = assetPath.slice(basePath.length)
  return resolve(root, relativePath)
}

function manifestSource(file: string): string {
  return `${basePath}_nuxt/${file}`
}

async function assetBytes(sources: string[], description: string): Promise<number> {
  const files = new Set<string>()
  for (const source of sources) {
    const file = outputPath(source)
    if (!(await Bun.file(file).exists())) {
      throw new Error(`Missing generated ${description} asset: ${source}`)
    }
    files.add(file)
  }
  return (await Promise.all([...files].map(size))).reduce((total, bytes) => total + bytes, 0)
}

async function routeAssetBytes(route: string, html: string) {
  const references = htmlAssetReferences(html)
  const pageKey = manifestPageKey(route)
  const pageEntry = clientManifest[pageKey]
  if (!pageEntry?.file) throw new Error(`Build manifest entry has no file: ${pageKey}`)
  await assetBytes([manifestSource(pageEntry.file)], 'manifest entry JavaScript')
  const manifestJs = manifestJavaScriptFiles(route, clientManifest).map(manifestSource)
  return {
    js: await assetBytes([...references.js, ...manifestJs], 'JavaScript'),
    css: await assetBytes(references.css, 'CSS linked by HTML'),
  }
}

let failed = false
for (const [route, expected] of Object.entries(budget.routes)) {
  const directory = routeDirectory(route)
  const htmlPath = resolve(directory, 'index.html')
  const html = await Bun.file(htmlPath).text()
  const payloadBytes = await size(resolve(directory, '_payload.json'))
  const { js: jsBytes, css: cssBytes } = await routeAssetBytes(route, html)
  const payloadLimit = Math.ceil(expected.payloadBytes * (1 + budget.margin))
  const jsLimit = Math.ceil(expected.entryJsBytes * (1 + budget.margin))
  const cssLimit = Math.ceil(expected.cssBytes * (1 + budget.margin))
  const payloadStatus = payloadBytes <= payloadLimit ? 'ok' : 'FAIL'
  const jsStatus = jsBytes <= jsLimit ? 'ok' : 'FAIL'
  const cssStatus = cssBytes <= cssLimit ? 'ok' : 'FAIL'
  console.log(
    `${route} payload=${payloadBytes}/${payloadLimit} ${payloadStatus} ` +
      `entry-js=${jsBytes}/${jsLimit} ${jsStatus} css=${cssBytes}/${cssLimit} ${cssStatus}`,
  )
  if (payloadStatus === 'FAIL' || jsStatus === 'FAIL' || cssStatus === 'FAIL') failed = true
}

if (failed) process.exit(1)
