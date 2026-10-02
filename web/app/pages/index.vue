<script setup lang="ts">
import oniJson from '#data/noaa-cpc-oni.json'
import type { Dataset, OniRecord } from '~/types/dataset'

const oni = oniJson as Omit<Dataset, 'records'> & { records: OniRecord[] }
const records = oni.records
const last = records.at(-1)
const DATA_TYPE_LABELS: Record<Dataset['data_type'], string> = {
  observed: 'Observado',
  estimated: 'Estimado',
  forecast: 'Pronóstico',
  official: 'Oficial',
}

const CPC_ONI_PAGE = 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/'
const ENFEN_COMUNICADOS = 'https://enfen.imarpe.gob.pe/downloads/comunicados/'
const SENAMHI_AVISOS = 'https://www.senamhi.gob.pe/?p=aviso-meteorologico'

// Si el último dato tiene 3 meses o más, NOAA (que publica cada mes) no se ha actualizado
// o nuestra descarga ha fallado. A los 2 meses es normal: el trimestre JJA se publica a inicios de septiembre.
const STALE_DATA_MONTHS = 3
const STALE_REVIEW_DAYS = 40

const phase = last ? ensoPhase(last.anomaly) : 'neutral'
const streak = phaseStreak(records)

/** Responde en llano a «¿hay El Niño (o La Niña)?» con la definición de episodio de NOAA. */
const status = computed(() => {
  if (!last || phase === 'neutral') {
    return {
      title: 'Ni El Niño ni La Niña',
      detail: 'El valor está entre −0,5 y +0,5 °C, el rango neutral según NOAA.',
    }
  }
  const name = phase === 'warm' ? 'El Niño' : 'La Niña'
  const side = phase === 'warm' ? 'sobre +0,5 °C' : 'bajo −0,5 °C'
  if (streak >= NOAA_EPISODE_SEASONS) {
    return {
      title: `Episodio ${name} según la definición de NOAA`,
      detail: `Lleva ${streak} trimestres seguidos ${side}; NOAA exige ${NOAA_EPISODE_SEASONS}.`,
    }
  }
  const umbral = phase === 'warm' ? 'Por encima del umbral de El Niño' : 'Por debajo del umbral de La Niña'
  return {
    title: `${umbral}, pero todavía no es un episodio`,
    detail: `Van ${streak} de los ${NOAA_EPISODE_SEASONS} trimestres seguidos ${side} que NOAA exige para hablar de un episodio ${name}.`,
  }
})

/**
 * La respuesta corta a la pregunta del titular. Habla de la regla de episodio de NOAA (5 trimestres seguidos
 * sobre el umbral), no de un estado oficial: NOAA monitorea hoy con el RONI. Pendiente de revisión de Contenido.
 */
const answer = computed(() => {
  if (!last) return null
  const value = `${formatAnomaly(last.anomaly)} °C`
  const rule = `${streak} de los ${NOAA_EPISODE_SEASONS} trimestres seguidos que la NOAA pide para hablar de un episodio`
  if (phase === 'warm') {
    return streak >= NOAA_EPISODE_SEASONS
      ? { short: 'Sí: ya cumple la regla de episodio de la NOAA.', lead: 'El Pacífico central está', value, tail: `sobre lo normal, y van ${streak} trimestres seguidos por encima del umbral.` }
      : { short: 'Todavía no es un episodio.', lead: 'El Pacífico central ya está', value, tail: `sobre lo normal, pero van ${rule}.` }
  }
  if (phase === 'cold') return { short: 'No.', lead: 'El Pacífico central está', value, tail: 'respecto a lo normal, del lado de La Niña.' }
  return { short: 'No.', lead: 'El Pacífico central está cerca de lo normal:', value, tail: 'de diferencia.' }
})

const reviewed = new Intl.DateTimeFormat('es', { dateStyle: 'long', timeZone: 'America/Lima' }).format(new Date(oni.ingestion_time))

