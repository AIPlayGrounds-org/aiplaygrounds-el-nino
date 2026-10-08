import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ChartShell from '~/components/ChartShell.vue'
import { ageDays, ageLabel, messages } from '~/messages'
import { staleAfterHours } from '~/types/dataset'
import { geometryFixture } from './fixtures/geometry'
import { gridFixture } from './fixtures/grid'
import { timeSeriesFixture } from './fixtures/time-series'

describe('ChartShell', () => {
  afterEach(() => vi.useRealTimers())

  it.each([
    ['time series', timeSeriesFixture],
    ['grid', gridFixture],
    ['geometry', geometryFixture],
  ])('renders provenance for a %s fixture', async (_kind, dataset) => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-10-03T00:00:00Z'))
    const wrapper = mount(ChartShell, {
      props: { dataset, summary: 'Resumen accesible de prueba' },
      slots: { default: '<div data-chart>chart</div>' },
    })
    await nextTick()

    expect(wrapper.find('[data-chart]').exists()).toBe(true)
    expect(wrapper.text()).toContain(dataset.variable)
    expect(wrapper.text()).toContain(dataset.unit)
    expect(wrapper.text()).toContain(dataset.temporal_resolution)
    expect(wrapper.text()).toContain(messages.dataType[dataset.data_type])
    expect(wrapper.text()).toContain(dataset.source.institution)
    const first = dataset.records[0]!
    const last = dataset.records.at(-1)!
    const coverage = first.start === last.end ? first.start : `${first.start}–${last.end}`
    expect(wrapper.get('.provenance').text()).toContain(coverage)
    const dataAge = wrapper.get('.data-age').text()
    expect(dataAge).toContain(`${messages.provenance.latestData}: ${last.end}`)
    expect(dataAge.includes(coverage)).toBe(coverage === last.end)
    expect(wrapper.text()).toContain('hace 2 días')
    expect(wrapper.text()).toContain('Resumen accesible de prueba')
  })

  it('ages a monthly record from the end of its month', () => {
    expect(ageLabel('2026-08', new Date('2026-10-03T00:00:00Z'))).toBe('hace 1 mes')
  })

  it('does not stale a monthly record 85 days after month-end', async () => {
    vi.useFakeTimers()
    const now = new Date('2026-09-23T00:00:00Z')
    vi.setSystemTime(now)
    const dataset = JSON.parse(JSON.stringify(timeSeriesFixture)) as typeof timeSeriesFixture
    dataset.ingestion_time = '2026-09-01T00:00:00Z'
    dataset.records.at(-1)!.end = '2026-06'

    expect(ageDays('2026-06', now)).toBe(85)
    expect(
      Math.floor((now.getTime() - new Date('2026-06-01T00:00:00Z').getTime()) / 86_400_000),
    ).toBe(114)
    const wrapper = mount(ChartShell, {
      props: { dataset, summary: 'Resumen accesible de prueba' },
      slots: { default: '<div data-chart>chart</div>' },
    })
    await nextTick()

    expect(wrapper.find('.stale-notice').exists()).toBe(false)
  })

  const now = new Date('2026-10-03T00:00:00Z')
  const mountAt = async (change: (dataset: typeof timeSeriesFixture) => void) => {
    vi.useFakeTimers()
    vi.setSystemTime(now)
    const dataset = JSON.parse(JSON.stringify(timeSeriesFixture)) as typeof timeSeriesFixture
    change(dataset)
    const wrapper = mount(ChartShell, {
      props: { dataset, summary: 'Resumen accesible de prueba' },
      slots: { default: '<div data-chart>chart</div>' },
    })
    await nextTick()
    return wrapper
  }
  const hoursAgo = (hours: number) => new Date(now.getTime() - hours * 3_600_000).toISOString()

  it.each([
    ['noaa-cpc-oni', 'monthly'],
    ['noaa-cpc-nino-weekly', 'weekly'],
    ['open-meteo-era5', 'daily'],
  ] as const)('stales a %s dataset only past its registry tolerance (%s)', async (id) => {
    const limit = staleAfterHours[id]!

    const onTime = await mountAt((dataset) => {
      dataset.id = id
      dataset.ingestion_time = hoursAgo(limit)
    })
    const late = await mountAt((dataset) => {
      dataset.id = id
      dataset.ingestion_time = hoursAgo(limit + 1)
    })

    expect(onTime.find('.stale-notice').exists()).toBe(false)
    expect(late.get('.stale-notice').text()).toContain(messages.provenance.staleSource)
  })

  it('has no update tolerance for a source that is updated by hand', async () => {
    expect(staleAfterHours['enfen-communique']).toBeUndefined()

    const wrapper = await mountAt((dataset) => {
      dataset.id = 'enfen-communique'
      dataset.ingestion_time = hoursAgo(24 * 400)
    })

    expect(wrapper.find('.stale-notice').exists()).toBe(false)
  })

  it.each([
    [89, false],
    [90, true],
    [91, true],
  ])('shows the stale notice for a record %i days old: %s', async (days, stale) => {
    const date = new Date(now.getTime() - days * 86_400_000).toISOString().slice(0, 10)

    const wrapper = await mountAt((dataset) => {
      dataset.ingestion_time = hoursAgo(1)
      dataset.records.at(-1)!.end = date
    })

    expect(wrapper.find('.stale-notice').exists()).toBe(stale)
  })
})
