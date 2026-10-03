<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { AriaComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { computed, ref } from 'vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import { formatMonth, formatValue } from '~/utils/format'
import {
  alignHistoryEvent,
  CURRENT_EVENT_ID,
  historyEventSelectorData,
  peakOfHistoryEvent,
  type HistoryEventId,
  type HistoryRegion,
} from '~/utils/historico'
import type { DatasetFor } from '~/types/datasets'

use([LineChart, AriaComponent, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{ dataset: DatasetFor<'noaa-ersst'> }>()
const region = ref<HistoryRegion>('nino34')
const availableEvents = historyEventSelectorData(props.dataset.records)
const selectedEvents = ref<HistoryEventId[]>([...availableEvents])
const theme = useChartTheme()
const currentYear = Number(props.dataset.records.at(-1)!.start.slice(0, 4))

const eventLabel = (event: HistoryEventId) => {
  if (event === CURRENT_EVENT_ID) return messages.historico.currentYear(currentYear)
  return messages.historico.events[event]
}
const peakLabel = (event: HistoryEventId) => {
  const peak = peakOfHistoryEvent(props.dataset.records, event, region.value)
  return peak
    ? `${eventLabel(event)} · ${messages.historico.peak(formatValue(peak.value), formatMonth(peak.month))}`
    : `${eventLabel(event)} · ${messages.historico.noPeak}`
}
const selectedSeries = computed(() =>
  selectedEvents.value.map((event) => ({
    event,
    points: alignHistoryEvent(props.dataset.records, event, region.value),
    label: peakLabel(event),
  })),
)
const maxOffset = computed(() =>
  Math.max(0, ...selectedSeries.value.map((series) => series.points.length)),
)
const summary = computed(() => {
  const regionName = messages.historico.regions[region.value]
  const peaks = selectedSeries.value
    .map((series) => {
      const peak = peakOfHistoryEvent(props.dataset.records, series.event, region.value)
      return peak
        ? `${eventLabel(series.event)}: ${formatValue(peak.value)} °C en ${formatMonth(peak.month)}`
        : null
    })
    .filter((peak): peak is string => peak !== null)
  return messages.historico.summary(regionName, peaks.join('; '))
})
const tableRows = computed(() =>
  Array.from({ length: maxOffset.value }, (_, index) => ({
    offset: index + 1,
    values: selectedSeries.value.map((series) => series.points[index]?.value ?? null),
  })),
)

const chartOption = computed(() => {
  const t = theme.value
  const colors = [t.warm, t.cold, t.accent, t.neutral]
  return {
    aria: { enabled: true, label: { description: summary.value } },
    animation: false,
    textStyle: { color: t.muted, fontFamily: t.font },
    grid: { left: 48, right: 18, top: 24, bottom: 42 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      formatter: (params: { seriesName: string; value: number | null; axisValue: number }[]) =>
        [
          `<b>${messages.historico.monthFromStart(params[0]?.axisValue ?? 0)}</b>`,
          ...params.map(
            (param) =>
              `${param.seriesName}: ${param.value === null ? messages.historico.missing : `${formatValue(param.value)} °C`}`,
          ),
        ].join('<br/>'),
    },
    xAxis: {
      type: 'category',
      name: messages.historico.months,
      data: Array.from({ length: maxOffset.value }, (_, index) => index + 1),
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
    },
    yAxis: {
      type: 'value',
      name: `${messages.historico.anomaly} (°C)`,
      axisLabel: { color: t.muted, formatter: (value: number) => formatValue(value) },
      splitLine: { lineStyle: { color: t.grid } },
    },
    series: selectedSeries.value.map((series, index) => ({
      name: series.label,
      type: 'line',
      data: series.points.map((point) => point.value),
      connectNulls: false,
      showSymbol: false,
      lineStyle: { width: 2, color: colors[index % colors.length] },
      itemStyle: { color: colors[index % colors.length] },
    })),
  }
})
</script>

<template>
  <ChartShell :dataset="dataset" :summary="summary">
    <div class="controls">
      <label>
        {{ messages.historico.regionLabel }}
        <select v-model="region">
          <option value="nino34">{{ messages.historico.regions.nino34 }}</option>
          <option value="nino12">{{ messages.historico.regions.nino12 }}</option>
        </select>
      </label>
      <fieldset>
        <legend>{{ messages.historico.eventsLabel }}</legend>
        <label v-for="event in availableEvents" :key="event">
          <input v-model="selectedEvents" type="checkbox" :value="event" />
          {{ eventLabel(event) }}
        </label>
      </fieldset>
    </div>

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

    <ul class="key" :aria-label="messages.historico.eventsLabel">
      <li v-for="(series, index) in selectedSeries" :key="series.event">
        <span
          class="swatch"
          :style="{
            backgroundColor: `var(--${index === 0 ? 'warm' : index === 1 ? 'cold' : index === 2 ? 'accent' : 'neutral-data'})`,
          }"
          aria-hidden="true"
        />
        {{ series.label }}
      </li>
    </ul>

    <details class="table-details">
      <summary>{{ messages.historico.tableSummary }}</summary>
      <div class="table-wrap">
        <table>
          <caption>
            {{
              messages.historico.tableCaption
            }}
          </caption>
          <thead>
            <tr>
              <th scope="col">{{ messages.historico.months }}</th>
              <th v-for="series in selectedSeries" :key="series.event" scope="col">
                {{ series.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableRows" :key="row.offset">
              <th scope="row">{{ row.offset }}</th>
              <td v-for="(value, index) in row.values" :key="selectedSeries[index]?.event">
                {{ value === null ? messages.historico.missing : `${formatValue(value)} °C` }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </ChartShell>
</template>

<style scoped>
.controls {
  display: grid;
  gap: 16px;
  margin-bottom: 18px;
}
.controls label,
fieldset {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}
.controls > label {
  justify-content: space-between;
}
select {
  min-height: 40px;
  padding: 4px 28px 4px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--surface);
  color: var(--text);
  font: inherit;
}
fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}
legend {
  width: 100%;
  margin-bottom: 4px;
  color: var(--muted);
  font-size: 0.9rem;
  font-weight: 650;
}
fieldset label {
  white-space: nowrap;
}
input {
  accent-color: var(--accent);
}
.chart {
  width: 100%;
  height: 380px;
}
.chart-placeholder {
  display: grid;
  min-height: 260px;
  place-items: center;
  color: var(--muted);
}
.key {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
  font-size: 0.95rem;
}
.swatch {
  display: inline-block;
  width: 0.75em;
  height: 0.75em;
  margin-right: 0.35em;
  border-radius: 50%;
}
.table-details {
  margin-top: 20px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}
.table-details summary {
  cursor: pointer;
  color: var(--link);
}
.table-wrap {
  overflow-x: auto;
  margin-top: 12px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  white-space: nowrap;
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
  text-align: right;
}
th:first-child,
td:first-child {
  text-align: left;
}
th {
  font-weight: 650;
}
@media (max-width: 599px) {
  .chart {
    height: 300px;
  }
}
</style>
