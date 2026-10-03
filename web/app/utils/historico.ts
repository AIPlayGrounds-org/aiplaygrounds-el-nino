import type { ErsstRecord, OniRecord } from '~/types/dataset'
import type { DatasetFor } from '~/types/datasets'

export const HISTORICAL_EVENT_IDS = ['1982-83', '1997-98', '2017'] as const
export const CURRENT_EVENT_ID = 'current' as const
export type HistoricalEventId = (typeof HISTORICAL_EVENT_IDS)[number]
export type HistoryEventId = HistoricalEventId | typeof CURRENT_EVENT_ID
export type HistoryRegion = 'nino34' | 'nino12'
export type HistoryWindow = readonly [string, string]
export type HistoryWindows = Partial<Record<HistoricalEventId, HistoryWindow>>

export type AlignedHistoryPoint = {
  offset: number
  month: string
  value: number | null
}

const yearOf = (month: string) => Number(month.slice(0, 4))
const monthIndex = (month: string) => {
  const [year, value] = month.split('-').map(Number)
  return year! * 12 + value! - 1
}
const monthAt = (index: number) => {
  const year = Math.floor(index / 12)
  const month = (index % 12) + 1
  return `${year}-${String(month).padStart(2, '0')}`
}

const recordsFor = (records: readonly ErsstRecord[], event: HistoryEventId) => {
  if (event === CURRENT_EVENT_ID) {
    const currentYear = yearOf(records.at(-1)?.start ?? '')
    return records.filter((record) => yearOf(record.start) === currentYear)
  }
  return records.filter((record) => record.event === event)
}

const fieldFor = (
  region: HistoryRegion,
): keyof Pick<ErsstRecord, 'nino34_anomaly' | 'nino12_anomaly'> =>
  region === 'nino34' ? 'nino34_anomaly' : 'nino12_anomaly'

/** Keep only the ERSST records used by the historical comparison page. */
export const shapeHistoricoDataset = (dataset: DatasetFor<'noaa-ersst'>) => {
  const currentYear = yearOf(dataset.records.at(-1)!.start)
  const records = dataset.records.filter(
    (record) => record.event !== undefined || yearOf(record.start) === currentYear,
  )
  return { ...dataset, records } as DatasetFor<'noaa-ersst'>
}

const oniMonth = (record: OniRecord) => monthAt(monthIndex(record.start) + 1)

/** Derive each historical event window from the event tags in the ERSST records. */
export const historyWindowsFromErsst = (records: readonly ErsstRecord[]): HistoryWindows => {
  const windows: HistoryWindows = {}
  for (const event of HISTORICAL_EVENT_IDS) {
    const eventRecords = records.filter((record) => record.event === event)
    const first = eventRecords[0]
    const last = eventRecords.at(-1)
    if (first && last) windows[event] = [first.start, last.start]
  }
  return windows
}

const alignRecords = <RecordType>(
  records: readonly RecordType[],
  firstMonth: string,
  lastMonth: string,
  monthForRecord: (record: RecordType) => string,
  valueForRecord: (record: RecordType) => number,
): AlignedHistoryPoint[] => {
  const firstIndex = monthIndex(firstMonth)
  const lastIndex = monthIndex(lastMonth)
  const byMonth = new Map(records.map((record) => [monthForRecord(record), record]))

  return Array.from({ length: lastIndex - firstIndex + 1 }, (_, index) => {
    const month = monthAt(firstIndex + index)
    const record = byMonth.get(month)
    return {
      offset: index + 1,
      month,
      value: record ? valueForRecord(record) : null,
    }
  })
}

export const peakOfHistoryPoints = (points: readonly AlignedHistoryPoint[]) =>
  points
    .filter((point): point is AlignedHistoryPoint & { value: number } => point.value !== null)
    .reduce<(AlignedHistoryPoint & { value: number }) | null>(
      (peak, point) => (peak === null || point.value > peak.value ? point : peak),
      null,
    )

