import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChartShell from '~/components/ChartShell.vue'
import OisstMap from '~/components/OisstMap.vue'
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'
import { buildOisstMap, cropOisst, formatBand, summarizeOisst } from '~/utils/oisstMap'
import { gridFixture } from './fixtures/grid'

const withAnomaly = (anomaly: (number | null)[][]): DatasetFor<'noaa-oisst'> => ({
  ...gridFixture,
  records: [{ ...gridFixture.records[0], anomaly }],
})

// ClientOnly is a Nuxt built-in; the chart itself needs a canvas, so only the static parts run here.
const mountMap = (dataset: DatasetFor<'noaa-oisst'>) =>
  mount(OisstMap, {
    props: { dataset },
    global: { components: { ChartShell }, stubs: { ClientOnly: true } },
  })

describe('OISST map data', () => {
  it('finds the warmest cell and describes it with directions', () => {
    const map = buildOisstMap(gridFixture.records[0])

    expect(map.warmest).toEqual({ lat: 0, lon: -79, value: 0.5 })
    expect(summarizeOisst(map, '2026-10-01', '°C')).toBe('Máxima +0,50 °C · 0° N, 79° O')
  })

  it('aggregates non-null cells into one-degree latitude bands', () => {
    const map = buildOisstMap(gridFixture.records[0])

    expect(map.bands).toEqual([
      { start: -1, end: 0, mean: 0.2, maximum: 0.2 },
      { start: 0, end: 1, mean: expect.closeTo(0.45), maximum: 0.5 },
    ])
    expect(formatBand(map.bands[0]!)).toBe('1° S–0° N')
  })

  it('has no warmest cell and no bands when every cell is null', () => {
    const map = buildOisstMap(
      withAnomaly([
        [null, null],
        [null, null],
      ]).records[0],
    )

    expect(map.points).toHaveLength(0)
    expect(map.warmest).toBeNull()
    expect(map.bands).toHaveLength(0)
    expect(summarizeOisst(map, '2026-10-01', '°C')).toBe(messages.oisst.empty('2026-10-01'))
  })

  it('crops the grid to the Peruvian coast window and keeps cells aligned', () => {
    const wide: DatasetFor<'noaa-oisst'> = {
      ...gridFixture,
      records: [
        {
          ...gridFixture.records[0],
          lat: [-30, -1, 0, 20],
          lon: [-100, -80, -79, -50],
          anomaly: [
            [9, 9, 9, 9],
            [9, 0.2, 0.1, 9],
            [9, 0.4, 0.5, 9],
            [9, 9, 9, 9],
          ],
        },
      ],
    }

    const [record] = cropOisst(wide).records

    expect(record.lat).toEqual([-1, 0])
    expect(record.lon).toEqual([-80, -79])
    expect(record.anomaly).toEqual([
      [0.2, 0.1],
      [0.4, 0.5],
    ])
  })
})

describe('OisstMap component', () => {
  it('renders the summary, provenance and band table for a grid fixture', () => {
    const wrapper = mountMap(gridFixture)

    expect(wrapper.text()).toContain('Máxima +0,50 °C')
    expect(wrapper.get('.provenance').text()).toContain(gridFixture.variable)
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
    expect(wrapper.get('summary').text()).toBe(messages.oisst.tableSummary)
  })

  it('shows the empty state instead of throwing when no cell has data', () => {
    const wrapper = mountMap(
      withAnomaly([
        [null, null],
        [null, null],
      ]),
    )

    expect(wrapper.text()).toContain(messages.oisst.empty('2026-10-01'))
    expect(wrapper.find('table').exists()).toBe(false)
  })

  it('shows the empty state instead of rendering a frame when the dataset has no records', () => {
    const empty = { ...gridFixture, records: [] } as unknown as DatasetFor<'noaa-oisst'>
    const wrapper = mountMap(empty)

    expect(wrapper.text()).toContain(messages.oisst.empty(messages.oisst.emptyPeriod))
    expect(wrapper.find('.map').exists()).toBe(false)
    expect(wrapper.text()).not.toMatch(/NaN|undefined/)
  })
})
