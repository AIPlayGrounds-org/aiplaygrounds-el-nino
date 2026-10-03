import type { DatasetLike } from "~/types/datasets";

export const geometryFixture = {
  id: "fixture-geometry",
  source: {
    institution: "Fuente de prueba",
    product: "Geometría de prueba",
    url: "https://example.com/geometry",
  },
  variable: "Límites de prueba",
  unit: "GeoJSON",
  data_type: "official",
  spatial_resolution: "Departamento",
  temporal_resolution: "Sin periodo",
  ingestion_time: "2026-10-01T00:00:00Z",
  processing_version: "test",
  records: [
    {
      start: "2026-10-01",
      end: "2026-10-01",
      geometry: {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            properties: { name: "Prueba" },
            geometry: {
              type: "Polygon",
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
    },
  ],
} satisfies DatasetLike;
