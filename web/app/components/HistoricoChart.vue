<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { AriaComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import TableFallback from '~/components/TableFallback.vue'
import { computed, ref } from 'vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import { formatMonth, formatValue } from '~/utils/format'
import {
  alignHistoryEvent,
  alignHistoryOniEvent,
  type AlignedHistoryPoint,
  CURRENT_EVENT_ID,
  historyEventSelectorData,
  historyWindowsFromErsst,
  peakOfHistoryPoints,
  type HistoryEventId,
  type HistoryRegion,
} from '~/utils/historico'
import type { HistoricoDataset, HistoricoOniDataset } from '~/utils/historico'

use([LineChart, AriaComponent, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{
  dataset: HistoricoDataset
  oni: HistoricoOniDataset
}>()
const region = ref<HistoryRegion>('nino34')
const availableEvents = historyEventSelectorData(props.dataset.records)
const selectedEvents = ref<HistoryEventId[]>([...availableEvents])
const theme = useChartTheme()
const currentYear = Number(props.dataset.records.at(-1)?.start.slice(0, 4) ?? '')
const eventWindows = historyWindowsFromErsst(props.dataset.records)
const EVENT_COLORS = {
  '1982-83': { css: 'warm', theme: 'warm' },
  '1997-98': { css: 'cold', theme: 'cold' },
  '2017': { css: 'accent', theme: 'accent' },
  current: { css: 'neutral-data', theme: 'neutral' },
} as const

const eventLabel = (event: HistoryEventId) => {
  if (event === CURRENT_EVENT_ID) return messages.historico.currentYear(currentYear)
  return messages.historico.events[event]
}
const regionForEvent = (event: HistoryEventId): HistoryRegion =>
  event === '2017' ? 'nino12' : region.value
const selectedSeries = computed(() =>
  selectedEvents.value.map((event) => {
    const selectedRegion = regionForEvent(event)
    const points = alignHistoryEvent(props.dataset.records, event, selectedRegion)
    return { event, region: selectedRegion, points, peak: peakOfHistoryPoints(points) }
  }),
)
const selectedOniSeries = computed(() =>
  selectedEvents.value
    .filter((event) => event !== '2017')
    .map((event) => {
      const points = alignHistoryOniEvent(props.oni.records, event, eventWindows)
      return { event, region: 'nino34' as const, points, peak: peakOfHistoryPoints(points) }
    }),
)
const maxOffset = computed(() =>
  Math.max(0, ...selectedSeries.value.map((series) => series.points.length)),
)
const maxOniOffset = computed(() =>
  Math.max(0, ...selectedOniSeries.value.map((series) => series.points.length)),
)
const labelFor = (
  event: HistoryEventId,
  region: HistoryRegion,
  peak: { value: number; month: string } | null,
) =>
  peak
    ? `${eventLabel(event)} · ${messages.historico.regions[region]} · ${messages.historico.peak(formatValue(peak.value), formatMonth(peak.month))}`
    : `${eventLabel(event)} · ${messages.historico.regions[region]} · ${messages.historico.noPeak}`
const summary = computed(() => {
  const peaks = selectedSeries.value.map((series) =>
    labelFor(series.event, series.region, series.peak),
  )
  return messages.historico.summary(peaks.join('; '))
})
const oniSummary = computed(() => {
  const peaks = selectedOniSeries.value.map((series) =>
    labelFor(series.event, series.region, series.peak),
  )
  return messages.historico.oniSummary(peaks.join('; '))
})
const tableRows = computed(() =>
  Array.from({ length: maxOffset.value }, (_, index) => ({
    offset: index + 1,
    values: selectedSeries.value.map((series) => series.points[index]?.value ?? null),
  })),
)
const oniTableRows = computed(() =>
  Array.from({ length: maxOniOffset.value }, (_, index) => ({
    offset: index + 1,
    values: selectedOniSeries.value.map((series) => series.points[index]?.value ?? null),
  })),
)
const eventColor = (event: HistoryEventId) => `var(--${EVENT_COLORS[event].css})`

type HistorySeries = {
  event: HistoryEventId
  region: HistoryRegion
  points: AlignedHistoryPoint[]
  peak: { value: number; month: string } | null
}

const chartOptionFor = (series: HistorySeries[], max: number, description: string) => {
  const t = theme.value
  return {
    aria: { enabled: true, label: { description } },
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
              `${param.seriesName}: ${
                param.value === null
                  ? messages.historico.missing
                  : messages.historico.value(formatValue(param.value), messages.page.degreeC)
              }`,
          ),
        ].join('<br/>'),
    },
    xAxis: {
      type: 'category',
      name: messages.historico.months,
      data: Array.from({ length: max }, (_, index) => index + 1),
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
    },
    yAxis: {
      type: 'value',
      name: messages.historico.value(messages.historico.anomaly, messages.page.degreeC),
      axisLabel: { color: t.muted, formatter: (value: number) => formatValue(value) },
      splitLine: { lineStyle: { color: t.grid } },
    },
    series: series.map((series) => ({
      name: labelFor(series.event, series.region, series.peak),
      type: 'line',
      data: series.points.map((point) => point.value),
      connectNulls: false,
      showSymbol: false,
      lineStyle: { width: 2, color: t[EVENT_COLORS[series.event].theme] },
      itemStyle: { color: t[EVENT_COLORS[series.event].theme] },
    })),
  }
}
const chartOption = computed(() =>
  chartOptionFor(selectedSeries.value, maxOffset.value, summary.value),
)
const oniChartOption = computed(() =>
  chartOptionFor(selectedOniSeries.value, maxOniOffset.value, oniSummary.value),
)
</script>

