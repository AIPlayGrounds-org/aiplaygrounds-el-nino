import { describe, expect, it } from 'vitest'
import { loadDataset, recomputeEnfenStale, validateDataset } from '../server/utils/loadDataset'
import type { DatasetId } from '~/types/datasets'
import { geometryFixture } from './fixtures/geometry'
import { enfenFixture } from './fixtures/panels'

describe('useDataset', () => {
  it('loads the ONI dataset with its narrowed record fields', async () => {
    const oni = await loadDataset('noaa-cpc-oni')
    expect(oni.id).toBe('noaa-cpc-oni')
    expect(oni.records[0]?.anomaly).toEqual(expect.any(Number))
  })

  it('loads the production geometry dataset with its narrowed record fields', async () => {
    const geometry = await loadDataset('limites-inei-ign')
    expect(geometry.records[0]?.departamentos.type).toBe('FeatureCollection')
    expect(validateDataset('limites-inei-ign', geometryFixture).records[0]?.version).toBe('v01')
  })

  describe('ENFEN staleness', () => {
    const published = async () => (await loadDataset('enfen-communique')).records[0]

    it('recomputes the flag from the build date instead of trusting the published one', async () => {
      const { end } = await published()
      const lastValidDay = new Date(`${end}T23:59:59-05:00`)
      const nextDay = new Date(`${end}T00:00:00-05:00`)
      nextDay.setUTCDate(nextDay.getUTCDate() + 1)

      expect((await loadDataset('enfen-communique', lastValidDay)).records[0].stale).toBe(false)
      expect((await loadDataset('enfen-communique', nextDay)).records[0].stale).toBe(true)
    })

    it('clears a stale flag that no longer applies', () => {
      const flagged = {
        ...enfenFixture,
        records: [{ ...enfenFixture.records[0], stale: true }],
      }

      const current = recomputeEnfenStale(flagged, new Date('2026-10-04T12:00:00-05:00'))

      expect(current.records[0].stale).toBe(false)
      expect(flagged.records[0].stale).toBe(true)
    })

    it('uses the Lima day, not the UTC day', () => {
      // 2026-10-16T02:00Z is still 2026-10-15 in Lima, the last day of the status.
      expect(
        recomputeEnfenStale(enfenFixture, new Date('2026-10-16T02:00:00Z')).records[0].stale,
      ).toBe(false)
      expect(
        recomputeEnfenStale(enfenFixture, new Date('2026-10-16T05:00:00Z')).records[0].stale,
      ).toBe(true)
    })
  })

  it('reports invalid datasets with the file id', () => {
    expect(() => validateDataset('noaa-cpc-oni', { id: 'wrong' })).toThrow(
      '[useDataset] data/noaa-cpc-oni.json is invalid:',
    )
  })

  it.each([
    ['noaa-cpc-oni', 'anomaly'],
    ['limites-inei-ign', 'version'],
    ['noaa-cpc-outlook', 'categories'],
    ['open-meteo-glofas', 'river_discharge'],
    ['enfen-communique', 'status'],
    ['noaa-oisst', 'lat'],
    ['noaa-ersst', 'nino3_anomaly'],
  ] as [Exclude<DatasetId, 'noaa-cpc-nino-weekly'>, string][])(
    'rejects a malformed kind-specific record in %s',
    async (id, field) => {
      const malformed = JSON.parse(JSON.stringify(await loadDataset(id))) as {
        records: Array<Record<string, unknown>>
      }
      delete malformed.records[0]![field]

      expect(() => validateDataset(id, malformed)).toThrow(
        `[useDataset] data/${id}.json is invalid:`,
      )
    },
  )

  it('rejects a malformed weekly Niño record', async () => {
    const malformed = JSON.parse(JSON.stringify(await loadDataset('noaa-cpc-nino-weekly'))) as {
      records: Array<Record<string, unknown>>
    }
    delete malformed.records[0]!.nino_1_2_sst

    expect(() => validateDataset('noaa-cpc-nino-weekly', malformed)).toThrow(
      '[useDataset] data/noaa-cpc-nino-weekly.json is invalid:',
    )
  })
})
