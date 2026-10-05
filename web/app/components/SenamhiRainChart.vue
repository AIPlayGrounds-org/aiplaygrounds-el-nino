<script setup lang="ts">
import { computed, ref } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { AriaComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import TableFallback from '~/components/TableFallback.vue'
import ChartShell from '~/components/ChartShell.vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import { formatDay, formatValue } from '~/utils/format'
import {
  SENAMHI_EVENT_YEARS,
  stationChartSeries,
  stationLabel,
  stationOptions,
  type SenamhiDataset,
  type SenamhiEvent,
} from '~/utils/senamhi'

use([LineChart, AriaComponent, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{ dataset: SenamhiDataset }>()
const options = stationOptions(props.dataset.records)
const selectedStation = ref(options[0]?.code ?? '')
const theme = useChartTheme()
const label = computed(() => stationLabel(props.dataset.records, selectedStation.value))
const series = computed(() => stationChartSeries(props.dataset.records, selectedStation.value))
const latestYear = computed(() =>
  Math.max(0, ...props.dataset.records.map((station) => station.latestYear)),
)
const snapshotDate = computed(() => formatDay(props.dataset.ingestion_time.slice(0, 10)))
const chartDataset = computed(() => {
  const station = props.dataset.records.find((item) => item.station === selectedStation.value)
  return {
    ...props.dataset,
    records: station ? [{ start: `${station.firstYear}-01`, end: `${station.latestYear}-12` }] : [],
  }
})
const summary = computed(() => {
  const station = label.value
  return station
    ? messages.historico.stations.summary(station.name, station.department)
    : messages.historico.stations.empty
})

const eventLabel = (event: SenamhiEvent) => messages.historico.stations.events[event]
const monthLabel = (offset: number) => messages.historico.stations.months[(offset - 1) % 12] ?? ''
const monthForEvent = (event: SenamhiEvent, offset: number) => {
  const year = SENAMHI_EVENT_YEARS[event][Math.floor((offset - 1) / 12)]
  return monthLabel(offset) + ' ' + year
}
const seriesFor = (event: SenamhiEvent) => series.value.find((item) => item.event === event)
const chartOption = computed(() => {
  const colors = [theme.value.warm, theme.value.cold, theme.value.accent]
  const first = seriesFor('1982-83')?.points ?? []
  const second = seriesFor('1997-98')?.points ?? []
  const climatology = first.map((point) => point.climatology)
  return {
    aria: {
      enabled: true,
      label: { description: messages.historico.stations.chartDescription },
    },
    animation: false,
    textStyle: { color: theme.value.muted, fontFamily: theme.value.font },
    grid: { left: 58, right: 18, top: 24, bottom: 54 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: theme.value.surface,
      borderColor: theme.value.border,
      textStyle: { color: theme.value.text },
      formatter: (params: { seriesName: string; value: number | null; dataIndex: number }[]) => {
        const offset = (params[0]?.dataIndex ?? 0) + 1
        return [
          '<b>Mes ' + offset + '</b>',
          ...params.map((param) => {
            const event =
              param.seriesName === eventLabel('1982-83')
                ? '1982-83'
                : param.seriesName === eventLabel('1997-98')
                  ? '1997-98'
                  : null
            return (
              param.seriesName +
              ' · ' +
              (event ? monthForEvent(event, offset) : monthLabel(offset)) +
              ': ' +
              (param.value === null
                ? messages.historico.stations.missing
                : formatValue(param.value) + ' mm')
            )
          }),
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'category',
      name: messages.historico.stations.monthsAxis,
      data: Array.from({ length: 24 }, (_, index) => index + 1),
      axisLine: { lineStyle: { color: theme.value.border } },
      axisLabel: {
        color: theme.value.muted,
        formatter: (value: number) => monthLabel(Number(value)),
      },
    },
    yAxis: {
      type: 'value',
      name: 'mm',
      min: 0,
      axisLabel: { color: theme.value.muted, formatter: (value: number) => formatValue(value) },
      splitLine: { lineStyle: { color: theme.value.grid } },
    },
    series: [
      {
        name: eventLabel('1982-83'),
        type: 'line',
        data: first.map((point) => point.precipitation),
        connectNulls: false,
        showSymbol: false,
        lineStyle: { width: 2, color: colors[0] },
        itemStyle: { color: colors[0] },
      },
      {
        name: eventLabel('1997-98'),
        type: 'line',
        data: second.map((point) => point.precipitation),
        connectNulls: false,
        showSymbol: false,
        lineStyle: { width: 2, color: colors[1] },
        itemStyle: { color: colors[1] },
      },
      {
        name: messages.historico.stations.climatology,
        type: 'line',
        data: climatology,
        connectNulls: false,
        showSymbol: false,
        lineStyle: { width: 2, type: 'dashed', color: colors[2] },
        itemStyle: { color: colors[2] },
      },
    ],
  }
})
const tableRows = computed(() =>
  Array.from({ length: 24 }, (_, index) => ({
    offset: index + 1,
    month: monthLabel(index + 1),
    first: seriesFor('1982-83')?.points[index]?.precipitation ?? null,
    second: seriesFor('1997-98')?.points[index]?.precipitation ?? null,
    climatology: seriesFor('1982-83')?.points[index]?.climatology ?? null,
  })),
)
</script>

<template>
  <ChartShell :dataset="chartDataset" :summary="summary">
    <div class="controls">
      <label for="senamhi-station">{{ messages.historico.stations.stationLabel }}</label>
      <select id="senamhi-station" v-model="selectedStation">
        <option v-for="station in options" :key="station.code" :value="station.code">
          {{ station.name }} · {{ station.department }}
        </option>
      </select>
    </div>
    <p v-if="label" class="station-note">
      {{
        messages.historico.stations.stationNote(label.name, label.department, label.lat, label.lon)
      }}
    </p>
    <NuxtErrorBoundary>
      <ClientOnly>
        <VChart class="chart" :option="chartOption" autoresize />
        <template #fallback>
          <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
        </template>
      </ClientOnly>
      <template #error>
        <div class="chart-placeholder">{{ messages.historico.stations.chartError }}</div>
      </template>
    </NuxtErrorBoundary>
    <ul class="key" :aria-label="messages.historico.stations.seriesLabel">
      <li><span class="swatch warm" aria-hidden="true" />{{ eventLabel('1982-83') }}</li>
      <li><span class="swatch cold" aria-hidden="true" />{{ eventLabel('1997-98') }}</li>
      <li>
        <span class="swatch climatology" aria-hidden="true" />{{
          messages.historico.stations.climatology
        }}
      </li>
    </ul>
    <TableFallback :label="messages.historico.stations.tableSummary">
      <table>
        <caption>
          {{
            messages.historico.stations.tableCaption
          }}
        </caption>
        <thead>
          <tr>
            <th scope="col">{{ messages.historico.stations.month }}</th>
            <th scope="col">{{ eventLabel('1982-83') }} (mm)</th>
            <th scope="col">{{ eventLabel('1997-98') }} (mm)</th>
            <th scope="col">{{ messages.historico.stations.climatology }} (mm)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in tableRows" :key="row.offset">
            <th scope="row">{{ row.offset }} · {{ row.month }}</th>
            <td>
              {{
                row.first === null ? messages.historico.stations.missing : formatValue(row.first)
              }}
            </td>
            <td>
              {{
                row.second === null ? messages.historico.stations.missing : formatValue(row.second)
              }}
            </td>
            <td>
              {{
                row.climatology === null
                  ? messages.historico.stations.missing
                  : formatValue(row.climatology)
              }}
            </td>
          </tr>
        </tbody>
      </table>
    </TableFallback>
    <p class="provenance-note">
      {{ messages.historico.stations.provenance(snapshotDate, latestYear) }}
      {{ messages.historico.stations.license }}
      {{ messages.historico.stations.refresh }}
      {{ messages.historico.stations.point }}
      <NuxtLink to="/territorio">{{ messages.historico.stations.crossCheck }}</NuxtLink
      >.
    </p>
  </ChartShell>
</template>

<style scoped>
.controls {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px;
  margin-bottom: 12px;
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
.station-note,
.provenance-note {
  color: var(--muted);
  font-size: 0.95rem;
}
.provenance-note {
  margin: 20px 0 0;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
.chart {
  width: 100%;
  height: 360px;
}
.chart-placeholder {
  min-height: 360px;
  display: grid;
  place-items: center;
  color: var(--muted);
}
.key {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
  color: var(--muted);
  font-size: 0.9rem;
}
.swatch {
  display: inline-block;
  width: 1.6rem;
  height: 0.15rem;
  margin-right: 6px;
  vertical-align: middle;
}
.warm {
  background: var(--warm);
}
.cold {
  background: var(--cold);
}
.climatology {
  height: 0;
  border-top: 2px dashed var(--accent);
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th,
td {
  padding: 8px;
  border-bottom: 1px solid var(--border);
  text-align: right;
}
th:first-child,
td:first-child {
  text-align: left;
}
</style>
