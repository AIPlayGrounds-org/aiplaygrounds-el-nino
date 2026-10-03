import type { Dataset } from "~/types/dataset";
import { formatDay } from "~/utils/format";

export const messages = {
  dataType: {
    observed: "Observado",
    estimated: "Estimado",
    forecast: "Pronóstico",
    official: "Oficial",
  } satisfies Record<Dataset["data_type"], string>,
  chart: {
    period: "Periodo del gráfico",
    rangeYears: "10 años",
    rangeDecades: "30 años",
    rangeAll: "Todo",
    anomaly: "Anomalía",
    seaTemperature: "Temperatura del mar",
    colors: "Colores de la línea",
    warmThreshold: "Sobre +0,5 °C (umbral de El Niño)",
    neutralRange: "Rango neutral, sombreado en verde agua",
    coldThreshold: "Bajo −0,5 °C (umbral de La Niña)",
    thresholdNote:
      "Las líneas discontinuas marcan los umbrales oficiales de la NOAA. El punto marca el último dato.",
  },
  oisst: {
    title: "¿Dónde está más caliente el mar?",
    lead:
      "La anomalía diaria de la temperatura superficial del mar frente a la costa del Perú, comparada con 1991–2020.",
    summary: (date: string, value: string, unit: string, location: string) =>
      `La celda más cálida del ${date} registra ${value} ${unit} (${location}).`,
    empty: (date: string) => `No hay celdas con datos disponibles para el ${date}.`,
    tableSummary: "Ver resumen por franjas de latitud",
    tableCaption: (date: string) => `Resumen por franjas de latitud del ${date}.`,
    latitudeBand: "Franja de latitud",
    mean: "Media",
    maximum: "Máxima anomalía",
    coordinate: (value: string, direction: string) => `${value}° ${direction}`,
    band: (start: string, end: string) => `${start}–${end}`,
    tooltip: (value: string, unit: string, latitude: string, longitude: string) =>
      `${value} ${unit}<br/>${latitude}, ${longitude}`,
    directions: {
      north: "N",
      south: "S",
      east: "E",
      west: "O",
    },
  },
  provenance: {
    variable: "Variable",
    unit: "Unidad",
    period: "Periodo",
    periodBase: "Base",
    dataType: "Tipo de dato",
    source: "Fuente",
    lastUpdate: "Última actualización",
    latestData: "Último dato",
    staleSource:
      "La fuente puede tener datos más recientes. Conservamos el último valor disponible.",
    ageToday: "hoy",
    ageDay: (days: number) => `hace ${days} día${days === 1 ? "" : "s"}`,
    ageMonth: (months: number) => `hace ${months} mes${months === 1 ? "" : "es"}`,
    ageYear: (years: number) => `hace ${years} año${years === 1 ? "" : "s"}`,
  },
  page: {
    brand: "WawaPacha",
    seoTitle: "Índice Oceánico El Niño (ONI) · WawaPacha",
    seoDescription:
      "Cuánto más caliente o más frío de lo normal está el Pacífico central, con el último dato de NOAA, su fecha y qué significa para el Perú.",
    title: "¿Llegó El Niño?",
    peruTitle: "¿Y qué significa para el Perú?",
    historyTitle: "Explora tú mismo",
    historyLead:
      "Elige el periodo y pasa el cursor (o el dedo) por la línea para ver cada trimestre.",
    methodsTitle: "Cómo lo hicimos",
    reviewSource: "Ver la fuente",
    chartLoading: "Cargando el gráfico…",
    chartError: "No se pudo dibujar el gráfico. Los últimos trimestres están en la tabla de abajo.",
    scrollCue: "Baja para entenderlo",
    tableSummary: "Ver los últimos 12 trimestres en una tabla",
    tableMonths: "Meses",
    tableCode: "Código",
    tableSeaTemperature: "Temperatura del mar",
    tableAnomaly: "Anomalía",
    tableThreshold: "Respecto al umbral",
    storyAria: "La historia del ONI, paso a paso",
    emptyTitle: "No hay datos del ONI disponibles ahora",
    emptyLead: "No pudimos cargar la serie. Puedes consultar el último dato directamente en la",
    oniSource: "página del ONI de la NOAA",
    newTab: " (se abre en una pestaña nueva)",
    enfenLink: "Comunicados oficiales de ENFEN",
    senamhiLink: "Avisos meteorológicos de SENAMHI",
    dataBy: "Por WawaPacha · Datos de la",
    territoryLink: "Territorio",
    observedUntil: (period: string) => `observados hasta ${period}`,
    signoff: "WawaPacha · Monitoreando el Fenómeno El Niño en el Perú",
    peruBody:
      "Todo lo que viste se mide en el Pacífico central, a más de 4000 km de nuestra costa. Para el mar frente al Perú, el índice oficial es otro: el ICEN de ENFEN, que se mide en la región Niño 1+2, junto a la costa.",
    peruWarning:
      "Un valor alto del ONI no es una alerta. En el Perú, los estados de alerta ante El Niño los declara ENFEN, y los avisos de lluvias, SENAMHI.",
    methodsBody:
      "Usamos el Índice Oceánico El Niño (ONI) que publica el Climate Prediction Center de la NOAA, sin modificarlo. Los umbrales (±0,5 °C) y la regla de cinco trimestres seguidos son los de la NOAA; no usamos umbrales propios.",
    methodsBodyTwo:
      "La NOAA usa hoy el RONI, una variante de este índice que descuenta el calentamiento general del océano, para su monitoreo oficial. El ONI se mantiene como la serie histórica de referencia, y sus últimos trimestres pueden revisarse.",
  },
  attribution: {
    openMeteoLabel: "Weather data by Open-Meteo.com",
    openMeteoUrl: "https://open-meteo.com/",
    credits: {
      "open-meteo-era5":
        "Contiene datos ERA5 del Copernicus Climate Change Service (C3S) y ECMWF.",
      "open-meteo-glofas":
        "Contiene datos GloFAS del Copernicus Emergency Management Service.",
    } as Record<string, string>,
  },
  territory: {
    seoTitle: "Lluvia por departamento · WawaPacha",
    seoDescription:
      "Explora la precipitación y su anomalía más reciente por departamento del Perú, con un cruce del periodo disponible de ERA5.",
    sectionLabel: "Territorio",
    title: "¿Dónde llovió?",
    lead:
      "Compara la precipitación y su anomalía más reciente por departamento. El mapa usa CHIRPS; ERA5 sirve como cruce del periodo disponible.",
    metricGroup: "Métrica del mapa",
    precipitation: "Precipitación",
    anomaly: "Anomalía",
    precipitationUnit: "mm",
    anomalyUnit: "mm",
    mapAria: (metric: string) => `Mapa de departamentos del Perú: ${metric}.`,
    mapSummary: (metric: string, date: string) =>
      `Mapa de la ${metric.toLowerCase()} más reciente por departamento, con datos CHIRPS hasta el ${formatDay(date)}.`,
    boundaryProvenance: "Límites departamentales:",
    boundaryLicense: "Licencia de los límites",
    mapTooltip: (region: string, metric: string, precipitation: string, anomaly: string) =>
      `<strong>${region}</strong><br/>${metric}<br/>Precipitación: ${precipitation}<br/>Anomalía: ${anomaly}`,
    chirpsSummary: (metric: string, date: string, count: number) =>
      `Tabla de ${metric.toLowerCase()} CHIRPS para ${count} departamentos. Último pentad: ${formatDay(date)}.`,
    chirpsCaption: (date: string) =>
      `Último registro CHIRPS por departamento, con fecha ${formatDay(date)}.`,
    tableSection: "Tablas de datos por departamento",
    tableSummary: "Ver la tabla de CHIRPS",
    department: "Departamento",
    code: "Código",
    noData: "Sin dato",
    loading: "Cargando el mapa…",
    chartError: "No se pudo dibujar el mapa. La tabla de abajo conserva los datos.",
    crossCheckTitle: "Cruce ERA5 del periodo disponible",
    crossCheckLead: (days: number, start: string, end: string) =>
      `Suma de los ${days} días disponibles, del ${formatDay(start)} al ${formatDay(end)}, junto al último valor de CHIRPS.`,
    crossCheckCaption: "ERA5 es una muestra puntual de una celda de 0,25°, no un promedio departamental.",
    chirpsValue: "CHIRPS más reciente",
    era5Sum: "ERA5 · suma del periodo",
    era5Unit: "mm",
    era5Missing: (availableDays: number, missingDays: number) =>
      `Sin dato completo: faltan ${missingDays} días; solo hay ${availableDays} disponibles.`,
    sampleType: "Tipo de muestra",
    pointSample: "Punto de celda de 0,25°",
    era5Summary: (days: number, start: string, end: string, count: number) =>
      `Cruce ERA5 de precipitación diaria: suma de los ${days} días disponibles, del ${formatDay(start)} al ${formatDay(end)}, para ${count} puntos departamentales. Cada valor es una muestra puntual de una celda de 0,25°.`,
  },
  panels: {
    weekly: {
      title: "¿Cómo está el mar frente al Perú?",
      summary: (date: string, nino12: string, nino34: string) =>
        `Anomalías semanales del mar hasta ${date}. Últimos valores: Niño 1+2 ${nino12} °C y Niño 3.4 ${nino34} °C.`,
      latest: "Último dato",
      latestValues: "Últimos valores",
      date: "Semana del",
      nino12: "Niño 1+2",
      nino34: "Niño 3.4",
      chartAxis: "Anomalía (°C)",
      chartDescription: "Anomalías semanales de la temperatura superficial del mar.",
      chartAria: "Anomalías semanales",
    },
    enfen: {
      title: "¿Qué dice el estado oficial del Perú?",
      summary: (status: string, date: string) =>
        `El comunicado de ENFEN del ${date} declara: ${status}.`,
      number: (number: number, year: number) => `Comunicado n.º ${number} · ${year}`,
      date: "Fecha",
      status: "Estado oficial",
      latestStatus: "Último estado oficial",
      nextDue: "Próxima fecha prevista",
      nextDueStale: (date: string) =>
        `Próximo comunicado previsto el ${date}; aún no publicado`,
      detail: "Ver el comunicado oficial",
    },
    outlook: {
      title: "¿Qué esperan los pronósticos?",
      sourceLabel: "Pronóstico de NOAA CPC",
      summary: (seasons: number, issueDate: string) =>
        `Probabilidades oficiales de NOAA CPC por categoría ENSO para ${seasons} temporadas móviles. Emisión: ${issueDate}.`,
      issueDate: "Emisión",
      season: "Temporada",
      probability: "Probabilidad",
      chartDescription: "Barras apiladas con las probabilidades por categoría ENSO.",
      chartAria: "Probabilidades del pronóstico",
      categoryLabels: {
        "..-2": "Índice ≤ −2,0 °C",
        "-2..-1.5": "−2,0 °C < índice ≤ −1,5 °C",
        "-1.5..-1": "−1,5 °C < índice ≤ −1,0 °C",
        "-1..-0.5": "−1,0 °C < índice ≤ −0,5 °C",
        "-0.5..0.5": "−0,5 °C < índice < 0,5 °C",
        "0.5..1": "0,5 °C ≤ índice < 1,0 °C",
        "1..1.5": "1,0 °C ≤ índice < 1,5 °C",
        "1.5..2": "1,5 °C ≤ índice < 2,0 °C",
        "2..": "Índice ≥ 2,0 °C",
      } as Record<string, string>,
    },
  },
  oni: {
    neutralTitle: "Ni El Niño ni La Niña",
    neutralDetail: "El valor está entre −0,5 y +0,5 °C, el rango neutral según NOAA.",
    warmName: "El Niño",
    coldName: "La Niña",
    warmSide: "sobre +0,5 °C",
    coldSide: "bajo −0,5 °C",
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
    yes: "Sí: ya cumple la regla de episodio de la NOAA.",
    notYet: "Todavía no es un episodio.",
    no: "No.",
    centralWarm: "El Pacífico central está",
    centralAbove: "El Pacífico central ya está",
    centralNear: "El Pacífico central está cerca de lo normal:",
    warmTail: (streak: number) =>
      `sobre lo normal, y van ${streak} trimestres seguidos por encima del umbral.`,
    warmNotYetTail: (rule: string) => `sobre lo normal, pero van ${rule}.`,
    coldTail: "respecto a lo normal, del lado de La Niña.",
    neutralTail: "de diferencia.",
    summary: (first: string, last: string, current: string, status: string) =>
      `Gráfico de la anomalía del ONI desde ${first} hasta ${last}. Último valor: ${current}. ${status}.`,
    rangeLabel: (phase: "warm" | "neutral" | "cold") =>
      ({ warm: "Sobre +0,5 °C", neutral: "Rango neutral", cold: "Bajo −0,5 °C" })[phase],
    chartAxis: "Anomalía (°C)",
  },
  story: {
    mapEquator: "línea ecuatorial",
    peru: "PERÚ",
    ninoRegion: "región Niño 3.4",
    distance: (km: string) => `más de ${km} km`,
    anomalyEquation: ["temperatura del mar − lo normal", "= anomalía"],
    sceneThresholdWarm: "umbral de El Niño (+0,5)",
    sceneNeutral: "rango neutral",
    sceneThresholdCold: "umbral de La Niña (−0,5)",
    counter: (current: number, total: number) => `${current} de ${total}`,
    stepMap:
      "Todo empieza en <strong>un rectángulo de océano</strong> en medio del Pacífico, justo sobre la línea ecuatorial. Los científicos lo llaman <strong>región Niño 3.4</strong>.",
    stepDistance: (km: string) =>
      `Queda lejos: a <strong>más de ${km} km</strong> de la costa del Perú. Pero lo que pasa ahí se sigue en todo el mundo, porque es la señal de referencia para El Niño.`,
    stepMeasure:
      "Cada mes, la NOAA de Estados Unidos mide la temperatura del mar en ese rectángulo y la compara con lo normal: un promedio de 30 años que la NOAA actualiza cada cinco. La diferencia se llama <strong>anomalía</strong>.",
    stepIndex: (period: string, value: string, phase: string) =>
      `Si promedias tres meses seguidos, obtienes el <strong>Índice Oceánico El Niño (ONI)</strong>. El último, de ${period}, es <strong class="v ${phase}">${value} °C</strong>.`,
    stepThreshold:
      "¿Es mucho? La NOAA usa dos umbrales. Desde <strong>+0,5 °C</strong> se habla de condiciones de El Niño; desde <strong>−0,5 °C</strong>, de La Niña. En medio está el <strong>rango neutral</strong>.",
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
    stepTodayWarmNone: "Ningún episodio anterior llegó más arriba.",
    stepTodayOther: (value: string, side: string) =>
      `¿Y hoy? El índice está en ${value} °C, ${side}.`,
    warmSide: "sobre +0,5 °C",
    coldSide: "bajo −0,5 °C",
    warmPhase: "más caliente",
    coldPhase: "más frío",
    neutralPhase: "cerca",
    warmName: "El Niño",
    coldName: "La Niña",
    episodeComplete: " Ya es un episodio.",
    episodeIncomplete: " Todavía no es un episodio.",
    rise: "subió",
    fall: "bajó",
    warmTodaySide: "del lado de La Niña",
    neutralTodaySide: "dentro del rango neutral",
    todayHigh: "tan alto como hoy",
    risePeriod: (steps: number) => `en ${steps} trimestres`,
    streak: (current: number, total: number) => `${current} de ${total}`,
  },
};

