<script setup lang="ts">
import { computed } from 'vue'
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'
import { formatDay } from '~/utils/format'

const props = defineProps<{
  dataset: DatasetFor<'enfen-communique'>
}>()

const record = props.dataset.records.at(-1)
const summary = computed(() =>
  record
    ? messages.panels.enfen.summary(record.status, formatDay(record.start))
    : messages.panels.enfen.empty,
)
</script>

<template>
  <section class="panel enfen-panel" aria-labelledby="enfen-title">
    <div class="prose">
      <h2 id="enfen-title">{{ messages.panels.enfen.title }}</h2>
    </div>
    <div class="figure">
      <ChartShell :dataset="dataset" :summary="summary">
        <article v-if="record" class="status-card">
          <p class="number">{{ messages.panels.enfen.number(record.number, record.year) }}</p>
          <dl>
            <div>
              <dt>{{ messages.panels.enfen.date }}</dt>
              <dd>
                <time :datetime="record.start">{{ formatDay(record.start) }}</time>
              </dd>
            </div>
            <div>
              <dt>
                {{
                  record.stale ? messages.panels.enfen.latestStatus : messages.panels.enfen.status
                }}
              </dt>
              <dd class="status">{{ record.status }}</dd>
            </div>
            <div>
              <dt>{{ messages.panels.enfen.nextDue }}</dt>
              <dd v-if="record.stale" class="stale-status" role="status">
                {{ messages.panels.enfen.nextDueStale(formatDay(record.end)) }}
              </dd>
              <dd v-else>
                <time :datetime="record.end">{{ formatDay(record.end) }}</time>
              </dd>
            </div>
          </dl>
          <a class="detail-link" :href="record.url" target="_blank" rel="noopener">
            {{ messages.panels.enfen.detail }}
            <span class="sr-only">{{ messages.page.newTab }}</span>
          </a>
        </article>
        <p v-else class="empty-state" role="status">{{ messages.panels.enfen.empty }}</p>
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
.status-card {
  display: grid;
  gap: 20px;
  padding: 20px 16px 16px;
  border-left: 5px solid var(--accent);
  background: var(--band);
}
.empty-state {
  margin: 0;
  padding: 32px 0;
  color: var(--muted);
}
.number {
  margin: 0;
  color: var(--muted);
  font-size: var(--fs-small);
  font-weight: 650;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px 24px;
  margin: 0;
}
dt {
  color: var(--muted);
  font-size: var(--fs-small);
}
dd {
  margin: 2px 0 0;
  font-variant-numeric: tabular-nums;
}
.status {
  font-size: clamp(1.35rem, 3vw, 1.75rem);
  font-weight: 800;
  line-height: 1.15;
}
.detail-link {
  width: fit-content;
  font-weight: 650;
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
@media (max-width: 599px) {
  dl {
    grid-template-columns: 1fr;
  }
}
</style>
