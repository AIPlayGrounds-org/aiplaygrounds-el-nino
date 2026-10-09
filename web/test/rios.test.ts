import { nextTick, defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import RiosChart from '~/components/RiosChart.vue'
import { messages } from '~/messages'
import {
  latestEstimatedRiverRecord,
  recordsForRiver,
  riverPoints,
  shapeRiosDataset,
} from '~/utils/rios'
import { loadDataset } from '../server/utils/loadDataset'

const passthrough = defineComponent({ template: '<div><slot /></div>' })

describe('rivers data shaping', () => {
  it('sorts shuffled records by point and date', async () => {
    const dataset = await loadDataset('open-meteo-glofas')
    const shuffled = { ...dataset, records: [...dataset.records].reverse() }
    const shaped = shapeRiosDataset(shuffled)

    expect(riverPoints(shaped.records)).toEqual([
      'Canete',
      'Chillon',
      'Chira',
      'Ica',
      'Majes-Colca',
      'Mantaro',
      'Pisco',
      'Piura',
      'Rimac',
      'Santa',
      'Tumbes',
    ])
    const piura = recordsForRiver(shaped.records, 'Piura')
    expect(piura[0]?.start).toBe('2026-09-26')
    expect(piura.at(-1)?.start).toBe('2027-04-30')
    expect(JSON.stringify(shaped).length).toBeLessThan(JSON.stringify(dataset).length / 2)
  })

  it('ignores missing and forecast values when finding the latest estimate', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const piura = recordsForRiver(dataset.records, 'Piura')
    const latest = latestEstimatedRiverRecord(piura)

    expect(piura.at(-1)?.river_discharge).toBeNull()
    expect(latest?.start).toBe('2026-10-03')
    expect(latestEstimatedRiverRecord([])).toBeUndefined()
    expect(recordsForRiver(dataset.records, 'missing')).toEqual([])
  })
})

describe('RiosChart', () => {
  it('shows a Spanish empty state without rendering a chart or empty table', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const empty = { ...dataset, records: [] } as unknown as typeof dataset
    const wrapper = mount(RiosChart, {
      props: { dataset: empty },
      global: { stubs: { ClientOnly: passthrough, NuxtErrorBoundary: passthrough } },
    })

    expect(wrapper.text()).toContain(messages.rios.emptySummary(''))
    expect(wrapper.find('.chart').exists()).toBe(false)
    expect(wrapper.find('table').exists()).toBe(false)
    expect(wrapper.text()).not.toMatch(/NaN|undefined/)
  })

  it('renders the point selector and updates the chart and table with real data', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const options: { series: { name: string }[] }[] = []
    const EchartsStub = defineComponent({
      name: 'EchartsStub',
      props: { option: { type: Object, required: true } },
      setup(props) {
        options.push(props.option as { series: { name: string }[] })
        return () => null
      },
    })
    const wrapper = mount(RiosChart, {
      props: { dataset },
      global: {
        stubs: {
          ClientOnly: passthrough,
          NuxtErrorBoundary: passthrough,
          VChart: EchartsStub,
          echarts: EchartsStub,
        },
      },
    })

    expect(wrapper.find('select').element.value).toBe('Canete')
    expect(wrapper.findAll('select option')).toHaveLength(11)
    expect(wrapper.findAll('tbody tr')).toHaveLength(217)
    expect(wrapper.text()).toContain('Sin dato')
    expect(wrapper.find('tbody tr').text()).toContain('No aplica')
    expect(options[0]?.series.map((series) => series.name)).toContain('Pronóstico del modelo')
    expect(wrapper.text()).toContain('Canete · 1.67 m³/s · 3 de octubre de 2026')
    expect(wrapper.text()).toContain('4 de octubre de 2026')

    await wrapper.find('select').setValue('Mantaro')
    await nextTick()

    expect(wrapper.find('select').element.value).toBe('Mantaro')
    expect(wrapper.find('caption').text()).toContain('Mantaro')
  })
})
