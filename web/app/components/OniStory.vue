<script setup lang="ts">
// Historia con scroll: los pasos de texto avanzan y el gráfico fijo cambia de escena.
// Todo número del texto sale de la serie, así que la historia se actualiza sola cada mes.
import { messages } from '~/messages'
import type { DatasetFor } from '~/types/datasets'

const props = defineProps<{ dataset: DatasetFor<'noaa-cpc-oni'> }>()
const records = props.dataset.records
type OniRecord = DatasetFor<'noaa-cpc-oni'>['records'][number]
const last = records.at(-1)!
const phase = ensoPhase(last.anomaly)
const streak = phaseStreak(records)

const fmt = formatAnomaly
const t = (r: OniRecord) => centerDate(r).getTime()

// Episodios con la regla de NOAA: 5 trimestres seguidos al otro lado del umbral.
const runs = (test: (a: number) => boolean) => {
  const out: OniRecord[][] = []
  let run: OniRecord[] = []
  for (const r of records) {
    if (test(r.anomaly)) run.push(r)
    else {
      if (run.length >= NOAA_EPISODE_SEASONS) out.push(run)
      run = []
    }
  }
  if (run.length >= NOAA_EPISODE_SEASONS) out.push(run)
  return out
}
const peakOf = (run: OniRecord[]) => run.reduce((a, b) => (Math.abs(b.anomaly) > Math.abs(a.anomaly) ? b : a))
// Se nombra como se recuerda, por el año de su pico: «1997-98», «2015-16».
const episodeName = (run: OniRecord[]) => {
  const peak = peakOf(run)
  const year = centerDate(peak).getUTCFullYear()
  const first = centerDate(peak).getUTCMonth() >= 6 ? year : year - 1
  return `${first}-${String(first + 1).slice(2)}`
}
const warmEpisodes = runs((a) => a >= ENSO_THRESHOLD)
  .filter((run) => run.at(-1) !== last)
  .map((run) => ({ name: episodeName(run), peak: peakOf(run) }))
const biggest = [...warmEpisodes].sort((a, b) => b.peak.anomaly - a.peak.anomaly).slice(0, 3)
const higherThanToday = warmEpisodes.filter((e) => e.peak.anomaly > last.anomaly)

const share = (records.filter((r) => r.anomaly < last.anomaly).length / records.length) * 100
const shareText = new Intl.NumberFormat('es', { maximumFractionDigits: 1 }).format(share)
const reached = records.filter((r) => r.anomaly >= last.anomaly)

// Último año: el punto más bajo (o más alto) antes del valor actual.
const year = records.slice(-13)
const turn = phase === 'cold' ? year.reduce((a, b) => (b.anomaly > a.anomaly ? b : a)) : year.reduce((a, b) => (b.anomaly < a.anomaly ? b : a))
const turnSteps = records.length - 1 - records.indexOf(turn)
const rise = Math.round((last.anomaly - turn.anomaly) * 100) / 100
// Punto a mitad del tramo, para colgar la anotación.
const middle = records[records.length - 1 - Math.ceil(turnSteps / 2)]!

const phaseWord = {
  warm: messages.story.warmPhase,
  cold: messages.story.coldPhase,
  neutral: messages.story.neutralPhase,
}[phase]

// Del borde este de Niño 3.4 (120° O) a la costa peruana (unos 81° O) hay unos 39° sobre el ecuador,
// es decir, unos 4300 km; el texto lo redondea hacia abajo.
const DISTANCE_KM = '4000'

