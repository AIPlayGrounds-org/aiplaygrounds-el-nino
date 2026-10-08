import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { datasetIdsSource, recordTypes } from '../scripts/dataset-ids'
import { datasetIds, staleAfterHours } from '~/types/dataset'
import catalog from '~/data/source-catalog.json'

const schema = JSON.parse(
  readFileSync(resolve(process.cwd(), '../schema/dataset.schema.json'), 'utf8'),
)

const oneRule = {
  ...schema,
  allOf: schema.allOf.filter(
    (rule: { if: { properties: { id: { const: string } } } }) =>
      rule.if.properties.id.const === 'noaa-cpc-oni',
  ),
}

describe('dataset ids', () => {
  it('lists every source of the generated catalog', () => {
    expect([...datasetIds]).toEqual(catalog.sources.map((source) => source.id))
  })

  it('names the record type the schema assigns to each source', () => {
    expect(recordTypes(schema, [...datasetIds])).toMatchObject({
      'noaa-cpc-oni': 'OniRecord',
      'noaa-oisst': 'GridRecord',
    })
  })

  it('falls back to the generic record for a source the schema does not map', () => {
    expect(recordTypes(oneRule, ['noaa-cpc-oni', 'new-source'])).toEqual({
      'noaa-cpc-oni': 'OniRecord',
      'new-source': 'DatasetRecord',
    })
  })

  it('rejects a schema rule for an id the catalog does not list', () => {
    expect(() => recordTypes(oneRule, ['new-source'])).toThrow(/not in the source catalog/)
  })

  it('writes the ids, the record map and the tolerances of automatic sources only', () => {
    const source = datasetIdsSource({ $defs: {} }, [
      { id: 'daily-source', stale_after_hours: 52 },
      { id: 'hand' },
    ])

    expect(source).toContain("  'daily-source',\n  'hand',\n] as const")
    expect(source).toContain("  'daily-source': DatasetRecord\n  hand: DatasetRecord\n")
    expect(source).toContain("{\n  'daily-source': 52,\n}")
  })

  it('takes the tolerances from the catalog', () => {
    const expected = Object.fromEntries(
      catalog.sources
        .filter((source) => 'stale_after_hours' in source)
        .map((source) => [source.id, (source as { stale_after_hours: number }).stale_after_hours]),
    )

    expect(staleAfterHours).toEqual(expected)
  })
})
