import Ajv2020 from 'ajv/dist/2020'
import datasetSchema from '../../../schema/dataset.schema.json'
import type { Dataset } from '~/types/dataset'
import type { DatasetFor, DatasetId } from '~/types/datasets'

const datasetLoaders: { [Id in DatasetId]: () => Promise<unknown> } = {
  'noaa-cpc-oni': () => import('#data/noaa-cpc-oni.json').then(({ default: value }) => value),
  'noaa-cpc-nino-weekly': () =>
    import('#data/noaa-cpc-nino-weekly.json').then(({ default: value }) => value),
  'noaa-cpc-outlook': () =>
    import('#data/noaa-cpc-outlook.json').then(({ default: value }) => value),
  'enfen-communique': () =>
    import('#data/enfen-communique.json').then(({ default: value }) => value),
  'limites-inei-ign': () =>
    import('#data/limites-inei-ign.json').then(({ default: value }) => value),
  chirps: () => import('#data/chirps.json').then(({ default: value }) => value),
  'open-meteo-era5': () => import('#data/open-meteo-era5.json').then(({ default: value }) => value),
  'noaa-oisst': () => import('#data/noaa-oisst.json').then(({ default: value }) => value),
  'open-meteo-glofas': () =>
    import('#data/open-meteo-glofas.json').then(({ default: value }) => value),
  'noaa-ersst': () => import('#data/noaa-ersst.json').then(({ default: value }) => value),
}

const ajv = new Ajv2020({ allErrors: true, strict: false })
const validateSchema = ajv.compile<Dataset>(datasetSchema)

const invalid = (id: DatasetId, detail: string): never => {
  throw new Error(`[useDataset] data/${id}.json is invalid: ${detail}`)
}

const schemaErrors = () =>
  (validateSchema.errors ?? [])
    .map((error) => `${error.instancePath || '$'} ${error.message ?? 'is invalid'}`)
    .join('; ')

export const validateDataset = <Id extends DatasetId>(id: Id, value: unknown): DatasetFor<Id> => {
  if (!validateSchema(value)) invalid(id, schemaErrors())
  if ((value as Dataset).id !== id) {
    invalid(id, `id is ${(value as Dataset).id}, expected ${id}`)
  }
  return value as DatasetFor<Id>
}

export const loadDataset = async <Id extends DatasetId>(id: Id): Promise<DatasetFor<Id>> => {
  const loader = datasetLoaders[id]
  if (!loader) {
    throw new Error(`[useDataset] data/${id}.json was not found in the static dataset catalog`)
  }
  return validateDataset(id, await loader())
}
