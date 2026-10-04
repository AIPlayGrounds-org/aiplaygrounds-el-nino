import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import IcenChart from '~/components/IcenChart.vue'
import { messages } from '~/messages'
import { loadDataset } from '../server/utils/loadDataset'

const passthrough = { template: '<div><slot /></div>' }

describe('IcenChart', () => {
  it('renders an ICEN chart and table fallback with its own source copy', async () => {
    const dataset = await loadDataset('enfen-icen')
    const options: { series: { name: string; data: number[] }[] }[] = []
    const chartStub = {
      props: ['option'],
      setup(props: { option: { series: { name: string; data: number[] }[] } }) {
        options.push(props.option)
        return () => null
      },
    }

    const wrapper = mount(IcenChart, {
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

    expect(wrapper.text()).toContain(messages.historico.icenNote)
    expect(wrapper.text()).toContain(messages.historico.icenTableCaption)
    expect(wrapper.findAll('details')).toHaveLength(1)
    expect(options).toHaveLength(1)
    expect(options[0]?.series[0]?.data).toHaveLength(dataset.records.length)
    expect(options[0]?.series[0]?.data[0]).toBe(-0.75)
    expect(wrapper.get('.provenance').text()).toContain(dataset.source.institution)
  })
})
