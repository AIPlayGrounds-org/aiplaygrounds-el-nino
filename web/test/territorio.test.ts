import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import DatasetAttribution from '~/components/DatasetAttribution.vue'
import {
  aggregateEra5,
  joinTerritoryRows,
  latestChirpsPerDepartment,
  metricValue,
  shapeDepartmentGeometry,
  shapeEra5Summary,
  shapeLatestChirps,
} from '~/composables/territorio'
import { loadDataset } from '../server/utils/loadDataset'
import {
  territoryChirpsDatasetFixture,
  territoryChirpsFixture,
  territoryEra5Fixture,
  territoryEra5DatasetFixture,
  territoryGeometryFixture,
} from './fixtures/territory'

describe('territory data transformations', () => {
  it('keeps the latest CHIRPS pentad per department and exposes both metrics', () => {
    const latest = latestChirpsPerDepartment(territoryChirpsFixture)
    const amazonas = latest.find((record) => record.code === 'PE01')!

    expect(latest).toHaveLength(2)
    expect(amazonas.end).toBe('2026-09-30')
    expect(metricValue(amazonas, 'precipitation')).toBe(4.2)
    expect(metricValue(amazonas, 'anomaly')).toBe(1.4)
  })

  it('counts the ERA5 window and refuses a sum when a day is null', () => {
    const aggregate = aggregateEra5(
      territoryEra5Fixture,
      territoryGeometryFixture.records[0]!.departamentos.features,
    )
    const amazonas = aggregate.departments.find((record) => record.code === 'PE01')!
    const lima = aggregate.departments.find((record) => record.code === 'PE15')!

    expect(aggregate.window).toEqual({ start: '2026-07-06', end: '2026-07-08', days: 3 })
    expect(amazonas).toMatchObject({ total: null, availableDays: 2, missingDays: 1 })
    expect(lima).toMatchObject({ total: 4.5, availableDays: 3, missingDays: 0 })
  })

  it('joins boundaries, latest CHIRPS and ERA5 rows by department code', () => {
    const latest = latestChirpsPerDepartment(territoryChirpsFixture)
    const era5 = aggregateEra5(
      territoryEra5Fixture,
      territoryGeometryFixture.records[0]!.departamentos.features,
    )
    const rows = joinTerritoryRows(territoryGeometryFixture.records[0]!, latest, era5.departments)
    const lima = rows.find((row) => row.code === 'PE15')!

    expect(rows.map((row) => row.code)).toEqual(['PE01', 'PE15'])
    expect(lima.region).toBe('Lima')
    expect(lima.chirps?.precipitation_mm).toBe(0.3)
    expect(lima.era5?.total).toBe(4.5)
  })

  it('keeps departments without ERA5 records and marks the whole window incomplete', () => {
    const withoutLima = territoryEra5Fixture.filter((record) => record.code !== 'PE15')
    const aggregate = aggregateEra5(
      withoutLima,
      territoryGeometryFixture.records[0]!.departamentos.features,
    )
    const lima = aggregate.departments.find((record) => record.code === 'PE15')!
    const rows = joinTerritoryRows(
      territoryGeometryFixture.records[0]!,
      latestChirpsPerDepartment(territoryChirpsFixture),
      aggregate.departments,
    )

    expect(aggregate.departments.map((record) => record.code)).toEqual(['PE01', 'PE15'])
    expect(lima).toMatchObject({ total: null, availableDays: 0, missingDays: 3 })
    expect(rows.find((row) => row.code === 'PE15')?.era5?.total).toBeNull()
  })

  it('keeps empty dataset shapes empty instead of manufacturing undefined records', () => {
    const emptyGeometry = {
      ...territoryGeometryFixture,
      records: [],
    } as unknown as typeof territoryGeometryFixture
    const emptyChirps = {
      ...territoryChirpsDatasetFixture,
      records: [],
    } as unknown as typeof territoryChirpsDatasetFixture
    const emptyEra5 = {
      ...territoryEra5DatasetFixture,
      records: [],
    } as unknown as typeof territoryEra5DatasetFixture

    expect(shapeDepartmentGeometry(emptyGeometry).records).toEqual([])
    expect(shapeLatestChirps(emptyChirps).records).toEqual([])
    expect(shapeEra5Summary([])(emptyEra5).records).toEqual([])
  })

  it('keeps only the latest CHIRPS pentad per department, oldest first', () => {
    const shaped = shapeLatestChirps(territoryChirpsDatasetFixture)

    expect(shaped.records.map((record) => [record.code, record.end])).toEqual([
      ['PE01', '2026-09-30'],
      ['PE15', '2026-09-30'],
    ])
    expect(shaped.source).toEqual(territoryChirpsDatasetFixture.source)
  })

  it('drops the province layer and keeps the newest boundary record', () => {
    const shaped = shapeDepartmentGeometry(territoryGeometryFixture)

    expect(shaped.records).toHaveLength(1)
    expect('provincias' in shaped.records[0]).toBe(false)
    expect(shaped.records[0].departamentos.features).toHaveLength(2)
    expect(shaped.records[0].license_url).toBe('https://example.com/license')
  })

  it('summarises ERA5 per department and bounds the period with two records', () => {
    const shaped = shapeEra5Summary(territoryGeometryFixture.records[0]!.departamentos.features)(
      territoryEra5DatasetFixture,
    )

    expect(shaped.records.map((record) => record.start)).toEqual(['2026-07-06', '2026-07-08'])
    expect(shaped.window).toEqual({ start: '2026-07-06', end: '2026-07-08', days: 3 })
    expect(shaped.departments.map((record) => record.total)).toEqual([null, 4.5])
  })

  it('shrinks the payload of the real datasets the page loads', async () => {
    const size = (value: unknown) => JSON.stringify(value).length
    const geometry = await loadDataset('limites-inei-ign')
    const chirps = await loadDataset('chirps')
    const era5 = await loadDataset('open-meteo-era5')
    const departments = geometry.records.at(-1)!.departamentos.features

    const shapedGeometry = shapeDepartmentGeometry(geometry)
    const shapedChirps = shapeLatestChirps(chirps)
    const shapedEra5 = shapeEra5Summary(departments)(era5)

    expect(size(shapedGeometry)).toBeLessThan(size(geometry) / 2)
    expect(size(shapedChirps)).toBeLessThan(size(chirps) / 10)
    expect(size(shapedEra5)).toBeLessThan(size(era5) / 5)
    expect(shapedChirps.records).toHaveLength(departments.length)
    expect(shapedEra5.departments).toHaveLength(departments.length)
  })
})

