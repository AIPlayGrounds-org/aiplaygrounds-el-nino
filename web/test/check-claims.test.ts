import { describe, expect, it } from 'vitest'
import { parseClaims } from '../scripts/claim-registry'
import { checkSiteClaims } from '../scripts/check-claims'
import { renderClaims } from '../scripts/generate-claims'

const escapedQuote = String.fromCharCode(92)
const registry = `
[[claim]]
id = "verified-id"
claim_es = "Una afirmación verificada con ${escapedQuote}"comillas${escapedQuote}"."
status = "verified"

[[claim]]
id = "pending-id"
claim_es = "Afirmación pendiente"
status = "pending"

[[claim]]
id = "multiline-id"
claim_es = """
Una afirmación
en varias líneas.
"""
status = "verified"
`

const site = (source: string, registryText = registry, story = '') =>
  checkSiteClaims({
    registry: registryText,
    appSources: [{ fileName: 'messages.ts', source }],
    story,
  })

describe('claim check', () => {
  it('runs the real site check entry point', async () => {
    expect((await checkSiteClaims()).errors).toEqual([])
  })

  it('rejects an unknown claim id', async () => {
    const result = await site("import { claim } from './claims'; claim('missing-id')")
    expect(result.errors).toEqual(['claim id is unknown: missing-id'])
  })

  it('rejects an unverified claim id', async () => {
    const result = await site("import { claim } from './claims'; claim('pending-id')")
    expect(result.errors).toEqual(['claim id is not verified: pending-id'])
  })

  it('rejects an unknown claim id in a Vue template', async () => {
    const result = await checkSiteClaims({
      registry,
      appSources: [
        { fileName: 'component.vue', source: "<template>{{ claim('missing-id') }}</template>" },
      ],
      story: '',
    })
    expect(result.errors).toEqual(['claim id is unknown: missing-id'])
  })

  it('accepts a verified claim id', async () => {
    const result = await site("import { claim } from './claims'; claim('verified-id')")
    expect(result).toEqual({ claimIds: ['verified-id'], errors: [] })
  })

  it('rejects a generated module that is stale after the registry changes', async () => {
    const generated = renderClaims(registry)
    const editedRegistry = registry.replace(
      'Una afirmación verificada',
      'Una afirmación actualizada',
    )
    const result = await site('', editedRegistry, '')
    const staleResult = await checkSiteClaims({
      registry: editedRegistry,
      appSources: [{ fileName: 'messages.ts', source: '' }],
      story: '',
      generatedClaims: generated,
    })

    expect(result.errors).toEqual([])
    expect(staleResult.errors).toEqual(['generated claims differ from registry'])
  })

  it('parses escaped quotes and multi-line claim_es values', async () => {
    expect(parseClaims(registry)).toEqual([
      {
        id: 'verified-id',
        claimEs: 'Una afirmación verificada con "comillas".',
        status: 'verified',
      },
      { id: 'pending-id', claimEs: 'Afirmación pendiente', status: 'pending' },
      { id: 'multiline-id', claimEs: 'Una afirmación\nen varias líneas.\n', status: 'verified' },
    ])
    const result = await site("import { claim } from './claims'; claim('multiline-id')")
    expect(result.errors).toEqual([])
  })

  it('checks claim ids linked from story.md', async () => {
    const result = await site(
      '',
      registry,
      '[verified-id](../evidence/claims.toml)\n[missing-id](../evidence/claims.toml)',
    )
    expect(result.errors).toEqual(['claim id is unknown: missing-id'])
  })
})
