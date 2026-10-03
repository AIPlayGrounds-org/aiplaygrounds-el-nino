import type {
  Dataset,
  EnfenRecord,
  ErsstRecord,
  GlofasRecord,
  GeometryRecord,
  GridRecord,
  OniRecord,
  OutlookRecord,
  WeeklyNinoRecord,
} from "~/types/dataset";

export type DatasetRecordMap = {
  "noaa-cpc-oni": OniRecord;
  "noaa-cpc-nino-weekly": WeeklyNinoRecord;
  "noaa-cpc-outlook": OutlookRecord;
  "enfen-communique": EnfenRecord;
  "limites-inei-ign": GeometryRecord;
  "noaa-oisst": GridRecord;
  "open-meteo-glofas": GlofasRecord;
  "noaa-ersst": ErsstRecord;
};

export type DatasetId = keyof DatasetRecordMap;

export type DatasetFor<Id extends DatasetId> = Omit<Dataset, "id" | "records"> & {
  id: Id;
  records: [DatasetRecordMap[Id], ...DatasetRecordMap[Id][]];
};

export type AnyDataset = DatasetFor<DatasetId>;

export type DatasetLike = AnyDataset;
