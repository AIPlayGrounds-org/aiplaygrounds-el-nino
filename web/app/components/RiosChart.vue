<script setup lang="ts">
import { computed, ref } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  AriaComponent,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import ChartShell from '~/components/ChartShell.vue'
import DatasetAttribution from '~/components/DatasetAttribution.vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import { formatDay, formatDischarge } from '~/utils/format'
import {
  firstForecastRiverRecord,
  latestAvailableRiverRecord,
  recordsForRiver,
  riverPoints,
  riverRangeLabel,
  type RiosDataset,
  type RiosRecord,
} from '~/utils/rios'

use([
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  AriaComponent,
  CanvasRenderer,
])

const props = defineProps<{ dataset: RiosDataset }>()
const rios = messages.rios
const points = riverPoints(props.dataset.records)
const selectedPoint = ref(points[0] ?? '')
const records = computed(() => recordsForRiver(props.dataset.records, selectedPoint.value))
const latest = computed(() => latestAvailableRiverRecord(records.value))
const firstForecast = computed(() => firstForecastRiverRecord(records.value))
const theme = useChartTheme()

const displayValue = (value: number | null) =>
  value === null ? rios.noData : `${formatDischarge(value)} ${props.dataset.unit}`
const displayRange = (record: RiosRecord) => {
  const range = riverRangeLabel(record)
  return range
    ? `${formatDischarge(range[0]!)}–${formatDischarge(range[1]!)} ${props.dataset.unit}`
    : rios.noData
}

const summary = computed(() => {
  if (!latest.value) return rios.emptySummary(selectedPoint.value)
  return rios.summary(
    selectedPoint.value,
    formatDay(latest.value.end),
    formatDischarge(latest.value.river_discharge!),
    props.dataset.unit,
    firstForecast.value ? formatDay(firstForecast.value.start) : rios.noData,
  )
})

const option = computed(() => {
  const t = theme.value
  const series = records.value
  const rangeBase = series.map((record) => {
    const range = record.data_type === 'forecast' ? riverRangeLabel(record) : null
    return [record.start, range?.[0] ?? null]
  })
  const rangeWidth = series.map((record) => {
    const range = record.data_type === 'forecast' ? riverRangeLabel(record) : null
    return [record.start, range ? range[1]! - range[0]! : null]
  })

  return {
    aria: { enabled: true, label: { description: rios.chartAria(selectedPoint.value) } },
    textStyle: { color: t.muted, fontFamily: t.font },
    color: [t.accent, t.warm, t.seaEdge],
    legend: {
      data: [rios.estimatedSeries, rios.forecastSeries, rios.rangeSeries],
      textStyle: { color: t.muted },
      top: 0,
    },
    grid: { left: 60, right: 20, top: 48, bottom: 58 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      valueFormatter: (value: number | null) =>
        value === null ? rios.noData : `${formatDischarge(value)} ${props.dataset.unit}`,
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted, hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      name: props.dataset.unit,
      nameTextStyle: { color: t.muted, align: 'left' },
      axisLabel: { color: t.muted, formatter: formatDischarge },
      splitLine: { lineStyle: { color: t.grid } },
      min: 0,
    },
    dataZoom: [{ type: 'inside' }],
    series: [
      {
        name: rios.estimatedSeries,
        type: 'line',
        data: series.map((record) => [
          record.start,
          record.data_type === 'estimated' ? record.river_discharge : null,
        ]),
        showSymbol: false,
        connectNulls: false,
        lineStyle: { color: t.accent, width: 2 },
        itemStyle: { color: t.accent },
      },
      {
        name: rios.forecastSeries,
        type: 'line',
        data: series.map((record) => [
          record.start,
          record.data_type === 'forecast' ? record.river_discharge : null,
        ]),
        showSymbol: false,
        connectNulls: false,
        lineStyle: { color: t.warm, width: 2, type: 'dashed' },
        itemStyle: { color: t.warm },
      },
      {
        name: 'range-base',
        type: 'line',
        data: rangeBase,
        stack: 'forecast-range',
        showSymbol: false,
        silent: true,
        lineStyle: { opacity: 0 },
        areaStyle: { opacity: 0 },
        tooltip: { show: false },
      },
      {
        name: rios.rangeSeries,
        type: 'line',
        data: rangeWidth,
        stack: 'forecast-range',
        showSymbol: false,
        silent: true,
        lineStyle: { opacity: 0 },
        areaStyle: { color: t.seaEdge, opacity: 0.3 },
        tooltip: { show: false },
      },
    ],
  }
})
</script>

<template>
  <ChartShell :dataset="dataset" :summary="summary">
    <div class="controls">
      <label for="river-point">{{ rios.pointLabel }}</label>
      <select id="river-point" v-model="selectedPoint">
        <option v-for="point in points" :key="point" :value="point">{{ point }}</option>
      </select>
    </div>
    <p class="model-note">{{ rios.modelNote }}</p>
    <NuxtErrorBoundary>
      <ClientOnly>
        <VChart
          class="chart"
          :option="option"
          autoresize
          :aria-label="rios.chartAria(selectedPoint)"
        />
        <template #fallback>
          <div class="chart-placeholder">{{ rios.chartLoading }}</div>
        </template>
      </ClientOnly>
      <template #error>
        <div class="chart-placeholder">{{ rios.chartError }}</div>
      </template>
    </NuxtErrorBoundary>
    <details class="table-fallback">
      <summary>{{ rios.tableSummary }}</summary>
      <div class="table-wrap">
        <table>
          <caption>
            {{
              rios.tableCaption(selectedPoint)
            }}
          </caption>
          <thead>
            <tr>
              <th scope="col">{{ rios.date }}</th>
              <th scope="col">{{ rios.dataType }}</th>
              <th scope="col" class="num">{{ rios.discharge }} ({{ dataset.unit }})</th>
              <th scope="col" class="num">{{ rios.forecastRange }} ({{ dataset.unit }})</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="`${record.point}-${record.start}`">
              <th scope="row">{{ formatDay(record.end) }}</th>
              <td>{{ record.data_type === 'forecast' ? rios.forecast : rios.estimated }}</td>
              <td class="num">{{ displayValue(record.river_discharge) }}</td>
              <td class="num">{{ displayRange(record) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
    <DatasetAttribution :dataset="dataset" />
  </ChartShell>
</template>

<style scoped>
.controls {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 12px;
  padding-bottom: 12px;
}
.controls label {
  color: var(--muted);
  font-size: 0.95rem;
  font-weight: 650;
}
select {
  min-height: 40px;
  padding: 4px 30px 4px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--surface);
  color: var(--text);
  font: inherit;
}
.model-note {
  margin: 0 0 12px;
  color: var(--muted);
  font-size: 0.95rem;
}
.chart,
.chart-placeholder {
  width: 100%;
  height: 430px;
}
.chart-placeholder {
  display: grid;
  place-items: center;
  color: var(--muted);
  text-align: center;
}
.table-fallback {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
.table-fallback summary {
  color: var(--text);
  cursor: pointer;
  font-weight: 650;
}
.table-wrap {
  overflow-x: auto;
  margin-top: 12px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
caption {
  margin-bottom: 8px;
  color: var(--muted);
  text-align: left;
}
th,
td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  white-space: nowrap;
}
thead th {
  color: var(--muted);
  font-size: 0.82rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
@media (max-width: 599px) {
  .chart,
  .chart-placeholder {
    height: 360px;
  }
}
</style>
