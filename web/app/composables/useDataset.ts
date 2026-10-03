import { useAsyncData } from "#imports";
import type { DatasetFor, DatasetId, DatasetRecordMap } from "~/types/datasets";

/**
 * Loads one schema-validated JSON dataset on the server and hydrates it from the Nuxt payload.
 * `shape` runs on the server before serialization, so the payload carries only what the page uses.
 */
export const useDataset = async <Id extends DatasetId>(
  id: Id,
  shape: (dataset: DatasetFor<Id>) => DatasetFor<Id> = (dataset) => dataset,
): Promise<DatasetFor<Id>> => {
  const { data, error } = await useAsyncData<DatasetFor<Id>>(`dataset:${id}`, async () => {
    const isServer = (import.meta as ImportMeta & { readonly server: boolean }).server;
    if (!isServer) {
      throw new Error(`[useDataset] data/${id}.json was not loaded in the server payload`);
    }
    const { loadDataset } = await import("~/../server/utils/loadDataset");
    return shape(await loadDataset(id));
  });

  if (error.value) throw error.value;
  if (!data.value) {
    throw new Error(`[useDataset] data/${id}.json was not found in the server payload`);
  }
  return data.value;
};

export type DatasetRecordFor<Id extends DatasetId> = DatasetRecordMap[Id];
