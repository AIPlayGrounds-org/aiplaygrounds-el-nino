<script setup lang="ts">
import { computed, ref } from 'vue'
import { MapChart } from 'echarts/charts'
import { AriaComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { registerMap, use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import ChartShell from '~/components/ChartShell.vue'
import DatasetAttribution from '~/components/DatasetAttribution.vue'
import { messages } from '~/messages'
import type { ChirpsRecord } from '~/types/dataset'
import { useChartTheme } from '~/composables/useChartTheme'
import { useDataset } from '~/composables/useDataset'
import { formatValue } from '~/utils/format'
import {
  joinTerritoryRows,
  metricValue,
  shapeDepartmentGeometry,
  shapeEra5Summary,
  shapeLatestChirps,
  type TerritoryMetric,
} from '~/composables/territorio'
import { useSiteSeo } from '~/composables/useSiteSeo'

use([MapChart, TooltipComponent, VisualMapComponent, AriaComponent, CanvasRenderer])

// Each dataset is reduced on the server to what this page draws, to keep the payload small.
const geometry = await useDataset('limites-inei-ign', shapeDepartmentGeometry)
const geometryRecord = geometry.records[0]
const [chirps, era5] = await Promise.all([
  useDataset('chirps', shapeLatestChirps),
  useDataset('open-meteo-era5', shapeEra5Summary(geometryRecord?.departamentos.features ?? [])),
])

const territory = messages.territory
const metric = ref<TerritoryMetric>('precipitation')
const mapName = 'wawapacha-peru-departamentos'

if (geometryRecord) registerMap(mapName, geometryRecord.departamentos)

const territoryRows = geometryRecord
  ? joinTerritoryRows(geometryRecord, chirps.records, era5.departments)
  : []
const latestChirps = territoryRows.flatMap((row) => (row.chirps ? [row.chirps] : []))
const latestByCode = new Map(latestChirps.map((record) => [record.code, record]))
const regionByCode = new Map(territoryRows.map((row) => [row.code, row.region]))
const latestChirpsDate = chirps.records.at(-1)?.end ?? ''
const era5Records = territoryRows.flatMap((row) =>
  row.era5 ? [{ ...row.era5, chirps: row.chirps }] : [],
)

const metricLabel = computed(() =>
  metric.value === 'precipitation' ? territory.precipitation : territory.anomaly,
)
const number = new Intl.NumberFormat('es-PE', { maximumFractionDigits: 1 })
const formatAmount = (value: number | null | undefined, unit: string) =>
  value === null || value === undefined
    ? territory.noData
    : territory.value(number.format(value), unit)
const displayPrecipitation = (value: number | null | undefined) =>
  formatAmount(value, territory.precipitationUnit)
const displayAnomaly = (value: number | null | undefined) =>
  value === null || value === undefined
    ? territory.noData
    : territory.value(formatValue(value), territory.anomalyUnit)
const displayMetricValue = (record: ChirpsRecord) =>
  metric.value === 'precipitation'
    ? displayPrecipitation(record.precipitation_mm)
    : displayAnomaly(record.anomaly_mm)
const displayEra5 = (record: (typeof era5Records)[number]) =>
  record.total === null
    ? territory.era5Missing(record.availableDays, record.missingDays)
    : formatAmount(record.total, territory.era5Unit)

const scale = computed(() => {
  if (metric.value === 'precipitation') {
    return {
      min: 0,
      max: Math.max(...latestChirps.map((record) => record.precipitation_mm ?? 0), 1),
    }
  }
  const maximum = Math.max(...latestChirps.map((record) => Math.abs(record.anomaly_mm ?? 0)), 1)
  return { min: -maximum, max: maximum }
})

const theme = useChartTheme()

const mapData = computed(() =>
  latestChirps.map((record) => ({
    name: record.code,
    value: metricValue(record, metric.value),
  })),
)

const option = computed(() => {
  const colors =
    metric.value === 'anomaly'
      ? theme.value.ramp
      : [theme.value.sea, theme.value.seaEdge, theme.value.deep]
  return {
    aria: { enabled: true, label: { description: territory.mapAria(metricLabel.value) } },
    textStyle: { color: theme.value.muted, fontFamily: theme.value.font },
    tooltip: {
      trigger: 'item',
      confine: true,
      backgroundColor: theme.value.surface,
      borderColor: theme.value.border,
      textStyle: { color: theme.value.text },
      formatter: (params: { name: string }) => {
        const record = latestByCode.get(params.name)
        if (!record) return regionByCode.get(params.name) ?? territory.noData
        return territory.mapTooltip(
          record.region,
          displayMetricValue(record),
          displayPrecipitation(record.precipitation_mm),
          displayAnomaly(record.anomaly_mm),
        )
      },
    },
    visualMap: {
      min: scale.value.min,
      max: scale.value.max,
      left: 'center',
      bottom: 8,
      calculable: false,
      textStyle: { color: theme.value.muted },
      inRange: { color: colors },
      formatter: (value: number) => number.format(value),
    },
    series: [
      {
        type: 'map',
        map: mapName,
        nameProperty: 'code',
        name: metricLabel.value,
        roam: true,
        selectedMode: false,
        data: mapData.value,
        itemStyle: {
          areaColor: theme.value.surface,
          borderColor: theme.value.border,
          borderWidth: 0.7,
        },
        emphasis: { itemStyle: { borderColor: theme.value.text, borderWidth: 1.5 } },
      },
    ],
  }
})

const chirpsSummary = computed(() =>
  latestChirpsDate
    ? territory.chirpsSummary(metricLabel.value, latestChirpsDate, latestChirps.length)
    : territory.tableEmpty,
)
const mapSummary = computed(() =>
  latestChirpsDate ? territory.mapSummary(metricLabel.value, latestChirpsDate) : territory.mapEmpty,
)
const era5Summary = computed(() =>
  era5.window.start
    ? territory.era5Summary(
        era5.window.days,
        era5.window.start,
        era5.window.end,
        era5Records.length,
      )
    : territory.era5Empty,
)

useSiteSeo({ title: territory.seoTitle, description: territory.seoDescription })
</script>

<template>
  <main id="main-content" class="territory-page">
    <header class="topbar">
      <NuxtLink class="brand" to="/">{{ messages.page.brand }}</NuxtLink>
      <span class="section-label">{{ territory.sectionLabel }}</span>
      <NuxtLink to="/rios">{{ messages.rios.sectionLabel }}</NuxtLink>
      <NuxtLink to="/aprende">{{ messages.page.learnLink }}</NuxtLink>
      <NuxtLink to="/metodologia">{{ messages.page.methodologyLink }}</NuxtLink>
    </header>

    <section class="intro" aria-labelledby="territory-title">
      <h1 id="territory-title">{{ territory.title }}</h1>
      <p>{{ territory.lead }}</p>
      <p>{{ territory.leadDetails }}</p>
      <div class="metric-toggle" role="group" :aria-label="territory.metricGroup">
        <button
          type="button"
          :aria-pressed="metric === 'precipitation'"
          @click="metric = 'precipitation'"
        >
          {{ territory.precipitation }}
        </button>
        <button type="button" :aria-pressed="metric === 'anomaly'" @click="metric = 'anomaly'">
          {{ territory.anomaly }}
        </button>
      </div>
    </section>

    <section class="map-section" aria-labelledby="map-title">
      <h2 id="map-title" class="sr-only">{{ territory.mapHeading }}</h2>
      <ChartShell :dataset="chirps" :summary="mapSummary">
        <template v-if="geometryRecord && latestChirps.length">
          <NuxtErrorBoundary>
            <ClientOnly>
              <VChart class="map" :option="option" autoresize />
              <template #fallback>
                <div class="chart-placeholder">{{ territory.loading }}</div>
              </template>
            </ClientOnly>
            <template #error>
              <div class="chart-placeholder">{{ territory.chartError }}</div>
            </template>
          </NuxtErrorBoundary>
        </template>
        <p v-else class="empty-state" role="status">{{ territory.mapEmpty }}</p>
        <p class="secondary-provenance">
          {{ territory.boundaryProvenance }}
          <a v-if="geometryRecord" :href="geometry.source.url" target="_blank" rel="noopener">
            {{ geometry.source.institution }}<span class="sr-only">{{ messages.page.newTab }}</span>
          </a>
          <template v-if="geometryRecord">
            · {{ geometryRecord.attribution }}
            <a :href="geometryRecord.license_url" target="_blank" rel="noopener">
              {{ territory.boundaryLicense }}<span class="sr-only">{{ messages.page.newTab }}</span>
            </a>
          </template>
        </p>
      </ChartShell>
    </section>

    <section class="tables" :aria-label="territory.tableSection">
      <ChartShell :dataset="chirps" :summary="chirpsSummary">
        <details v-if="latestChirps.length" open>
          <summary>{{ territory.tableSummary }}</summary>
          <div class="table-wrap" role="region" :aria-label="territory.tableSummary" tabindex="0">
            <table>
              <caption>
                {{
                  territory.chirpsCaption(latestChirpsDate)
                }}
              </caption>
              <thead>
                <tr>
                  <th scope="col">{{ territory.department }}</th>
                  <th scope="col">{{ territory.code }}</th>
                  <th scope="col" class="num">{{ territory.precipitation }}</th>
                  <th scope="col" class="num">{{ territory.anomaly }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in latestChirps" :key="record.code">
                  <th scope="row">{{ record.region }}</th>
                  <td>{{ record.code }}</td>
                  <td class="num">{{ displayPrecipitation(record.precipitation_mm) }}</td>
                  <td class="num">{{ displayAnomaly(record.anomaly_mm) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
        <p v-else class="empty-state" role="status">{{ territory.tableEmpty }}</p>
      </ChartShell>

      <ChartShell :dataset="era5" :summary="era5Summary">
        <div v-if="era5Records.length" class="cross-check">
          <h2>{{ territory.crossCheckTitle }}</h2>
          <p>{{ territory.crossCheckClaim }}</p>
          <p>{{ territory.crossCheckLimits }}</p>
          <p>
            {{ territory.crossCheckLead(era5.window.days, era5.window.start, era5.window.end) }}
          </p>
          <div
            class="table-wrap"
            role="region"
            :aria-label="territory.crossCheckCaption"
            tabindex="0"
          >
            <table>
              <caption>
                {{
                  territory.crossCheckCaption
                }}
              </caption>
              <thead>
                <tr>
                  <th scope="col">{{ territory.department }}</th>
                  <th scope="col">{{ territory.code }}</th>
                  <th scope="col" class="num">{{ territory.chirpsValue }}</th>
                  <th scope="col" class="num">{{ territory.era5Sum }}</th>
                  <th scope="col">{{ territory.sampleType }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in era5Records" :key="record.code">
                  <th scope="row">{{ record.region }}</th>
                  <td>{{ record.code }}</td>
                  <td class="num">{{ displayPrecipitation(record.chirps?.precipitation_mm) }}</td>
                  <td class="num">{{ displayEra5(record) }}</td>
                  <td>{{ territory.pointSample }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <DatasetAttribution :dataset="era5" />
        </div>
        <p v-else class="empty-state" role="status">{{ territory.era5Empty }}</p>
      </ChartShell>
    </section>
  </main>
</template>

<style scoped>
.territory-page {
  min-height: 100svh;
  padding-bottom: 64px;
}
.topbar {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 18px 16px;
}
.brand {
  color: var(--text);
  font-family: var(--hand);
  font-size: 1.5rem;
  line-height: 1;
  text-decoration: none;
}
.section-label {
  color: var(--muted);
  font-size: 0.95rem;
}
.intro,
.map-section,
.tables {
  max-width: 1100px;
  margin-right: auto;
  margin-left: auto;
  padding-right: 16px;
  padding-left: 16px;
}
.intro {
  padding-top: clamp(40px, 8vw, 88px);
  padding-bottom: 32px;
}
h1 {
  max-width: 18ch;
  margin: 0;
  font-size: clamp(2.75rem, 8vw, 5.25rem);
  font-weight: 900;
  line-height: 0.96;
  letter-spacing: -0.035em;
  text-wrap: balance;
}
.intro p {
  max-width: 44rem;
  margin: 24px 0 0;
  color: var(--muted);
  font-size: 1.15rem;
}
.metric-toggle {
  display: inline-flex;
  gap: 6px;
  margin-top: 24px;
}
.metric-toggle button {
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--paper);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 0.95rem;
}
.metric-toggle button[aria-pressed='true'] {
  border-color: var(--text);
  background: var(--text);
  color: var(--paper);
  font-weight: 650;
}
.map-section {
  padding-bottom: 32px;
}
.map {
  width: 100%;
  height: min(65vw, 620px);
  min-height: 360px;
}
.chart-placeholder {
  display: grid;
  min-height: 360px;
  place-items: center;
  color: var(--muted);
  text-align: center;
}
.secondary-provenance {
  margin: 16px;
  color: var(--muted);
  font-size: 0.95rem;
}
.tables {
  display: grid;
  gap: 32px;
}
.tables > * {
  min-width: 0;
}
details {
  padding: 16px;
}
summary {
  color: var(--text);
  cursor: pointer;
  font-weight: 650;
}
.table-wrap {
  overflow-x: auto;
  margin-top: 16px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
caption {
  margin-bottom: 12px;
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
.cross-check {
  padding: 16px;
}
h2 {
  margin: 0;
  font-size: 1.4rem;
  line-height: 1.15;
}
.cross-check p {
  margin: 10px 0 0;
  color: var(--muted);
}
.empty-state {
  margin: 0;
  padding: 32px 16px;
  color: var(--muted);
}
@media (max-width: 599px) {
  .map {
    min-height: 320px;
  }
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
