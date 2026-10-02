// Formato de los JSON que publica el pipeline en data/ (docs/datos.md §4).

export interface Dataset<R> {
  id: string
  source: { institution: string; product: string; url: string }
  variable: string
  unit: string
  data_type: 'observado' | 'estimado' | 'pronóstico'
  spatial_resolution: string
  temporal_resolution: string
  reference_period: string
  ingestion_time: string
  processing_version: string
  records: R[]
}

export interface OniRecord {
  season: string
  start: string // AAAA-MM
  end: string // AAAA-MM
  sst: number
  anomaly: number
}
