import type { DatasetFor } from '~/types/datasets'

export const timeSeriesFixture = {
  id: 'noaa-cpc-oni',
  source: {
    institution: 'Fuente de prueba',
    product: 'Serie temporal de prueba',
    url: 'https://example.com/time-series',
  },
  variable: 'Anomalía de prueba',
  unit: '°C',
  data_type: 'observed',
  spatial_resolution: 'Región de prueba',
  temporal_resolution: 'Mensual',
  ingestion_time: '2026-10-01T00:00:00Z',
  processing_version: 'test',
  records: [
    { season: 'JJA', start: '2026-06', end: '2026-08', sst: 25.1, anomaly: 0.4 },
    { season: 'JAS', start: '2026-07', end: '2026-09', sst: 25.3, anomaly: 0.7 },
  ],
} satisfies DatasetFor<'noaa-cpc-oni'>
