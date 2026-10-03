import enfenJson from "#data/enfen-communique.json";
import weeklyJson from "#data/noaa-cpc-nino-weekly.json";
import oniJson from "#data/noaa-cpc-oni.json";
import outlookJson from "#data/noaa-cpc-outlook.json";
import ersstJson from "#data/noaa-ersst.json";
import oisstJson from "#data/noaa-oisst.json";
import glofasJson from "#data/open-meteo-glofas.json";
import type { AnyDataset, DatasetFor, DatasetId, DatasetRecordMap } from "~/types/datasets";

const rawDatasets: Record<DatasetId, unknown> = {
  "noaa-cpc-oni": oniJson,
  "noaa-cpc-nino-weekly": weeklyJson,
  "noaa-cpc-outlook": outlookJson,
  "enfen-communique": enfenJson,
  "noaa-oisst": oisstJson,
  "open-meteo-glofas": glofasJson,
  "noaa-ersst": ersstJson,
};

const REQUIRED_PROVENANCE = [
  "id",
  "source",
  "variable",
  "unit",
  "data_type",
  "spatial_resolution",
  "temporal_resolution",
  "ingestion_time",
  "processing_version",
  "records",
] as const;

const DATA_TYPES = new Set(["observed", "estimated", "forecast", "official"]);

const isObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const isString = (value: unknown): value is string => typeof value === "string";

const isNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);

const invalid = (id: DatasetId, detail: string): never => {
  throw new Error(`[useDataset] data/${id}.json is invalid: ${detail}`);
};

const objectOrInvalid = (
  id: DatasetId,
  value: unknown,
  detail: string,
): Record<string, unknown> => {
  if (!isObject(value)) invalid(id, detail);
  return value as Record<string, unknown>;
};

const arrayOrInvalid = (id: DatasetId, value: unknown, detail: string): unknown[] => {
  if (!Array.isArray(value)) invalid(id, detail);
  return value as unknown[];
};

const validateRecord = (id: DatasetId, record: unknown, index: number): Record<string, unknown> => {
  const object = objectOrInvalid(id, record, `records[${index}] must be an object`);
  if (!isString(object.start) || !isString(object.end)) {
    invalid(id, `records[${index}] must include string start and end fields`);
  }
  return object;
};

const validateSpecificRecords = (id: DatasetId, records: Record<string, unknown>[]) => {
  for (const [index, record] of records.entries()) {
    if (
      id === "noaa-cpc-oni" &&
      (!isString(record.season) || !isNumber(record.sst) || !isNumber(record.anomaly))
    ) {
      invalid(id, `records[${index}] must include season, numeric sst, and numeric anomaly fields`);
    }
    if (id === "noaa-oisst") {
      const lat = record.lat as unknown;
      const lon = record.lon as unknown;
      const anomaly = record.anomaly as unknown;
      if (!Array.isArray(lat) || !Array.isArray(lon) || !Array.isArray(anomaly)) {
        invalid(id, `records[${index}] must include lat, lon, and anomaly arrays`);
      }
      const latValues = lat as unknown[];
      const lonValues = lon as unknown[];
      const anomalyRows = anomaly as unknown[];
      if (
        anomalyRows.some((row: unknown) => !Array.isArray(row) || row.length !== lonValues.length)
      ) {
        invalid(id, `records[${index}].anomaly must be rectangular and match lon`);
      }
      if (anomalyRows.length !== latValues.length) {
        invalid(id, `records[${index}].anomaly must match lat`);
      }
    }
    if (
      id === "enfen-communique" &&
      (!isString(record.status) || !isString(record.url) || typeof record.stale !== "boolean")
    ) {
      invalid(id, `records[${index}] must include status, url, and stale fields`);
    }
  }
};

export const validateDataset = <Id extends DatasetId>(id: Id, value: unknown): DatasetFor<Id> => {
  const dataset = objectOrInvalid(id, value, "the root value must be an object");
  for (const field of REQUIRED_PROVENANCE) {
    if (!(field in dataset)) invalid(id, `missing required field ${field}`);
  }
  if (dataset.id !== id) invalid(id, `id is ${String(dataset.id)}, expected ${id}`);
  if (
    !isObject(dataset.source) ||
    !isString(dataset.source.institution) ||
    !isString(dataset.source.product) ||
    !isString(dataset.source.url)
  ) {
    invalid(id, "source must include institution, product, and url");
  }
  for (const field of [
    "variable",
    "unit",
    "spatial_resolution",
    "temporal_resolution",
    "ingestion_time",
    "processing_version",
  ]) {
    if (!isString(dataset[field])) invalid(id, `${field} must be a string`);
  }
  if (!DATA_TYPES.has(dataset.data_type as string))
    invalid(id, `data_type ${String(dataset.data_type)} is not in the schema enum`);
  const rawRecords = arrayOrInvalid(id, dataset.records, "records must be a non-empty array");
  if (rawRecords.length === 0) invalid(id, "records must be a non-empty array");
  const records = rawRecords.map((record, index) => validateRecord(id, record, index));
  validateSpecificRecords(id, records);
  return dataset as DatasetFor<Id>;
};

const datasets = Object.fromEntries(
  (Object.keys(rawDatasets) as DatasetId[]).map((id) => [id, validateDataset(id, rawDatasets[id])]),
) as { [Id in DatasetId]: DatasetFor<Id> };

/** Loads one validated JSON dataset at build time with its id-specific record type. */
export const useDataset = <Id extends DatasetId>(id: Id): DatasetFor<Id> => {
  const dataset = datasets[id] as AnyDataset | undefined;
  if (!dataset)
    throw new Error(`[useDataset] data/${id}.json was not found in the static dataset catalog`);
  return dataset as DatasetFor<Id>;
};

export type DatasetRecordFor<Id extends DatasetId> = DatasetRecordMap[Id];
