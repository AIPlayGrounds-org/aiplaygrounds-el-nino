import Ajv2020 from "ajv/dist/2020";
import enfenJson from "#data/enfen-communique.json";
import geometryJson from "#data/limites-inei-ign.json";
import weeklyJson from "#data/noaa-cpc-nino-weekly.json";
import oniJson from "#data/noaa-cpc-oni.json";
import outlookJson from "#data/noaa-cpc-outlook.json";
import ersstJson from "#data/noaa-ersst.json";
import oisstJson from "#data/noaa-oisst.json";
import glofasJson from "#data/open-meteo-glofas.json";
import datasetSchema from "../../../schema/dataset.schema.json";
import type { Dataset } from "~/types/dataset";
import type { AnyDataset, DatasetFor, DatasetId, DatasetRecordMap } from "~/types/datasets";

const rawDatasets: Record<DatasetId, unknown> = {
  "noaa-cpc-oni": oniJson,
  "noaa-cpc-nino-weekly": weeklyJson,
  "noaa-cpc-outlook": outlookJson,
  "enfen-communique": enfenJson,
  "limites-inei-ign": geometryJson,
  "noaa-oisst": oisstJson,
  "open-meteo-glofas": glofasJson,
  "noaa-ersst": ersstJson,
};

const ajv = new Ajv2020({ allErrors: true, strict: false });
const validateSchema = ajv.compile<Dataset>(datasetSchema);

const invalid = (id: DatasetId, detail: string): never => {
  throw new Error(`[useDataset] data/${id}.json is invalid: ${detail}`);
};

const schemaErrors = () =>
  (validateSchema.errors ?? [])
    .map((error) => `${error.instancePath || "$"} ${error.message ?? "is invalid"}`)
    .join("; ");

export const validateDataset = <Id extends DatasetId>(id: Id, value: unknown): DatasetFor<Id> => {
  if (!validateSchema(value)) invalid(id, schemaErrors());
  if ((value as Dataset).id !== id) {
    invalid(id, `id is ${(value as Dataset).id}, expected ${id}`);
  }
  return value as DatasetFor<Id>;
};

const datasets = Object.fromEntries(
  (Object.keys(rawDatasets) as DatasetId[]).map((id) => [id, validateDataset(id, rawDatasets[id])]),
) as { [Id in DatasetId]: DatasetFor<Id> };

/** Loads one schema-validated JSON dataset at build time with its id-specific record type. */
export const useDataset = <Id extends DatasetId>(id: Id): DatasetFor<Id> => {
  const dataset = datasets[id] as AnyDataset | undefined;
  if (!dataset) {
    throw new Error(`[useDataset] data/${id}.json was not found in the static dataset catalog`);
  }
  return dataset as DatasetFor<Id>;
};

export type DatasetRecordFor<Id extends DatasetId> = DatasetRecordMap[Id];