// La antigüedad depende del día en que se abre la página, así que se calcula en el navegador.
const now = ref<Date | null>(null)
onMounted(() => (now.value = new Date()))
const staleNotice = computed(() => {
  if (!now.value || !last) return null
  const dataMonths = monthsSince(last.end, now.value)
  const reviewDays = Math.floor((now.value.getTime() - new Date(oni.ingestion_time).getTime()) / 86_400_000)
  if (dataMonths >= STALE_DATA_MONTHS) {
    return `El último dato es de ${monthName(last.end)}, hace ${dataMonths} meses. NOAA publica cada mes, así que puede haber datos más recientes en la fuente.`
  }
  if (reviewDays >= STALE_REVIEW_DAYS) {
    return `Revisamos la fuente por última vez hace ${reviewDays} días. Puede haber datos más recientes en la fuente.`
  }
  return null
})

const description = computed(() =>
  last
    ? `Gráfico de la anomalía del ONI desde ${monthName(records[0]!.start)} hasta ${monthName(last.end)}. ` +
      `Último valor: ${seasonLabel(last)}, ${formatAnomaly(last.anomaly)} °C. ${status.value.title}.`
    : '',
)

const recent = records.slice(-12).reverse()
const phaseLabel = { warm: 'Sobre +0,5 °C', neutral: 'Rango neutral', cold: 'Bajo −0,5 °C' } as const

useSeoMeta({
  title: 'Índice Oceánico El Niño (ONI) · WawaPacha',
  description:
    'Cuánto más caliente o más frío de lo normal está el Pacífico central, con el último dato de NOAA, su fecha y qué significa para el Perú.',
  ogTitle: 'Índice Oceánico El Niño (ONI) · WawaPacha',
  ogDescription: last ? `${seasonLabel(last)}: ${formatAnomaly(last.anomaly)} °C. ${status.value.title}.` : 'Índice Oceánico El Niño (ONI).',
})
</script>


