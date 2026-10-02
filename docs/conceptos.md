# Conceptos para leer los datos

Glosario de las ideas que se repiten en las fuentes de WawaPacha. Cada ficha de [`fuentes/`](fuentes/README.md) explica en su sección **Cómo leer el dato** lo propio de esa fuente y enlaza aquí para lo común.

Los ejemplos usan valores reales consultados el 2026-10-01.

---

## ENSO

**El Niño–Oscilación del Sur** (ENSO, por sus siglas en inglés) es una variación natural del clima en el océano Pacífico tropical. Tiene tres fases:

| Fase | Qué pasa en el Pacífico ecuatorial |
|---|---|
| **El Niño** | El mar se calienta más de lo normal en el centro y el este. |
| **La Niña** | El mar se enfría más de lo normal en esas mismas zonas. |
| **Neutral** | Ni una cosa ni la otra. |

Cada fase dura meses y cambia el patrón de lluvias y temperaturas en muchas regiones del mundo, incluido el Perú.

## El Niño Costero

Calentamiento del mar **frente a la costa del Perú y Ecuador** (región Niño 1+2). Puede ocurrir aunque en el Pacífico central no haya El Niño, como en **2017**. Por eso el Perú tiene su propio índice, el [ICEN](#índices-enso-oni-roni-e-icen), y su propia comisión oficial, el **ENFEN**.

En WawaPacha, "El Niño" a secas se refiere al fenómeno del Pacífico central. El costero siempre se nombra como **El Niño Costero**.

## Regiones Niño

Cajas del Pacífico ecuatorial donde se mide la temperatura del mar. Cada índice usa una:

| Región | Ubicación | Para qué sirve |
|---|---|---|
| **Niño 1+2** | 0°–10°S, 90°W–80°W | Frente a Perú y Ecuador. Base de El Niño Costero y del ICEN. |
| **Niño 3** | 5°N–5°S, 150°W–90°W | Pacífico este. |
| **Niño 3.4** | 5°N–5°S, 170°W–120°W | Pacífico central. Base del ONI y de la definición internacional de El Niño. |
| **Niño 4** | 5°N–5°S, 160°E–150°W | Pacífico oeste-central. |

Un valor "de Niño 3.4" es el **promedio de toda la caja**, no la temperatura de un punto.

## Temperatura superficial del mar (SST)

La temperatura del agua en la superficie del océano. Se abrevia **SST** (*sea surface temperature*) o **TSM** en español. Se mide en **°C**, con satélites y con boyas y barcos (**in situ**).

Algunos productos, como OSTIA, entregan la **SST fundacional**: la temperatura un poco por debajo de la superficie, sin el calentamiento que produce el sol durante el día. No es exactamente lo mismo que la SST de otros productos.

## Anomalía

La **diferencia entre el valor observado y el valor normal** para ese lugar y esa época del año:

```
anomalía = valor observado − valor normal
```

**Ejemplo.** En la semana centrada en el 23 de septiembre de 2026, el mar en Niño 1+2 estaba a **25,4 °C** con una anomalía de **+4,7 °C** según NOAA CPC. Eso significa que lo normal para esa semana es unos **20,7 °C**, y el mar estaba 4,7 °C más caliente.

Se usa la anomalía y no el valor directo porque la temperatura del mar cambia naturalmente con las estaciones. "25 °C" no dice si es raro; "+4,7 °C sobre lo normal" sí.

Una anomalía alta **no es lo mismo que un peligro**. Dice que algo es inusual, no qué consecuencias tendrá.

## Periodo base

El periodo de años que se usa para calcular el "valor normal" de una anomalía. También se llama **climatología**. Suele ser de 30 años:

| Fuente | Periodo base |
|---|---|
| Índices semanales NOAA CPC, probabilidades CPC (RONI) | 1991–2020 |
| OISST (NOAA PSL), ERSST v5 | 1971–2000 |
| ONI | Bases de 30 años que se actualizan cada 5 años |

**Regla:** dos anomalías con periodos base distintos **no se pueden comparar ni restar directamente**. Un mismo mar puede tener anomalías distintas según el periodo base, porque el "normal" de 1971–2000 es más frío que el de 1991–2020. Cada gráfico debe decir su periodo base.

## Media móvil trimestral

Promedio de **tres meses seguidos** que avanza mes a mes. Se usa en el ONI y el ICEN para suavizar los cambios de un mes a otro. Cada trimestre se nombra con las iniciales de sus meses en inglés:

```
DJF → dic ene feb
JFM →     ene feb mar
FMA →         feb mar abr
...
JJA → jun jul ago
```

Los trimestres **se solapan**: cada mes aparece en tres filas seguidas. Un valor de **JJA 2026** está "centrado" en julio y no se conoce hasta que termina agosto.

## Umbral

Valor oficial a partir del cual se declara una condición. **WawaPacha no inventa umbrales propios**: solo usa los que publica cada institución.

**Ejemplo.** Para NOAA, hay condiciones de El Niño cuando el ONI es **≥ +0,5 °C durante al menos cinco trimestres seguidos**. Entre AMJ y JJA 2026 el ONI llevaba tres trimestres seguidos por encima de +0,5 °C. Eso basta para decir que **supera el umbral**, pero no para decir que el episodio está **confirmado** según el ONI.

## Índices ENSO: ONI, RONI e ICEN

| Índice | Quién | Región | Qué es |
|---|---|---|---|
| **ONI** | NOAA CPC | Niño 3.4 | Media móvil trimestral de la anomalía de SST. Referencia internacional histórica. |
| **RONI** | NOAA CPC | Niño 3.4 | Como el ONI, pero restando el calentamiento medio de todo el trópico, para separar El Niño del calentamiento general del océano. NOAA lo usa hoy para su monitoreo y pronóstico oficiales. |
| **ICEN** | ENFEN | Niño 1+2 | Media móvil trimestral de la anomalía de SST frente al Perú. Índice oficial peruano para El Niño Costero. |

ONI y RONI pueden dar valores distintos para el mismo trimestre. Cuando se muestren juntos hay que explicar la diferencia.

## Tipos de dato

Cada dato publicado se etiqueta con uno de estos tipos:

| Tipo | Qué es | Ejemplo |
|---|---|---|
| **Observado** | Medido directamente o calculado a partir de mediciones. | ONI, índices semanales, estaciones. |
| **Estimado** | Calculado por un modelo a partir de satélites y mediciones, para cubrir zonas sin medición directa. También se llama **análisis**. | OISST, CHIRPS, IMERG. |
| **Pronóstico** | Lo que se espera que pase. | Probabilidades CPC, pluma IRI. |

Nunca se mezclan en una misma línea de un gráfico sin distinguirlos.

## Rejilla y resolución

Muchos productos satelitales dividen el mapa en una **rejilla** de celdas (también *grid* o *raster*) y dan un valor por celda. El tamaño de la celda es la **resolución espacial**:

| Resolución | Tamaño aproximado en el ecuador | Ejemplo |
|---|---|---|
| 2° | ~220 km | ERSST v5 |
| 0,25° | ~28 km | OISST |
| 0,1° | ~11 km | IMERG, PISCO |
| 0,05° | ~5,5 km | CHIRPS, OSTIA |

Una celda de 28 km **no ve detalles de la costa**: mezcla mar y, a veces, tierra. La **resolución temporal** es cada cuánto hay un valor: media hora, diaria, semanal, mensual, trimestral.

## Latencia y revisiones

- **Latencia:** el retraso entre el periodo que describe un dato y el momento en que se publica. El ONI de JJA (hasta agosto) se publica a principios de septiembre, y el de JAS a principios de octubre; un aviso de SENAMHI se publica antes de que empiece.
- **Revisiones:** muchos datos recientes son **preliminares** y se corrigen después. OISST avisa que los datos de menos de 15 días pueden cambiar; NOAA avisa que los últimos valores del ONI pueden cambiar hasta dos meses después.

Por eso la web muestra siempre **el periodo del dato**, no solo la fecha de descarga.

## Pronóstico probabilístico

En lugar de decir "pasará X", da **la probabilidad de cada resultado**. Por ejemplo, para el trimestre OND 2026 NOAA CPC da 98 % de probabilidad a la categoría más fuerte de El Niño (índice ≥ 2,0 °C) y 2 % a la siguiente.

- Las probabilidades de todas las categorías suman 100 %.
- Una probabilidad alta de El Niño **no dice qué impactos tendrá en el Perú**.
- Una **pluma de modelos** es otra forma de mostrar un pronóstico: una línea por modelo, para ver cuánto coinciden. WawaPacha no promedia modelos ni construye un consenso propio.

## Precipitación

La cantidad de lluvia (o nieve derretida) caída en un periodo. Se mide en **milímetros**: **1 mm = 1 litro por metro cuadrado**. Siempre va con su periodo de acumulación: "12 mm en 24 horas" no es lo mismo que "12 mm en un mes".

Algunos productos usan **pentadas**: periodos de unos cinco días (seis por mes; la última tiene entre 3 y 6 días).

## Nivel y caudal

- **Nivel:** la altura del agua del río en una estación, en metros.
- **Caudal:** el volumen de agua que pasa por un punto cada segundo, en **m³/s**.

Cada estación tiene sus propios **niveles críticos**, que publica la autoridad. Un mismo caudal puede ser normal en un río grande y peligroso en uno pequeño.

## Aviso, alerta y emergencia

Tres cosas distintas que no deben confundirse:

| Término | Qué es | Cuándo | Ejemplo |
|---|---|---|---|
| **Aviso** | Pronóstico oficial de un fenómeno peligroso, con zona, vigencia y nivel. | **Antes** del evento. | Aviso SENAMHI de lluvias, nivel naranja. |
| **Estado de alerta** | Condición declarada por una comisión oficial sobre un fenómeno en curso o esperado. | Mientras dura la condición. | Estado del sistema de alerta ENFEN. |
| **Reporte de emergencia** | Registro de daños o afectaciones que ya ocurrieron. | **Después** del evento. | Reporte COEN de INDECI. |

Cada aviso o alerta tiene **vigencia**: un aviso vencido nunca se muestra como vigente.
