<script setup lang="ts">
// Franjas de temperatura: cada trimestre desde 1950 es una franja vertical, del azul de La Niña
// al naranja de El Niño según su anomalía. Es decorativa (la historia y la tabla dan los datos),
// pero su color sale de la serie, no de una paleta inventada.
import type { DatasetFor } from '~/types/datasets'

const props = defineProps<{ dataset: DatasetFor<'noaa-cpc-oni'> }>()
const records = props.dataset.records

// Escala divergente: frío (−2,5) → neutro (0) → cálido (+2,6), interpolada en RGB entre tres paradas.
const COLD = [42, 95, 168]
const NEUTRAL = [214, 222, 220]
const WARM = [217, 84, 26]
const mix = (a: number[], b: number[], k: number) =>
  a.map((v, i) => Math.round(v + (b[i]! - v) * k))
const colorFor = (anomaly: number) => {
  const c =
    anomaly < 0
      ? mix(NEUTRAL, COLD, Math.min(1, -anomaly / 2.5))
      : mix(NEUTRAL, WARM, Math.min(1, anomaly / 2.6))
  return `rgb(${c.join(',')})`
}
const stripes = records.map((r, i) => ({ x: i, fill: colorFor(r.anomaly) }))
// El año de cada trimestre es el de su mes central, como en la tabla de NOAA (DJF 1950 empieza en diciembre de 1949).
const first = centerDate(records[0]!).getUTCFullYear()
const last = centerDate(records.at(-1)!).getUTCFullYear()
</script>

<template>
  <div class="stripes" aria-hidden="true">
    <svg :viewBox="`0 0 ${stripes.length} 1`" preserveAspectRatio="none">
      <!-- Cada franja es un poco más ancha que su paso para que no queden rendijas al escalar. -->
      <rect v-for="s in stripes" :key="s.x" :x="s.x" y="0" width="1.6" height="1" :fill="s.fill" />
    </svg>
    <span class="year start">{{ first }}</span>
    <span class="year end">{{ last }}</span>
  </div>
</template>

<style scoped>
.stripes {
  position: relative;
  height: var(--stripes-height, 36px);
}
svg {
  display: block;
  width: 100%;
  height: 100%;
}
.year {
  position: absolute;
  bottom: calc(100% + 6px);
  font-family: var(--hand);
  font-size: 1rem;
  line-height: 1;
  color: var(--stripes-label, var(--muted));
}
.start {
  left: 16px;
}
.end {
  right: 16px;
}
</style>