<template>
  <div class="site">
    <main>
      <template v-if="last && answer">
        <div class="cover">
        <header class="topbar">
          <span class="brand">WawaPacha</span>
        </header>
        <section class="hero" aria-labelledby="oni-title">
          <h1 id="oni-title">¿Llegó El Niño?</h1>
          <p class="answer">
            <strong>{{ answer.short }}</strong>
            {{ answer.lead }}
            <span class="value" :class="phase">{{ answer.value }}</span>
            {{ answer.tail }}
          </p>
          <p class="byline">
            Por WawaPacha · Datos de la
            <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">NOAA<span class="sr-only"> (se abre en una pestaña nueva)</span></a>,
            observados hasta {{ monthName(last.end) }}
          </p>
          <p v-if="staleNotice" class="notice" role="status">
            {{ staleNotice }}
            <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">Ver la fuente<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
          </p>
          <p class="cue" aria-hidden="true">
            Baja para entenderlo
            <svg width="18" height="28" viewBox="0 0 18 28"><path d="M9 2 V24 M2 17 L9 24 L16 17" /></svg>
          </p>
        </section>
        <OniStripes class="cover-stripes" :records="records" />
        </div>

        <OniStory :records="records" />

        <div class="sand">
        <article class="prose">
          <h2 id="oni-peru">¿Y qué significa para el Perú?</h2>
          <p>
            Todo lo que viste se mide en el Pacífico central, a más de 4000 km de nuestra costa. Para el mar frente al
            Perú, el índice oficial es otro: el <strong>ICEN</strong> de ENFEN, que se mide en la región Niño 1+2, junto a
            la costa.
          </p>
          <p class="key-point">
            <strong>Un valor alto del ONI no es una alerta.</strong> En el Perú, los estados de alerta ante El Niño los
            declara ENFEN, y los avisos de lluvias, SENAMHI.
          </p>
          <ul class="links">
            <li><a :href="ENFEN_COMUNICADOS" target="_blank" rel="noopener">Comunicados oficiales de ENFEN<span class="sr-only"> (se abre en una pestaña nueva)</span></a></li>
            <li><a :href="SENAMHI_AVISOS" target="_blank" rel="noopener">Avisos meteorológicos de SENAMHI<span class="sr-only"> (se abre en una pestaña nueva)</span></a></li>
          </ul>
        </article>
        </div>

        <section class="explore" aria-labelledby="oni-history">
          <div class="prose">
            <h2 id="oni-history">Explora tú mismo</h2>
            <p>Elige el periodo y pasa el cursor (o el dedo) por la línea para ver cada trimestre.</p>
          </div>
          <figure class="figure">
            <NuxtErrorBoundary>
              <ClientOnly>
                <OniChart :records="records" :description="description" />
                <template #fallback>
                  <div class="chart-placeholder">Cargando el gráfico…</div>
                </template>
              </ClientOnly>
              <template #error>
                <div class="chart-placeholder">
                  No se pudo dibujar el gráfico. Los últimos trimestres están en la tabla de abajo.
                </div>
              </template>
            </NuxtErrorBoundary>
            <figcaption>
              <ul class="key" aria-label="Colores de la línea">
                <li><span class="swatch warm" aria-hidden="true" />Sobre +0,5 °C (umbral de El Niño)</li>
                <li><span class="swatch neutral" aria-hidden="true" />Rango neutral, sombreado en verde agua</li>
                <li><span class="swatch cold" aria-hidden="true" />Bajo −0,5 °C (umbral de La Niña)</li>
              </ul>
              Las líneas discontinuas marcan los umbrales oficiales de la NOAA. El punto marca el último dato.
            </figcaption>
          </figure>

          <details class="prose">
            <summary>Ver los últimos 12 trimestres en una tabla</summary>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Meses</th>
                    <th scope="col">Código</th>
                    <th scope="col" class="num">Temperatura del mar</th>
                    <th scope="col" class="num">Anomalía</th>
                    <th scope="col">Respecto al umbral</th>
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
        <OniStripes class="end-stripes" :records="records" />
        <footer class="prose methods">
          <h2>Cómo lo hicimos</h2>
          <p>
            Usamos el Índice Oceánico El Niño (ONI) que publica el Climate Prediction Center de la NOAA, sin modificarlo.
            Los umbrales (±0,5 °C) y la regla de cinco trimestres seguidos son los de la NOAA; no usamos umbrales propios.
          </p>
          <p>
            La NOAA usa hoy el RONI, una variante de este índice que descuenta el calentamiento general del océano, para su
            monitoreo oficial. El ONI se mantiene como la serie histórica de referencia, y sus últimos trimestres pueden
            revisarse.
          </p>
          <dl class="meta">
            <div>
              <dt>Fuente</dt>
              <dd>
                <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">{{ oni.source.institution }}<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
                · <a :href="oni.source.url" target="_blank" rel="noopener">datos originales<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
              </dd>
            </div>
            <div><dt>Tipo de dato</dt><dd>{{ DATA_TYPE_LABELS[oni.data_type] }}</dd></div>
            <div><dt>Datos hasta</dt><dd>{{ monthName(last.end) }}</dd></div>
            <div><dt>Fuente revisada</dt><dd>{{ reviewed }}</dd></div>
          </dl>
          <details>
            <summary>Ver detalle técnico</summary>
            <dl class="tech">
              <div><dt>Variable</dt><dd>{{ oni.variable }}</dd></div>
              <div><dt>Unidad</dt><dd>{{ oni.unit }}</dd></div>
              <div><dt>Cobertura</dt><dd>{{ oni.spatial_resolution }}</dd></div>
              <div><dt>Resolución temporal</dt><dd>{{ oni.temporal_resolution }}</dd></div>
              <div><dt>Periodo base</dt><dd>{{ oni.reference_period }}</dd></div>
              <div><dt>Serie</dt><dd>{{ records.length }} trimestres, de {{ monthName(records[0]!.start) }} a {{ monthName(last.end) }}</dd></div>
              <div><dt>Versión del procesamiento</dt><dd>{{ oni.processing_version }}</dd></div>
            </dl>
          </details>
          <p class="sign">WawaPacha · Monitoreando el Fenómeno El Niño en el Perú</p>
        </footer>
        </div>
      </template>

      <section v-else class="hero" aria-labelledby="oni-empty">
        <h1 id="oni-empty">No hay datos del ONI disponibles ahora</h1>
        <p class="answer">
          No pudimos cargar la serie. Puedes consultar el último dato directamente en la
          <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">página del ONI de la NOAA<span class="sr-only"> (se abre en una pestaña nueva)</span></a>.
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
  justify-content: center;
  padding: 18px 16px 0;
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
.value.warm { color: var(--warm-on-deep); }
.value.cold { color: var(--on-deep); text-decoration: underline 3px var(--cold); text-underline-offset: 0.18em; }
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
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(5px); }
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
.swatch.warm { background: var(--warm); }
.swatch.neutral { background: var(--neutral-data); box-shadow: 0 0 0 4px var(--band); }
.swatch.cold { background: var(--cold); }

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
