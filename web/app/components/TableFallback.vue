<script setup lang="ts">
defineProps<{ label: string }>()
</script>

<template>
  <details class="table-fallback">
    <summary>{{ label }}</summary>
    <div class="table-wrap" role="region" :aria-label="label" tabindex="0">
      <slot />
    </div>
  </details>
</template>

<style scoped>
.table-fallback {
  min-width: 0;
  max-width: 100%;
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}
.table-fallback summary {
  min-height: 44px;
  color: var(--text);
  cursor: pointer;
  font-weight: 650;
}
.table-wrap {
  max-width: 100%;
  margin-top: 12px;
  overflow-x: auto;
}
:deep(table) {
  border-collapse: collapse;
  white-space: nowrap;
}
:deep(caption) {
  margin-bottom: 8px;
  color: var(--muted);
  text-align: left;
}
:deep(th),
:deep(td) {
  border-bottom: 1px solid var(--border);
  padding: 8px 10px;
  text-align: left;
}
:deep(th) {
  font-weight: 650;
}
</style>
