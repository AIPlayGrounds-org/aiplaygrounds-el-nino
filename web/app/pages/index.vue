<script setup lang="ts">
import { messages } from '~/messages'
import { useDataset } from '~/composables/useDataset'
import { cropOisst } from '~/utils/oisstMap'
import { ENFEN_COMUNICADOS, SENAMHI_AVISOS } from '~/links'

const oni = await useDataset('noaa-cpc-oni')
const oisst = await useDataset('noaa-oisst', cropOisst)
const weekly = await useDataset('noaa-cpc-nino-weekly')
const enfen = await useDataset('enfen-communique')
const outlook = await useDataset('noaa-cpc-outlook')
const records = oni.records
const last = records.at(-1)

const CPC_ONI_PAGE = 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/'
const phase = last ? ensoPhase(last.anomaly) : 'neutral'
const streak = phaseStreak(records)

/** Responde en llano a «¿hay El Niño (o La Niña)?» con la definición de episodio de NOAA. */
const status = computed(() => {
  if (!last || phase === 'neutral') {
    return {
      title: messages.oni.neutralTitle,
      detail: messages.oni.neutralDetail,
    }
  }
  const name = phase === 'warm' ? messages.oni.warmName : messages.oni.coldName
  const side = phase === 'warm' ? messages.oni.warmSide : messages.oni.coldSide
  if (streak >= NOAA_EPISODE_SEASONS) {
    return {
      title: messages.oni.episodeTitle(name),
      detail: messages.oni.episodeDetail(streak, side),
    }
  }
  const umbral =
    phase === 'warm'
      ? messages.oni.aboveTitle(messages.oni.warmName)
      : messages.oni.belowTitle(messages.oni.coldName)
  return {
    title: umbral,
    detail: messages.oni.belowDetail(streak, side, name),
  }
})

/**
 * La respuesta corta a la pregunta del titular. Habla de la regla de episodio de NOAA (5 trimestres seguidos
 * sobre el umbral), no de un estado oficial: NOAA monitorea hoy con el RONI. Pendiente de revisión de Contenido.
 */
const answer = computed(() => {
  if (!last) return null
  const value = `${formatAnomaly(last.anomaly)} °C`
  const rule = messages.oni.episodeRule(streak)
  if (phase === 'warm') {
    return streak >= NOAA_EPISODE_SEASONS
      ? {
          short: messages.oni.yes,
          lead: messages.oni.centralWarm,
          value,
          tail: messages.oni.warmTail(streak),
        }
      : {
          short: messages.oni.notYet,
          lead: messages.oni.centralAbove,
          value,
          tail: messages.oni.warmNotYetTail(rule),
        }
  }
  if (phase === 'cold')
    return {
      short: messages.oni.no,
      lead: messages.oni.centralWarm,
      value,
      tail: messages.oni.coldTail,
    }
  return {
    short: messages.oni.no,
    lead: messages.oni.centralNear,
    value,
    tail: messages.oni.neutralTail,
  }
})

const description = computed(() =>
  last
    ? messages.oni.summary(
        monthName(records[0]!.start),
        monthName(last.end),
        `${seasonLabel(last)}, ${formatAnomaly(last.anomaly)} °C`,
        status.value.title,
      )
    : '',
)

const recent = records.slice(-12).reverse()
const phaseLabel = {
  warm: messages.oni.rangeLabel('warm'),
  neutral: messages.oni.rangeLabel('neutral'),
  cold: messages.oni.rangeLabel('cold'),
} as const

useSeoMeta({
  title: messages.page.seoTitle,
  description: messages.page.seoDescription,
  ogTitle: messages.page.seoTitle,
  ogDescription: last
    ? `${seasonLabel(last)}: ${formatAnomaly(last.anomaly)} °C. ${status.value.title}.`
    : messages.page.seoTitle,
})
</script>

