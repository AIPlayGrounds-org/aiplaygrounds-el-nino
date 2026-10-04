import { nextTick, defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import RiosChart from '~/components/RiosChart.vue'
import {
  latestAvailableRiverRecord,
  recordsForRiver,
  riverPoints,
  shapeRiosDataset,
} from '~/utils/rios'
import { loadDataset } from '../server/utils/loadDataset'

const passthrough = defineComponent({ template: '<div><slot /></div>' })

describe('rivers data shaping', () => {
  it('keeps the source point order and sorts each point by date', async () => {
    const dataset = await loadDataset('open-meteo-glofas')
    const shaped = shapeRiosDataset(dataset)

    expect(riverPoints(shaped.records)).toEqual([
      'Piura',
      'Tumbes',
      'Chira',
      'Rimac',
      'Santa',
      'Chillon',
      'Canete',
      'Ica',
      'Pisco',
      'Majes-Colca',
      'Mantaro',
    ])
    const piura = recordsForRiver(shaped.records, 'Piura')
    expect(piura[0]?.start).toBe('2026-09-26')
    expect(piura.at(-1)?.start).toBe('2027-04-30')
    expect(JSON.stringify(shaped).length).toBeLessThan(JSON.stringify(dataset).length / 2)
  })

  it('ignores missing discharge values when finding the latest value', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const piura = recordsForRiver(dataset.records, 'Piura')
    const latest = latestAvailableRiverRecord(piura)

    expect(piura.at(-1)?.river_discharge).toBeNull()
    expect(latest?.start).toBe('2027-04-04')
    expect(latestAvailableRiverRecord([])).toBeUndefined()
    expect(recordsForRiver(dataset.records, 'missing')).toEqual([])
  })
})

describe('RiosChart', () => {
  it('renders the point selector and updates the chart and table with real data', async () => {
    const dataset = shapeRiosDataset(await loadDataset('open-meteo-glofas'))
    const options: { series: { name: string }[] }[] = []
    const chartStub = defineComponent({
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
          VChart: chartStub,
          echarts: chartStub,
        },
      },
    })

    expect(wrapper.find('select').element.value).toBe('Piura')
    expect(wrapper.findAll('select option')).toHaveLength(11)
    expect(wrapper.findAll('tbody tr')).toHaveLength(217)
    expect(wrapper.text()).toContain('Sin dato')
    expect(options[0]?.series.map((series) => series.name)).toContain('Pronóstico del modelo')

    await wrapper.find('select').setValue('Mantaro')
    await nextTick()

    expect(wrapper.find('select').element.value).toBe('Mantaro')
    expect(wrapper.find('caption').text()).toContain('Mantaro')
  })
})
