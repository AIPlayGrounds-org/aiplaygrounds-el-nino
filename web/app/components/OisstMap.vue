<script setup lang="ts">
import { use } from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import {
  AriaComponent,
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'

use([
  HeatmapChart,
  AriaComponent,
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  CanvasRenderer,
])

const props = defineProps<{ dataset: DatasetFor<'noaa-oisst'> }>()
const record = props.dataset.records.at(-1)!

// The source grid covers a wider Pacific window; this view keeps the Peruvian coast readable.
const VIEW = { west: -90, east: -70, south: -20, north: 10 }

const visibleLatitudes = record.lat
  .map((value, index) => ({ value, index }))
  .filter(({ value }) => value >= VIEW.south && value <= VIEW.north)
const visibleLongitudes = record.lon
  .map((value, index) => ({ value, index }))
  .filter(({ value }) => value >= VIEW.west && value <= VIEW.east)

const points = visibleLatitudes.flatMap(({ value: lat, index: latIndex }) =>
  visibleLongitudes.flatMap(({ value: lon, index: lonIndex }) => {
    const value = record.anomaly[latIndex]?.[lonIndex]
    return value === null || value === undefined
      ? []
      : [[lon, lat, value] as [number, number, number]]
  }),
)

const valueMax = Math.max(...points.map(([, , value]) => Math.abs(value)), 0.01)
const tableRows = visibleLatitudes.map(({ value: lat, index: latIndex }) => ({
  lat,
  values: visibleLongitudes.map(
    ({ index: lonIndex }) => record.anomaly[latIndex]?.[lonIndex] ?? null,
  ),
}))
const warmest = points.reduce(
  (current, point) => (point[2] > current[2] ? point : current),
  points[0]!,
)
const number = new Intl.NumberFormat('es', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const display = (value: number | null) =>
  value === null ? '—' : number.format(value).replace('-', '−')
const summary = `${props.dataset.variable}. ${messages.provenance.latestData}: ${record.end}. ${messages.chart.anomaly}: ${display(warmest[2])} ${props.dataset.unit} (${display(warmest[1])}°, ${display(warmest[0])}°).`

const readTheme = () => {
  const css = getComputedStyle(document.documentElement)
  const value = (name: string) => css.getPropertyValue(name).trim()
  return {
    text: value('--text'),
    muted: value('--muted'),
    border: value('--border'),
    surface: value('--surface'),
    grid: value('--chart-grid'),
    cold: value('--cold'),
    neutral: value('--neutral-data'),
    warm: value('--warm'),
    font: value('--font'),
  }
}

const theme = ref(
  import.meta.client
    ? readTheme()
    : {
        text: '',
        muted: '',
        border: '',
        surface: '',
        grid: '',
        cold: '',
        neutral: '',
        warm: '',
        font: '',
      },
)
const darkQuery = import.meta.client ? window.matchMedia('(prefers-color-scheme: dark)') : undefined
const refreshTheme = () => (theme.value = readTheme())
onMounted(() => darkQuery?.addEventListener('change', refreshTheme))
onBeforeUnmount(() => darkQuery?.removeEventListener('change', refreshTheme))

const option = computed(() => {
  const t = theme.value
  return {
    aria: { enabled: true, label: { description: summary } },
    animation: false,
    textStyle: { color: t.muted, fontFamily: t.font },
    grid: { left: 44, right: 28, top: 20, bottom: 64 },
    tooltip: {
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      formatter: (
        params: { value: [number, number, number] } | { value: [number, number, number] }[],
      ) => {
        const item = Array.isArray(params) ? params[0] : params
        if (!item) return ''
        const [lon, lat, value] = item.value
        return `${display(value)} ${props.dataset.unit}<br/>${display(lat)}°, ${display(lon)}°`
      },
    },
    xAxis: {
      type: 'value',
      min: VIEW.west,
      max: VIEW.east,
      interval: 5,
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
      splitLine: { lineStyle: { color: t.grid } },
    },
    yAxis: {
      type: 'value',
      min: VIEW.south,
      max: VIEW.north,
      interval: 5,
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
      splitLine: { lineStyle: { color: t.grid } },
    },
    visualMap: {
      min: -valueMax,
      max: valueMax,
      dimension: 2,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      itemWidth: 180,
      itemHeight: 10,
      textStyle: { color: t.muted },
      inRange: { color: [t.cold, t.neutral, t.warm] },
    },
    series: [
      {
        type: 'heatmap',
        data: points,
        itemStyle: { borderColor: t.surface, borderWidth: 0.5 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: t.text } },
      },
    ],
  }
})
</script>

<template>
  <ChartShell :dataset="dataset" :summary="summary">
    <div class="map-content">
      <p class="map-meta">
        {{ messages.provenance.latestData }}: {{ record.end }} ·
        {{ messages.provenance.periodBase }}:
        {{ dataset.reference_period ?? '—' }}
      </p>
      <ClientOnly>
        <VChart class="map" :option="option" autoresize />
        <template #fallback>
          <div class="map-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
      <details class="table-fallback">
        <summary>{{ messages.provenance.latestData }}</summary>
        <div class="table-wrap">
          <table>
            <caption>
              {{
                dataset.variable
              }}
              ·
              {{
                record.end
              }}
            </caption>
            <thead>
              <tr>
                <th scope="col">°</th>
                <th v-for="longitude in visibleLongitudes" :key="longitude.index" scope="col">
                  {{ display(longitude.value) }}°
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableRows" :key="row.lat">
                <th scope="row">{{ display(row.lat) }}°</th>
                <td v-for="(value, index) in row.values" :key="visibleLongitudes[index]!.index">
                  {{ display(value) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </div>
  </ChartShell>
</template>

<style scoped>
.map-content {
  min-width: 0;
}
.map-meta {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 0.95rem;
}
.map {
  width: 100%;
  height: clamp(320px, 52vw, 520px);
}
.map-placeholder {
  width: 100%;
  height: clamp(320px, 52vw, 520px);
}
.table-fallback {
  margin-top: 12px;
  border-top: 1px solid var(--border);
  padding-top: 10px;
}
.table-fallback summary {
  cursor: pointer;
  color: var(--muted);
  font-size: 0.95rem;
}
.table-wrap {
  max-width: 100%;
  overflow: auto;
  margin-top: 12px;
}
table {
  border-collapse: collapse;
  font-size: 0.8rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
caption {
  margin-bottom: 8px;
  text-align: left;
}
th,
td {
  padding: 4px 6px;
  border: 1px solid var(--border);
  text-align: right;
}
th {
  background: var(--band);
  font-weight: 650;
}
</style>
