import type { DatasetFor, DatasetWithRecords, SenamhiEstacionesRecord } from '~/types/datasets'

export type SenamhiEvent = '1982-83' | '1997-98'

export type SenamhiDataset = Omit<DatasetWithRecords<'senamhi-estaciones'>, 'records'> & {
  records: SenamhiStation[]
}

export type SenamhiStation = Pick<
  SenamhiEstacionesRecord,
  'station' | 'region' | 'department' | 'lat' | 'lon'
> & {
  firstYear: number
  latestYear: number
  climatology: (number | null)[]
  precipitation: (number | null)[]
}

export const SENAMHI_EVENT_YEARS: Record<SenamhiEvent, readonly number[]> = {
  '1982-83': [1982, 1983],
  '1997-98': [1997, 1998],
}

const senamhiEventYears = Object.values(SENAMHI_EVENT_YEARS).flat()

const eventForYear = (year: number): SenamhiEvent | null => {
  for (const [event, years] of Object.entries(SENAMHI_EVENT_YEARS) as [
    SenamhiEvent,
    readonly number[],
  ][]) {
    if (years.includes(year)) return event
  }
  return null
}

export const shapeSenamhiDataset = (dataset: DatasetFor<'senamhi-estaciones'>): SenamhiDataset => {
  const firstYears = new Map<string, number>()
  const latestYears = new Map<string, number>()
  for (const record of dataset.records) {
    const year = Number(record.start.slice(0, 4))
    firstYears.set(record.station, Math.min(firstYears.get(record.station) ?? year, year))
    latestYears.set(record.station, Math.max(latestYears.get(record.station) ?? 0, year))
  }
  const stations = new Map<string, SenamhiStation>()
  for (const sourceRecord of dataset.records) {
    const year = Number(sourceRecord.start.slice(0, 4))
    const month = Number(sourceRecord.start.slice(5, 7)) - 1
    if (eventForYear(year) === null && year !== latestYears.get(sourceRecord.station)) continue
    const station = stations.get(sourceRecord.station)
    if (!station) {
      stations.set(sourceRecord.station, {
        station: sourceRecord.station,
        region: sourceRecord.region,
        department: sourceRecord.department,
        lat: sourceRecord.lat,
        lon: sourceRecord.lon,
        firstYear: firstYears.get(sourceRecord.station)!,
        latestYear: latestYears.get(sourceRecord.station)!,
        climatology: Array.from({ length: 12 }, () => null),
        precipitation: Array.from({ length: 48 }, () => null),
      })
    }
    const stationRecord = stations.get(sourceRecord.station)!
    if (eventForYear(year) !== null) {
      stationRecord.precipitation[eventOffset(year, month)] = sourceRecord.precipitation_mm
    }
    if (stationRecord.climatology[month] === null) {
      stationRecord.climatology[month] = sourceRecord.precipitation_median_mm
    }
  }
  return {
    ...dataset,
    records: [...stations.values()].sort((left, right) =>
      left.region.localeCompare(right.region, 'es'),
    ),
  }
}

const eventOffset = (year: number, month: number) => senamhiEventYears.indexOf(year) * 12 + month

export const stationOptions = (stations: readonly SenamhiStation[]) =>
  stations.map((station) => ({
    code: station.station,
    name: station.region,
    department: station.department,
    lat: station.lat,
    lon: station.lon,
  }))

export type SenamhiChartPoint = {
  offset: number
  month: string
  precipitation: number | null
  climatology: number | null
}

export type SenamhiChartSeries = {
  event: SenamhiEvent
  points: SenamhiChartPoint[]
}

export const stationChartSeries = (
  stations: readonly SenamhiStation[],
  stationCode: string,
): SenamhiChartSeries[] => {
  const selected = stations.find((station) => station.station === stationCode)
  return (Object.keys(SENAMHI_EVENT_YEARS) as SenamhiEvent[]).map((event) => {
    const points = SENAMHI_EVENT_YEARS[event].flatMap((year, yearIndex) =>
      Array.from({ length: 12 }, (_, monthIndex) => {
        const month = String(year) + '-' + String(monthIndex + 1).padStart(2, '0')
        const precipitation =
          selected?.precipitation[senamhiEventYears.indexOf(year) * 12 + monthIndex]
        return {
          offset: yearIndex * 12 + monthIndex + 1,
          month,
          precipitation: precipitation ?? null,
          climatology: selected?.climatology[monthIndex] ?? null,
        }
      }),
    )
    return { event, points }
  })
}

export const stationLabel = (stations: readonly SenamhiStation[], stationCode: string) => {
  const station = stations.find((candidate) => candidate.station === stationCode)
  return station
    ? {
        code: station.station,
        name: station.region,
        department: station.department,
        lat: station.lat,
        lon: station.lon,
      }
    : null
}
