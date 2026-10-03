import type { DatasetFor } from '~/types/datasets'

export const territoryGeometryFixture = {
  id: 'limites-inei-ign',
  source: {
    institution: 'Instituto Geográfico Nacional (IGN)',
    product: 'Límites departamentales de prueba',
    url: 'https://example.com/geometry',
  },
  variable: 'Geometría departamental',
  unit: 'No aplica',
  data_type: 'official',
  spatial_resolution: 'Departamento',
  temporal_resolution: 'Versión cartográfica',
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
          {
            type: 'Feature',
            properties: { name: 'Lima', code: 'PE15' },
            geometry: {
              type: 'Polygon',
              coordinates: [
                [
                  [-77, -13],
                  [-76, -13],
                  [-76, -12],
                  [-77, -13],
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
      license_url: 'https://example.com/license',
    },
  ],
} satisfies DatasetFor<'limites-inei-ign'>

export const territoryChirpsFixture = [
  {
    region: 'Amazonas',
    code: 'PE01',
    start: '2026-09-21',
    end: '2026-09-25',
    precipitation_mm: 1.2,
    anomaly_mm: -2.1,
  },
  {
    region: 'Amazonas',
    code: 'PE01',
    start: '2026-09-26',
    end: '2026-09-30',
    precipitation_mm: 4.2,
    anomaly_mm: 1.4,
  },
  {
    region: 'Lima',
    code: 'PE15',
    start: '2026-09-26',
    end: '2026-09-30',
    precipitation_mm: 0.3,
    anomaly_mm: -0.8,
  },
] satisfies DatasetFor<'chirps'>['records']

export const territoryEra5Fixture = [
  {
    region: 'Amazonas',
    code: 'PE01',
    start: '2026-07-06',
    end: '2026-07-06',
    precipitation_mm: 1.1,
  },
  {
    region: 'Amazonas',
    code: 'PE01',
    start: '2026-07-07',
    end: '2026-07-07',
    precipitation_mm: null,
  },
  {
    region: 'Amazonas',
    code: 'PE01',
    start: '2026-07-08',
    end: '2026-07-08',
    precipitation_mm: 2.2,
  },
  {
    region: 'Lima',
    code: 'PE15',
    start: '2026-07-06',
    end: '2026-07-06',
    precipitation_mm: 0.5,
  },
  {
    region: 'Lima',
    code: 'PE15',
    start: '2026-07-07',
    end: '2026-07-07',
    precipitation_mm: 1.5,
  },
  {
    region: 'Lima',
    code: 'PE15',
    start: '2026-07-08',
    end: '2026-07-08',
    precipitation_mm: 2.5,
  },
] satisfies DatasetFor<'open-meteo-era5'>['records']

export const territoryEra5DatasetFixture = {
  id: 'open-meteo-era5',
  source: {
    institution:
      'Open-Meteo (intermediary); ERA5 data from the Copernicus Climate Change Service (C3S) and ECMWF',
    product: 'Historical Weather API, model era5',
    url: 'https://archive-api.open-meteo.com/v1/archive',
  },
  variable: 'Precipitación diaria acumulada',
  unit: 'mm',
  data_type: 'estimated',
  spatial_resolution: '0,25°',
  temporal_resolution: 'Diaria',
  ingestion_time: '2026-10-01T00:00:00Z',
  processing_version: 'test',
  records: territoryEra5Fixture,
} satisfies DatasetFor<'open-meteo-era5'>

export const territoryChirpsDatasetFixture = {
  id: 'chirps',
  source: {
    institution: 'Climate Hazards Center, UC Santa Barbara',
    product: 'CHIRPS v3',
    url: 'https://data.chc.ucsb.edu/products/CHIRPS/v3.0/pentads/',
  },
  variable: 'Precipitación',
  unit: 'mm',
  data_type: 'estimated',
  spatial_resolution: '0,05°',
  temporal_resolution: 'Pentad',
  ingestion_time: '2026-10-01T00:00:00Z',
  processing_version: 'test',
  records: territoryChirpsFixture,
} satisfies DatasetFor<'chirps'>