type Scene = 'map' | 'chart'
type Step = { scene: Scene; html: string; state: string }
const steps: Step[] = [
  {
    scene: 'map',
    state: 'box',
    html: messages.story.stepMap,
  },
  {
    scene: 'map',
    state: 'distance',
    html: messages.story.stepDistance(DISTANCE_KM),
  },
  {
    scene: 'map',
    state: 'measure',
    html: messages.story.stepMeasure,
  },
  {
    scene: 'chart',
    state: 'dot',
    html: messages.story.stepIndex(seasonMonths(last), fmt(last.anomaly), phase),
  },
  {
    scene: 'chart',
    state: 'band',
    html: messages.story.stepThreshold,
  },
  {
    scene: 'chart',
    state: 'year',
    html: Math.abs(rise) >= 0.5 ? messages.story.stepChange(seasonMonths(turn), fmt(turn.anomaly), turnSteps, rise > 0 ? messages.story.rise : messages.story.fall, formatMagnitude(rise)) : messages.story.stepSmallChange(fmt(turn.anomaly), fmt(last.anomaly)),
  },
  {
    scene: 'chart',
    state: 'streak',
    html:
      phase === 'neutral'
        ? messages.story.stepNeutralStreak(NOAA_EPISODE_SEASONS)
        : messages.story.stepStreak(
            phaseWord,
            phase === 'warm' ? messages.story.warmName : messages.story.coldName,
            NOAA_EPISODE_SEASONS,
            phase === 'warm' ? messages.story.warmSide : messages.story.coldSide,
            streak,
            streak >= NOAA_EPISODE_SEASONS ? messages.story.episodeComplete : messages.story.episodeIncomplete,
          ),
  },
  {
    scene: 'chart',
    state: 'history',
    html: messages.story.stepHistory(records.length, monthName(records[0]!.start)),
  },
  {
    scene: 'chart',
    state: 'peaks',
    html: messages.story.stepPeaks(biggest.map((e) => e.name).join('</strong>, <strong>'), fmt(Math.floor(Math.min(...biggest.map((e) => e.peak.anomaly)) * 2) / 2)),
  },
  {
    scene: 'chart',
    state: 'today',
    html:
      phase === 'warm'
        ? messages.story.stepTodayWarm(fmt(last.anomaly), shareText, higherThanToday.length ? messages.story.stepTodayWarmHigher(higherThanToday.length) : messages.story.stepTodayWarmNone)
        : messages.story.stepTodayOther(fmt(last.anomaly), phase === 'cold' ? messages.story.warmTodaySide : messages.story.neutralTodaySide),
  },
]

// Paso activo: el último cuyo borde superior ya pasó la línea de lectura (la mitad de la pantalla;
// en móvil, más abajo, porque el texto pasa bajo el gráfico). Se calcula en cada scroll, así que
// también funciona al saltar directo a un punto de la página.
const active = ref(0)
const stepEls = ref<HTMLElement[]>([])
let pending = 0
const updateActive = () => {
  pending = 0
  const line = window.innerHeight * (window.matchMedia('(max-width: 959px)').matches ? 0.78 : 0.55)
  let index = 0
  stepEls.value.forEach((el, i) => {
    if (el.getBoundingClientRect().top < line) index = i
  })
  active.value = index
}
const onScroll = () => {
  if (!pending) pending = requestAnimationFrame(updateActive)
}
onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  updateActive()
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  cancelAnimationFrame(pending)
})
const step = computed(() => steps[active.value]!)

// Tamaño real del gráfico, para dibujar en píxeles y que el texto no se deforme.
const box = ref<HTMLElement | null>(null)
const size = reactive({ w: 720, h: 560 })
let resize: ResizeObserver | undefined
onMounted(() => {
  resize = new ResizeObserver(([e]) => {
    size.w = e!.contentRect.width
    size.h = e!.contentRect.height
  })
  if (box.value) resize.observe(box.value)
})
onBeforeUnmount(() => resize?.disconnect())
const narrow = computed(() => size.w < 560)

