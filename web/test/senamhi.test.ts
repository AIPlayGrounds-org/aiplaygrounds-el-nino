import { describe, expect, it } from 'vitest'
import { shapeSenamhiDataset, stationChartSeries, stationOptions } from '~/utils/senamhi'
import type { DatasetFor } from '~/types/datasets'

const record = (station: string, start: string, precipitation: number | null) => ({
  station,
  region: station === 'a' ? 'ALFA' : 'BETA',
  department: 'PIURA',
  lat: -5,
  lon: -80,
  start,
  end: start,
  precipitation_mm: precipitation,
  precipitation_days: precipitation === null ? 0 : 31,
  tmax_c: 30,
  tmax_days: 31,
  tmin_c: 20,
  tmin_days: 31,
  precipitation_median_mm: 10,
})

const dataset = {
  id: 'senamhi-estaciones',
  source: { institution: 'SENAMHI', product: 'stations', url: 'https://example.test' },
  variable: 'rain',
  unit: 'mm',
  data_type: 'observed',
  spatial_resolution: 'Station point',
  temporal_resolution: 'Monthly',
  ingestion_time: '2026-10-04T00:00:00+00:00',
  processing_version: '0.1.0',
  records: [
    record('a', '1982-01', 30),
    record('a', '1982-02', null),
    record('a', '1997-01', 50),
    record('a', '1997-02', 60),
  ],
} as DatasetFor<'senamhi-estaciones'>

describe('SENAMHI station history shaping', () => {
  it('keeps only the two requested event windows and exposes stations', () => {
    const shaped = shapeSenamhiDataset(dataset)
    expect(shaped.records).toHaveLength(1)
    expect(shaped.records[0]).toMatchObject({ firstYear: 1982, latestYear: 1997 })
    expect(shaped.records[0]?.precipitation).toHaveLength(48)
    expect(stationOptions(shaped.records)).toEqual([
      { code: 'a', name: 'ALFA', department: 'PIURA', lat: -5, lon: -80 },
    ])
  })

  it('aligns each event to a 24-month axis and preserves missing observations', () => {
    const [first, second] = stationChartSeries(shapeSenamhiDataset(dataset).records, 'a')
    expect(first?.points).toHaveLength(24)
    expect(first?.points[0]).toMatchObject({
      offset: 1,
      month: '1982-01',
      precipitation: 30,
    })
    expect(first?.points[1]?.precipitation).toBeNull()
    expect(second?.points[0]).toMatchObject({ month: '1997-01', precipitation: 50 })
    expect(second?.points[23]?.precipitation).toBeNull()
  })
})
