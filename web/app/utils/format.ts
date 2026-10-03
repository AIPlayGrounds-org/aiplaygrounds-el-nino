const valueFormat = new Intl.NumberFormat('es', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
  signDisplay: 'exceptZero',
})
const dayFormat = new Intl.DateTimeFormat('es', { dateStyle: 'long', timeZone: 'America/Lima' })
const monthFormat = new Intl.DateTimeFormat('es', {
  month: 'long',
  year: 'numeric',
  timeZone: 'America/Lima',
})

/** «+0,5» o «−0,5»: un decimal y el signo menos tipográfico. */
export const formatValue = (value: number) => valueFormat.format(value).replace('-', '−')

/** «28 de septiembre de 2026», a partir de AAAA-MM-DD. */
export const formatDay = (date: string) => dayFormat.format(new Date(`${date}T12:00:00Z`))

/** «septiembre de 2026», a partir de AAAA-MM. */
export const formatMonth = (date: string) => {
  const [year, month] = date.split('-').map(Number)
  return monthFormat.format(new Date(Date.UTC(year!, month! - 1, 1, 12)))
}