<template>
  <div v-if="dataset.records.length || oni.records.length" class="controls">
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
  <p v-if="dataset.records.length || oni.records.length" class="coastal-note">
    {{ messages.historico.coastalNote }}
  </p>

  <ChartShell :dataset="dataset" :summary="summary">
    <template v-if="dataset.records.length">
      <h3>{{ messages.historico.ersstTitle }}</h3>

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
        <li v-for="series in selectedSeries" :key="series.event">
          <span
            class="swatch"
            :style="{ backgroundColor: eventColor(series.event) }"
            aria-hidden="true"
          />
          {{ labelFor(series.event, series.region, series.peak) }}
        </li>
      </ul>

      <TableFallback :label="messages.historico.tableSummary">
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
                {{ labelFor(series.event, series.region, series.peak) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableRows" :key="row.offset">
              <th scope="row">{{ row.offset }}</th>
              <td v-for="(value, index) in row.values" :key="selectedSeries[index]?.event">
                {{
                  value === null
                    ? messages.historico.missing
                    : messages.historico.value(formatValue(value), messages.page.degreeC)
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </TableFallback>
    </template>
    <p v-else class="empty-state" role="status">{{ messages.historico.empty }}</p>
  </ChartShell>

  <ChartShell :dataset="oni" :summary="oniSummary">
    <template v-if="oni.records.length">
      <h3>{{ messages.historico.oniTitle }}</h3>
      <p class="oni-note">{{ messages.historico.oniNote }}</p>
      <NuxtErrorBoundary>
        <ClientOnly>
          <VChart class="chart" :option="oniChartOption" autoresize />
          <template #fallback>
            <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
          </template>
        </ClientOnly>
        <template #error>
          <div class="chart-placeholder">{{ messages.page.chartError }}</div>
        </template>
      </NuxtErrorBoundary>
      <ul class="key" :aria-label="messages.historico.eventsLabel">
        <li v-for="series in selectedOniSeries" :key="series.event">
          <span
            class="swatch"
            :style="{ backgroundColor: eventColor(series.event) }"
            aria-hidden="true"
          />
          {{ labelFor(series.event, series.region, series.peak) }}
        </li>
      </ul>
      <TableFallback :label="messages.historico.oniTableSummary">
        <table>
          <caption>
            {{
              messages.historico.oniTableCaption
            }}
          </caption>
          <thead>
            <tr>
              <th scope="col">{{ messages.historico.months }}</th>
              <th v-for="series in selectedOniSeries" :key="series.event" scope="col">
                {{ labelFor(series.event, series.region, series.peak) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in oniTableRows" :key="row.offset">
              <th scope="row">{{ row.offset }}</th>
              <td v-for="(value, index) in row.values" :key="selectedOniSeries[index]?.event">
                {{
                  value === null
                    ? messages.historico.missing
                    : messages.historico.value(formatValue(value), messages.page.degreeC)
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </TableFallback>
    </template>
    <p v-else class="empty-state" role="status">{{ messages.historico.empty }}</p>
  </ChartShell>
</template>

<style scoped>
.controls {
  display: grid;
  gap: 16px;
  margin-bottom: 18px;
}
.coastal-note,
.oni-note {
  margin: 0 0 16px;
  color: var(--muted);
  font-size: 0.95rem;
}
h3 {
  margin: 0 0 12px;
  font-size: 1.25rem;
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
  min-height: 44px;
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
  min-height: 44px;
  white-space: nowrap;
}
input {
  appearance: none;
  display: grid;
  width: 44px;
  height: 44px;
  margin: 0;
  place-content: center;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--surface);
  color: var(--accent);
}
input::after {
  width: 10px;
  height: 5px;
  transform: rotate(-45deg) scale(0);
  border-bottom: 2px solid currentColor;
  border-left: 2px solid currentColor;
  content: '';
}
input:checked::after {
  transform: rotate(-45deg) scale(1);
}
input:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 3px;
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
.empty-state {
  margin: 0;
  padding: 32px 0;
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
