<script setup lang="ts">
import RiosChart from '~/components/RiosChart.vue'
import { useDataset } from '~/composables/useDataset'
import { messages } from '~/messages'
import { ENFEN_COMUNICADOS, SENAMHI_AVISOS } from '~/links'
import { shapeRiosDataset } from '~/utils/rios'

const rios = await useDataset('open-meteo-glofas', shapeRiosDataset)

useSeoMeta({ title: messages.rios.seoTitle, description: messages.rios.seoDescription })
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

    <main>
      <section class="intro" aria-labelledby="rios-title">
        <p class="eyebrow">{{ messages.page.brand }}</p>
        <h1 id="rios-title">{{ messages.rios.title }}</h1>
        <p>{{ messages.rios.lead }}</p>
      </section>

      <section class="figure" aria-labelledby="rios-title">
        <RiosChart :dataset="rios" />
      </section>

      <section class="alerts" aria-labelledby="alerts-title">
        <h2 id="alerts-title">{{ messages.rios.alertsTitle }}</h2>
        <p>{{ messages.rios.alertsLead }}</p>
        <ul>
          <li>
            <a :href="ENFEN_COMUNICADOS" target="_blank" rel="noopener"
              >{{ messages.rios.enfenLink
              }}<span class="sr-only">{{ messages.page.newTab }}</span></a
            >
          </li>
          <li>
            <a :href="SENAMHI_AVISOS" target="_blank" rel="noopener"
              >{{ messages.rios.senamhiLink
              }}<span class="sr-only">{{ messages.page.newTab }}</span></a
            >
          </li>
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
  max-width: 42rem;
  margin-top: 24px;
  color: var(--muted);
  font-size: 1.2rem;
}
.figure {
  max-width: 68rem;
}
.alerts {
  max-width: 44rem;
  margin-top: 48px;
  padding-top: 28px;
  border-top: 1px solid var(--border);
}
.alerts h2 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2rem);
  line-height: 1.1;
}
.alerts p {
  margin: 12px 0 0;
  color: var(--muted);
}
.alerts ul {
  margin: 16px 0 0;
  padding-left: 1.2em;
}
@media (max-width: 599px) {
  .header {
    flex-wrap: wrap;
    gap: 12px 20px;
    padding-inline: 16px;
  }
  .brand {
    flex-basis: 100%;
  }
  main {
    padding: 40px 16px 56px;
  }
}
</style>