// ---------- Escena del mapa ----------
const COAST: [number, number][] = [
  [-92, 16],
  [-86, 12],
  [-84.6, 8],
  [-83.5, 8.4],
  [-82.9, 8.1],
  [-80.4, 7.3],
  [-79.6, 8.6],
  [-78.4, 8.2],
  [-77.9, 7.2],
  [-77.4, 6],
  [-77.5, 4],
  [-78.5, 2.4],
  [-78.9, 1.5],
  [-80.1, 0.8],
  [-80.5, -0.5],
  [-80.9, -1.6],
  [-80.9, -2.2],
  [-80, -2.6],
  [-79.9, -3.3],
  [-80.3, -3.5],
  [-81, -4],
  [-81.3, -4.6],
  [-81.1, -5.1],
  [-81.2, -5.9],
  [-79.9, -6.8],
  [-79, -8.1],
  [-78.6, -9.1],
  [-77.6, -10.8],
  [-77.15, -12.05],
  [-76.3, -13.7],
  [-75.2, -15.4],
  [-73.8, -16.3],
  [-72.1, -17],
  [-71.3, -17.7],
  [-70.3, -18.4],
  [-70.2, -20],
  [-70.6, -26],
  [-71.5, -30],
  [-71.7, -40],
]
const LAND = [...COAST, [-40, -40], [-40, 16]] as [number, number][]
const map = computed(() => {
  // En pantallas estrechas el encuadre se acerca al Perú; Niño 3.4 sale por el borde oeste.
  const e = narrow.value ? { west: -150, east: -66, north: 14, south: -24 } : { west: -176, east: -64, north: 16, south: -26 }
  const pad = 24
  const top = narrow.value ? 64 : 24
  const bottom = narrow.value ? size.h * 0.42 : pad
  const scale = Math.min((size.w - pad * 2) / (e.east - e.west), (size.h - top - bottom) / (e.north - e.south))
  const ox = (size.w - (e.east - e.west) * scale) / 2
  const oy = top + (size.h - top - bottom - (e.north - e.south) * scale) / 2
  const x = (lon: number) => ox + (lon - e.west) * scale
  const y = (lat: number) => oy + (e.north - lat) * scale
  return {
    land: LAND.map(([lon, lat]) => `${x(lon).toFixed(1)},${y(lat).toFixed(1)}`).join(' '),
    frame: { x: ox, y: oy, width: (e.east - e.west) * scale, height: (e.north - e.south) * scale },
    nino34: { x: x(-170), y: y(5), width: x(-120) - x(-170), height: y(-5) - y(5) },
    equator: y(0),
    arrow: { x1: x(-120), y1: y(-5), x2: x(-77.2), y2: y(-12.2) },
    distance: { x: (x(-120) + x(-77.2)) / 2, y: (y(-5) + y(-12.2)) / 2 + 26 },
    peru: { x: x(-75), y: y(-9) },
    label: { x: Math.max(x(-145), ox + 8), y: y(5) - 12 },
    equatorLabel: { x: x(-117), y: y(0) - 8 },
    thermo: { x: Math.max(x(-170), ox + 8), y: y(-5) + 30 },
  }
})

// ---------- Escena del gráfico ----------
type Domain = { x0: number; x1: number; y0: number; y1: number }
const MONTH = 30.44 * 86_400_000
const recent = records.at(-13)!
const domains: Record<string, Domain> = {
  dot: { x0: t(recent) - MONTH, x1: t(last) + 2 * MONTH, y0: -1.5, y1: 2.5 },
  history: { x0: t(records[0]!) - 12 * MONTH, x1: t(last) + 12 * MONTH, y0: -2.2, y1: 3 },
}
const target = (state: string): Domain => (['history', 'peaks', 'today'].includes(state) ? domains.history! : domains.dot!)

