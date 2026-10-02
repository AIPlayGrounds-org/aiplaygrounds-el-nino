# Concepts for reading the data

The ideas that recur across WawaPacha's sources. What is specific to one source,
such as its format quirks, is in the notes of [`sources.md`](sources.md). The
examples use real values consulted on 2026-10-01.

## ENSO

**El Niño–Southern Oscillation** (ENSO) is a natural swing in the climate of the
tropical Pacific. In **El Niño** the sea in the central and eastern Pacific
warms above normal, in **La Niña** it cools below normal, and in the **Neutral**
phase it does neither. Each phase lasts months and changes the pattern of rain
and temperature in many parts of the world, including Peru.

## El Niño Costero

A warming of the sea **off the coast of Peru and Ecuador** (the Niño 1+2
region). It can happen even when the central Pacific has no El Niño, as in
**2017**. That is why Peru has its own index, the
[ICEN](#enso-indices-oni-roni-and-icen), and its own official commission,
**ENFEN**. In WawaPacha plain "El Niño" means the central Pacific phenomenon.

## Niño regions

Boxes in the equatorial Pacific where each index measures sea temperature. A
value "for Niño 3.4" is the **average over the whole box**.

| Region       | Location             | What it is for                                                                        |
| ------------ | -------------------- | ------------------------------------------------------------------------------------- |
| **Niño 1+2** | 0°–10°S, 90°W–80°W   | Off Peru and Ecuador. The basis of El Niño Costero and the ICEN.                      |
| **Niño 3**   | 5°N–5°S, 150°W–90°W  | Eastern Pacific.                                                                      |
| **Niño 3.4** | 5°N–5°S, 170°W–120°W | Central Pacific. The basis of the ONI and of the international definition of El Niño. |
| **Niño 4**   | 5°N–5°S, 160°E–150°W | West-central Pacific.                                                                 |

## Sea surface temperature (SST)

The temperature of the ocean surface, in **°C** (**TSM** in Spanish). Satellites
and buoys and ships (**in situ**) measure it. Some products, such as OSTIA, give
the **foundation SST**: just below the surface, without the sun's daytime
warming. It differs slightly from other products.

## Anomaly

The **difference between the observed value and the normal value** for that
place and time of year. Sea temperature changes with the seasons, so "25 °C"
does not say whether that is unusual and "+4.7 °C above normal" does. A high
anomaly is **not a danger**: it says something is unusual, not what follows from
it.

**Example.** In the week centered on 23 September 2026, the sea in Niño 1+2 was
at **25.4 °C**, **+4.7 °C** above the normal of about **20.7 °C** (NOAA CPC).

## Base period

The span of years, usually 30, used to compute the "normal value" of an anomaly.
It is also called the **climatology**.

| Source                                            | Base period                          |
| ------------------------------------------------- | ------------------------------------ |
| NOAA CPC weekly indices, CPC probabilities (RONI) | 1991–2020                            |
| OISST (NOAA PSL), ERSST v5                        | 1971–2000                            |
| ONI                                               | 30-year bases, updated every 5 years |

**Rule:** two anomalies with different base periods **cannot be compared or
subtracted directly**, because the "normal" of 1971–2000 is colder than the
normal of 1991–2020. Every chart states its base period.

## Three-month moving average

The average of **three consecutive months**, moving forward one month at a time.
The ONI and the ICEN use it to smooth month-to-month changes. Each season is
named with the initials of its months in English: DJF is December–February, JFM
is January–March, up to JJA, June–August. Seasons **overlap**: each month is in
three consecutive rows. A **JJA 2026** value is centered on July and is not
known until August ends.

## Threshold

An official value above which a condition is declared. **WawaPacha does not
invent thresholds.** It uses only those each institution publishes.

**Example.** For NOAA, El Niño conditions exist when the ONI is **≥ +0.5 °C for
at least five consecutive seasons**. From AMJ to JJA 2026 it was above +0.5 °C
for three. That is **over the threshold**, but not enough for the ONI to
**confirm** the episode.

## ENSO indices: ONI, RONI and ICEN

| Index    | Who      | Region   | What it is                                                                                                                                                                              |
| -------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ONI**  | NOAA CPC | Niño 3.4 | The three-month moving average of the SST anomaly. The historical international reference.                                                                                              |
| **RONI** | NOAA CPC | Niño 3.4 | Like the ONI, but with the average warming of the whole tropics subtracted, to separate El Niño from general ocean warming. NOAA now uses it for its official monitoring and forecasts. |
| **ICEN** | ENFEN    | Niño 1+2 | The three-month moving average of the SST anomaly off Peru. The official Peruvian index for El Niño Costero.                                                                            |

The ONI and the RONI can differ for a season. Shown together, the difference is
explained.

## Data types

Every published dataset has one of these types. The JSON stores the Spanish word
in parentheses. The types are never mixed on one line of a chart without telling
them apart.

| Type                        | What it is                                                                                                                 | Example                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **Observed** (`observado`)  | Measured directly, or computed from measurements.                                                                          | ONI, weekly indices, stations. |
| **Estimated** (`estimado`)  | Computed by a model from satellites and measurements, to cover areas with no direct measurement. Also called **analysis**. | OISST, CHIRPS, IMERG.          |
| **Forecast** (`pronóstico`) | What is expected to happen.                                                                                                | CPC probabilities, IRI plume.  |

## Grid and resolution

Satellite products divide the map into a **grid** of cells (a _raster_) with one
value per cell. The cell size is the **spatial resolution**. A 28 km cell
**cannot see coastal detail**: it mixes sea and, at times, land. The **temporal
resolution** is how often there is a value: half-hourly to quarterly.

| Resolution | Approximate size at the equator | Example       |
| ---------- | ------------------------------- | ------------- |
| 2°         | ~220 km                         | ERSST v5      |
| 0.25°      | ~28 km                          | OISST         |
| 0.1°       | ~11 km                          | IMERG, PISCO  |
| 0.05°      | ~5.5 km                         | CHIRPS, OSTIA |

## Latency and revisions

- **Latency:** the delay between the period a value describes and its
  publication. The ONI for JJA comes out in early September, the one for JAS in
  early October. A SENAMHI notice comes out before the event starts.
- **Revisions:** recent values are often **preliminary**. OISST data less than
  15 days old can change, and the latest ONI values can change for up to two
  months.

So the site shows **the period of the data**, not only the download date.

## Probabilistic forecast

It gives **the probability of each outcome** instead of a single answer. For the
OND 2026 season NOAA CPC gives 98 % to the strongest El Niño category (index ≥
2.0 °C) and 2 % to the one below. The probabilities add up to 100 %. A high
probability of El Niño **says nothing about the impacts in Peru**. A **model
plume** shows one line per model, to see how much they agree. WawaPacha does not
average models or build its own consensus.

## Precipitation

The amount of rain (or melted snow) that fell over a period, in **millimeters**:
**1 mm = 1 liter per square meter**. It always comes with its accumulation
period: "12 mm in 24 hours" is not "12 mm in a month". **Pentads** are periods
of about five days (six per month, the last one 3 to 6 days long).

## Level and discharge

**Level** is the height of the river water at a station, in meters.
**Discharge** (_caudal_) is the volume of water passing a point each second, in
**m³/s**. Each station has its own **critical levels**, published by the
authority: the same discharge can be normal in a large river and dangerous in a
small one.

## Notice, alert and emergency

Three different things that must not be confused:

| Term                                           | What it is                                                                               | When                       | Example                            |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------- |
| **Notice** (_aviso_)                           | An official forecast of a dangerous phenomenon, with an area, a validity and a level.    | **Before** the event.      | SENAMHI rain notice, orange level. |
| **Alert status** (_estado de alerta_)          | A condition declared by an official commission about a phenomenon under way or expected. | While the condition lasts. | The ENFEN alert system status.     |
| **Emergency report** (_reporte de emergencia_) | A record of damage or impact that has already happened.                                  | **After** the event.       | INDECI COEN report.                |

Every notice or alert has a **validity period**. An expired notice is never
shown as current.
