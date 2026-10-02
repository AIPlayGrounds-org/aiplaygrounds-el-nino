<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  AriaComponent,
  DataZoomComponent,
  GridComponent,
  MarkLineComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import type { OniRecord } from '~/types/dataset'

// Solo se cargan las piezas de ECharts que se usan, para que la página pese menos.
use([LineChart, GridComponent, TooltipComponent, MarkLineComponent, DataZoomComponent, VisualMapComponent, AriaComponent, CanvasRenderer])

const props = defineProps<{
  records: OniRecord[]
  /** Resumen en texto de la serie, para lectores de pantalla. */
  description: string
}>()

// ECharts dibuja en un canvas y no ve el CSS: los colores se leen de las variables del tema
// y se vuelven a leer cuando el sistema cambia entre modo claro y oscuro.
const readTheme = () => {
  const css = getComputedStyle(document.documentElement)
  const v = (name: string) => css.getPropertyValue(name).trim()
  return {
    text: v('--text'),
    muted: v('--muted'),
    border: v('--border'),
    surface: v('--surface'),
    grid: v('--chart-grid'),
    warm: v('--warm'),
    cold: v('--cold'),
    neutral: v('--neutral-data'),
  }
}

const theme = ref(readTheme())
const darkQuery = window.matchMedia('(prefers-color-scheme: dark)')
const refreshTheme = () => (theme.value = readTheme())
onMounted(() => darkQuery.addEventListener('change', refreshTheme))
onBeforeUnmount(() => darkQuery.removeEventListener('change', refreshTheme))

const option = computed(() => {
  const t = theme.value
  const data = props.records.map((r, index) => [centerDate(r).toISOString().slice(0, 10), r.anomaly, index])
  const initialStart = centerDate(props.records.at(-1)!)
  initialStart.setUTCFullYear(initialStart.getUTCFullYear() - 30)

  return {
    aria: { enabled: true, label: { description: props.description } },
    textStyle: { color: t.muted, fontFamily: 'inherit' },
    grid: { left: 52, right: 16, top: 16, bottom: 72 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      formatter: (params: { data: [string, number, number] }[]) => {
        const record = props.records[params[0]!.data[2]]!
        return [
          `<b>${seasonLabel(record)}</b> · ${seasonMonths(record)}`,
          `Anomalía: ${formatAnomaly(record.anomaly)} °C`,
          `Temperatura del mar: ${formatTemperature(record.sst)} °C`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
    },
    yAxis: {
      type: 'value',
      name: 'Anomalía (°C)',
      nameTextStyle: { color: t.muted, align: 'left' },
      axisLabel: { color: t.muted, formatter: (v: number) => formatAnomaly(v) },
      splitLine: { lineStyle: { color: t.grid } },
    },
    // Color de la línea según el umbral oficial: cálido sobre +0,5 °C, frío bajo −0,5 °C, neutro en medio.
    visualMap: {
      show: false,
      dimension: 1,
      pieces: [
        { gte: ENSO_THRESHOLD, color: t.warm },
        { gt: -ENSO_THRESHOLD, lt: ENSO_THRESHOLD, color: t.neutral },
        { lte: -ENSO_THRESHOLD, color: t.cold },
      ],
    },
    dataZoom: [
      {
        type: 'slider',
        startValue: initialStart.toISOString().slice(0, 10),
        borderColor: t.border,
        textStyle: { color: t.muted },
        fillerColor: 'rgba(127, 127, 127, 0.15)',
        dataBackground: { lineStyle: { color: t.muted }, areaStyle: { color: t.grid } },
        selectedDataBackground: { lineStyle: { color: t.muted }, areaStyle: { color: t.grid } },
        handleStyle: { color: t.surface, borderColor: t.muted },
        moveHandleStyle: { color: t.muted },
      },
      { type: 'inside' },
    ],
    series: [
      {
        type: 'line',
        data,
        showSymbol: false,
        lineStyle: { width: 1.5 },
        markLine: {
          symbol: 'none',
          silent: true,
          lineStyle: { type: 'dashed', color: t.muted },
          label: {
            position: 'insideEndTop',
            color: t.muted,
            formatter: (p: { value: number }) => `${formatAnomaly(p.value)} °C`,
          },
          data: [{ yAxis: ENSO_THRESHOLD }, { yAxis: -ENSO_THRESHOLD }],
        },
      },
    ],
  }
})
</script>

<template>
  <VChart class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart {
  height: 360px;
  width: 100%;
}
</style>
