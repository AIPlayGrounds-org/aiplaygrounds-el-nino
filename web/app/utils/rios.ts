import type { GlofasRecord } from '~/types/dataset'
import type { DatasetFor } from '~/types/datasets'

export type RiosRecord = Pick<
  GlofasRecord,
  | 'point'
  | 'start'
  | 'end'
  | 'data_type'
  | 'river_discharge'
  | 'river_discharge_p25'
  | 'river_discharge_p75'
>

export type RiosDataset = Omit<DatasetFor<'open-meteo-glofas'>, 'records'> & {
  records: [RiosRecord, ...RiosRecord[]]
}

/** Keep points in a stable order, then make each point's daily series chronological. */
export const shapeRiosDataset = (dataset: DatasetFor<'open-meteo-glofas'>): RiosDataset => {
  const points = riverPoints(dataset.records)
  const pointOrder = new Map(points.map((point, index) => [point, index]))
  const records = dataset.records
    .map(
      ({
        point,
        start,
        end,
        data_type,
        river_discharge,
        river_discharge_p25,
        river_discharge_p75,
      }) => ({
        point,
        start,
        end,
        data_type,
        river_discharge,
        river_discharge_p25,
        river_discharge_p75,
      }),
    )
    .sort(
      (a, b) =>
        (pointOrder.get(a.point) ?? Number.MAX_SAFE_INTEGER) -
          (pointOrder.get(b.point) ?? Number.MAX_SAFE_INTEGER) || a.start.localeCompare(b.start),
    )

  return { ...dataset, records: [records[0]!, ...records.slice(1)] }
}

/** Return points alphabetically, so selector order does not depend on record order. */
export const riverPoints = (records: readonly Pick<GlofasRecord, 'point'>[]) =>
  [...new Set(records.map((record) => record.point))].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0))

/** Select one point from the already shaped chronological dataset. */
export const recordsForRiver = (records: readonly RiosRecord[], point: string) =>
  records.filter((record) => record.point === point)

export const latestEstimatedRiverRecord = (records: readonly RiosRecord[]) =>
  [...records]
    .reverse()
    .find((record) => record.data_type === 'estimated' && record.river_discharge !== null)

export const firstForecastRiverRecord = (records: readonly RiosRecord[]) =>
  records.find((record) => record.data_type === 'forecast')

export const riverRange = (record: RiosRecord): [number, number] | null =>
  record.river_discharge_p25 !== null && record.river_discharge_p75 !== null
    ? [record.river_discharge_p25, record.river_discharge_p75]
    : null
