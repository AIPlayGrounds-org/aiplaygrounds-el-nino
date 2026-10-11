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
      'Jequetepeque',
      'Majes-Colca',
      'Mantaro',
      'Pisco',
      'Piura',
      'Rimac',
      'Santa',
      'Tumbes',
    ])
    const piura = recordsForRiver(shaped.records, 'Piura')
    const dates = piura.map((record) => record.start)
    expect(piura.length).toBeGreaterThan(0)
    expect(dates).toEqual([...dates].sort())
    expect(piura[0]?.start).toBe(dates[0])
    expect(piura.at(-1)?.start).toBe(dates.at(-1))
    expect(JSON.stringify(shaped).length).toBeLessThan(JSON.stringify(dataset).length / 2)
  })

  it('ignores missing and forecast values when finding the latest estimate', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const piura = recordsForRiver(dataset.records, 'Piura')
    const latest = latestEstimatedRiverRecord(piura)

    const estimated = piura.filter((record) => record.data_type === 'estimated')
    expect(estimated.length).toBeGreaterThan(0)
    expect(latest).toEqual(estimated.at(-1))
    expect(latest?.river_discharge).not.toBeNull()
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

    const canete = recordsForRiver(dataset.records, 'Canete')
    expect(wrapper.find('select').element.value).toBe('Canete')
    expect(wrapper.findAll('select option')).toHaveLength(riverPoints(dataset.records).length)
    expect(wrapper.findAll('tbody tr')).toHaveLength(canete.length)
    expect(wrapper.text()).toContain('Sin dato')
    expect(wrapper.find('tbody tr').text()).toContain('No aplica')
    expect(options[0]?.series.map((series) => series.name)).toContain('Pronóstico del modelo')
    expect(wrapper.text()).toContain('Canete · ')
    expect(wrapper.text()).toContain('m³/s')

    await wrapper.find('select').setValue('Mantaro')
    await nextTick()

    expect(wrapper.find('select').element.value).toBe('Mantaro')
    expect(wrapper.find('caption').text()).toContain('Mantaro')
  })
})
