import { useAsyncData } from "#imports";
import type { DatasetFor, DatasetId, DatasetRecordMap } from "~/types/datasets";

/**
 * Loads one schema-validated JSON dataset on the server and hydrates it from the Nuxt payload.
 * `shape` runs on the server before serialization, so the payload carries only what the page uses.
 * It may return a narrower or extended dataset.
 */
export const useDataset = async <Id extends DatasetId, Shaped = DatasetFor<Id>>(
  id: Id,
  shape?: (dataset: DatasetFor<Id>) => Shaped,
): Promise<Shaped> => {
  const { data, error } = await useAsyncData<Shaped>(`dataset:${id}`, async () => {
    const isServer = (import.meta as ImportMeta & { readonly server: boolean }).server;
    if (!isServer) {
      throw new Error(`[useDataset] data/${id}.json was not loaded in the server payload`);
    }
    const { loadDataset } = await import("~/../server/utils/loadDataset");
    const dataset = await loadDataset(id);
    return shape ? shape(dataset) : (dataset as Shaped);
  });

  if (error.value) throw error.value;
  if (!data.value) {
    throw new Error(`[useDataset] data/${id}.json was not found in the server payload`);
  }
  return data.value as Shaped;
};

export type DatasetRecordFor<Id extends DatasetId> = DatasetRecordMap[Id];
