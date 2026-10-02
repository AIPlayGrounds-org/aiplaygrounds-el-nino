<script setup lang="ts">
import oniJson from '~~/data/noaa-cpc-oni.json'
import type { Dataset, OniRecord } from '~/types/dataset'

const oni = oniJson as Dataset<OniRecord>
const records = oni.records
const last = records.at(-1)
const previous = records.at(-2)

const CPC_ONI_PAGE = 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/'
const ENFEN_COMUNICADOS = 'https://enfen.imarpe.gob.pe/downloads/comunicados/'
const SENAMHI_AVISOS = 'https://www.senamhi.gob.pe/?p=aviso-meteorologico'

// Si el último dato tiene 3 meses o más, NOAA (que publica cada mes) no se ha actualizado
// o nuestra descarga ha fallado. A los 2 meses es normal: el trimestre JJA se publica a inicios de septiembre.
const STALE_DATA_MONTHS = 3
const STALE_REVIEW_DAYS = 40

const phase = last ? ensoPhase(last.anomaly) : 'neutral'
const streak = phaseStreak(records)

/** La frase principal, en palabras: el número va dentro de ella, no solo. */
const headline = computed(() => {
  if (!last) return null
  const months = seasonMonths(last)
  if (phase === 'warm') return { lead: `Entre ${months}, el Pacífico central estuvo`, value: `${formatMagnitude(last.anomaly)} °C`, tail: 'más caliente de lo normal.' }
  if (phase === 'cold') return { lead: `Entre ${months}, el Pacífico central estuvo`, value: `${formatMagnitude(last.anomaly)} °C`, tail: 'más frío de lo normal.' }
  return { lead: `Entre ${months}, el Pacífico central estuvo cerca de lo normal:`, value: `${formatAnomaly(last.anomaly)} °C`, tail: 'de diferencia.' }
})

/** Estado frente al umbral oficial de NOAA. Los trimestres se solapan: n trimestres cubren n + 2 meses. */
const status = computed(() => {
  if (!last || phase === 'neutral') {
    return {
      title: 'Dentro del rango neutral',
      detail: 'Entre −0,5 y +0,5 °C: ni El Niño ni La Niña según el umbral de NOAA.',
    }
  }
  const name = phase === 'warm' ? 'El Niño' : 'La Niña'
  const side = phase === 'warm' ? 'sobre +0,5 °C' : 'bajo −0,5 °C'
  const seasons = streak === 1 ? '1 trimestre' : `${streak} trimestres seguidos`
  const detail =
    streak >= NOAA_EPISODE_SEASONS
      ? `Lleva ${seasons} ${side} (${streak + 2} meses): cumple la definición de episodio ${name} de NOAA.`
      : `Lleva ${seasons} ${side} (${streak + 2} meses). NOAA habla de episodio ${name} a partir de ${NOAA_EPISODE_SEASONS} trimestres seguidos.`
  return { title: `Por ${phase === 'warm' ? 'encima' : 'debajo'} del umbral de ${name}`, detail }
})

