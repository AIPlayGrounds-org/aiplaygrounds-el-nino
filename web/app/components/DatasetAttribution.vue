<script setup lang="ts">
import { messages } from '~/messages'
import type { DatasetLike } from '~/types/datasets'

const props = defineProps<{ dataset: DatasetLike }>()

// Only Open-Meteo datasets carry the link; their institution and product are already in ChartShell.
const credit = messages.attribution.credits[props.dataset.id]
</script>

<template>
  <p v-if="credit" class="dataset-attribution">
    <a :href="messages.attribution.openMeteoUrl" target="_blank" rel="noopener">
      {{ messages.attribution.openMeteoLabel }}
      <span class="sr-only">{{ messages.page.newTab }}</span>
    </a>
    <span> · {{ credit }}</span>
  </p>
</template>

<style scoped>
.dataset-attribution {
  margin: 16px 0 0;
  color: var(--muted);
  font-size: 0.9rem;
}
</style>
