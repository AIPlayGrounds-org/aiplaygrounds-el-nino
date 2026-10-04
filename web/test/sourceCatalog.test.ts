import sourceCatalogJson from '~/data/source-catalog.json'
import { describe, expect, it } from 'vitest'
import { loadDataset } from '../server/utils/loadDataset'
import {
  sourceCatalogDatasetFixture,
  sourceCatalogRegistryFixture,
  sourceCatalogVocabularyFixture,
} from './fixtures/source-catalog'
import { buildSourceCatalog, validateSourceCatalog } from '~/utils/sourceCatalog'

describe('buildSourceCatalog', () => {
  it('groups multi-page sources while preserving registry ordering and links', () => {
    const catalog = buildSourceCatalog(
      sourceCatalogRegistryFixture,
      sourceCatalogDatasetFixture,
      sourceCatalogVocabularyFixture.routes,
    )
    const home = catalog.groups.find((group) => group.page === '/')
    const history = catalog.groups.find((group) => group.page === '/historico')
    const territory = catalog.groups.find((group) => group.page === '/territorio')

    expect(catalog.groups.map((group) => group.page)).toEqual(['/', '/historico', '/territorio'])
    expect(catalog.groups.map((group) => group.label)).toEqual([
      'Inicio',
      'Histórico',
      'Territorio',
    ])
    expect(home?.sources.map((source) => source.id)).toEqual(['noaa-cpc-oni', 'source-a'])
    expect(history?.sources.map((source) => source.id)).toEqual(['noaa-cpc-oni'])
    expect(territory?.sources.map((source) => source.id)).toEqual(['source-b'])
    expect(home?.sources[0]).toMatchObject({
      providerUrl: 'https://example.com/provider-oni',
      dataUrl: 'https://example.com/data-oni',
      license: 'CC BY 4.0. Attribution text kept in the registry.',
      lastUpdate: '2026-09-30T00:00:00+00:00',
    })
    expect(territory?.sources[0]).toMatchObject({
      referencePeriod: null,
      license: null,
      lastUpdate: '2026-10-01T00:00:00+00:00',
    })
  })

  it('rejects a source with no page assignment', () => {
    const unmapped = { ...sourceCatalogRegistryFixture[1]!, site_pages: [] }

    expect(() =>
      buildSourceCatalog(
        [unmapped],
        sourceCatalogDatasetFixture,
        sourceCatalogVocabularyFixture.routes,
      ),
    ).toThrow('source-b has no site page')
  })
})

describe('validateSourceCatalog', () => {
  it.each([
    ['data_type', { data_type: 'bogus' }],
    ['name', { name: '' }],
    ['site_pages', { site_pages: [] }],
    ['site_pages', { site_pages: ['/unlabelled'] }],
  ])('rejects an invalid %s field', (field, change) => {
    const source = { ...sourceCatalogRegistryFixture[0]!, ...change } as unknown as Record<
      string,
      unknown
    >

    expect(() =>
      validateSourceCatalog({ ...sourceCatalogVocabularyFixture, sources: [source] }),
    ).toThrow(field)
  })

  it('takes route labels from the generated vocabulary', () => {
    const document = validateSourceCatalog({
      ...sourceCatalogVocabularyFixture,
      sources: sourceCatalogRegistryFixture,
    })

    expect(document.routes).toEqual(sourceCatalogVocabularyFixture.routes)
  })
})

describe('generated source catalog', () => {
  it('takes the last update from the validated dataset loader', async () => {
    const document = validateSourceCatalog(sourceCatalogJson)
    const enfen = await loadDataset('enfen-communique')
    const source = document.sources.find((entry) => entry.id === enfen.id)!
    const catalog = buildSourceCatalog([source], [enfen], document.routes)

    expect(catalog.groups[0]?.sources[0]?.lastUpdate).toBe(enfen.ingestion_time)
  })
})
