import Ajv2020 from 'ajv/dist/2020'
import datasetSchema from '../../../schema/dataset.schema.json'
import type { Dataset } from '~/types/dataset'
import type { DatasetFor, DatasetId, DatasetRecordMap } from '~/types/datasets'

const datasetLoaders: { [Id in DatasetId]: () => Promise<unknown> } = {
  'noaa-cpc-oni': () => import('#data/noaa-cpc-oni.json').then(({ default: value }) => value),
  'noaa-cpc-nino-weekly': () =>
    import('#data/noaa-cpc-nino-weekly.json').then(({ default: value }) => value),
  'noaa-cpc-outlook': () =>
    import('#data/noaa-cpc-outlook.json').then(({ default: value }) => value),
  'enfen-communique': () =>
    import('#data/enfen-communique.json').then(({ default: value }) => value),
  'enfen-icen': () => import('#data/enfen-icen.json').then(({ default: value }) => value),
  'limites-inei-ign': () =>
    import('#data/limites-inei-ign.json').then(({ default: value }) => value),
  chirps: () => import('#data/chirps.json').then(({ default: value }) => value),
  'open-meteo-era5': () => import('#data/open-meteo-era5.json').then(({ default: value }) => value),
  'noaa-oisst': () => import('#data/noaa-oisst.json').then(({ default: value }) => value),
  'open-meteo-glofas': () =>
    import('#data/open-meteo-glofas.json').then(({ default: value }) => value),
  'noaa-ersst': () => import('#data/noaa-ersst.json').then(({ default: value }) => value),
  'senamhi-estaciones': () =>
    import('#data/senamhi-estaciones.json').then(({ default: value }) => value),
}

export const isDatasetId = (id: string): id is DatasetId => Object.hasOwn(datasetLoaders, id)

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

// ENFEN publishes in Lima, which has no daylight saving time.
const limaDay = (now: Date) =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima' }).format(now)

/** The published `stale` flag dates from the last pipeline run; a build compares `end` with its own Lima day. */
export const recomputeEnfenStale = (
  dataset: DatasetFor<'enfen-communique'>,
  now: Date,
): DatasetFor<'enfen-communique'> => {
  const today = limaDay(now)
  const refresh = (record: DatasetRecordMap['enfen-communique']) => ({
    ...record,
    stale: today > record.end,
  })
  const [first, ...rest] = dataset.records
  return { ...dataset, records: [refresh(first), ...rest.map(refresh)] }
}

export const loadDataset = async <Id extends DatasetId>(
  id: Id,
  now: Date = new Date(),
): Promise<DatasetFor<Id>> => {
  const loader = datasetLoaders[id]
  if (!loader) {
    throw new Error(`[useDataset] data/${id}.json was not found in the static dataset catalog`)
  }
  const dataset = validateDataset(id, await loader())
  return id === 'enfen-communique'
    ? (recomputeEnfenStale(dataset as DatasetFor<'enfen-communique'>, now) as DatasetFor<Id>)
    : dataset
}
