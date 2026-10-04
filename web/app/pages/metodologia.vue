<script setup lang="ts">
import DatasetAttribution from '~/components/DatasetAttribution.vue'
import { useSourceCatalog } from '~/composables/useSourceCatalog'
import { dataTypeLabel, messages } from '~/messages'
import { formatDay } from '~/utils/format'
import { sourceGroupId } from '~/utils/sourceCatalog'

const methodology = messages.metodologia
const catalog = await useSourceCatalog()
const sourceNamesByDataType = (dataType: string) =>
  [
    ...new Set(
      catalog.groups
        .flatMap((group) => group.sources)
        .filter((source) => source.dataType === dataType)
        .map((source) => source.name),
    ),
  ].join(', ')
const estimatedSources = sourceNamesByDataType('estimated')
const forecastSources = sourceNamesByDataType('forecast')

useSeoMeta({ title: methodology.seoTitle, description: methodology.seoDescription })
</script>

<template>
  <div class="page">
    <header class="header">
      <NuxtLink class="brand" to="/">{{ messages.page.brand }}</NuxtLink>
      <NuxtLink to="/territorio">{{ messages.page.territoryLink }}</NuxtLink>
      <NuxtLink to="/historico">{{ messages.historico.historyNav }}</NuxtLink>
      <NuxtLink to="/rios">{{ messages.rios.sectionLabel }}</NuxtLink>
      <NuxtLink to="/aprende">{{ messages.page.learnLink }}</NuxtLink>
      <NuxtLink to="/metodologia">{{ messages.page.methodologyLink }}</NuxtLink>
    </header>

    <main id="main-content">
      <section class="intro" aria-labelledby="methodology-title">
        <p class="eyebrow">{{ methodology.sectionLabel }}</p>
        <h1 id="methodology-title">{{ methodology.title }}</h1>
        <p>{{ methodology.lead }}</p>
      </section>

      <section
        v-for="group in catalog.groups"
        :key="group.page"
        class="source-group"
        :aria-labelledby="`${sourceGroupId(group.page)}-title`"
      >
        <h2 :id="`${sourceGroupId(group.page)}-title`">
          {{ group.label }}
        </h2>
        <div class="source-list">
          <article v-for="source in group.sources" :key="source.id" class="source-card">
            <h3>{{ source.name }}</h3>
            <p class="provider">
              {{ methodology.provider }}:
              <a :href="source.providerUrl" target="_blank" rel="noopener">
                {{ source.provider }}<span class="sr-only">{{ messages.page.newTab }}</span>
              </a>
            </p>
            <dl>
              <div>
                <dt>{{ methodology.variable }}</dt>
                <dd>{{ source.variable }}</dd>
              </div>
              <div>
                <dt>{{ methodology.unit }}</dt>
                <dd>{{ source.unit }}</dd>
              </div>
              <div>
                <dt>{{ methodology.resolution }}</dt>
                <dd>
                  <span>{{ methodology.spatialResolution }}: {{ source.spatialResolution }}</span>
                  <span>{{ methodology.temporalResolution }}: {{ source.temporalResolution }}</span>
                </dd>
              </div>
              <div>
                <dt>{{ methodology.referencePeriod }}</dt>
                <dd>{{ source.referencePeriod ?? methodology.noReferencePeriod }}</dd>
              </div>
              <div>
                <dt>{{ methodology.license }}</dt>
                <dd>{{ source.license ?? methodology.noLicense }}</dd>
              </div>
              <div>
                <dt>{{ methodology.lastUpdate }}</dt>
                <dd>
                  <time :datetime="source.lastUpdate">{{
                    formatDay(source.lastUpdate.slice(0, 10))
                  }}</time>
                  · {{ dataTypeLabel(source.dataType) }}
                </dd>
              </div>
            </dl>
            <p class="source-links">
              <a :href="source.dataUrl" target="_blank" rel="noopener">
                {{ methodology.dataLink }}<span class="sr-only">{{ messages.page.newTab }}</span>
              </a>
            </p>
            <DatasetAttribution :dataset="source" />
          </article>
        </div>
      </section>

      <section class="note-section" aria-labelledby="methodology-types-title">
        <h2 id="methodology-types-title">{{ methodology.dataTypeTitle }}</h2>
        <p>{{ methodology.dataTypeLead }}</p>
        <ul>
          <li>
            <strong>{{ dataTypeLabel('observed') }}.</strong>
            {{ methodology.dataTypeDescription('observed') }}
          </li>
          <li>
            <strong>{{ dataTypeLabel('estimated') }}.</strong>
            {{ methodology.dataTypeDescription('estimated') }}
          </li>
          <li>
            <strong>{{ dataTypeLabel('forecast') }}.</strong>
            {{ methodology.dataTypeDescription('forecast') }}
          </li>
          <li>
            <strong>{{ dataTypeLabel('official') }}.</strong>
            {{ methodology.dataTypeDescription('official') }}
          </li>
        </ul>
      </section>

      <section class="note-section" aria-labelledby="methodology-models-title">
        <h2 id="methodology-models-title">{{ methodology.modelTitle }}</h2>
        <p>{{ methodology.modelBody(estimatedSources, forecastSources) }}</p>
      </section>

      <section class="note-section" aria-labelledby="methodology-limits-title">
        <h2 id="methodology-limits-title">{{ methodology.limitsTitle }}</h2>
        <ul>
          <li v-for="limit in methodology.limits" :key="limit">{{ limit }}</li>
        </ul>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100svh;
}
.header {
  display: flex;
  align-items: baseline;
  gap: 24px;
  max-width: 68rem;
  margin: 0 auto;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border);
}
.brand {
  margin-right: auto;
  color: var(--text);
  font-family: var(--hand);
  font-size: 1.5rem;
  line-height: 1;
  text-decoration: none;
}
main {
  max-width: 68rem;
  margin: 0 auto;
  padding: 56px 20px 80px;
}
.intro {
  max-width: 44rem;
  margin-bottom: 54px;
}
.eyebrow {
  margin: 0 0 8px;
  color: var(--accent);
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
h1 {
  max-width: 15ch;
  margin: 0;
  font-size: clamp(2.7rem, 8vw, 5.3rem);
  line-height: 0.98;
  letter-spacing: -0.03em;
  text-wrap: balance;
}
.intro > p:last-child {
  max-width: 42rem;
  margin-top: 24px;
  color: var(--muted);
  font-size: 1.2rem;
}
.source-group {
  margin-top: 48px;
}
h2 {
  margin: 0 0 18px;
  font-size: clamp(1.5rem, 3vw, 2rem);
  line-height: 1.1;
}
.source-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 28rem), 1fr));
  gap: 18px;
}
.source-card {
  padding: 24px;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--sea) 32%, var(--paper));
}
.source-card h3 {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.2;
}
.provider {
  margin: 10px 0 22px;
  color: var(--muted);
  font-size: 1rem;
}
.source-card dl {
  margin: 0;
}
.source-card dl > div {
  display: grid;
  grid-template-columns: minmax(8rem, 0.7fr) 1.3fr;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--border);
}
.source-card dt {
  color: var(--muted);
  font-size: 0.95rem;
}
.source-card dd {
  margin: 0;
  overflow-wrap: anywhere;
  font-size: 1rem;
}
.source-card dd span {
  display: block;
}
.source-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin: 18px 0 0;
  font-size: 1rem;
}
.note-section {
  max-width: 48rem;
  margin-top: 64px;
  padding-top: 28px;
  border-top: 1px solid var(--border);
}
.note-section p {
  margin-top: 0;
  color: var(--muted);
}
.note-section ul {
  margin: 16px 0 0;
  padding-left: 1.2em;
}
@media (max-width: 900px) {
  .header {
    flex-wrap: wrap;
    gap: 12px 20px;
  }
  .brand {
    flex-basis: 100%;
  }
}
@media (max-width: 599px) {
  .header {
    padding-inline: 16px;
  }
  main {
    padding: 40px 16px 56px;
  }
  .source-card {
    padding: 18px;
  }
  .source-card dl > div {
    display: block;
  }
  .source-card dt {
    margin-bottom: 3px;
  }
}
</style>
