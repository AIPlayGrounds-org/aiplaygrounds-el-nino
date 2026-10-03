# Sources

The sources the pipeline reads. The rest of the registry is in
[`sources.toml`](../sources.toml). `uv run wawapacha-pipeline sources`, run from
`pipeline/`, generates this file. Do not edit it by hand.

Verdicts: **automatable** (the pipeline downloads it) and **manual** (a person
loads it).

| ID                              | Source                                                                                          | Block   | Verdict     |
| ------------------------------- | ----------------------------------------------------------------------------------------------- | ------- | ----------- |
| [`noaa-cpc-oni`](#noaa-cpc-oni) | NOAA Climate Prediction Center (CPC): Oceanic Niño Index (ONI)                                  | ENSO    | automatable |
| [`noaa-ersst`](#noaa-ersst)     | NOAA National Centers for Environmental Information (NCEI): ERSSTv5 monthly Niño-region indices | History | automatable |

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

### noaa-ersst

Reviewed on 2026-10-02.
[Official page](https://www.ncei.noaa.gov/products/extended-reconstructed-sst).

| Field               | Value                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------- |
| Institution         | NOAA National Centers for Environmental Information (NCEI)                                    |
| Product             | ERSSTv5 monthly Niño-region indices                                                           |
| Variable            | Anomalía mensual de la temperatura superficial del mar en Niño 1+2, Niño 3, Niño 3.4 y Niño 4 |
| Unit                | °C                                                                                            |
| Data type           | estimated                                                                                     |
| Update              | monthly                                                                                       |
| Spatial resolution  | Regiones Niño 1+2, Niño 3, Niño 3.4 y Niño 4                                                  |
| Temporal resolution | Mensual                                                                                       |
| History             | From January 1854                                                                             |
| Cadence             | Monthly                                                                                       |
| Reference period    | 1971–2000                                                                                     |
| License             | No access or use restrictions according to the NCEI ERDDAP metadata, with a disclaimer.       |
| Access              | HTTP text file                                                                                |
| Download URL        | https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat                    |
| Format              | Six-column whitespace-delimited text: year, month, NINO3, NINO4, NINO3.4, NINO1.2             |
| Authentication      | none                                                                                          |

Notes:

- The published file is the small NCEI index, not the 2° grid. Its columns are
  NINO3, NINO4, NINO3.4 and NINO1.2; the module publishes them as
  `nino3_anomaly`, `nino4_anomaly`, `nino34_anomaly` and `nino12_anomaly`.
- The NCEI index supplies one row per month and does not document a
  missing-value token. A month is accepted only when all four finite anomalies
  are present.
- Event labels use the inclusive ENFEN Technical Note 01-2024 chronology:
  1982-07–1983-11, 1997-04–1998-08 and 2017-01–2017-04. This is computed
  metadata; it is not an additional anomaly.
- The anomalies are ERSSTv5 values on the 1971–2000 climatology. They are not
  ONI or ICEN values.
- Citation: Huang et al. (2017), NOAA NCEI, DOI 10.7289/V5T72FNM. Accessed
  2026-10-02.
