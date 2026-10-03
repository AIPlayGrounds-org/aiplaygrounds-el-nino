import type { DatasetFor } from '~/types/datasets'

export const geometryFixture = {
  id: 'limites-inei-ign',
  source: {
    institution: 'Fuente de prueba',
    product: 'Geometría de prueba',
    url: 'https://example.com/geometry',
  },
  variable: 'Límites de prueba',
  unit: 'GeoJSON',
  data_type: 'official',
  spatial_resolution: 'Departamento',
  temporal_resolution: 'Sin periodo',
  ingestion_time: '2026-10-01T00:00:00Z',
  processing_version: 'test',
  records: [
    {
      start: '2020-07-14',
      end: '2020-07-14',
      version: 'v01',
      departamentos: {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            properties: { name: 'Amazonas', code: 'PE01' },
            geometry: {
              type: 'Polygon',
              coordinates: [
                [
                  [-80, -5],
                  [-79, -5],
                  [-79, -4],
                  [-80, -5],
                ],
              ],
            },
          },
        ],
      },
      provincias: {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            properties: { name: 'Chachapoyas', code: 'PE0101', parent: 'PE01' },
            geometry: {
              type: 'Polygon',
              coordinates: [
                [
                  [-80, -5],
                  [-79, -5],
                  [-79, -4],
                  [-80, -5],
                ],
              ],
            },
          },
        ],
      },
      attribution: 'Instituto Geográfico Nacional (IGN)',
      license_url: 'https://www.gob.pe/ign',
    },
  ],
} satisfies DatasetFor<'limites-inei-ign'>
