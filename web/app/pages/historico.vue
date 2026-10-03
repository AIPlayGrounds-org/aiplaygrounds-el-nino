<script setup lang="ts">
import { messages } from '~/messages'
import { useDataset } from '~/composables/useDataset'
import HistoricoChart from '~/components/HistoricoChart.vue'
import { shapeHistoricoDataset, shapeHistoricoOniDataset } from '~/utils/historico'

const ersst = await useDataset('noaa-ersst', shapeHistoricoDataset)
const oni = await useDataset('noaa-cpc-oni', (dataset) =>
  shapeHistoricoOniDataset(dataset, ersst.records),
)

useSeoMeta({
  title: messages.historico.seoTitle,
  description: messages.historico.seoDescription,
})
</script>

<template>
  <div class="page">
    <header class="header">
      <NuxtLink class="brand" to="/">{{ messages.page.brand }}</NuxtLink>
      <NuxtLink to="/territorio">{{ messages.page.territoryLink }}</NuxtLink>
      <NuxtLink to="/historico">{{ messages.historico.historyNav }}</NuxtLink>
    </header>
    <main>
      <section class="intro" aria-labelledby="history-title">
        <p class="eyebrow">{{ messages.page.brand }}</p>
        <h1 id="history-title">{{ messages.historico.title }}</h1>
        <p>{{ messages.historico.lead }}</p>
      </section>
      <section class="figure" aria-labelledby="comparison-title" data-dataset="noaa-ersst">
        <h2 id="comparison-title">{{ messages.historico.comparisonTitle }}</h2>
        <HistoricoChart :dataset="ersst" :oni="oni" />
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
  justify-content: space-between;
  gap: 24px;
  max-width: 68rem;
  margin: 0 auto;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border);
}
.brand {
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
  margin-bottom: 44px;
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
  max-width: 38rem;
  margin-top: 24px;
  color: var(--muted);
  font-size: 1.2rem;
}
h2 {
  margin: 0 0 16px;
  font-size: clamp(1.5rem, 3vw, 2rem);
}
@media (max-width: 599px) {
  .header {
    padding-inline: 16px;
  }
  main {
    padding: 40px 16px 56px;
  }
}
</style>
