import type { Dataset } from '~/types/dataset'
import { formatDay } from '~/utils/format'

const dataTypeDescriptions = {
  observed: 'la fuente publica una observación o un índice derivado de observaciones.',
  estimated: 'la fuente publica un valor calculado, interpolado o producido por un modelo.',
  forecast: 'la fuente publica un valor para una fecha futura.',
  official: 'la fuente publica un estado institucional.',
} satisfies Record<Dataset['data_type'], string>

export const messages = {
  dataType: {
    observed: 'Observado',
    estimated: 'Estimado',
    forecast: 'Pronóstico',
    official: 'Oficial',
  } satisfies Record<Dataset['data_type'], string>,
  chart: {
    period: 'Periodo del gráfico',
    rangeYears: '10 años',
    rangeDecades: '30 años',
    rangeAll: 'Todo',
    anomaly: 'Anomalía',
    seaTemperature: 'Temperatura del mar',
    colors: 'Colores de la línea',
    warmThreshold: 'Sobre +0,5 °C (umbral de El Niño)',
    neutralRange: 'Rango neutral, sombreado en verde agua',
    coldThreshold: 'Bajo −0,5 °C (umbral de La Niña)',
    thresholdNote:
      'Las líneas discontinuas marcan los umbrales oficiales de la NOAA. El punto marca el último dato.',
  },
  oisst: {
    title: '¿Dónde está más caliente el mar?',
    lead: 'La anomalía diaria de la temperatura superficial del mar frente a la costa del Perú, comparada con 1991–2020.',
    summary: (date: string, value: string, unit: string, location: string) =>
      `La celda más cálida del ${date} registra ${value} ${unit} (${location}).`,
    empty: (date: string) => `No hay celdas con datos disponibles para el ${date}.`,
    tableSummary: 'Ver resumen por franjas de latitud',
    tableCaption: (date: string) => `Resumen por franjas de latitud del ${date}.`,
    latitudeBand: 'Franja de latitud',
    mean: 'Media',
    maximum: 'Máxima anomalía',
    coordinate: (value: string, direction: string) => `${value}° ${direction}`,
    band: (start: string, end: string) => `${start}–${end}`,
    tooltip: (value: string, unit: string, latitude: string, longitude: string) =>
      `${value} ${unit}<br/>${latitude}, ${longitude}`,
    directions: {
      north: 'N',
      south: 'S',
      east: 'E',
      west: 'O',
    },
  },
  provenance: {
    variable: 'Variable',
    unit: 'Unidad',
    period: 'Periodo',
    periodBase: 'Base',
    dataType: 'Tipo de dato',
    source: 'Fuente',
    lastUpdate: 'Última actualización',
    latestData: 'Último dato',
    staleSource:
      'La fuente puede tener datos más recientes. Conservamos el último valor disponible.',
    ageToday: 'hoy',
    ageDay: (days: number) => `hace ${days} día${days === 1 ? '' : 's'}`,
    ageMonth: (months: number) => `hace ${months} mes${months === 1 ? '' : 'es'}`,
    ageYear: (years: number) => `hace ${years} año${years === 1 ? '' : 's'}`,
  },
  page: {
    brand: 'WawaPacha',
    seoTitle: 'Índice Oceánico El Niño (ONI) · WawaPacha',
    seoDescription:
      'Cuánto más caliente o más frío de lo normal está el Pacífico central, con el último dato de NOAA, su fecha y qué significa para el Perú.',
    title: '¿Llegó El Niño?',
    peruTitle: '¿Y qué significa para el Perú?',
    historyTitle: 'Explora tú mismo',
    historyLead:
      'Elige el periodo y pasa el cursor (o el dedo) por la línea para ver cada trimestre.',
    methodsTitle: 'Cómo lo hicimos',
    reviewSource: 'Ver la fuente',
    chartLoading: 'Cargando el gráfico…',
    chartError: 'No se pudo dibujar el gráfico. Los últimos trimestres están en la tabla de abajo.',
    scrollCue: 'Baja para entenderlo',
    tableSummary: 'Ver los últimos 12 trimestres en una tabla',
    tableMonths: 'Meses',
    tableCode: 'Código',
    tableSeaTemperature: 'Temperatura del mar',
    tableAnomaly: 'Anomalía',
    tableThreshold: 'Respecto al umbral',
    storyAria: 'La historia del ONI, paso a paso',
    emptyTitle: 'No hay datos del ONI disponibles ahora',
    emptyLead: 'No pudimos cargar la serie. Puedes consultar el último dato directamente en la',
    oniSource: 'página del ONI de la NOAA',
    newTab: ' (se abre en una pestaña nueva)',
    enfenLink: 'Comunicados oficiales de ENFEN',
    senamhiLink: 'Avisos meteorológicos de SENAMHI',
    dataBy: 'Por WawaPacha · Datos de la',
    territoryLink: 'Territorio',
    observedUntil: (period: string) => `observados hasta ${period}`,
    signoff: 'WawaPacha · Monitoreando el Fenómeno El Niño en el Perú',
    learnLink: 'Aprende',
    methodologyLink: 'Metodología',
    peruBody:
      'Todo lo que viste se mide en el Pacífico central, a más de 4000 km de nuestra costa. Para el mar frente al Perú, el índice oficial es otro: el ICEN de ENFEN, que se mide en la región Niño 1+2, junto a la costa.',
    peruWarning:
      'Un valor alto del ONI no es una alerta. En el Perú, los estados de alerta ante El Niño los declara ENFEN, y los avisos de lluvias, SENAMHI.',
    methodsBody:
      'Usamos el Índice Oceánico El Niño (ONI) que publica el Climate Prediction Center de la NOAA, sin modificarlo. Los umbrales (±0,5 °C) y la regla de cinco trimestres seguidos son los de la NOAA; no usamos umbrales propios.',
    methodsBodyTwo:
      'La NOAA usa hoy el RONI, una variante de este índice que descuenta el calentamiento general del océano, para su monitoreo oficial. El ONI se mantiene como la serie histórica de referencia, y sus últimos trimestres pueden revisarse.',
  },
  historico: {
    historyNav: 'Histórico',
    seoTitle: 'Histórico de anomalías del mar · WawaPacha',
    seoDescription:
      'Compara por mes las anomalías de la temperatura superficial del mar durante eventos históricos y el año en curso.',
    title: 'Los eventos, mes a mes',
    lead: 'Compara la forma de las anomalías mensuales de ERSSTv5 desde el inicio de cada evento. El valor y el mes del pico se calculan de los datos mostrados.',
    comparisonTitle: 'Una misma escala de meses desde el inicio',
    ersstTitle: 'ERSSTv5 mensual',
    oniTitle: 'ONI oficial',
    oniNote: 'El ONI es la media móvil oficial de tres meses de la anomalía en Niño 3.4.',
    coastalNote:
      'Para 2017, la línea costera usa solo ERSST en Niño 1+2; el ONI no corresponde a esa región.',
    regionLabel: 'Región',
    regions: {
      nino34: 'Niño 3.4',
      nino12: 'Niño 1+2 (costa)',
    },
    eventsLabel: 'Eventos que se muestran',
    events: {
      '1982-83': '1982–83',
      '1997-98': '1997–98',
      '2017': '2017 · El Niño Costero',
    },
    currentYear: (year: number) => `${year} · año en curso`,
    peak: (value: string, month: string) => `pico ${value} °C en ${month}`,
    noPeak: 'sin datos',
    summary: (peaks: string) =>
      `Comparación de la anomalía mensual por región, alineada desde el primer mes disponible de cada evento. Picos: ${peaks || 'sin datos disponibles'}.`,
    oniSummary: (peaks: string) =>
      `Comparación del ONI oficial, una media móvil de tres meses de la anomalía en Niño 3.4. Picos: ${peaks || 'sin datos disponibles'}.`,
    anomaly: 'Anomalía',
    months: 'Meses desde el inicio',
    monthFromStart: (month: number) => `Mes ${month} desde el inicio`,
    missing: 'Sin dato',
    tableSummary: 'Ver la tabla de datos',
    tableCaption: 'Valores por mes desde el inicio de cada serie.',
    oniTableSummary: 'Ver la tabla del ONI',
    oniTableCaption: 'Valores del ONI por mes desde el inicio de cada serie.',
  },
  attribution: {
    openMeteoLabel: 'Weather data by Open-Meteo.com',
    openMeteoUrl: 'https://open-meteo.com/',
    credits: {
      'open-meteo-era5': 'Contiene datos ERA5 del Copernicus Climate Change Service (C3S) y ECMWF.',
      'open-meteo-glofas': 'Contiene datos GloFAS del Copernicus Emergency Management Service.',
    } as Record<string, string>,
  },
  metodologia: {
    seoTitle: 'Cómo lo hicimos · WawaPacha',
    seoDescription:
      'Qué mide cada fuente de WawaPacha, de dónde viene, cómo se clasifica y cuándo se actualizó.',
    sectionLabel: 'Metodología',
    title: 'Cómo lo hicimos',
    lead: 'Estas fichas salen del registro de fuentes y de los archivos de datos que publica el sitio. No copiamos aquí los detalles a mano: la página se reconstruye en cada generación.',
    provider: 'Proveedor',
    variable: 'Variable',
    unit: 'Unidad',
    resolution: 'Resolución',
    spatialResolution: 'Espacial',
    temporalResolution: 'Temporal',
    referencePeriod: 'Periodo de referencia',
    noReferencePeriod: 'No declarado en el registro.',
    license: 'Licencia o atribución',
    noLicense: 'El registro no declara una licencia o atribución.',
    lastUpdate: 'Última actualización del archivo',
    dataLink: 'Archivo o servicio consultado',
    dataTypeTitle: 'Qué significa cada tipo de dato',
    dataTypeLead:
      'La etiqueta viene del registro. WawaPacha la conserva para separar observaciones, estimaciones, pronósticos y estados oficiales.',
    dataTypeDescription: (type: Dataset['data_type']) => dataTypeDescriptions[type],
    modelTitle: 'Observado y estimado no son lo mismo',
    modelBody: (estimatedSources: string, forecastSources: string) =>
      `Estas fuentes aparecen como estimadas en el registro: ${estimatedSources || 'ninguna'}. Las fuentes marcadas como pronóstico son: ${forecastSources || 'ninguna'}. El sitio conserva esas etiquetas y no las convierte en mediciones.`,
    limitsTitle: 'Lo que este sitio no hace',
    limits: [
      'No produce pronósticos propios.',
      'No transforma un índice en una alerta.',
      'No afirma impactos en personas, actividades o lugares.',
    ],
    sourceHeading: 'Fuente',
  },
  aprende: {
    seoTitle: 'Aprende sobre El Niño y La Niña · WawaPacha',
    seoDescription:
      'Una explicación breve de El Niño, La Niña, las regiones Niño, el ONI y la costa del Perú.',
    sectionLabel: 'Aprende',
    title: 'El Niño, La Niña y el mar frente al Perú',
    lead: 'Una guía breve para leer los índices del océano sin confundir una región del Pacífico con otra.',
    phenomenonTitle: 'El Niño y La Niña',
    phenomenonBody:
      'Son las fases cálida y fría de una variación del sistema océano-atmósfera del Pacífico tropical. NOAA las explica dentro de ENSO, la Oscilación del Sur de El Niño.',
    regionsTitle: 'Las regiones Niño',
    regionsLead:
      'Son zonas del Pacífico que se usan para resumir la temperatura superficial del mar. NOAA publica estas delimitaciones:',
    regions: [
      ['Niño 1+2', '0–10°S, 90–80°O'],
      ['Niño 3', '5°N–5°S, 150–90°O'],
      ['Niño 3.4', '5°N–5°S, 170–120°O'],
      ['Niño 4', '5°N–5°S, 160°E–150°O'],
    ],
    oniTitle: 'El ONI',
    oniBody:
      'El Índice Oceánico El Niño es la media móvil de tres meses de la anomalía de la temperatura superficial del mar en la región Niño 3.4. NOAA usa sus umbrales y su regla de persistencia para describir episodios históricos de El Niño y La Niña.',
    coastTitle: 'Por qué importa la costa del Perú',
    coastBody:
      'Niño 1+2 está junto a la costa oriental del Pacífico, mientras que Niño 3.4 está en el Pacífico central. Por eso el ONI no es el índice costero peruano: ENFEN define y comunica por separado El Niño Costero y La Niña Costera.',
    sourcesTitle: 'Fuentes para seguir leyendo',
    noaaIndices: 'Regiones e índices de NOAA',
    noaaOni: 'Definición del ONI de NOAA',
    noaaExplainer: 'Explicación de ENSO de NOAA',
    enfenDefinitions: 'Notas técnicas de ENFEN',
    sourceNote: 'Los umbrales y las regiones de esta página enlazan a esas definiciones.',
  },
  territory: {
    seoTitle: 'Lluvia por departamento · WawaPacha',
    seoDescription:
      'Explora la precipitación y su anomalía más reciente por departamento del Perú, con un cruce del periodo disponible de ERA5.',
    sectionLabel: 'Territorio',
    title: '¿Dónde llovió?',
    lead: 'Compara la precipitación y su anomalía más reciente por departamento. El mapa usa CHIRPS; ERA5 sirve como cruce del periodo disponible.',
    metricGroup: 'Métrica del mapa',
    precipitation: 'Precipitación',
    anomaly: 'Anomalía',
    precipitationUnit: 'mm',
    anomalyUnit: 'mm',
    mapAria: (metric: string) => `Mapa de departamentos del Perú: ${metric}.`,
    mapSummary: (metric: string, date: string) =>
      `Mapa de la ${metric.toLowerCase()} más reciente por departamento, con datos CHIRPS hasta el ${formatDay(date)}.`,
    boundaryProvenance: 'Límites departamentales:',
    boundaryLicense: 'Licencia de los límites',
    mapTooltip: (region: string, metric: string, precipitation: string, anomaly: string) =>
      `<strong>${region}</strong><br/>${metric}<br/>Precipitación: ${precipitation}<br/>Anomalía: ${anomaly}`,
    chirpsSummary: (metric: string, date: string, count: number) =>
      `Tabla de ${metric.toLowerCase()} CHIRPS para ${count} departamentos. Último pentad: ${formatDay(date)}.`,
    chirpsCaption: (date: string) =>
      `Último registro CHIRPS por departamento, con fecha ${formatDay(date)}.`,
    tableSection: 'Tablas de datos por departamento',
    tableSummary: 'Ver la tabla de CHIRPS',
    department: 'Departamento',
    code: 'Código',
    noData: 'Sin dato',
    loading: 'Cargando el mapa…',
    chartError: 'No se pudo dibujar el mapa. La tabla de abajo conserva los datos.',
    crossCheckTitle: 'Cruce ERA5 del periodo disponible',
    crossCheckLead: (days: number, start: string, end: string) =>
      `Suma de los ${days} días disponibles, del ${formatDay(start)} al ${formatDay(end)}, junto al último valor de CHIRPS.`,
    crossCheckCaption:
      'ERA5 es una muestra puntual de una celda de 0,25°, no un promedio departamental.',
    chirpsValue: 'CHIRPS más reciente',
    era5Sum: 'ERA5 · suma del periodo',
    era5Unit: 'mm',
    era5Missing: (availableDays: number, missingDays: number) =>
      `Sin dato completo: faltan ${missingDays} días; solo hay ${availableDays} disponibles.`,
    sampleType: 'Tipo de muestra',
    pointSample: 'Punto de celda de 0,25°',
    era5Summary: (days: number, start: string, end: string, count: number) =>
      `Cruce ERA5 de precipitación diaria: suma de los ${days} días disponibles, del ${formatDay(start)} al ${formatDay(end)}, para ${count} puntos departamentales. Cada valor es una muestra puntual de una celda de 0,25°.`,
  },
  rios: {
    seoTitle: 'Caudal de ríos · WawaPacha',
    seoDescription:
      'Consulta el caudal diario estimado y pronosticado por punto de cuenca en el modelo GloFAS.',
    sectionLabel: 'Ríos',
    title: '¿Cómo viene el caudal?',
    lead: 'Explora el caudal diario estimado por GloFAS en puntos representativos de cuencas del Perú. La serie separa los días recientes del pronóstico del modelo.',
    modelNote:
      'GloFAS es un modelo hidrológico: estos valores no son mediciones de un caudalímetro. El rango sombreado muestra los percentiles 25–75 del conjunto del pronóstico, cuando están disponibles.',
    pointLabel: 'Punto de cuenca',
    estimatedSeries: 'Estimación del modelo',
    forecastSeries: 'Pronóstico del modelo',
    rangeSeries: 'Rango p25–p75 del pronóstico',
    chartDescription: 'Caudal diario estimado y pronosticado por punto de cuenca.',
    chartAria: (point: string) => `Caudal diario en ${point}.`,
    chartLoading: 'Cargando el gráfico…',
    chartError: 'No se pudo dibujar el gráfico. La tabla de abajo conserva los datos.',
    summary: (
      point: string,
      date: string,
      value: string,
      unit: string,
      forecastDate: string | null,
    ) =>
      `En ${point}, el último valor estimado del periodo reciente es ${value} ${unit} (${date}).${forecastDate ? ` El pronóstico del modelo comienza el ${forecastDate}.` : ''}`,
    emptySummary: (point: string) => `No hay valores de caudal disponibles para ${point}.`,
    tableSummary: 'Ver la tabla de datos',
    tableCaption: (point: string) => `Caudal diario del modelo para ${point}.`,
    date: 'Fecha',
    dataType: 'Tipo de dato',
    discharge: 'Caudal',
    forecastRange: 'Rango del pronóstico (p25–p75)',
    notApplicable: 'No aplica',
    noData: 'Sin dato',
    estimated: 'Estimado',
    forecast: 'Pronóstico',
    alertsTitle: 'Fuentes oficiales de alertas',
    alertsLead:
      'Para comunicados oficiales y avisos meteorológicos, consulta directamente a las instituciones responsables:',
    enfenLink: 'Comunicados oficiales de ENFEN',
    senamhiLink: 'Avisos meteorológicos de SENAMHI',
  },
  panels: {
    weekly: {
      title: '¿Cómo está el mar frente al Perú?',
      summary: (date: string, nino12: string, nino34: string) =>
        `Anomalías semanales del mar hasta ${date}. Últimos valores: Niño 1+2 ${nino12} °C y Niño 3.4 ${nino34} °C.`,
      latest: 'Último dato',
      latestValues: 'Últimos valores',
      date: 'Semana del',
      nino12: 'Niño 1+2',
      nino34: 'Niño 3.4',
      chartAxis: 'Anomalía (°C)',
      chartDescription: 'Anomalías semanales de la temperatura superficial del mar.',
      chartAria: 'Anomalías semanales',
    },
    enfen: {
      title: '¿Qué dice el estado oficial del Perú?',
      summary: (status: string, date: string) =>
        `El comunicado de ENFEN del ${date} declara: ${status}.`,
      number: (number: number, year: number) => `Comunicado n.º ${number} · ${year}`,
      date: 'Fecha',
      status: 'Estado oficial',
      latestStatus: 'Último estado oficial',
      nextDue: 'Próxima fecha prevista',
      nextDueStale: (date: string) => `Próximo comunicado previsto el ${date}; aún no publicado`,
      detail: 'Ver el comunicado oficial',
    },
    outlook: {
      title: '¿Qué esperan los pronósticos?',
      sourceLabel: 'Pronóstico de NOAA CPC',
      summary: (seasons: number, issueDate: string) =>
        `Probabilidades oficiales de NOAA CPC por categoría ENSO para ${seasons} temporadas móviles. Emisión: ${issueDate}.`,
      issueDate: 'Emisión',
      season: 'Temporada',
      probability: 'Probabilidad',
      chartDescription: 'Barras apiladas con las probabilidades por categoría ENSO.',
      chartAria: 'Probabilidades del pronóstico',
      categoryLabels: {
        '..-2': 'Índice ≤ −2,0 °C',
        '-2..-1.5': '−2,0 °C < índice ≤ −1,5 °C',
        '-1.5..-1': '−1,5 °C < índice ≤ −1,0 °C',
        '-1..-0.5': '−1,0 °C < índice ≤ −0,5 °C',
        '-0.5..0.5': '−0,5 °C < índice < 0,5 °C',
        '0.5..1': '0,5 °C ≤ índice < 1,0 °C',
        '1..1.5': '1,0 °C ≤ índice < 1,5 °C',
        '1.5..2': '1,5 °C ≤ índice < 2,0 °C',
        '2..': 'Índice ≥ 2,0 °C',
      } as Record<string, string>,
    },
  },
  oni: {
    neutralTitle: 'Ni El Niño ni La Niña',
    neutralDetail: 'El valor está entre −0,5 y +0,5 °C, el rango neutral según NOAA.',
    warmName: 'El Niño',
    coldName: 'La Niña',
    warmSide: 'sobre +0,5 °C',
    coldSide: 'bajo −0,5 °C',
    episodeRule: (streak: number) =>
      `${streak} de los 5 trimestres seguidos que la NOAA pide para hablar de un episodio`,
    episodeTitle: (name: string) => `Episodio ${name} según la definición de NOAA`,
    episodeDetail: (streak: number, side: string) =>
      `Lleva ${streak} trimestres seguidos ${side}; NOAA exige 5.`,
    aboveTitle: (name: string) =>
      `Por encima del umbral de ${name}, pero todavía no es un episodio`,
    belowTitle: (name: string) =>
      `Por debajo del umbral de ${name}, pero todavía no es un episodio`,
    belowDetail: (streak: number, side: string, name: string) =>
      `Van ${streak} de los 5 trimestres seguidos ${side} que NOAA exige para hablar de un episodio ${name}.`,
    yes: 'Sí: ya cumple la regla de episodio de la NOAA.',
    notYet: 'Todavía no es un episodio.',
    no: 'No.',
    centralWarm: 'El Pacífico central está',
    centralAbove: 'El Pacífico central ya está',
    centralNear: 'El Pacífico central está cerca de lo normal:',
    warmTail: (streak: number) =>
      `sobre lo normal, y van ${streak} trimestres seguidos por encima del umbral.`,
    warmNotYetTail: (rule: string) => `sobre lo normal, pero van ${rule}.`,
    coldTail: 'respecto a lo normal, del lado de La Niña.',
    neutralTail: 'de diferencia.',
    summary: (first: string, last: string, current: string, status: string) =>
      `Gráfico de la anomalía del ONI desde ${first} hasta ${last}. Último valor: ${current}. ${status}.`,
    rangeLabel: (phase: 'warm' | 'neutral' | 'cold') =>
      ({ warm: 'Sobre +0,5 °C', neutral: 'Rango neutral', cold: 'Bajo −0,5 °C' })[phase],
    chartAxis: 'Anomalía (°C)',
  },
  story: {
    mapEquator: 'línea ecuatorial',
    peru: 'PERÚ',
    ninoRegion: 'región Niño 3.4',
    distance: (km: string) => `más de ${km} km`,
    anomalyEquation: ['temperatura del mar − lo normal', '= anomalía'],
    sceneThresholdWarm: 'umbral de El Niño (+0,5)',
    sceneNeutral: 'rango neutral',
    sceneThresholdCold: 'umbral de La Niña (−0,5)',
    counter: (current: number, total: number) => `${current} de ${total}`,
    stepMap:
      'Todo empieza en <strong>un rectángulo de océano</strong> en medio del Pacífico, justo sobre la línea ecuatorial. Los científicos lo llaman <strong>región Niño 3.4</strong>.',
    stepDistance: (km: string) =>
      `Queda lejos: a <strong>más de ${km} km</strong> de la costa del Perú. Pero lo que pasa ahí se sigue en todo el mundo, porque es la señal de referencia para El Niño.`,
    stepMeasure:
      'Cada mes, la NOAA de Estados Unidos mide la temperatura del mar en ese rectángulo y la compara con lo normal: un promedio de 30 años que la NOAA actualiza cada cinco. La diferencia se llama <strong>anomalía</strong>.',
    stepIndex: (period: string, value: string, phase: string) =>
      `Si promedias tres meses seguidos, obtienes el <strong>Índice Oceánico El Niño (ONI)</strong>. El último, de ${period}, es <strong class="v ${phase}">${value} °C</strong>.`,
    stepThreshold:
      '¿Es mucho? La NOAA usa dos umbrales. Desde <strong>+0,5 °C</strong> se habla de condiciones de El Niño; desde <strong>−0,5 °C</strong>, de La Niña. En medio está el <strong>rango neutral</strong>.',
    stepChange: (period: string, value: string, steps: number, direction: string, amount: string) =>
      `Hace no tanto, en ${period}, el índice estaba en <strong>${value} °C</strong>. En ${steps} trimestres ${direction} <strong>${amount} °C</strong>.`,
    stepSmallChange: (from: string, to: string) =>
      `En el último año, el índice se movió poco: de ${from} °C a ${to} °C.`,
    stepNeutralStreak: (total: number) =>
      `Para hablar de un episodio, la NOAA exige <strong>${total} trimestres seguidos</strong> fuera del rango neutral. Hoy el índice está dentro.`,
    stepStreak: (
      phase: string,
      name: string,
      total: number,
      side: string,
      streak: number,
      result: string,
    ) =>
      `Pero un trimestre ${phase} no basta. Para hablar de un episodio de ${name}, la NOAA exige <strong>${total} trimestres seguidos</strong> ${side}. Van <strong>${streak}</strong>.${result}`,
    stepHistory: (count: number, first: string) =>
      `Ahora alejemos la vista. Esta es la serie completa: <strong>${count} trimestres</strong> desde ${first}.`,
    stepPeaks: (names: string, threshold: string) =>
      `Los picos más altos son episodios que muchos recuerdan: <strong>${names}</strong>. Todos pasaron de <strong>${threshold} °C</strong>.`,
    stepTodayWarm: (value: string, share: string, higher: string) =>
      `¿Y hoy? ${value} °C es más que el <strong>${share} %</strong> de todos los trimestres desde 1950. ${higher}`,
    stepTodayWarmHigher: (count: number) =>
      `Solo en <strong>${count} episodios</strong> el índice llegó más arriba.`,
    stepTodayWarmNone: 'Ningún episodio anterior llegó más arriba.',
    stepTodayOther: (value: string, side: string) =>
      `¿Y hoy? El índice está en ${value} °C, ${side}.`,
    warmSide: 'sobre +0,5 °C',
    coldSide: 'bajo −0,5 °C',
    warmPhase: 'más caliente',
    coldPhase: 'más frío',
    neutralPhase: 'cerca',
    warmName: 'El Niño',
    coldName: 'La Niña',
    episodeComplete: ' Ya es un episodio.',
    episodeIncomplete: ' Todavía no es un episodio.',
    rise: 'subió',
    fall: 'bajó',
    warmTodaySide: 'del lado de La Niña',
    neutralTodaySide: 'dentro del rango neutral',
    todayHigh: 'tan alto como hoy',
    risePeriod: (steps: number) => `en ${steps} trimestres`,
    streak: (current: number, total: number) => `${current} de ${total}`,
  },
}