const dom = reactive<Domain>({ ...domains.dot! })
let frame = 0
const reduced = import.meta.client && window.matchMedia('(prefers-reduced-motion: reduce)').matches
watch(
  () => step.value.state,
  (state) => {
    const to = target(state)
    const from = { ...dom }
    cancelAnimationFrame(frame)
    if (reduced) return Object.assign(dom, to)
    const start = performance.now()
    const tick = (now: number) => {
      const k = Math.min(1, (now - start) / 1100)
      const e = 1 - Math.pow(1 - k, 4)
      dom.x0 = from.x0 + (to.x0 - from.x0) * e
      dom.x1 = from.x1 + (to.x1 - from.x1) * e
      dom.y0 = from.y0 + (to.y0 - from.y0) * e
      dom.y1 = from.y1 + (to.y1 - from.y1) * e
      if (k < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
  },
)

const plot = computed(() => {
  const m = narrow.value ? { top: 72, right: 82, bottom: Math.round(size.h * 0.42) + 28, left: 40 } : { top: 56, right: 104, bottom: 44, left: 52 }
  const w = size.w - m.left - m.right
  const h = size.h - m.top - m.bottom
  const x = (ms: number) => m.left + ((ms - dom.x0) / (dom.x1 - dom.x0)) * w
  const y = (v: number) => m.top + ((dom.y1 - v) / (dom.y1 - dom.y0)) * h
  const path = records.map((r, i) => `${i ? 'L' : 'M'}${x(t(r)).toFixed(1)},${y(r.anomaly).toFixed(1)}`).join('')
  const span = (dom.x1 - dom.x0) / (12 * MONTH)
  const every = span > 40 ? 10 : span > 12 ? 5 : span > 3 ? 1 : 0
  const years: { x: number; label: string }[] = []
  const fromYear = new Date(dom.x0).getUTCFullYear()
  const toYear = new Date(dom.x1).getUTCFullYear()
  for (let yr = fromYear; yr <= toYear; yr++) {
    const ms = Date.UTC(yr, 0, 1)
    if (ms < dom.x0 || ms > dom.x1) continue
    if (every && yr % every !== 0) continue
    years.push({ x: x(ms), label: String(yr) })
    if (!every) {
      const mid = Date.UTC(yr, 6, 1)
      if (mid > dom.x0 && mid < dom.x1) years.push({ x: x(mid), label: 'jul' })
    }
  }
  if (!every) {
    const mid = Date.UTC(fromYear, 6, 1)
    if (mid > dom.x0 && !years.some((yr) => yr.label === 'jul' && Math.abs(yr.x - x(mid)) < 1)) years.unshift({ x: x(mid), label: 'jul' })
  }
  const ys = [-2, -1, 0, 1, 2, 3].filter((v) => v >= dom.y0 && v <= dom.y1)
  return { m, w, h, x, y, path, years, ys }
})
const pt = (r: OniRecord) => ({ cx: plot.value.x(t(r)), cy: plot.value.y(r.anomaly) })
const streakRecords = computed(() => (phase === 'neutral' ? [] : records.slice(-streak)))
const s = computed(() => step.value.state)
const show = (...states: string[]) => states.includes(s.value)
const lineOn = computed(() => !show('dot', 'band'))
</script>

<template>
  <section class="story" :aria-label="messages.page.storyAria">
    <div class="graphic" aria-hidden="true">
      <div ref="box" class="graphic-box">
        <svg :viewBox="`0 0 ${size.w} ${size.h}`">
          <!-- Escena 1: dónde se mide. -->
          <g class="scene" :class="{ on: step.scene === 'map' }">
            <rect class="sea" v-bind="map.frame" />
            <line class="equator" :x1="map.frame.x" :x2="map.frame.x + map.frame.width" :y1="map.equator" :y2="map.equator" />
            <text class="hand faint" :x="map.equatorLabel.x" :y="map.equatorLabel.y">
              {{ messages.story.mapEquator }}
            </text>
            <clipPath id="story-map-clip"><rect v-bind="map.frame" /></clipPath>
            <polygon class="land" :points="map.land" clip-path="url(#story-map-clip)" />
            <text class="country" :x="map.peru.x" :y="map.peru.y">{{ messages.story.peru }}</text>
            <rect class="nino-box" v-bind="map.nino34" clip-path="url(#story-map-clip)" />
            <text class="hand warm" :x="map.label.x" :y="map.label.y">
              {{ messages.story.ninoRegion }}
            </text>
            <g class="fade" :class="{ on: show('distance') }">
              <line class="arrow" v-bind="map.arrow" marker-end="url(#story-arrow)" marker-start="url(#story-arrow)" />
              <text class="hand" :x="map.distance.x" :y="map.distance.y" text-anchor="middle">
                {{ messages.story.distance(DISTANCE_KM) }}
              </text>
            </g>
            <g class="fade" :class="{ on: show('measure') }">
              <text class="hand warm big" :x="map.thermo.x" :y="map.thermo.y">
                <tspan :x="map.thermo.x">{{ messages.story.anomalyEquation[0] }}</tspan>
                <tspan :x="map.thermo.x" dy="1.2em">{{ messages.story.anomalyEquation[1] }}</tspan>
              </text>
            </g>
            <defs>
              <marker id="story-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M0,0 L10,5 L0,10 z" class="arrow-head" />
              </marker>
            </defs>
          </g>

          <!-- Escena 2: el índice en el tiempo. -->
          <g class="scene" :class="{ on: step.scene === 'chart' }">
            <clipPath id="story-plot">
              <rect :x="plot.m.left" :y="plot.m.top - 30" :width="plot.w + 20" :height="plot.h + 30" />
            </clipPath>
            <clipPath id="story-warm">
              <rect :x="0" :y="0" :width="size.w" :height="Math.max(0, plot.y(ENSO_THRESHOLD))" />
            </clipPath>
            <clipPath id="story-cold">
              <rect :x="0" :y="plot.y(-ENSO_THRESHOLD)" :width="size.w" :height="size.h" />
            </clipPath>

            <g class="grid">
              <g v-for="v in plot.ys" :key="v">
                <line :x1="plot.m.left" :x2="plot.m.left + plot.w" :y1="plot.y(v)" :y2="plot.y(v)" :class="{ zero: v === 0 }" />
                <text :x="plot.m.left - 10" :y="plot.y(v) + 4" text-anchor="end">{{ v > 0 ? '+' : v < 0 ? '−' : '' }}{{ Math.abs(v) }}</text>
              </g>
              <text :x="plot.m.left - 10" :y="plot.m.top - 18" class="unit">°C</text>
              <g v-for="yr in plot.years" :key="`${yr.label}-${Math.round(yr.x)}`">
                <text :x="yr.x" :y="plot.m.top + plot.h + 26" text-anchor="middle">
                  {{ yr.label }}
                </text>
              </g>
            </g>

            <g class="fade" :class="{ on: !show('dot') }">
              <rect class="band" :x="plot.m.left" :width="plot.w" :y="plot.y(ENSO_THRESHOLD)" :height="plot.y(-ENSO_THRESHOLD) - plot.y(ENSO_THRESHOLD)" />
              <line class="threshold" :x1="plot.m.left" :x2="plot.m.left + plot.w" :y1="plot.y(ENSO_THRESHOLD)" :y2="plot.y(ENSO_THRESHOLD)" />
              <line class="threshold" :x1="plot.m.left" :x2="plot.m.left + plot.w" :y1="plot.y(-ENSO_THRESHOLD)" :y2="plot.y(-ENSO_THRESHOLD)" />
              <g class="fade" :class="{ on: show('band', 'year', 'streak') }">
                <text class="hand warm" :x="plot.m.left + 8" :y="plot.y(ENSO_THRESHOLD) - 8">
                  {{ messages.story.sceneThresholdWarm }}
                </text>
                <text class="hand faint" :x="plot.m.left + 8" :y="plot.y(0) + 6">
                  {{ messages.story.sceneNeutral }}
                </text>
                <text class="hand cold" :x="plot.m.left + 8" :y="plot.y(-ENSO_THRESHOLD) + 22">
                  {{ messages.story.sceneThresholdCold }}
                </text>
              </g>
            </g>

            <g class="fade" :class="{ on: lineOn }" clip-path="url(#story-plot)">
              <path class="line" :d="plot.path" />
              <path class="line warm" :d="plot.path" clip-path="url(#story-warm)" />
              <path class="line cold" :d="plot.path" clip-path="url(#story-cold)" />
            </g>

            <!-- La subida (o bajada) del último año, anotada a mano junto al tramo. -->
            <g class="fade" :class="{ on: show('year') && Math.abs(rise) >= 0.5 }">
              <text class="hand rise" :class="phase" :x="pt(middle).cx + 14" :y="pt(middle).cy + 4">
                <tspan :x="pt(middle).cx + 14">{{ rise > 0 ? '+' : '−' }}{{ formatMagnitude(rise) }} °C</tspan>
                <tspan :x="pt(middle).cx + 14" dy="1.15em">
                  {{ messages.story.risePeriod(turnSteps) }}
                </tspan>
              </text>
            </g>

            <!-- La racha: los trimestres seguidos al otro lado del umbral. -->
            <g class="fade" :class="{ on: show('streak') }">
              <circle v-for="r in streakRecords" :key="r.start" class="streak-dot" :class="phase" v-bind="pt(r)" r="7" />
            </g>

            <g class="fade" :class="{ on: show('peaks') }">
              <g v-for="e in biggest" :key="e.name">
                <line class="leader" :x1="pt(e.peak).cx" :x2="pt(e.peak).cx" :y1="pt(e.peak).cy - 6" :y2="pt(e.peak).cy - 26" />
                <text class="hand" :x="pt(e.peak).cx" :y="pt(e.peak).cy - 32" text-anchor="middle">
                  {{ e.name }}
                </text>
              </g>
            </g>

            <g class="fade" :class="{ on: show('today') && phase === 'warm' }">
              <line class="today-line" :x1="plot.m.left" :x2="plot.m.left + plot.w" :y1="plot.y(last.anomaly)" :y2="plot.y(last.anomaly)" />
              <circle v-for="r in reached" :key="r.start" class="reached" v-bind="pt(r)" r="3.5" />
              <!-- En móvil la serie está muy apretada: el rótulo sube sobre el gráfico con una guía hasta la línea. -->
              <template v-if="narrow">
                <line class="today-line" :x1="plot.m.left + 10" :x2="plot.m.left + 10" :y1="plot.m.top - 14" :y2="plot.y(last.anomaly)" />
                <text class="hand warm" :x="plot.m.left + 16" :y="plot.m.top - 16">
                  {{ messages.story.todayHigh }}
                </text>
              </template>
              <text v-else class="hand warm" :x="plot.m.left + 8" :y="plot.y(last.anomaly) - 8">
                {{ messages.story.todayHigh }}
              </text>
            </g>

            <!-- El último dato, siempre visible en esta escena. -->
            <circle class="last-dot" :class="phase" v-bind="pt(last)" :r="show('dot', 'band') ? 9 : 6" />
            <text class="last-label" :class="phase" :x="pt(last).cx + (narrow ? 10 : 14)" :y="pt(last).cy + 7">{{ fmt(last.anomaly) }} °C</text>
          </g>
        </svg>

        <!-- Contador de la racha: 5 casillas, llenas las que ya van. -->
        <div v-if="phase !== 'neutral'" class="counter" :class="[phase, { on: show('streak') }]">
          <span v-for="i in NOAA_EPISODE_SEASONS" :key="i" class="slot" :class="{ full: i <= streak }" />
          <span class="counter-text">{{ messages.story.streak(Math.min(streak, NOAA_EPISODE_SEASONS), NOAA_EPISODE_SEASONS) }}</span>
        </div>
      </div>
    </div>

    <div class="steps">
      <div v-for="(st, i) in steps" :key="i" ref="stepEls" class="step" :class="{ active: i === active }" :data-step="i">
        <!-- Textos propios, armados con datos de la serie; ningún dato viene del usuario. -->
        <p v-html="st.html" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.story {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}
.graphic {
  position: sticky;
  top: 0;
  height: 100vh;
  height: 100svh;
  grid-area: 1 / 1;
  z-index: 0;
}
.graphic-box {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}
.steps {
  grid-area: 1 / 1;
  position: relative;
  z-index: 1;
  padding: 70vh 16px 40vh;
  pointer-events: none;
}
.step {
  max-width: 34rem;
  margin: 0 auto 75vh;
  pointer-events: auto;
}
.step:last-child {
  margin-bottom: 0;
}
/* En móvil el texto pasa por encima del gráfico, en tarjetas legibles. */
.step p {
  margin: 0;
  padding: 18px 20px;
  background: color-mix(in srgb, var(--paper) 94%, transparent);
  border: 1px solid var(--border);
  font-size: 1.125rem;
  line-height: 1.55;
  transition: opacity 0.3s ease-out;
}
.step:not(.active) p {
  opacity: 0.55;
}
.step :deep(strong) {
  font-weight: 650;
}
.step :deep(.v) {
  white-space: nowrap;
}
.step :deep(.v.warm) {
  color: var(--warm-text);
}
.step :deep(.v.cold) {
  color: var(--cold-text);
}

@media (min-width: 960px) {
  .story {
    grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
    column-gap: 48px;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
  }
  .graphic {
    grid-area: 1 / 2;
  }
  .steps {
    grid-area: 1 / 1;
    padding: 40vh 0 50vh;
  }
  .step {
    margin-bottom: 70vh;
  }
  .step p {
    padding: 0;
    background: none;
    border: 0;
    font-size: 1.1875rem;
  }
  .step:not(.active) p {
    opacity: 0.3;
  }
}

/* Escenas: se funden una con otra. */
.scene,
.fade {
  opacity: 0;
  transition: opacity 0.6s ease-out;
}
.scene.on,
.fade.on {
  opacity: 1;
}
.sea {
  fill: var(--sea);
}
.land {
  fill: var(--land);
  stroke: var(--sea-edge);
  stroke-width: 1.5;
}
.equator {
  stroke: var(--sea-edge);
  stroke-dasharray: 3 5;
}
.country {
  fill: var(--muted);
  font-size: 13px;
  font-weight: 650;
  letter-spacing: 0.12em;
}
.nino-box {
  fill: var(--warm-tint);
  stroke: var(--warm);
  stroke-width: 2.5;
}
.arrow {
  stroke: var(--text);
  stroke-width: 1.5;
  stroke-dasharray: 5 4;
}
.arrow-head {
  fill: var(--text);
}
.hand {
  font-family: var(--hand);
  font-size: 19px;
  fill: var(--text);
}
@media (max-width: 559px) {
  .hand.rise {
    font-size: 16px;
  }
}
.hand.big {
  font-size: 21px;
}
.hand.warm {
  fill: var(--warm-text);
}
.hand.cold {
  fill: var(--cold-text);
}
.hand.faint {
  fill: var(--muted);
}

.grid line {
  stroke: var(--chart-grid);
}
.grid line.zero {
  stroke: var(--border);
}
.grid text {
  fill: var(--muted);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}
.band {
  fill: var(--band);
}
.threshold {
  stroke: var(--faint);
  stroke-dasharray: 4 4;
}
.line {
  fill: none;
  stroke: var(--neutral-data);
  stroke-width: 1.75;
  stroke-linejoin: round;
}
.line.warm {
  stroke: var(--warm);
  stroke-width: 2.25;
}
.line.cold {
  stroke: var(--cold);
  stroke-width: 2.25;
}
.streak-dot {
  fill: none;
  stroke-width: 2.5;
}
.streak-dot.warm {
  stroke: var(--warm);
}
.streak-dot.cold {
  stroke: var(--cold);
}
.leader {
  stroke: var(--text);
}
.today-line {
  stroke: var(--warm);
  stroke-dasharray: 2 4;
}
.reached {
  fill: var(--warm);
}
.last-dot {
  fill: var(--neutral-data);
  stroke: var(--paper);
  stroke-width: 2;
  transition: r 0.4s ease-out;
}
.last-dot.warm {
  fill: var(--warm);
}
.last-dot.cold {
  fill: var(--cold);
}
.last-label {
  font-size: clamp(17px, 4.5vw, 24px);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  fill: var(--text);
  paint-order: stroke;
  stroke: var(--paper);
  stroke-width: 5px;
}
.last-label.warm {
  fill: var(--warm-text);
}
.last-label.cold {
  fill: var(--cold-text);
}

.counter {
  position: absolute;
  right: 104px;
  top: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.5s ease-out;
}
.counter.on {
  opacity: 1;
}
.slot {
  width: 22px;
  height: 22px;
  border: 2px solid var(--faint);
}
.counter.warm .slot.full {
  background: var(--warm);
  border-color: var(--warm);
}
.counter.cold .slot.full {
  background: var(--cold);
  border-color: var(--cold);
}
.counter-text {
  margin-left: 8px;
  font-family: var(--hand);
  font-size: 1.375rem;
}
@media (max-width: 559px) {
  .counter {
    right: 16px;
    top: 16px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .scene,
  .fade,
  .counter,
  .step p {
    transition: none;
  }
}
</style>
