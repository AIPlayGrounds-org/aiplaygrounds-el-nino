<script setup lang="ts">
import { ageLabel, dataTypeLabel, messages } from "~/messages";
import type { DatasetLike } from "~/types/datasets";

const props = defineProps<{
  dataset: DatasetLike;
  summary: string;
}>();

const lastRecord = props.dataset.records.at(-1);
const formatDate = (date: string) =>
  new Intl.DateTimeFormat("es", { dateStyle: "long", timeZone: "America/Lima" }).format(
    new Date(date),
  );
const updateDate = formatDate(props.dataset.ingestion_time);
const updateAge = ageLabel(props.dataset.ingestion_time);
const dataAge = lastRecord ? ageLabel(lastRecord.end) : null;
const period = lastRecord
  ? lastRecord.start === lastRecord.end
    ? lastRecord.end
    : `${lastRecord.start}–${lastRecord.end}`
  : "—";
const periodDetails = [
  props.dataset.temporal_resolution,
  period,
  props.dataset.reference_period
    ? `${messages.provenance.periodBase}: ${props.dataset.reference_period}`
    : null,
]
  .filter(Boolean)
  .join(" · ");
</script>

<template>
  <section class="chart-shell" :aria-label="`${dataset.variable} · ${dataset.unit}`">
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
          <span> ({{ updateAge }})</span>
        </dd>
      </div>
    </dl>
    <p v-if="dataAge" class="data-age">
      {{ messages.provenance.latestData }}: {{ period }} ({{ dataAge }}).
    </p>
  </section>
</template>

<style scoped>
.chart-shell {
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
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
