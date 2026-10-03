<script setup lang="ts">
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { AriaComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { computed } from 'vue'
import { useChartTheme } from '~/composables/useChartTheme'
import { messages, outlookCategoryKey, outlookCategoryLabel } from '~/messages'
import { formatMonth } from '~/utils/format'
import type { DatasetFor } from '~/types/datasets'

use([BarChart, GridComponent, TooltipComponent, AriaComponent, CanvasRenderer])

const props = defineProps<{
  dataset: DatasetFor<'noaa-cpc-outlook'>
}>()

const records = props.dataset.records
// Frío a cálido, sea cual sea el orden en que cada registro traiga las categorías.
const categories = [...records[0]!.categories].sort(
  (a, b) => (a.lower_bound ?? -Infinity) - (b.lower_bound ?? -Infinity),
)
const probability = (record: (typeof records)[number], key: string) =>
  record.categories.find((category) => outlookCategoryKey(category) === key)?.probability ?? null
const issueDate = formatMonth(records[0]!.issue_date)
const summary = computed(() => messages.panels.outlook.summary(records.length, issueDate))
const theme = useChartTheme()

const option = computed(() => {
  const t = theme.value
  return {
    aria: { enabled: true, label: { description: messages.panels.outlook.chartDescription } },
    textStyle: { color: t.muted, fontFamily: t.font },
    grid: { left: 48, right: 18, top: 24, bottom: 34 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      confine: true,
      backgroundColor: t.surface,
      borderColor: t.border,
      textStyle: { color: t.text },
      valueFormatter: (value: number) => `${value} %`,
    },
    xAxis: {
      type: 'value',
      name: messages.panels.outlook.probability,
      max: 100,
      axisLabel: { color: t.muted, formatter: (value: number) => `${value} %` },
      splitLine: { lineStyle: { color: t.grid } },
    },
    yAxis: {
      type: 'category',
      inverse: true,
      name: messages.panels.outlook.season,
      data: records.map((record) => record.season),
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
    },
    series: categories.map((category, categoryIndex) => ({
      name: outlookCategoryLabel(category),
      type: 'bar',
      stack: 'probability',
      data: records.map((record) => probability(record, outlookCategoryKey(category))),
      itemStyle: { color: t.ramp[categoryIndex], borderColor: t.surface, borderWidth: 1 },
    })),
  }
})
</script>

<template>
  <section class="panel outlook-panel" aria-labelledby="outlook-title">
    <div class="prose">
      <h2 id="outlook-title">{{ messages.panels.outlook.title }}</h2>
      <p class="source-label">{{ messages.panels.outlook.sourceLabel }}</p>
    </div>
    <div class="figure">
      <ChartShell :dataset="dataset" :summary="summary">
        <div class="outlook-meta">
          <span>{{ messages.panels.outlook.issueDate }}: {{ issueDate }}</span>
        </div>
        <NuxtErrorBoundary>
          <ClientOnly>
            <VChart class="chart" :option="option" autoresize :aria-label="messages.panels.outlook.chartAria" />
            <template #fallback>
              <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
            </template>
          </ClientOnly>
          <template #error>
            <div class="chart-placeholder">{{ messages.page.chartError }}</div>
          </template>
        </NuxtErrorBoundary>
        <ul class="category-key" :aria-label="messages.panels.outlook.probability">
          <li v-for="(category, index) in categories" :key="category.category">
            <span class="swatch" :style="{ backgroundColor: `var(--ramp-${index + 1})` }" aria-hidden="true" />
            {{ outlookCategoryLabel(category) }}
          </li>
        </ul>
      </ChartShell>
    </div>
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
  margin: 0 0 8px;
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.source-label {
  margin: 0;
  color: var(--muted);
  font-size: var(--fs-small);
  font-style: italic;
}
.figure {
  max-width: 960px;
  margin: 20px auto 0;
  padding: 0 16px;
}
.outlook-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 4px 16px;
  padding: 0 0 16px;
  color: var(--muted);
  font-size: var(--fs-small);
}
.chart {
  width: 100%;
  height: 430px;
}
.chart-placeholder {
  height: 430px;
  display: grid;
  place-items: center;
  color: var(--muted);
}
.category-key {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px 20px;
  margin: 16px 0 0;
  padding: 16px 0 0;
  border-top: 1px solid var(--border);
  list-style: none;
  color: var(--muted);
  font-size: var(--fs-small);
  line-height: 1.35;
}
.swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 5px;
  border-radius: 50%;
  vertical-align: 0;
}
@media (max-width: 599px) {
  .chart,
  .chart-placeholder {
    height: 360px;
  }
  .category-key {
    grid-template-columns: 1fr;
  }
}
</style>