<template>
  <div class="site">
    <main id="main-content">
      <template v-if="last && answer">
        <div class="cover">
          <header class="topbar">
            <span class="brand">{{ messages.page.brand }}</span>
            <NuxtLink to="/territorio">{{ messages.page.territoryLink }}</NuxtLink>
            <NuxtLink to="/historico">{{ messages.historico.historyNav }}</NuxtLink>
            <NuxtLink to="/rios">{{ messages.rios.sectionLabel }}</NuxtLink>
            <NuxtLink to="/aprende">{{ messages.page.learnLink }}</NuxtLink>
            <NuxtLink to="/metodologia">{{ messages.page.methodologyLink }}</NuxtLink>
          </header>
          <section class="hero" aria-labelledby="oni-title">
            <h1 id="oni-title">{{ messages.page.title }}</h1>
            <p class="answer">
              <strong>{{ answer.short }}</strong>
              {{ answer.lead }}
              <span class="value" :class="phase">{{ answer.value }}</span>
              {{ answer.tail }}
            </p>
            <p class="byline">
              {{ messages.page.dataBy }}
              <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener"
                >NOAA<span class="sr-only">{{ messages.page.newTab }}</span></a
              >,
              {{ messages.page.observedUntil(monthName(last.end)) }}
            </p>
            <p class="cue" aria-hidden="true">
              {{ messages.page.scrollCue }}
              <svg width="18" height="28" viewBox="0 0 18 28">
                <path d="M9 2 V24 M2 17 L9 24 L16 17" />
              </svg>
            </p>
          </section>
          <OniStripes class="cover-stripes" :dataset="oni" />
        </div>

        <OniStory :dataset="oni" />

        <section class="oisst-panel" aria-labelledby="oisst-title">
          <div class="prose">
            <h2 id="oisst-title">{{ messages.oisst.title }}</h2>
            <p>{{ messages.oisst.lead }}</p>
          </div>
          <div class="figure">
            <OisstMap :dataset="oisst" />
          </div>
        </section>

        <div class="sand">
          <article class="prose">
            <h2 id="oni-peru">{{ messages.page.peruTitle }}</h2>
            <p>{{ messages.page.peruBody }}</p>
            <p class="key-point">
              <strong>{{ messages.page.peruWarning }}</strong>
            </p>
            <ul class="links">
              <li>
                <a :href="ENFEN_COMUNICADOS" target="_blank" rel="noopener"
                  >{{ messages.page.enfenLink
                  }}<span class="sr-only">{{ messages.page.newTab }}</span></a
                >
              </li>
              <li>
                <a :href="SENAMHI_AVISOS" target="_blank" rel="noopener"
                  >{{ messages.page.senamhiLink
                  }}<span class="sr-only">{{ messages.page.newTab }}</span></a
                >
              </li>
            </ul>
          </article>
        </div>

        <NinoWeeklyPanel :dataset="weekly" />
        <EnfenPanel :dataset="enfen" />
        <OutlookPanel :dataset="outlook" />

        <section class="explore" aria-labelledby="oni-history">
          <div class="prose">
            <h2 id="oni-history">{{ messages.page.historyTitle }}</h2>
            <p>{{ messages.page.historyLead }}</p>
          </div>
          <figure class="figure">
            <ChartShell :dataset="oni" :summary="description">
              <NuxtErrorBoundary>
                <ClientOnly>
                  <OniChart :dataset="oni" :description="description" />
                  <template #fallback>
                    <div class="chart-placeholder">{{ messages.page.chartLoading }}</div>
                  </template>
                </ClientOnly>
                <template #error>
                  <div class="chart-placeholder">
                    {{ messages.page.chartError }}
                  </div>
                </template>
              </NuxtErrorBoundary>
            </ChartShell>
            <figcaption>
              <ul class="key" :aria-label="messages.chart.colors">
                <li>
                  <span class="swatch warm" aria-hidden="true" />{{ messages.chart.warmThreshold }}
                </li>
                <li>
                  <span class="swatch neutral" aria-hidden="true" />{{
                    messages.chart.neutralRange
                  }}
                </li>
                <li>
                  <span class="swatch cold" aria-hidden="true" />{{ messages.chart.coldThreshold }}
                </li>
              </ul>
              {{ messages.chart.thresholdNote }}
            </figcaption>
          </figure>

          <details class="prose">
            <summary>{{ messages.page.tableSummary }}</summary>
            <div
              class="table-wrap"
              role="region"
              :aria-label="messages.page.tableSummary"
              tabindex="0"
            >
              <table>
                <thead>
                  <tr>
                    <th scope="col">{{ messages.page.tableMonths }}</th>
                    <th scope="col">{{ messages.page.tableCode }}</th>
                    <th scope="col" class="num">{{ messages.page.tableSeaTemperature }}</th>
                    <th scope="col" class="num">{{ messages.page.tableAnomaly }}</th>
                    <th scope="col">{{ messages.page.tableThreshold }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in recent" :key="r.start">
                    <th scope="row">{{ seasonMonths(r) }}</th>
                    <td>{{ seasonLabel(r) }}</td>
                    <td class="num">{{ formatTemperature(r.sst) }} °C</td>
                    <td class="num">{{ formatAnomaly(r.anomaly) }} °C</td>
                    <td>{{ phaseLabel[ensoPhase(r.anomaly)] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </section>

        <div class="deep-end">
          <OniStripes class="end-stripes" :dataset="oni" />
          <footer class="prose methods">
            <h2>{{ messages.page.methodsTitle }}</h2>
            <p>{{ messages.page.methodsBody }}</p>
            <p>{{ messages.page.methodsBodyTwo }}</p>
            <p class="sign">{{ messages.page.signoff }}</p>
          </footer>
        </div>
      </template>

      <section v-else class="hero" aria-labelledby="oni-empty">
        <h1 id="oni-empty">{{ messages.page.emptyTitle }}</h1>
        <p class="answer">
          {{ messages.page.emptyLead }}
          <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener"
            >{{ messages.page.oniSource }}<span class="sr-only">{{ messages.page.newTab }}</span></a
          >.
        </p>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Portada sobre el mar profundo. */
.cover {
  background: var(--deep);
  color: var(--on-deep);
  --link: var(--on-deep);
  --focus: var(--on-deep);
  --muted: var(--on-deep-muted);
}
.cover-stripes {
  --stripes-height: 40px;
  --stripes-label: var(--on-deep-muted);
}
.topbar {
  display: flex;
  align-items: center;
  gap: 24px;
  justify-content: center;
  padding: 18px 16px 0;
  background: var(--deep);
  color: var(--on-deep);
}
.topbar a {
  color: var(--on-deep);
}
.brand {
  font-family: var(--hand);
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: 0.02em;
}

/* Primer viewport: la pregunta, enorme; la respuesta corta debajo. */
.hero {
  min-height: calc(100svh - 150px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 40px;
  text-align: center;
}
h1 {
  margin: 0;
  max-width: 11ch;
  font-size: clamp(3.25rem, 13vw, 6rem);
  font-weight: 900;
  line-height: 0.92;
  letter-spacing: -0.03em;
  text-wrap: balance;
}
.answer {
  margin: 28px 0 0;
  max-width: 30rem;
  font-size: clamp(1.2rem, 2.6vw, 1.4rem);
  line-height: 1.45;
  text-wrap: pretty;
}
.answer strong {
  display: block;
  margin-bottom: 6px;
  font-weight: 700;
}
.value {
  font-weight: 800;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.value.warm {
  color: var(--warm-on-deep);
}
.value.cold {
  color: var(--on-deep);
  text-decoration: underline 3px var(--cold);
  text-underline-offset: 0.18em;
}
.byline {
  margin: 22px 0 0;
  font-size: 0.9375rem;
  font-style: italic;
  color: var(--muted);
}
.notice {
  --link: var(--notice-text);
  margin: 20px 0 0;
  max-width: 32rem;
  padding: 12px 16px;
  background: var(--notice-bg);
  color: var(--notice-text);
  font-size: 1rem;
  text-align: left;
}
.cue {
  margin: 48px 0 0;
  display: grid;
  justify-items: center;
  gap: 6px;
  font-family: var(--hand);
  font-size: 1.25rem;
  color: var(--muted);
}
.cue svg {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
@media (prefers-reduced-motion: no-preference) {
  .cue svg {
    animation: baja 2.4s ease-in-out 3;
  }
}
@keyframes baja {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(5px);
  }
}

/* El Perú, sobre arena: el desierto de la costa. */
.sand {
  margin-top: 48px;
  padding: clamp(48px, 8vw, 88px) 0 clamp(40px, 7vw, 72px);
  background: var(--sand);
}

/* Después de la historia: una columna de lectura, como un ensayo. */
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
.prose p {
  margin: 0 0 18px;
}
.key-point {
  font-size: 1.25rem;
  line-height: 1.45;
}
.links {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 6px;
  font-weight: 600;
}

.explore {
  padding: clamp(64px, 10vw, 112px) 0 0;
}
.oisst-panel {
  padding: clamp(64px, 10vw, 112px) 0 0;
}
.figure {
  max-width: 960px;
  margin: 8px auto 0;
  padding: 0 16px;
}
/* Misma altura que botones + gráfico, para que la página no salte al cargarlo. */
.chart-placeholder {
  height: 410px;
  display: grid;
  place-items: center;
  padding: 16px;
  text-align: center;
  color: var(--muted);
}
@media (max-width: 599px) {
  .topbar {
    flex-wrap: wrap;
    gap: 12px 16px;
  }
  .topbar .brand {
    flex-basis: 100%;
    text-align: center;
  }
  .chart-placeholder {
    height: 360px;
  }
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
.swatch.warm {
  background: var(--warm);
}
.swatch.neutral {
  background: var(--neutral-data);
  box-shadow: 0 0 0 4px var(--band);
}
.swatch.cold {
  background: var(--cold);
}

details {
  margin-top: 24px;
}
summary {
  cursor: pointer;
  font-weight: 650;
  width: fit-content;
}
summary::marker {
  color: var(--text);
}
.table-wrap {
  max-width: 100%;
  overflow-x: auto;
  margin-top: 12px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.95rem;
}
th,
td {
  text-align: left;
  padding: 8px 14px 8px 0;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
thead th {
  color: var(--muted);
  font-weight: 600;
  font-size: var(--fs-small);
}
.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* Pie sobre el mar profundo, abierto por las franjas: cierra lo que abrió la portada. */
.deep-end {
  margin-top: clamp(72px, 10vw, 120px);
  background: var(--deep);
  color: var(--on-deep);
  --link: var(--on-deep);
  --focus: var(--on-deep);
  --muted: var(--on-deep-muted);
  --text: var(--on-deep);
  --border: color-mix(in srgb, var(--on-deep) 22%, transparent);
}
.end-stripes {
  --stripes-height: 14px;
}
.end-stripes :deep(.year) {
  display: none;
}
.methods {
  padding-top: 48px;
  padding-bottom: 64px;
  font-size: 1rem;
  color: var(--muted);
}
.methods h2 {
  color: var(--text);
  font-size: 1.4rem;
}
.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px 24px;
  margin: 24px 0 0;
}
.meta dt,
.tech dt {
  font-size: var(--fs-small);
}
.meta dd,
.tech dd {
  margin: 0;
  color: var(--text);
}
.tech {
  display: grid;
  gap: 10px;
  margin: 12px 0 0;
}
@media (min-width: 560px) {
  .tech div {
    display: grid;
    grid-template-columns: 12rem 1fr;
    gap: 16px;
  }
}
.sign {
  margin-top: 48px !important;
  font-family: var(--hand);
  font-size: 1.25rem;
  text-align: center;
}
</style>
