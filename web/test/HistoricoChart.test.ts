import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import HistoricoChart from '~/components/HistoricoChart.vue'
import ChartShell from '~/components/ChartShell.vue'
import { messages } from '~/messages'
import { shapeHistoricoDataset, shapeHistoricoOniDataset } from '~/utils/historico'
import { loadDataset } from '../server/utils/loadDataset'

const passthrough = { template: '<div><slot /></div>' }

describe('HistoricoChart', () => {
  it('shows a Spanish empty state for both missing series without empty chart frames', async () => {
    const [ersst, oni] = await Promise.all([loadDataset('noaa-ersst'), loadDataset('noaa-cpc-oni')])
    const emptyErsst = { ...ersst, records: [] }
    const emptyOni = { ...oni, records: [] }
    const wrapper = mount(HistoricoChart, {
      props: { dataset: emptyErsst, oni: emptyOni },
      global: {
        components: { ChartShell },
        stubs: { ClientOnly: passthrough, NuxtErrorBoundary: passthrough, VChart: passthrough },
      },
    })

    expect(wrapper.findAll('.empty-state')).toHaveLength(2)
    expect(wrapper.text()).toContain(messages.historico.empty)
    expect(wrapper.find('.chart').exists()).toBe(false)
    expect(wrapper.text()).not.toMatch(/NaN|undefined/)
  })

  it('renders selectors, the ONI series, and the ERSST table fallback', async () => {
    const [fullErsst, fullOni] = await Promise.all([
      loadDataset('noaa-ersst'),
      loadDataset('noaa-cpc-oni'),
    ])
    const ersst = shapeHistoricoDataset(fullErsst)
    const oni = shapeHistoricoOniDataset(fullOni, ersst.records)
    const options: { series: { name: string; data: (number | null)[] }[] }[] = []
    const chartStub = {
      props: ['option'],
      setup(props: { option: { series: { name: string; data: (number | null)[] }[] } }) {
        options.push(props.option)
        return () => null
      },
    }
    const wrapper = mount(HistoricoChart, {
      props: { dataset: ersst, oni },
      global: {
        components: { ChartShell },
        stubs: {
          ClientOnly: passthrough,
          NuxtErrorBoundary: passthrough,
          VChart: chartStub,
          echarts: chartStub,
        },
      },
    })

    expect(wrapper.find('select').element.value).toBe('nino34')
    expect(wrapper.findAll('input[type="checkbox"]')).toHaveLength(4)
    expect(wrapper.text()).toContain(messages.historico.oniNote)
    expect(wrapper.findAll('details')).toHaveLength(2)
    expect(wrapper.findAll('tbody tr').length).toBeGreaterThan(0)
    expect(wrapper.text()).toContain('+0,5 °C')
    expect(wrapper.text()).toContain('+0,8 °C')
    expect(wrapper.text()).toContain(messages.historico.missing)
    expect(options).toHaveLength(2)
    expect(options[0]!.series).toHaveLength(4)
    const coastalSeries = options[0]!.series.find((series) => series.name.includes('2017'))
    expect(coastalSeries?.name).toContain(messages.historico.regions.nino12)
    expect(coastalSeries?.data[0]).toBe(0.93)
    expect(options[1]!.series.map((series) => series.name)).not.toEqual(
      expect.arrayContaining([expect.stringContaining('2017')]),
    )
  })
})
