<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { AriaComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { computed } from 'vue'
import ChartShell from '~/components/ChartShell.vue'
import TableFallback from '~/components/TableFallback.vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import { formatValue } from '~/utils/format'
import type { DatasetWithRecords } from '~/types/datasets'

use([LineChart, AriaComponent, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{ dataset: DatasetWithRecords<'enfen-icen'> }>()
const theme = useChartTheme()
const summary = messages.historico.icenSummary
const chartOption = computed(() => {
  const colors = theme.value
  return {
    aria: { enabled: true, label: { description: summary } },
    animation: false,
    textStyle: { color: colors.muted, fontFamily: colors.font },
    grid: { left: 48, right: 18, top: 24, bottom: 42 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: colors.surface,
      borderColor: colors.border,
      textStyle: { color: colors.text },
      formatter: (params: { axisValue: string; value: number }[]) => {
        const point = params[0]
        return point
          ? `${point.axisValue}<br/>${messages.historico.icenTooltip(formatValue(point.value))}`
          : ''
      },
    },
    xAxis: {
      type: 'category',
      data: props.dataset.records.map((record) => record.start),
      axisLine: { lineStyle: { color: colors.border } },
      axisLabel: { color: colors.muted, hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      name: messages.historico.icenValue,
      axisLabel: { color: colors.muted, formatter: (value: number) => formatValue(value) },
      splitLine: { lineStyle: { color: colors.grid } },
    },
    series: [
      {
        name: messages.historico.icenTitle,
        type: 'line',
        data: props.dataset.records.map((record) => record.icen),
        showSymbol: false,
        lineStyle: { width: 2, color: colors.accent },
        itemStyle: { color: colors.accent },
      },
    ],
  }
})
</script>

<template>
  <ChartShell :dataset="dataset" :summary="summary">
    <template v-if="dataset.records.length">
      <p class="icen-note">{{ messages.historico.icenNote }}</p>
      <NuxtErrorBoundary>
        <ClientOnly>
          <VChart class="chart" :option="chartOption" autoresize />
          <template #fallback>
            <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
          </template>
        </ClientOnly>
        <template #error>
          <div class="chart-placeholder">{{ messages.page.chartError }}</div>
        </template>
      </NuxtErrorBoundary>
      <TableFallback :label="messages.historico.icenTableSummary">
        <table>
          <caption>
            {{
              messages.historico.icenTableCaption
            }}
          </caption>
          <thead>
            <tr>
              <th scope="col">{{ messages.historico.icenMonth }}</th>
              <th scope="col">{{ messages.historico.icenValue }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in dataset.records" :key="record.start">
              <th scope="row">{{ record.start }}</th>
              <td>{{ formatValue(record.icen) }} {{ messages.historico.degreeC }}</td>
            </tr>
          </tbody>
        </table>
      </TableFallback>
    </template>
    <p v-else class="empty-state" role="status">{{ messages.historico.empty }}</p>
  </ChartShell>
</template>

<style scoped>
.icen-note {
  margin: 0 0 16px;
  color: var(--muted);
  font-size: 0.95rem;
}
</style>
