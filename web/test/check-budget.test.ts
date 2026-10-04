import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { htmlAssetReferences } from '../scripts/budget-assets'

describe('budget asset references', () => {
  it('counts modulepreload scripts and stylesheet links without counting data-src', () => {
    const fixture = readFileSync(resolve(process.cwd(), 'test/fixtures/budget.html'), 'utf8')

    expect(htmlAssetReferences(fixture)).toEqual({
      js: ['/wawapacha/_nuxt/route.js', '/wawapacha/_nuxt/lazy.js', '/wawapacha/_nuxt/entry.js'],
      css: ['/wawapacha/_nuxt/route.css'],
    })
  })
})
