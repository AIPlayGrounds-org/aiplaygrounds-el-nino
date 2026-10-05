import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import Ajv2020 from 'ajv/dist/2020'
import datasetSchema from '../../../schema/dataset.schema.json'
import type { Dataset } from '~/types/dataset'
import type { DatasetFor, DatasetId, DatasetRecordMap } from '~/types/datasets'

// The build runs from web/, so the pipeline's data/ directory is one level up.
// Reading the files keeps them out of the bundler, which turns JSON into JavaScript
// and needs gigabytes of memory for the largest datasets.
const dataDirectory = resolve(process.cwd(), '..', 'data')

const datasetIds = [
  'noaa-cpc-oni',
  'noaa-cpc-nino-weekly',
  'noaa-cpc-outlook',
  'enfen-communique',
  'enfen-icen',
  'limites-inei-ign',
  'chirps',
  'open-meteo-era5',
  'noaa-oisst',
  'open-meteo-glofas',
  'noaa-ersst',
  'senamhi-estaciones',
] as const satisfies readonly DatasetId[]

const readDataset = async (id: DatasetId): Promise<unknown> =>
  JSON.parse(await readFile(resolve(dataDirectory, `${id}.json`), 'utf8'))

export const isDatasetId = (id: string): id is DatasetId =>
  (datasetIds as readonly string[]).includes(id)

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
  if (!isDatasetId(id)) {
    throw new Error(`[useDataset] data/${id}.json was not found in the static dataset catalog`)
  }
  const dataset = validateDataset(id, await readDataset(id))
  return id === 'enfen-communique'
    ? (recomputeEnfenStale(dataset as DatasetFor<'enfen-communique'>, now) as DatasetFor<Id>)
    : dataset
}
