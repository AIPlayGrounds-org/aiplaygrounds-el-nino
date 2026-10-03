<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  AriaComponent,
  DataZoomComponent,
  GridComponent,
  MarkAreaComponent,
  MarkLineComponent,
  MarkPointComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'

// Solo se cargan las piezas de ECharts que se usan, para que la página pese menos.
use([
  LineChart,
  GridComponent,
  TooltipComponent,
  MarkAreaComponent,
  MarkLineComponent,
  MarkPointComponent,
  DataZoomComponent,
  VisualMapComponent,
  AriaComponent,
  CanvasRenderer,
])

const props = defineProps<{
  dataset: DatasetFor<'noaa-cpc-oni'>
  /** Resumen en texto de la serie, para lectores de pantalla. */
  description: string
}>()
const records = props.dataset.records

// Este componente solo se monta en el navegador (está dentro de <ClientOnly>), así que puede leer window.
const narrow = window.matchMedia('(max-width: 599px)').matches

const RANGES = [
  { years: 10, label: messages.chart.rangeYears },
  { years: 30, label: messages.chart.rangeDecades },
  { years: null, label: messages.chart.rangeAll },
] as const
type RangeYears = (typeof RANGES)[number]['years']

/** Periodo elegido con los botones. En pantallas estrechas empieza en 10 años, que caben bien. */
const selected = ref<RangeYears>(narrow ? 10 : 30)

const isoDay = (d: Date) => d.toISOString().slice(0, 10)
const lastDate = centerDate(records.at(-1)!)
const startFor = (years: RangeYears) => {
  if (years === null) return isoDay(centerDate(records[0]!))
  const d = new Date(lastDate)
  d.setUTCFullYear(d.getUTCFullYear() - years)
  return isoDay(d)
}
const initialStart = startFor(selected.value)

const chart = ref<InstanceType<typeof VChart> | null>(null)
const choose = (years: RangeYears) => {
  selected.value = years
  chart.value?.dispatchAction({
    type: 'dataZoom',
    dataZoomIndex: 0,
    startValue: startFor(years),
    endValue: isoDay(lastDate),
  })
}

const theme = useChartTheme()

const axisNumber = new Intl.NumberFormat('es', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
  signDisplay: 'exceptZero',
})

const option = computed(() => {
  const t = theme.value
  const data = records.map((r, index) => [isoDay(centerDate(r)), r.anomaly, index])
  const last = records.at(-1)!
  const lastColor = { warm: t.warm, cold: t.cold, neutral: t.neutral }[ensoPhase(last.anomaly)]

  return {
    aria: { enabled: true, label: { description: props.description } },
    textStyle: { color: t.muted, fontFamily: t.font },
    // A la derecha cabe la etiqueta del último dato y las de los umbrales.
    grid: { left: narrow ? 40 : 48, right: narrow ? 80 : 96, top: 28, bottom: 28 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      formatter: (params: { data: [string, number, number] }[]) => {
        const record = records[params[0]!.data[2]]!
        return [
          `<b>${seasonLabel(record)}</b> · ${seasonMonths(record)}`,
          `${messages.chart.anomaly}: ${formatAnomaly(record.anomaly)} °C`,
          `${messages.chart.seaTemperature}: ${formatTemperature(record.sst)} °C`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.axis, hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      name: messages.oni.chartAxis,
      nameTextStyle: { color: t.axis, align: 'left' },
      axisLabel: {
        color: t.axis,
        formatter: (v: number) => axisNumber.format(v).replace('-', '−'),
      },
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
    // El periodo se elige solo con los botones: este zoom no tiene barra ni gestos propios.
    dataZoom: [{ type: 'inside', disabled: true, startValue: initialStart }],
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
          // Etiquetas fuera del área de la línea, con un decimal como en la leyenda («+0,5 °C»).
          label: {
            position: 'end',
            color: t.muted,
            formatter: (p: { value: number }) =>
              `${axisNumber.format(p.value).replace('-', '−')} °C`,
          },
          data: [{ yAxis: ENSO_THRESHOLD }, { yAxis: -ENSO_THRESHOLD }],
        },
        // El rango neutral, sombreado en verde agua (el mar en calma).
        markArea: {
          silent: true,
          itemStyle: { color: t.band },
          data: [[{ yAxis: -ENSO_THRESHOLD }, { yAxis: ENSO_THRESHOLD }]],
        },
        // El último dato, el mismo del que habla la frase principal de la página.
        markPoint: {
          symbol: 'circle',
          symbolSize: 9,
          itemStyle: { color: lastColor, borderColor: t.surface, borderWidth: 2 },
          // A la derecha del punto, fuera de la línea: así no se confunde con un pico anterior.
          label: {
            position: 'right',
            distance: 8,
            // El último dato, en el color de su fase.
            color: lastColor,
            fontWeight: 760,
            fontSize: narrow ? 15 : 18,
            backgroundColor: t.surface,
            padding: [2, 4],
            formatter: () => `${formatAnomaly(last.anomaly)} °C`,
          },
          data: [{ coord: [isoDay(centerDate(last)), last.anomaly] }],
        },
      },
    ],
  }
})
</script>

<template>
  <div>
    <div class="ranges" role="group" :aria-label="messages.chart.period">
      <button
        v-for="r in RANGES"
        :key="r.label"
        type="button"
        :aria-pressed="selected === r.years"
        @click="choose(r.years)"
      >
        {{ r.label }}
      </button>
    </div>
    <VChart ref="chart" class="chart" :option="option" autoresize />
  </div>
</template>

<style scoped>
/* Selector de periodo: botones discretos; el elegido, en tinta. */
.ranges {
  display: inline-flex;
  gap: 6px;
  margin-bottom: 12px;
}
.ranges button {
  font: inherit;
  font-size: 0.9375rem;
  min-height: 36px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--paper);
  color: var(--text);
  cursor: pointer;
  transition:
    border-color 0.15s ease-out,
    background-color 0.15s ease-out;
}
.ranges button:hover {
  border-color: var(--text);
}
.ranges button[aria-pressed='true'] {
  background: var(--text);
  border-color: var(--text);
  color: var(--paper);
  font-weight: 650;
}
@media (pointer: coarse) {
  .ranges button {
    min-height: 44px;
    padding: 0 18px;
  }
}
.chart {
  height: 360px;
  width: 100%;
}
@media (max-width: 599px) {
  .chart {
    height: 300px;
  }
}
</style>