const change = computed(() => {
  if (!last || !previous) return null
  const delta = Math.round((last.anomaly - previous.anomaly) * 100) / 100
  const before = `el trimestre anterior (${seasonLabel(previous)})`
  if (delta === 0) return `Igual que ${before}.`
  return `${formatMagnitude(delta)} °C ${delta > 0 ? 'más' : 'menos'} que ${before}.`
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
    <header class="site-header">
      <span class="brand">WawaPacha</span>
      <span class="tagline">Monitoreando el Fenómeno El Niño en el Perú</span>
    </header>

    <main class="page">
      <h1>Índice Oceánico El Niño (ONI)</h1>
      <p class="lead">
        Cuánto más caliente o más frío de lo normal está el mar en el Pacífico central (región Niño 3.4), promediado cada
        tres meses. Es el índice internacional de referencia para El Niño, con datos desde 1950.
      </p>

      <section v-if="last && headline" class="card" aria-labelledby="oni-now">
        <h2 id="oni-now" class="sr-only">Último dato</h2>
        <p class="headline">
          {{ headline.lead }}
          <strong class="value" :class="phase">{{ headline.value }}</strong>
          {{ headline.tail }}
        </p>
        <p v-if="change" class="change">{{ change }}</p>
        <p class="status">
          <strong>{{ status.title }}.</strong> {{ status.detail }}
        </p>

        <section class="peru" aria-labelledby="oni-peru">
          <h2 id="oni-peru">¿Qué significa para el Perú?</h2>
          <p>
            Este índice mide el Pacífico central, a más de 4000 km de la costa peruana. Para el mar frente al Perú, el
            índice oficial es el ICEN de ENFEN (región Niño 1+2).
          </p>
          <p>
            <strong>Un valor alto aquí no es una alerta.</strong> En el Perú, los estados de alerta ante El Niño los declara
            ENFEN, y los avisos de lluvias, SENAMHI.
          </p>
          <ul class="links">
            <li><a :href="ENFEN_COMUNICADOS" target="_blank" rel="noopener">Comunicados oficiales de ENFEN<span class="sr-only"> (se abre en una pestaña nueva)</span></a></li>
            <li><a :href="SENAMHI_AVISOS" target="_blank" rel="noopener">Avisos meteorológicos de SENAMHI<span class="sr-only"> (se abre en una pestaña nueva)</span></a></li>
          </ul>
        </section>

        <p v-if="staleNotice" class="notice" role="status">
          {{ staleNotice }}
          <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">Ver la fuente<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
        </p>

        <figure class="figure" aria-labelledby="oni-history">
          <h2 id="oni-history">Evolución desde 1950</h2>
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
              <li><span class="swatch neutral" aria-hidden="true" />Rango neutral</li>
              <li><span class="swatch cold" aria-hidden="true" />Bajo −0,5 °C (umbral de La Niña)</li>
            </ul>
            Las líneas discontinuas marcan los umbrales. Usa la barra inferior para cambiar el periodo: empieza mostrando los
            últimos 30 años.
          </figcaption>
        </figure>

        <details>
          <summary>Ver los últimos 12 trimestres en una tabla</summary>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Trimestre</th>
                  <th scope="col">Meses</th>
                  <th scope="col" class="num">Temperatura</th>
                  <th scope="col" class="num">Anomalía</th>
                  <th scope="col">Respecto al umbral</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in recent" :key="r.start">
                  <th scope="row">{{ seasonLabel(r) }}</th>
                  <td>{{ seasonMonths(r) }}</td>
                  <td class="num">{{ formatTemperature(r.sst) }} °C</td>
                  <td class="num">{{ formatAnomaly(r.anomaly) }} °C</td>
                  <td>{{ phaseLabel[ensoPhase(r.anomaly)] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>

        <dl class="meta">
          <div>
            <dt>Fuente</dt>
            <dd>
              <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">{{ oni.source.institution }}<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
              · <a :href="oni.source.url" target="_blank" rel="noopener">datos originales<span class="sr-only"> (se abre en una pestaña nueva)</span></a>
            </dd>
          </div>
          <div>
            <dt>Tipo de dato</dt>
            <dd>Observado</dd>
          </div>
          <div>
            <dt>Datos hasta</dt>
            <dd>{{ monthName(last.end) }} · fuente revisada el {{ reviewed }}</dd>
          </div>
        </dl>
        <p class="note">
          NOAA usa hoy el RONI, una variante de este índice que descuenta el calentamiento general del océano, para su
          monitoreo oficial. El ONI se mantiene como la serie histórica de referencia, y sus últimos trimestres pueden
          revisarse.
        </p>

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
      </section>

      <section v-else class="card" aria-labelledby="oni-empty">
        <h2 id="oni-empty">No hay datos del ONI disponibles ahora</h2>
        <p>
          No pudimos cargar la serie. Puedes consultar el último dato directamente en la
          <a :href="CPC_ONI_PAGE" target="_blank" rel="noopener">página del ONI de NOAA<span class="sr-only"> (se abre en una pestaña nueva)</span></a>.
        </p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.site-header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}
.brand {
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}
.tagline {
  color: var(--muted);
  font-size: 0.9rem;
}
.page {
  max-width: 880px;
  margin: 0 auto;
  padding: 32px 16px 64px;
}
h1 {
  margin: 0 0 8px;
  font-size: clamp(1.6rem, 4vw, 2.1rem);
  letter-spacing: -0.02em;
  text-wrap: balance;
}
h2 {
  font-size: 1.05rem;
  margin: 0 0 8px;
}
.lead {
  color: var(--muted);
  margin: 0 0 24px;
  line-height: 1.55;
  max-width: 68ch;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: clamp(16px, 3vw, 24px);
}
.headline {
  margin: 0;
  font-size: clamp(1.15rem, 2.6vw, 1.4rem);
  line-height: 1.45;
  max-width: 40ch;
  text-wrap: pretty;
}
.value {
  font-size: 1.5em;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.value.warm { color: var(--warm); }
.value.cold { color: var(--cold); }
.change {
  margin: 8px 0 0;
  color: var(--muted);
}
.status {
  margin: 16px 0 0;
  line-height: 1.5;
  max-width: 68ch;
}
.peru {
  margin: 24px 0 0;
  padding: 16px;
  border-radius: 10px;
  background: var(--inset);
}
.peru p {
  margin: 0 0 8px;
  line-height: 1.55;
  max-width: 68ch;
}
.links {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 20px;
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}
.notice {
  margin: 16px 0 0;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--notice-bg);
  color: var(--notice-text);
  line-height: 1.5;
}
.figure {
  margin: 32px 0 0;
}
.chart-placeholder {
  height: 360px;
  display: grid;
  place-items: center;
  padding: 16px;
  text-align: center;
  color: var(--muted);
}
figcaption {
  font-size: 0.9rem;
  color: var(--muted);
  line-height: 1.5;
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
  width: 14px;
  height: 3px;
  margin-right: 8px;
  vertical-align: middle;
  border-radius: 2px;
}
.swatch.warm { background: var(--warm); }
.swatch.neutral { background: var(--neutral-data); }
.swatch.cold { background: var(--cold); }
details {
  margin-top: 16px;
}
summary {
  cursor: pointer;
  font-weight: 600;
  width: fit-content;
}
.table-wrap {
  overflow-x: auto;
  margin-top: 12px;
}
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.95rem;
}
th,
td {
  text-align: left;
  padding: 8px 12px 8px 0;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
thead th {
  color: var(--muted);
  font-weight: 600;
  font-size: 0.85rem;
}
.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 32px;
  margin: 24px 0 0;
}
.meta dt,
.tech dt {
  font-size: 0.85rem;
  color: var(--muted);
}
.meta dd,
.tech dd {
  margin: 0;
}
.note {
  margin: 12px 0 0;
  font-size: 0.9rem;
  color: var(--muted);
  line-height: 1.5;
  max-width: 68ch;
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
