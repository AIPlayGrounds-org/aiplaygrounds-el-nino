type Schema = {
  allOf?: {
    if: { properties: { id: { const: string } } }
    then: { properties: { records: { items: { $ref: string } } } }
  }[]
  $defs: Record<string, { title?: string }>
}

const GENERIC_RECORD = 'DatasetRecord'

/** The record type of each source id: the schema's `allOf` rule, or the generic record. */
export function recordTypes(schema: Schema, ids: readonly string[]): Record<string, string> {
  const named: Record<string, string> = {}
  for (const rule of schema.allOf ?? []) {
    const ref = rule.then.properties.records.items.$ref
    const title = schema.$defs[ref.replace('#/$defs/', '')]?.title
    if (!title) throw new Error(`${ref} has no title to name its record type`)
    named[rule.if.properties.id.const] = title
  }
  const unknown = Object.keys(named).filter((id) => !ids.includes(id))
  if (unknown.length) {
    throw new Error(`The schema maps ids that are not in the source catalog: ${unknown.join(', ')}`)
  }
  return Object.fromEntries(ids.map((id) => [id, named[id] ?? GENERIC_RECORD]))
}

export type CatalogSource = { id: string; stale_after_hours?: number }

/** The ids, the record type of each and its update tolerance, appended to the generated types. */
export function datasetIdsSource(schema: Schema, sources: readonly CatalogSource[]): string {
  const ids = sources.map((source) => source.id)
  const records = recordTypes(schema, ids)
  const key = (id: string) => (/^[a-z]+$/.test(id) ? id : `'${id}'`)
  return [
    '',
    'export const datasetIds = [',
    ...ids.map((id) => `  '${id}',`),
    '] as const',
    '',
    'export type DatasetId = (typeof datasetIds)[number]',
    '',
    'export type DatasetRecordMap = {',
    ...ids.map((id) => `  ${key(id)}: ${records[id]}`),
    '}',
    '',
    '/** Hours after which a published dataset counts as late. Sources updated by hand have none. */',
    'export const staleAfterHours: Partial<Record<DatasetId, number>> = {',
    ...sources.flatMap((source) =>
      source.stale_after_hours === undefined
        ? []
        : [`  ${key(source.id)}: ${source.stale_after_hours},`],
    ),
    '}',
    '',
  ].join('\n')
}