describe('DatasetAttribution', () => {
  it('links Open-Meteo and credits ERA5 and Copernicus without repeating the source', () => {
    const wrapper = mount(DatasetAttribution, {
      props: { dataset: territoryEra5DatasetFixture },
    })
    const link = wrapper.get('a')

    expect(link.text()).toContain('Weather data by Open-Meteo.com')
    expect(link.attributes('href')).toBe('https://open-meteo.com/')
    expect(wrapper.text()).toContain('ERA5')
    expect(wrapper.text()).toContain('Copernicus Climate Change Service')
    expect(wrapper.text()).not.toContain(territoryEra5DatasetFixture.source.product)
  })

  it('credits GloFAS with the Copernicus Emergency Management Service', async () => {
    const wrapper = mount(DatasetAttribution, {
      props: { dataset: await loadDataset('open-meteo-glofas') },
    })

    expect(wrapper.get('a').attributes('href')).toBe('https://open-meteo.com/')
    expect(wrapper.text()).toContain('Copernicus Emergency Management Service')
  })

  it('prints nothing for a dataset that is not from Open-Meteo', () => {
    const wrapper = mount(DatasetAttribution, {
      props: { dataset: territoryChirpsDatasetFixture },
    })

    expect(wrapper.find('a').exists()).toBe(false)
    expect(wrapper.text()).toBe('')
  })
})
