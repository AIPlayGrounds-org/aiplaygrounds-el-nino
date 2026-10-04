import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  htmlAssetReferences,
  manifestJavaScriptFiles,
  type ClientManifest,
} from '../scripts/budget-assets'

describe('budget asset references', () => {
  it('counts modulepreload scripts and stylesheet links without counting data-src', () => {
    const fixture = readFileSync(resolve(process.cwd(), 'test/fixtures/budget.html'), 'utf8')

    expect(htmlAssetReferences(fixture)).toEqual({
      js: [
        '/wawapacha/_nuxt/route.js',
        '/wawapacha/_nuxt/lazy.mjs',
        '/wawapacha/_nuxt/prefetched.js',
        '/wawapacha/_nuxt/entry.js',
      ],
      css: ['/wawapacha/_nuxt/route.css'],
    })
  })

  it('follows dynamic imports and reports a missing manifest key', () => {
    const manifest = {
      'pages/index.vue': {
        resourceType: 'script',
        file: 'page.js',
        imports: ['_shared.js'],
        dynamicImports: ['pages/lazy.vue'],
      },
      '_shared.js': { resourceType: 'script', file: 'shared.js' },
      'pages/lazy.vue': { resourceType: 'script', file: 'lazy.js' },
    } satisfies ClientManifest

    expect(manifestJavaScriptFiles('/', manifest)).toEqual(['page.js', 'shared.js', 'lazy.js'])
    expect(() =>
      manifestJavaScriptFiles('/', {
        ...manifest,
        'pages/index.vue': { ...manifest['pages/index.vue'], imports: ['missing.js'] },
      }),
    ).toThrow('Build manifest is missing missing.js')
  })
})
