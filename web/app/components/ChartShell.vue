<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ageDays, ageLabel, dataTypeLabel, messages } from '~/messages'
import { staleAfterHours, type DatasetId } from '~/types/dataset'
import type { DatasetLike } from '~/types/datasets'

const props = defineProps<{
  dataset: DatasetLike
  summary: string
}>()

const firstRecord = props.dataset.records[0]
const lastRecord = props.dataset.records.at(-1)
// The registry owns the update tolerance for each automatic source.
const staleUpdateHours = staleAfterHours[props.dataset.id as DatasetId]
const STALE_RECORD_DAYS = 90
const now = ref<Date | null>(null)
onMounted(() => (now.value = new Date()))
const formatDate = (date: string) =>
  new Intl.DateTimeFormat('es', { dateStyle: 'long', timeZone: 'America/Lima' }).format(
    new Date(date),
  )
const updateDate = formatDate(props.dataset.ingestion_time)
const updateAge = computed(() =>
  now.value ? ageLabel(props.dataset.ingestion_time, now.value) : null,
)
const dataAge = computed(() =>
  now.value && lastRecord ? ageLabel(lastRecord.end, now.value) : null,
)
const staleNotice = computed(() => {
  if (!now.value) return false
  const updateHours =
    (now.value.getTime() - new Date(props.dataset.ingestion_time).getTime()) / 3_600_000
  const recordDays = lastRecord ? ageDays(lastRecord.end, now.value) : 0
  return (
    (staleUpdateHours !== undefined && updateHours > staleUpdateHours) ||
    recordDays >= STALE_RECORD_DAYS
  )
})
const period =
  firstRecord && lastRecord
    ? firstRecord.start === lastRecord.end
      ? firstRecord.start
      : `${firstRecord.start}–${lastRecord.end}`
    : '—'
const periodDetails = [
  props.dataset.temporal_resolution,
  period,
  props.dataset.reference_period
    ? `${messages.provenance.periodBase}: ${props.dataset.reference_period}`
    : null,
]
  .filter(Boolean)
  .join(' · ')
</script>

<template>
  <div class="chart-shell" role="group" :aria-label="`${dataset.variable} · ${dataset.unit}`">
    <div class="chart-region">
      <slot />
    </div>
    <p class="chart-summary">{{ summary }}</p>
    <dl class="provenance">
      <div>
        <dt>{{ messages.provenance.variable }}</dt>
        <dd>{{ dataset.variable }}</dd>
      </div>
      <div>
        <dt>{{ messages.provenance.unit }}</dt>
        <dd>{{ dataset.unit }}</dd>
      </div>
      <div>
        <dt>{{ messages.provenance.period }}</dt>
        <dd>{{ periodDetails }}</dd>
      </div>
      <div>
        <dt>{{ messages.provenance.dataType }}</dt>
        <dd>{{ dataTypeLabel(dataset.data_type) }}</dd>
      </div>
      <div>
        <dt>{{ messages.provenance.source }}</dt>
        <dd>
          <a :href="dataset.source.url" target="_blank" rel="noopener">
            {{ dataset.source.institution }}
            <span class="sr-only">{{ messages.page.newTab }}</span>
          </a>
          <span aria-hidden="true"> · {{ dataset.source.product }}</span>
        </dd>
      </div>
      <div>
        <dt>{{ messages.provenance.lastUpdate }}</dt>
        <dd>
          <time :datetime="dataset.ingestion_time">{{ updateDate }}</time>
          <span v-if="updateAge"> ({{ updateAge }})</span>
        </dd>
      </div>
    </dl>
    <p v-if="dataAge" class="data-age">
      {{ messages.provenance.latestData }}: {{ lastRecord?.end ?? '—' }} ({{ dataAge }}).
    </p>
    <p v-if="staleNotice" class="stale-notice" role="status">
      {{ messages.provenance.staleSource }}
      <a :href="dataset.source.url" target="_blank" rel="noopener">
        {{ messages.page.reviewSource }}
        <span class="sr-only">{{ messages.page.newTab }}</span>
      </a>
    </p>
  </div>
</template>

<style scoped>
.chart-shell {
  min-width: 0;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}
.chart-region {
  padding: 16px 16px 0;
}
.chart-summary {
  max-width: 60rem;
  margin: 12px 16px 0;
  color: var(--muted);
  font-size: 0.95rem;
}
.provenance {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr));
  gap: 12px 20px;
  margin: 20px 16px 0;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  font-size: 0.95rem;
}
.provenance div {
  min-width: 0;
}
.provenance dt {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 650;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.provenance dd {
  margin: 2px 0 0;
  overflow-wrap: anywhere;
}
.data-age {
  margin: 16px;
  padding: 10px 12px;
  border-left: 3px solid var(--accent);
  background: var(--band);
  font-size: 0.95rem;
}
.stale-notice {
  margin: 0 16px 16px;
  color: var(--muted);
  font-size: 0.95rem;
}
</style>
