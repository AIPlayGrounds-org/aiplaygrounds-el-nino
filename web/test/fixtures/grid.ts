import type { DatasetFor } from '~/types/datasets'

export const gridFixture = {
  id: 'noaa-oisst',
  source: {
    institution: 'Fuente de prueba',
    product: 'Malla de prueba',
    url: 'https://example.com/grid',
  },
  variable: 'Anomalía de temperatura',
  unit: '°C',
  data_type: 'estimated',
  spatial_resolution: 'Malla de prueba',
  temporal_resolution: 'Diaria',
  ingestion_time: '2026-10-01T00:00:00Z',
  processing_version: 'test',
  records: [
    {
      start: '2026-10-01',
      end: '2026-10-01',
      lat: [-1, 0],
      lon: [-80, -79],
      anomaly: [
        [0.2, null],
        [0.4, 0.5],
      ],
    },
  ],
} satisfies DatasetFor<'noaa-oisst'>
