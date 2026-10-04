<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  AriaComponent,
  DataZoomComponent,
  GridComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { computed } from 'vue'
import TableFallback from '~/components/TableFallback.vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'
import { formatDay, formatValue } from '~/utils/format'

use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, AriaComponent, CanvasRenderer])

const props = defineProps<{
  dataset: DatasetFor<'noaa-cpc-nino-weekly'>
}>()

const records = props.dataset.records
const last = records.at(-1)
// El gráfico guarda toda la serie y abre en los últimos dos años.
const initialStart = records[Math.max(0, records.length - 104)]?.start ?? ''

const summary = computed(() =>
  last
    ? messages.panels.weekly.summary(
        formatDay(last.end),
        formatValue(last.nino_1_2_anomaly),
        formatValue(last.nino_3_4_anomaly),
      )
    : messages.panels.weekly.empty,
)
const theme = useChartTheme()

const option = computed(() => {
  const t = theme.value
  const series = [
    {
      name: messages.panels.weekly.nino12,
      data: records.map((record) => [record.start, record.nino_1_2_anomaly]),
      color: t.warm,
    },
    {
      name: messages.panels.weekly.nino34,
      data: records.map((record) => [record.start, record.nino_3_4_anomaly]),
      color: t.accent,
    },
  ]

  return {
    aria: { enabled: true, label: { description: messages.panels.weekly.chartDescription } },
    textStyle: { color: t.muted, fontFamily: t.font },
    grid: { left: 46, right: 20, top: 24, bottom: 32 },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      valueFormatter: (value: number) => `${formatValue(value)} °C`,
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted, hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      name: messages.panels.weekly.chartAxis,
      nameTextStyle: { color: t.muted, align: 'left' },
      axisLabel: {
        color: t.muted,
        formatter: formatValue,
      },
      splitLine: { lineStyle: { color: t.grid } },
    },
    dataZoom: [{ type: 'inside', startValue: initialStart }],
    series: series.map(({ name, data, color }) => ({
      name,
      type: 'line',
      data,
      showSymbol: false,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
    })),
  }
})
</script>

<template>
  <section class="panel weekly-panel" aria-labelledby="weekly-title">
    <div class="prose">
      <h2 id="weekly-title">{{ messages.panels.weekly.title }}</h2>
    </div>
    <figure class="figure">
      <ChartShell :dataset="dataset" :summary="summary">
        <div v-if="last" class="latest-grid" :aria-label="messages.panels.weekly.latestValues">
          <div>
            <span class="latest-label"
              >{{ messages.panels.weekly.latest }} · {{ messages.panels.weekly.nino12 }}</span
            >
            <strong>{{ formatValue(last.nino_1_2_anomaly) }} {{ dataset.unit }}</strong>
          </div>
          <div>
            <span class="latest-label"
              >{{ messages.panels.weekly.latest }} · {{ messages.panels.weekly.nino34 }}</span
            >
            <strong>{{ formatValue(last.nino_3_4_anomaly) }} {{ dataset.unit }}</strong>
          </div>
          <time :datetime="last.end"
            >{{ messages.panels.weekly.date }} {{ formatDay(last.end) }}</time
          >
        </div>
        <template v-if="last">
          <NuxtErrorBoundary>
            <ClientOnly>
              <VChart
                class="chart"
                :option="option"
                autoresize
                :aria-label="messages.panels.weekly.chartAria"
              />
              <template #fallback>
                <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
              </template>
            </ClientOnly>
            <template #error>
              <div class="chart-placeholder">{{ messages.page.chartError }}</div>
            </template>
          </NuxtErrorBoundary>
        </template>
        <p v-else class="empty-state" role="status">{{ messages.panels.weekly.empty }}</p>
        <TableFallback v-if="records.length" :label="messages.panels.weekly.tableSummary">
          <table>
            <caption>
              {{
                messages.panels.weekly.tableCaption
              }}
            </caption>
            <thead>
              <tr>
                <th scope="col">{{ messages.panels.weekly.date }}</th>
                <th scope="col">{{ messages.panels.weekly.nino12 }}</th>
                <th scope="col">{{ messages.panels.weekly.nino34 }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in records" :key="record.start">
                <th scope="row">{{ formatDay(record.end) }}</th>
                <td>{{ formatValue(record.nino_1_2_anomaly) }} {{ dataset.unit }}</td>
                <td>{{ formatValue(record.nino_3_4_anomaly) }} {{ dataset.unit }}</td>
              </tr>
            </tbody>
          </table>
        </TableFallback>
      </ChartShell>
      <figcaption>
        <ul class="key" :aria-label="messages.panels.weekly.chartDescription">
          <li>
            <span class="swatch nino12" aria-hidden="true" />{{ messages.panels.weekly.nino12 }}
          </li>
          <li>
            <span class="swatch nino34" aria-hidden="true" />{{ messages.panels.weekly.nino34 }}
          </li>
        </ul>
      </figcaption>
    </figure>
  </section>
</template>

<style scoped>
.panel {
  padding: clamp(64px, 10vw, 112px) 0 0;
}
.prose {
  max-width: 38rem;
  margin: 0 auto;
  padding: 0 16px;
}
h2 {
  margin: 0 0 16px;
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.figure {
  max-width: 960px;
  margin: 8px auto 0;
  padding: 0 16px;
}
.latest-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 20px;
  padding: 0 0 16px;
}
.latest-grid > div {
  display: grid;
  gap: 2px;
}
.latest-label {
  color: var(--muted);
  font-size: var(--fs-small);
}
.latest-grid strong {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-variant-numeric: tabular-nums;
}
.latest-grid time {
  grid-column: 1 / -1;
  color: var(--muted);
  font-size: var(--fs-small);
}
.chart {
  width: 100%;
  height: 380px;
}
.chart-placeholder {
  height: 380px;
  display: grid;
  place-items: center;
  color: var(--muted);
}
.empty-state {
  margin: 0;
  padding: 32px 0;
  color: var(--muted);
}
figcaption {
  font-size: var(--fs-small);
  color: var(--muted);
}
.key {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 20px;
  margin: 8px 0;
  padding: 0;
  list-style: none;
  color: var(--text);
}
.swatch {
  display: inline-block;
  width: 16px;
  height: 3px;
  margin-right: 8px;
  vertical-align: middle;
}
.swatch.nino12 {
  background: var(--warm);
}
.swatch.nino34 {
  background: var(--accent);
}
@media (max-width: 599px) {
  .chart,
  .chart-placeholder {
    height: 320px;
  }
}
</style>
