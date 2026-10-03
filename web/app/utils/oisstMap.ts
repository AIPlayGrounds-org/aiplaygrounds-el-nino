import { messages } from '~/messages'
import type { GridRecord } from '~/types/dataset'
import type { DatasetFor } from '~/types/datasets'
import { formatAnomaly } from '~/utils/enso'

/** Peruvian Pacific coast, in °N and °E. The page draws only this window, close to square. */
export const OISST_VIEW = { west: -90, east: -70, south: -20, north: 2 } as const

export type OisstPoint = {
  lat: number
  lon: number
  value: number
}

export type OisstBand = {
  start: number
  end: number
  mean: number
  maximum: number
}

export type OisstMapData = {
  latitudes: number[]
  longitudes: number[]
  points: OisstPoint[]
  bands: OisstBand[]
  warmest: OisstPoint | null
  valueMax: number
}

const within = (value: number, low: number, high: number) => value >= low && value <= high

/** Keeps the rows and columns inside `OISST_VIEW`. */
export const cropGridRecord = (record: GridRecord): GridRecord => {
  const rows = record.lat.flatMap((lat, index) =>
    within(lat, OISST_VIEW.south, OISST_VIEW.north) ? [index] : [],
  )
  const columns = record.lon.flatMap((lon, index) =>
    within(lon, OISST_VIEW.west, OISST_VIEW.east) ? [index] : [],
  )
  return {
    ...record,
    lat: rows.map((row) => record.lat[row]!) as GridRecord['lat'],
    lon: columns.map((column) => record.lon[column]!) as GridRecord['lon'],
    anomaly: rows.map((row) =>
      columns.map((column) => record.anomaly[row]![column]!),
    ) as GridRecord['anomaly'],
  }
}

/** Crops every record so the page payload carries only the cells it draws. */
export const cropOisst = (dataset: DatasetFor<'noaa-oisst'>): DatasetFor<'noaa-oisst'> => {
  const [first, ...rest] = dataset.records
  return { ...dataset, records: [cropGridRecord(first), ...rest.map(cropGridRecord)] }
}

export const buildOisstMap = (record: GridRecord): OisstMapData => {
  const points: OisstPoint[] = []
  record.lat.forEach((lat, row) => {
    record.lon.forEach((lon, column) => {
      const value = record.anomaly[row]?.[column]
      if (value !== null && value !== undefined) points.push({ lat, lon, value })
    })
  })

  const bandValues = new Map<number, number[]>()
  for (const point of points) {
    const start = Math.floor(point.lat)
    bandValues.set(start, [...(bandValues.get(start) ?? []), point.value])
  }
  const bands = [...bandValues.entries()]
    .sort(([a], [b]) => a - b)
    .map(([start, values]) => ({
      start,
      end: start + 1,
      mean: values.reduce((sum, value) => sum + value, 0) / values.length,
      maximum: Math.max(...values),
    }))

  const warmest = points.reduce<OisstPoint | null>(
    (current, point) => (current === null || point.value > current.value ? point : current),
    null,
  )

  return {
    latitudes: [...record.lat],
    longitudes: [...record.lon],
    points,
    bands,
    warmest,
    valueMax: Math.max(...points.map((point) => Math.abs(point.value)), 0.01),
  }
}

const degrees = new Intl.NumberFormat('es', { maximumFractionDigits: 2 })

/** «5° S», «79° O»: directions instead of signed degrees. */
export const formatCoordinate = (value: number, axis: 'latitude' | 'longitude') => {
  const { directions } = messages.oisst
  const direction =
    axis === 'latitude'
      ? value < 0
        ? directions.south
        : directions.north
      : value < 0
        ? directions.west
        : directions.east
  return messages.oisst.coordinate(degrees.format(Math.abs(value)), direction)
}

export const formatBand = (band: OisstBand) =>
  messages.oisst.band(
    formatCoordinate(band.start, 'latitude'),
    formatCoordinate(band.end, 'latitude'),
  )

export const summarizeOisst = (map: OisstMapData, date: string, unit: string) =>
  map.warmest
    ? messages.oisst.summary(
        date,
        formatAnomaly(map.warmest.value),
        unit,
        `${formatCoordinate(map.warmest.lat, 'latitude')}, ${formatCoordinate(map.warmest.lon, 'longitude')}`,
      )
    : messages.oisst.empty(date)
