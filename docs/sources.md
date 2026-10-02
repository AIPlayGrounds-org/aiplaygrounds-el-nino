# Sources

The sources the pipeline reads. The rest of the registry is in
[`sources.toml`](../sources.toml). `uv run wawapacha-pipeline sources`, run from
`pipeline/`, generates this file. Do not edit it by hand.

Verdicts: **automatable** (the pipeline downloads it) and **manual** (a person
loads it).

| ID                              | Source                                                         | Block | Verdict     |
| ------------------------------- | -------------------------------------------------------------- | ----- | ----------- |
| [`noaa-cpc-oni`](#noaa-cpc-oni) | NOAA Climate Prediction Center (CPC): Oceanic Niño Index (ONI) | ENSO  | automatable |

### noaa-cpc-oni

Reviewed on 2026-09-27.
[Official page](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/).

| Field               | Value                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------- |
| Institution         | NOAA Climate Prediction Center (CPC)                                                  |
| Product             | Oceanic Niño Index (ONI)                                                              |
| Variable            | Anomalía de la temperatura superficial del mar en Niño 3.4, media móvil de tres meses |
| Unit                | °C                                                                                    |
| Data type           | observed                                                                              |
| Update              | monthly                                                                               |
| Spatial resolution  | Región Niño 3.4 (5°N–5°S, 170°W–120°W)                                                |
| Temporal resolution | Trimestral móvil                                                                      |
| History             | From DJF 1950                                                                         |
| Cadence             | Monthly. CPC updates the table by the 5th of each month at the latest.                |
| Reference period    | Periodos de 30 años que CPC actualiza cada 5 años                                     |
| Access              | HTTP, text file                                                                       |
| Download URL        | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt                              |
| Format              | Column text: `SEAS YR TOTAL ANOM`                                                     |
| Authentication      | none                                                                                  |

Notes:

- The file declares no version. CPC keeps historical tables for v5 (ERSSTv5) and
  v6 (ERSSTv6). The JJA 2026 value matches v6.
- The year of `DJF` is the year of January and February: `DJF 1950` runs from
  December 1949 to February 1950.
- Recent values can be revised up to two months after they are first published.
- CPC uses the RONI, not the ONI, for its official monitoring and forecasts. The
  ONI stays as the historical series.
- CPC flags a warm or cold period when the ONI reaches ±0.5 °C for at least five
  consecutive, overlapping seasons.
