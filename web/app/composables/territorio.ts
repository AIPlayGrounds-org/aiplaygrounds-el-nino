import type { BoundaryFeature, ChirpsRecord, Era5Record, GeometryRecord } from '~/types/dataset'
import type { DatasetFor } from '~/types/datasets'

export type TerritoryMetric = 'precipitation' | 'anomaly'

export type Era5Department = {
  code: string
  region: string
  total: number | null
  availableDays: number
  missingDays: number
}

export type TerritoryRow = {
  code: string
  region: string
  chirps: ChirpsRecord | undefined
  era5: Era5Department | undefined
}

export type Era5Window = {
  start: string
  end: string
  days: number
}

const datesBetween = (start: string, end: string) => {
  const dates: string[] = []
  const current = new Date(`${start}T00:00:00Z`)
  const last = new Date(`${end}T00:00:00Z`)
  while (current <= last) {
    dates.push(current.toISOString().slice(0, 10))
    current.setUTCDate(current.getUTCDate() + 1)
  }
  return dates
}

export const latestChirpsPerDepartment = (records: readonly ChirpsRecord[]) => {
  const latest = new Map<string, ChirpsRecord>()
  for (const record of records) {
    const current = latest.get(record.code)
    if (!current || record.end > current.end) latest.set(record.code, record)
  }
  return [...latest.values()].sort((a, b) => a.region.localeCompare(b.region))
}

export const metricValue = (record: ChirpsRecord, metric: TerritoryMetric) =>
  metric === 'precipitation' ? record.precipitation_mm : record.anomaly_mm

export const aggregateEra5 = (
  records: readonly Era5Record[],
  boundaries: readonly BoundaryFeature[],
) => {
  const ordered = [...records].sort((a, b) => a.start.localeCompare(b.start))
  const start = ordered[0]?.start ?? ''
  const end = ordered.at(-1)?.end ?? ''
  const dates = start && end ? datesBetween(start, end) : []
  const window: Era5Window = { start, end, days: dates.length }
  const byCode = new Map<string, { region: string; values: Map<string, number | null> }>(
    boundaries.map((boundary) => [
      boundary.properties.code,
      { region: boundary.properties.name, values: new Map() },
    ]),
  )

  for (const record of ordered) {
    const department = byCode.get(record.code) ?? { region: record.region, values: new Map() }
    department.values.set(record.start, record.precipitation_mm)
    byCode.set(record.code, department)
  }

  const departments = [...byCode.entries()]
    .map(([code, department]): Era5Department => {
      const missingDays = dates.filter(
        (date) => !department.values.has(date) || department.values.get(date) === null,
      ).length
      const availableDays = dates.length - missingDays
      const total = missingDays
        ? null
        : dates.reduce((sum, date) => sum + (department.values.get(date) ?? 0), 0)
      return { code, region: department.region, total, availableDays, missingDays }
    })
    .sort((a, b) => a.region.localeCompare(b.region))

  return { window, departments }
}

export const joinTerritoryRows = (
  geometry: Pick<GeometryRecord, 'departamentos'>,
  chirps: readonly ChirpsRecord[],
  era5: readonly Era5Department[],
) => {
  const boundaries = new Map(
    geometry.departamentos.features.map((feature) => [feature.properties.code, feature]),
  )
  const chirpsByCode = new Map(chirps.map((record) => [record.code, record]))
  const era5ByCode = new Map(era5.map((record) => [record.code, record]))
  const codes = new Set([...boundaries.keys(), ...chirpsByCode.keys(), ...era5ByCode.keys()])

  return [...codes]
    .map((code): TerritoryRow => {
      const boundary = boundaries.get(code)
      const chirpsRecord = chirpsByCode.get(code)
      const era5Record = era5ByCode.get(code)
      return {
        code,
        region: boundary?.properties.name ?? chirpsRecord?.region ?? era5Record?.region ?? code,
        chirps: chirpsRecord,
        era5: era5Record,
      }
    })
    .sort((a, b) => a.region.localeCompare(b.region))
}

export type DepartmentGeometry = Omit<DatasetFor<'limites-inei-ign'>, 'records'> & {
  records: [Omit<GeometryRecord, 'provincias'>]
}

export type Era5Summary = DatasetFor<'open-meteo-era5'> & {
  window: Era5Window
  departments: Era5Department[]
}

/** Keeps the newest boundary record without the province layer, which the page never draws. */
export const shapeDepartmentGeometry = (
  dataset: DatasetFor<'limites-inei-ign'>,
): DepartmentGeometry => {
  const { start, end, version, departamentos, attribution, license_url } = dataset.records.at(-1)!
  return { ...dataset, records: [{ start, end, version, departamentos, attribution, license_url }] }
}

/**
 * Keeps the latest pentad per department, oldest first, so the first and last record bound the
 * period that ChartShell prints.
 */
export const shapeLatestChirps = (dataset: DatasetFor<'chirps'>): DatasetFor<'chirps'> => {
  const [first, ...rest] = latestChirpsPerDepartment(dataset.records).sort(
    (a, b) => a.end.localeCompare(b.end) || a.region.localeCompare(b.region),
  )
  return { ...dataset, records: [first!, ...rest] }
}

/**
 * Replaces the daily records with the per-department totals the table shows. The records keep only
 * the first and last day, which is all ChartShell reads for the period.
 */
export const shapeEra5Summary =
  (boundaries: readonly BoundaryFeature[]) =>
  (dataset: DatasetFor<'open-meteo-era5'>): Era5Summary => {
    const { window, departments } = aggregateEra5(dataset.records, boundaries)
    const ordered = [...dataset.records].sort((a, b) => a.start.localeCompare(b.start))
    return { ...dataset, records: [ordered[0]!, ordered.at(-1)!], window, departments }
  }
