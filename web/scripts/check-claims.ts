import { readdir, readFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import * as ts from 'typescript'
import { parseClaims } from './claim-registry'
import { renderClaims } from './generate-claims'

export type ClaimCheckResult = {
  claimIds: string[]
  errors: string[]
}

type AppSource = { fileName: string; source: string }

const claimCallIds = (source: string, fileName: string): string[] => {
  const file = ts.createSourceFile(fileName, source, ts.ScriptTarget.Latest, true)
  const ids: string[] = []
  const visit = (node: ts.Node) => {
    if (
      ts.isCallExpression(node) &&
      ts.isIdentifier(node.expression) &&
      node.expression.text === 'claim' &&
      node.arguments.length === 1 &&
      ts.isStringLiteral(node.arguments[0])
    ) {
      ids.push(node.arguments[0].text)
    }
    ts.forEachChild(node, visit)
  }
  visit(file)
  return ids
}

const templateClaimIds = (source: string): string[] => {
  const ids: string[] = []
  const callPattern = /\bclaim\(\s*(['"])([^'"]+)\1\s*\)/gu
  for (const match of source.matchAll(callPattern)) ids.push(match[2])
  return ids
}

const appClaimIds = (sources: AppSource[]): string[] =>
  sources.flatMap(({ fileName, source }) => {
    if (!fileName.endsWith('.vue')) return claimCallIds(source, fileName)
    const scriptSources = source.match(/<script(?:\s[^>]*)?>[\s\S]*?<\/script>/gu) ?? []
    return [
      ...scriptSources.flatMap((block) =>
        claimCallIds(block.replace(/^<script(?:\s[^>]*)?>|<\/script>$/gu, ''), fileName),
      ),
      ...templateClaimIds(source),
    ]
  })

const storyClaimIds = (source: string): string[] => {
  const ids: string[] = []
  const linkPattern = /\[([a-z0-9-]+)\]\(\.\.\/evidence\/claims\.toml\)/gu
  for (const match of source.matchAll(linkPattern)) ids.push(match[1])
  return ids
}

const validateClaimIds = (registryText: string, claimIds: string[]): ClaimCheckResult => {
  const claims = parseClaims(registryText)
  const byId = new Map(claims.map((claim) => [claim.id, claim]))
  const uniqueIds = [...new Set(claimIds)]
  const errors = uniqueIds.flatMap((id) => {
    const claim = byId.get(id)
    if (!claim) return [`claim id is unknown: ${id}`]
    if (claim.status !== 'verified') return [`claim id is not verified: ${id}`]
    return []
  })
  return { claimIds: uniqueIds, errors }
}

const generatedClaimMap = (source: string): Map<string, string> | null => {
  const file = ts.createSourceFile('claims.ts', source, ts.ScriptTarget.Latest, true)
  let result: Map<string, string> | null = null
  const visit = (node: ts.Node) => {
    if (
      ts.isVariableDeclaration(node) &&
      ts.isIdentifier(node.name) &&
      node.name.text === 'verifiedClaims'
    ) {
      const initializer = node.initializer
      const object =
        initializer && ts.isAsExpression(initializer) ? initializer.expression : initializer
      if (!object || !ts.isObjectLiteralExpression(object)) return
      const claims = new Map<string, string>()
      for (const property of object.properties) {
        if (!ts.isPropertyAssignment(property)) return
        const key = property.name
        const id =
          ts.isStringLiteral(key) || ts.isIdentifier(key) || ts.isNumericLiteral(key)
            ? key.text
            : null
        const value = property.initializer
        if (!id || !ts.isStringLiteral(value)) return
        claims.set(id, value.text)
      }
      result = claims
    }
    ts.forEachChild(node, visit)
  }
  visit(file)
  return result
}

const generatedClaimsMatchRegistry = (registryText: string, generatedSource: string): boolean => {
  const expected = new Map(
    parseClaims(registryText)
      .filter((claim) => claim.status === 'verified')
      .map((claim) => [claim.id, claim.claimEs]),
  )
  const actual = generatedClaimMap(generatedSource)
  if (!actual || actual.size !== expected.size) return false
  return [...expected].every(([id, text]) => actual.get(id) === text)
}

export const checkClaims = (
  registryText: string,
  appSources: AppSource[],
  story: string,
  generatedSource?: string,
) => {
  const result = validateClaimIds(registryText, [
    ...appClaimIds(appSources),
    ...storyClaimIds(story),
  ])
  if (
    generatedSource !== undefined &&
    !generatedClaimsMatchRegistry(registryText, generatedSource)
  ) {
    result.errors.push('generated claims differ from registry')
  }
  return result
}

const sourceFiles = async (directory: string): Promise<string[]> => {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(
    entries.map((entry) => {
      const path = join(directory, entry.name)
      if (entry.isDirectory()) return sourceFiles(path)
      return /\.(ts|vue)$/u.test(entry.name) ? [path] : []
    }),
  )
  return nested.flat(2)
}

type SiteSources = {
  registry?: string
  appSources?: AppSource[]
  story?: string
  generatedClaims?: string
}

export const checkSiteClaims = async (fixtures?: SiteSources) => {
  const root = process.cwd()
  const registry =
    fixtures?.registry ?? (await readFile(resolve(root, '../evidence/claims.toml'), 'utf8'))
  const appSources =
    fixtures?.appSources ??
    (await Promise.all(
      (await sourceFiles(join(root, 'app'))).map(async (fileName) => ({
        fileName,
        source: await readFile(fileName, 'utf8'),
      })),
    ))
  const story = fixtures?.story ?? (await readFile(resolve(root, '../docs/story.md'), 'utf8'))
  const generatedClaims =
    fixtures?.generatedClaims ??
    (fixtures?.registry
      ? renderClaims(registry)
      : await readFile(resolve(root, 'app/data/claims.ts'), 'utf8'))
  return checkClaims(registry, appSources, story, generatedClaims)
}

if (import.meta.main) {
  const result = await checkSiteClaims()
  if (result.errors.length) {
    for (const error of result.errors) console.error(error)
    process.exitCode = 1
  } else {
    console.log(`claim check passed: ${result.claimIds.length} verified claim ids`)
  }
}
