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
import { computed } from 'vue'
import TableFallback from '~/components/TableFallback.vue'
import { messages } from '~/messages'
import { useChartTheme } from '~/composables/useChartTheme'
import { formatAnomaly } from '~/utils/enso'
import { buildOisstMap, formatBand, formatCoordinate, summarizeOisst } from '~/utils/oisstMap'
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
const record = props.dataset.records[0]
const mapData = record
  ? buildOisstMap(record)
  : { latitudes: [], longitudes: [], points: [], bands: [], warmest: null, valueMax: 0.01 }
const date = record?.end ?? ''
const summary = summarizeOisst(mapData, date || messages.oisst.emptyPeriod, props.dataset.unit)
const theme = useChartTheme()
const chartPoints = mapData.points.map(
  (point) =>
    [
      formatCoordinate(point.lon, 'longitude'),
      formatCoordinate(point.lat, 'latitude'),
      point.value,
    ] as [string, string, number],
)
const longitudeLabels = mapData.longitudes.map((value) => formatCoordinate(value, 'longitude'))
const latitudeLabels = mapData.latitudes.map((value) => formatCoordinate(value, 'latitude'))

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
        params: { value: [string, string, number] } | { value: [string, string, number] }[],
      ) => {
        const item = Array.isArray(params) ? params[0] : params
        if (!item) return ''
        const [longitude, latitude, value] = item.value
        return messages.oisst.tooltip(formatAnomaly(value), props.dataset.unit, latitude, longitude)
      },
    },
    xAxis: {
      type: 'category',
      data: longitudeLabels,
      axisLabel: { color: t.muted, interval: 3 },
      axisLine: { lineStyle: { color: t.border } },
      splitLine: { lineStyle: { color: t.grid } },
    },
    yAxis: {
      type: 'category',
      data: latitudeLabels,
      axisLabel: { color: t.muted, interval: 3 },
      axisLine: { lineStyle: { color: t.border } },
      splitLine: { lineStyle: { color: t.grid } },
    },
    visualMap: {
      min: -mapData.valueMax,
      max: mapData.valueMax,
      dimension: 2,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      itemWidth: 12,
      itemHeight: 200,
      text: [
        `${formatAnomaly(mapData.valueMax)} ${props.dataset.unit}`,
        `${formatAnomaly(-mapData.valueMax)} ${props.dataset.unit}`,
      ],
      calculable: false,
      textStyle: { color: t.muted },
      inRange: { color: [t.cold, t.neutral, t.warm] },
    },
    series: [
      {
        type: 'heatmap',
        data: chartPoints,
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: t.text } },
      },
    ],
  }
})
</script>

<template>
  <ChartShell :dataset="dataset" :summary="summary">
    <div class="map-content">
      <ClientOnly v-if="mapData.points.length">
        <VChart class="map" :option="option" autoresize />
        <template #fallback>
          <div class="map-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
      <TableFallback v-if="mapData.bands.length" :label="messages.oisst.tableSummary">
        <table>
          <caption>
            {{
              messages.oisst.tableCaption(date)
            }}
          </caption>
          <thead>
            <tr>
              <th scope="col">{{ messages.oisst.latitudeBand }}</th>
              <th scope="col">{{ messages.oisst.mean }}</th>
              <th scope="col">{{ messages.oisst.maximum }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="band in mapData.bands" :key="band.start">
              <th scope="row">{{ formatBand(band) }}</th>
              <td>{{ formatAnomaly(band.mean) }} {{ dataset.unit }}</td>
              <td>{{ formatAnomaly(band.maximum) }} {{ dataset.unit }}</td>
            </tr>
          </tbody>
        </table>
      </TableFallback>
    </div>
  </ChartShell>
</template>

<style scoped>
.map-content {
  min-width: 0;
}
/* 40 x 44 cells of 0.5 degrees: the frame keeps them square. */
.map,
.map-placeholder {
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
  aspect-ratio: 640 / 740;
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
