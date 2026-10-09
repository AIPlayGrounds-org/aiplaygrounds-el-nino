// Classify ONI anomalies with NOAA's official thresholds.
import type { OniRecord } from '~/types/dataset'
import { messages } from '~/messages'

export const ENSO_THRESHOLD = 0.5
// NOAA habla de episodio El Niño o La Niña a partir de 5 trimestres seguidos sobre el umbral.
export const NOAA_EPISODE_SEASONS = 5

export type EnsoPhase = 'warm' | 'neutral' | 'cold'

export const ensoPhase = (anomaly: number): EnsoPhase =>
  anomaly >= ENSO_THRESHOLD ? 'warm' : anomaly <= -ENSO_THRESHOLD ? 'cold' : 'neutral'

/** Trimestres seguidos, contando hacia atrás desde el último, en la misma fase que el último. */
export const phaseStreak = (records: OniRecord[]): number => {
  const last = records.at(-1)
  if (!last) return 0
  const phase = ensoPhase(last.anomaly)
  let count = 0
  for (let i = records.length - 1; i >= 0 && ensoPhase(records[i]!.anomaly) === phase; i--) count++
  return count
}

const MONTHS = [
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
]

const parseMonth = (yyyymm: string) => {
  const [year, month] = yyyymm.split('-').map(Number)
  return { year: year!, month: month! }
}

/** «2026-08» → «agosto de 2026». */
export const monthName = (yyyymm: string) => {
  const { year, month } = parseMonth(yyyymm)
  return messages.calendar.month(MONTHS[month - 1]!, year)
}

/** Meses que cubre un trimestre: «junio a agosto de 2026» o «diciembre de 1949 a febrero de 1950». */
export const seasonMonths = (record: OniRecord) => {
  const start = parseMonth(record.start)
  const end = parseMonth(record.end)
  return start.year === end.year
    ? messages.calendar.sameYearRange(MONTHS[start.month - 1]!, monthName(record.end))
    : messages.calendar.crossYearRange(monthName(record.start), monthName(record.end))
}

/** Fecha del mes central del trimestre (JJA 2026 → 2026-07-01), para dibujarlo y para nombrarlo. */
export const centerDate = (record: OniRecord) => {
  const { year, month } = parseMonth(record.start)
  return new Date(Date.UTC(year, month, 1))
}

/** «JJA 2026»: el año es el del mes central, como en la tabla de NOAA. */
export const seasonLabel = (record: OniRecord) =>
  `${record.season} ${centerDate(record).getUTCFullYear()}`

/** Meses enteros transcurridos entre dos meses AAAA-MM y una fecha. */
export const monthsSince = (yyyymm: string, now: Date) => {
  const { year, month } = parseMonth(yyyymm)
  return (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month)
}

const decimal = (digits: number, sign: boolean) =>
  new Intl.NumberFormat('es', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: sign ? 'exceptZero' : 'never',
  })

/** «+1,80» o «−0,60» (con el signo menos tipográfico, como en el resto de textos). */
export const formatAnomaly = (value: number) => decimal(2, true).format(value).replace('-', '−')
/** «1,80» (sin signo) */
export const formatMagnitude = (value: number) => decimal(2, false).format(Math.abs(value))
/** «29,09» */
export const formatTemperature = (value: number) => decimal(2, false).format(value)