export const dataTypeLabel = (type: Dataset['data_type']) => messages.dataType[type]
const dateAtEndOfPeriod = (date: string) => {
  const month = /^(\d{4})-(\d{2})$/.exec(date)
  return month ? new Date(Date.UTC(Number(month[1]), Number(month[2]), 0)) : new Date(date)
}

export const ageDays = (date: string, now = new Date()) =>
  Math.max(0, Math.floor((now.getTime() - dateAtEndOfPeriod(date).getTime()) / 86_400_000))

export const ageLabel = (date: string, now = new Date()) => {
  const days = ageDays(date, now)
  if (days === 0) return messages.provenance.ageToday
  if (days < 30) return messages.provenance.ageDay(days)
  const months = Math.floor(days / 30.4375)
  if (months < 12) return messages.provenance.ageMonth(months)
  return messages.provenance.ageYear(Math.floor(months / 12))
}

type OutlookBounds = {
  category: string
  lower_bound: number | null
  upper_bound: number | null
}

export const outlookCategoryKey = (category: OutlookBounds) =>
  `${category.lower_bound ?? ''}..${category.upper_bound ?? ''}`

export const outlookCategoryLabel = (category: OutlookBounds) =>
  messages.panels.outlook.categoryLabels[outlookCategoryKey(category)] ?? category.category
