import type { Dataset, DatasetId, DatasetRecordMap } from '~/types/dataset'

export type { DatasetId, DatasetRecordMap } from '~/types/dataset'

export type DatasetFor<Id extends DatasetId> = Omit<Dataset, 'id' | 'records'> & {
  id: Id
  records: [DatasetRecordMap[Id], ...DatasetRecordMap[Id][]]
}

export type DatasetWithRecords<Id extends DatasetId> = Omit<DatasetFor<Id>, 'records'> & {
  records: DatasetRecordMap[Id][]
}

export type AnyDataset = DatasetFor<DatasetId>

/** Provenance and period shape accepted by shared shells after server-side shaping. */
export type DatasetLike = Omit<Dataset, 'records'> & {
  records: { start: string; end: string }[]
}
