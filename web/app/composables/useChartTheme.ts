import { onBeforeUnmount, onMounted, ref } from 'vue'

export const RAMP_STEPS = 9

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
  sea: string
  seaEdge: string
  deep: string
  accent: string
  font: string
  /** Rampa divergente de nueve pasos, de frío fuerte a cálido fuerte. */
  ramp: string[]
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
  sea: '--sea',
  seaEdge: '--sea-edge',
  deep: '--deep',
  accent: '--accent',
  font: '--font',
} as const

const readTheme = (): ChartTheme => {
  const css = import.meta.client ? getComputedStyle(document.documentElement) : null
  const value = (variable: string) => css?.getPropertyValue(variable).trim() ?? ''
  return {
    ...(Object.fromEntries(
      Object.entries(THEME_VARIABLES).map(([key, variable]) => [key, value(variable)]),
    ) as Omit<ChartTheme, 'ramp'>),
    ramp: Array.from({ length: RAMP_STEPS }, (_, index) => value(`--ramp-${index + 1}`)),
  }
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
