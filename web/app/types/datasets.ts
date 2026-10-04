import type {
  Dataset,
  ChirpsRecord,
  EnfenRecord,
  Era5Record,
  ErsstRecord,
  GlofasRecord,
  GeometryRecord,
  GridRecord,
  OniRecord,
  OutlookRecord,
  WeeklyNinoRecord,
} from '~/types/dataset'

export type DatasetRecordMap = {
  'noaa-cpc-oni': OniRecord
  'noaa-cpc-nino-weekly': WeeklyNinoRecord
  'noaa-cpc-outlook': OutlookRecord
  'enfen-communique': EnfenRecord
  'limites-inei-ign': GeometryRecord
  chirps: ChirpsRecord
  'open-meteo-era5': Era5Record
  'noaa-oisst': GridRecord
  'open-meteo-glofas': GlofasRecord
  'noaa-ersst': ErsstRecord
}

export type DatasetId = keyof DatasetRecordMap

export type DatasetFor<Id extends DatasetId> = Omit<Dataset, 'id' | 'records'> & {
  id: Id
  records: [DatasetRecordMap[Id], ...DatasetRecordMap[Id][]]
}

export type AnyDataset = DatasetFor<DatasetId>

/** Provenance and period shape accepted by shared shells after server-side shaping. */
export type DatasetLike = Omit<Dataset, 'records'> & {
  records: { start: string; end: string }[]
}
