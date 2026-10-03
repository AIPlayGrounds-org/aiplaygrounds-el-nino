import type { DatasetFor } from "~/types/datasets";

const source = {
  institution: "Fuente de prueba",
  product: "Producto de prueba",
  url: "https://example.com/panels",
};

export const enfenFixture = {
  id: "enfen-communique",
  source,
  variable: "Estado del sistema de alerta de El Niño Costero",
  unit: "Estado oficial",
  data_type: "official",
  spatial_resolution: "Costa del Perú",
  temporal_resolution: "Por comunicado",
  ingestion_time: "2026-10-02T23:14:16+00:00",
  processing_version: "test",
  records: [
    {
      number: 17,
      year: 2026,
      status: "Alerta de El Niño Costero",
      url: "https://example.com/comunicado-17-2026",
      start: "2026-09-28",
      end: "2026-10-15",
      stale: false,
      checked_at: "2026-10-02",
    },
  ],
} satisfies DatasetFor<"enfen-communique">;

const bounds: [number | null, number | null, string][] = [
  [null, -2, "Index ≤ -2.0°C"],
  [-2, -1.5, "-1.5°C ≥ Index > -2.0°C"],
  [-1.5, -1, "-1.0°C ≥ Index > -1.5°C"],
  [-1, -0.5, "-0.5°C ≥ Index > -1.0°C"],
  [-0.5, 0.5, "−0.5°C < Index < 0.5°C"],
  [0.5, 1, "0.5°C ≤ Index < 1.0°C"],
  [1, 1.5, "1.0°C ≤ Index < 1.5°C"],
  [1.5, 2, "1.5°C ≤ Index < 2.0°C"],
  [2, null, "Index ≥ 2.0°C"],
];

const season = (name: string, start: string, end: string) => ({
  issue_date: "2026-09",
  season: name,
  start,
  end,
  categories: bounds.map(([lower_bound, upper_bound, category], index) => ({
    category,
    lower_bound,
    upper_bound,
    probability: index === 7 ? 23 : index === 8 ? 77 : 0,
  })),
});

export const outlookFixture = {
  id: "noaa-cpc-outlook",
  source,
  variable: "Probabilidad de cada categoría de intensidad ENSO, por temporada",
  unit: "%",
  data_type: "forecast",
  spatial_resolution: "Un valor por categoría y temporada",
  temporal_resolution: "Temporadas móviles de tres meses",
  ingestion_time: "2026-10-03T13:37:11+00:00",
  processing_version: "test",
  records: [
    season("ASO", "2026-08", "2026-10"),
    season("SON", "2026-09", "2026-11"),
    season("OND", "2026-10", "2026-12"),
  ],
} satisfies DatasetFor<"noaa-cpc-outlook">;