/** Keep only the ONI records needed for the historical comparison page. */
export const shapeHistoricoOniDataset = (
  dataset: DatasetFor<'noaa-cpc-oni'>,
  ersstRecords: readonly ErsstRecord[],
) => {
  const windows = historyWindowsFromErsst(ersstRecords)
  const currentYear = yearOf(oniMonth(dataset.records.at(-1)!))
  const records = dataset.records.filter((record) => {
    const month = oniMonth(record)
    return (
      yearOf(month) === currentYear ||
      HISTORICAL_EVENT_IDS.filter((event) => event !== '2017').some((event) => {
        const window = windows[event]
        if (!window) return false
        const [start, end] = window
        const monthNumber = monthIndex(month)
        return monthNumber >= monthIndex(start) && monthNumber <= monthIndex(end)
      })
    )
  })
  return { ...dataset, records } as DatasetFor<'noaa-cpc-oni'>
}

/** Return selector ids that have records in the shaped or full ERSST dataset. */
export const historyEventSelectorData = (records: readonly ErsstRecord[]) => {
  const currentYear = yearOf(records.at(-1)?.start ?? '')
  const historical = HISTORICAL_EVENT_IDS.filter((event) =>
    records.some((record) => record.event === event),
  )
  return [
    ...historical,
    ...(records.some((record) => yearOf(record.start) === currentYear) ? [CURRENT_EVENT_ID] : []),
  ] as HistoryEventId[]
}

/** Align each event to its own first month and preserve gaps as null values. */
export const alignHistoryEvent = (
  records: readonly ErsstRecord[],
  event: HistoryEventId,
  region: HistoryRegion,
): AlignedHistoryPoint[] => {
  const eventRecords = recordsFor(records, event)
  const first = eventRecords[0]
  const last = eventRecords.at(-1)
  if (!first || !last) return []

  const field = fieldFor(region)
  return alignRecords(
    eventRecords,
    first.start,
    last.start,
    (record) => record.start,
    (record) => record[field],
  )
}

export const peakOfHistoryEvent = (
  records: readonly ErsstRecord[],
  event: HistoryEventId,
  region: HistoryRegion,
) => {
  return peakOfHistoryPoints(alignHistoryEvent(records, event, region))
}

const oniRecordsFor = (
  records: readonly OniRecord[],
  event: HistoryEventId,
  windows: HistoryWindows,
) => {
  if (event === CURRENT_EVENT_ID) {
    const currentYear = yearOf(oniMonth(records.at(-1)!))
    return records.filter((record) => yearOf(oniMonth(record)) === currentYear)
  }
  const window = windows[event]
  if (!window) return []
  const [start, end] = window
  return records.filter((record) => {
    const month = monthIndex(oniMonth(record))
    return month >= monthIndex(start) && month <= monthIndex(end)
  })
}

/** Align official ONI seasons to the same event-relative month axis as ERSST. */
export const alignHistoryOniEvent = (
  records: readonly OniRecord[],
  event: HistoryEventId,
  windows: HistoryWindows,
): AlignedHistoryPoint[] => {
  const eventRecords = oniRecordsFor(records, event, windows)
  const first = eventRecords[0]
  const last = eventRecords.at(-1)
  if (!first || !last) return []

  const firstMonth = event === CURRENT_EVENT_ID ? oniMonth(first) : windows[event]?.[0]
  const lastMonth = event === CURRENT_EVENT_ID ? oniMonth(last) : windows[event]?.[1]
  if (!firstMonth || !lastMonth) return []
  return alignRecords(eventRecords, firstMonth, lastMonth, oniMonth, (record) => record.anomaly)
}

export const peakOfHistoryOniEvent = (
  records: readonly OniRecord[],
  event: HistoryEventId,
  windows: HistoryWindows,
) => peakOfHistoryPoints(alignHistoryOniEvent(records, event, windows))
