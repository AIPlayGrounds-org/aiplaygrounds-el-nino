import type {
  Dataset,
  DatasetRecord,
  EnfenRecord,
  ErsstRecord,
  GlofasRecord,
  GeometryRecord,
  GridRecord,
  OniRecord,
  OutlookRecord,
} from "~/types/dataset";

export interface WeeklyNinoRecord extends DatasetRecord {
  nino_1_2_sst: number;
  nino_1_2_anomaly: number;
  nino_3_sst: number;
  nino_3_anomaly: number;
  nino_3_4_sst: number;
  nino_3_4_anomaly: number;
  nino_4_sst: number;
  nino_4_anomaly: number;
}

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

export type DatasetLike = Omit<Dataset, "records"> & {
  records: [{ start: string; end: string }, ...{ start: string; end: string }[]];
};
