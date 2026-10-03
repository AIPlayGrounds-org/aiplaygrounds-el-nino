import { onBeforeUnmount, onMounted, ref } from 'vue'

type ChartTheme = {
  text: string
  muted: string
  border: string
  surface: string
  grid: string
  band: string
  axis: string
  cold: string
  neutral: string
  warm: string
  font: string
}

const THEME_VARIABLES = {
  text: '--text',
  muted: '--muted',
  border: '--border',
  surface: '--surface',
  grid: '--chart-grid',
  band: '--band',
  axis: '--muted',
  cold: '--cold',
  neutral: '--neutral-data',
  warm: '--warm',
  font: '--font',
} as const

const readTheme = (): ChartTheme => {
  const css = import.meta.client ? getComputedStyle(document.documentElement) : null
  return Object.fromEntries(
    Object.entries(THEME_VARIABLES).map(([key, variable]) => [
      key,
      css?.getPropertyValue(variable).trim() ?? '',
    ]),
  ) as ChartTheme
}

export const useChartTheme = () => {
  const theme = ref(readTheme())
  const darkQuery = import.meta.client
    ? window.matchMedia('(prefers-color-scheme: dark)')
    : undefined
  const refreshTheme = () => (theme.value = readTheme())
  onMounted(() => darkQuery?.addEventListener('change', refreshTheme))
  onBeforeUnmount(() => darkQuery?.removeEventListener('change', refreshTheme))
  return theme
}
