import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import HistoricoChart from '~/components/HistoricoChart.vue'
import ChartShell from '~/components/ChartShell.vue'
import { messages } from '~/messages'
import { shapeHistoricoDataset, shapeHistoricoOniDataset } from '~/utils/historico'
import { loadDataset } from '../server/utils/loadDataset'

const passthrough = { template: '<div><slot /></div>' }

describe('HistoricoChart', () => {
  it('renders selectors, the ONI series, and the ERSST table fallback', async () => {
    const [ersst, oni] = await Promise.all([
      loadDataset('noaa-ersst').then(shapeHistoricoDataset),
      loadDataset('noaa-cpc-oni').then(shapeHistoricoOniDataset),
    ])
    const options: { series: { name: string }[] }[] = []
    const chartStub = {
      props: ['option'],
      setup(props: { option: { series: { name: string }[] } }) {
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
    expect(wrapper.find('details').exists()).toBe(true)
    expect(options).toHaveLength(2)
    expect(options[0]!.series).toHaveLength(4)
    expect(options[1]!.series.map((series) => series.name)).not.toEqual(
      expect.arrayContaining([expect.stringContaining('2017')]),
    )
  })
})