export const dataTypeLabel = (type: Dataset["data_type"]) => messages.dataType[type];
const dateAtEndOfPeriod = (date: string) => {
  const month = /^(\d{4})-(\d{2})$/.exec(date);
  return month
    ? new Date(Date.UTC(Number(month[1]), Number(month[2]), 0))
    : new Date(date);
};

export const ageDays = (date: string, now = new Date()) =>
  Math.max(0, Math.floor((now.getTime() - dateAtEndOfPeriod(date).getTime()) / 86_400_000));

export const ageLabel = (date: string, now = new Date()) => {
  const days = ageDays(date, now);
  if (days === 0) return messages.provenance.ageToday;
  if (days < 30) return messages.provenance.ageDay(days);
  const months = Math.floor(days / 30.4375);
  if (months < 12) return messages.provenance.ageMonth(months);
  return messages.provenance.ageYear(Math.floor(months / 12));
};

type OutlookBounds = {
  category: string;
  lower_bound: number | null;
  upper_bound: number | null;
};

export const outlookCategoryKey = (category: OutlookBounds) =>
  `${category.lower_bound ?? ""}..${category.upper_bound ?? ""}`;

export const outlookCategoryLabel = (category: OutlookBounds) =>
  messages.panels.outlook.categoryLabels[outlookCategoryKey(category)] ?? category.category;
