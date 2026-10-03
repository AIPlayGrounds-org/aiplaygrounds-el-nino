# Sources

The sources the pipeline reads. The rest of the registry is in
[`sources.toml`](../sources.toml). `uv run wawapacha-pipeline sources`, run from
`pipeline/`, generates this file. Do not edit it by hand.

Verdicts: **automatable** (the pipeline publishes it) and **manual** (a person
loads it).

| ID                                      | Source                                                                                                       | Block   | Verdict     |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------- | ----------- |
| [`noaa-cpc-oni`](#noaa-cpc-oni)         | NOAA Climate Prediction Center (CPC): Oceanic Niño Index (ONI)                                               | ENSO    | automatable |
| [`enfen-communique`](#enfen-communique) | Comisión Multisectorial ENFEN: Comunicado Oficial ENFEN                                                      | Alerts  | automatable |
| [`noaa-oisst`](#noaa-oisst)             | NOAA NCEI, distributed by NOAA PSL: Daily Optimum Interpolation Sea Surface Temperature (OISST), version 2.1 | SST     | automatable |
| [`noaa-ersst`](#noaa-ersst)             | NOAA National Centers for Environmental Information (NCEI): ERSSTv5 monthly Niño-region indices              | History | automatable |

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

### enfen-communique

Reviewed on 2026-10-02.
[Official page](https://enfen.imarpe.gob.pe/downloads/comunicados/).

| Field               | Value                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------- |
| Institution         | Comisión Multisectorial ENFEN                                                           |
| Product             | Comunicado Oficial ENFEN                                                                |
| Variable            | Estado del sistema de alerta de El Niño Costero                                         |
| Unit                | Estado oficial                                                                          |
| Data type           | official                                                                                |
| Update              | manual                                                                                  |
| Spatial resolution  | Costa del Perú                                                                          |
| Temporal resolution | Por comunicado, cada dos semanas aproximadamente                                        |
| Cadence             | Irregular. In the archive consulted, about every two weeks.                             |
| Access              | Hand-filled YAML, read from the communiqué HTML                                         |
| Download URL        | https://enfen.imarpe.gob.pe/downloads/comunicados/                                      |
| Format              | YAML: one `enfen` mapping with number, year, date, status, url, next_due and checked_at |
| Authentication      | none                                                                                    |

Notes:

- A person fills `pipeline/inputs/enfen.yaml` from the newest communiqué, about
  every two weeks and at least once a month. Open the archive, copy the number,
  date, exact status and detail URL from the communiqué HTML, copy the next-due
  date it states, set `checked_at` to today, then run
  `uv run wawapacha-pipeline run enfen-communique` from `pipeline/`. The
  `update` is `manual` for this reason: due selection never runs it.
- The pipeline does not download. It validates the YAML and publishes one
  record. `access.url` is the archive where the person reads the communiqué.
- The status is one of five exact phrases: `No Activo`,
  `Vigilancia de El Niño Costero`, `Alerta de El Niño Costero`,
  `Vigilancia de La Niña Costera`, `Alerta de La Niña Costera`. Anything else is
  rejected, never normalized. The communiqué's own sentence around the phrase
  varies, so only the phrase is stored.
- The URL must be the IMARPE detail page of the same number and year,
  `https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-<number>-<year>/`.
  The PDF is not the canonical link.
- Computed: the record's `start` is the communiqué date and its `end` is the
  next-due date the communiqué states, because the status holds until the next
  communiqué. `stale` is true when the ingestion date, in Lima time, is after
  `end`. A stale record means nobody has refreshed the YAML in time. It is
  recomputed only when the pipeline runs, so the site should also compare `end`
  with its own build date.
- Each communiqué has an HTML page and one PDF. Communiqué No. 17-2026, of
  2026-09-28, states `Alerta de El Niño Costero` in the HTML and says the next
  one is due on 2026-10-15.

### noaa-oisst

Reviewed on 2026-10-02.
[Official page](https://www.ncei.noaa.gov/products/optimum-interpolation-sst).

| Field               | Value                                                                                                                      |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Institution         | NOAA NCEI, distributed by NOAA PSL                                                                                         |
| Product             | Daily Optimum Interpolation Sea Surface Temperature (OISST), version 2.1                                                   |
| Variable            | Anomalía de la temperatura superficial del mar respecto a la climatología 1991–2020                                        |
| Unit                | °C                                                                                                                         |
| Data type           | estimated                                                                                                                  |
| Update              | daily                                                                                                                      |
| Spatial resolution  | Malla de 0,5° × 0,5° entre 20°N–25°S y 120°W–60°W                                                                          |
| Temporal resolution | Diaria                                                                                                                     |
| History             | From 1981-09-01. The published file holds only the latest day.                                                             |
| Cadence             | Daily, with preliminary data. On 2026-10-02 PSL held up to 2026-10-01. NCEI's final version arrives about two weeks later. |
| Reference period    | 1991–2020                                                                                                                  |
| License             | The ERDDAP metadata allow free use and redistribution, with a disclaimer. They do not name a formal license.               |
| Access              | NOAA PSL NCSS (NetCDF subset service)                                                                                      |
| Download URL        | https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.oisst.v2.highres                                                      |
| Format              | NetCDF classic (`accept=netcdf`): `sst.day.mean.<year>.nc` and `sst.day.mean.ltm.1991-2020.nc`                             |
| Authentication      | none                                                                                                                       |

Notes:

- A level 4 product: it merges satellite (AVHRR and VIIRS) and in situ
  observations, interpolated onto a complete grid.
- Computed here: the daily SST of the latest day minus the PSL daily climatology
  (`sst.day.mean.ltm.1991-2020.nc`) for the same month and day, on the 0.25°
  grid. The product's own `anom` variable is not used: it is based on 1971–2000.
- The published grid is the mean of each 2 × 2 block of 0.25° cells, ignoring
  missing cells, rounded to 2 decimals. A block with no value is `null`. The
  axes are the block centers, with longitude in °E, negative to the west
  (-119.75 to -60.25).
- Baseline checked on 2026-10-02. The climatology file's global metadata says
  1971–2000, but its time axis says 1991/01/01–2020/12/31. Over the 38 CPC weeks
  of 2026 up to 23SEP2026, the mean of this anomaly over the Niño 3.4 box
  (5°N–5°S, 170°W–120°W) differs from `wksst9120.for` by -0.005 °C on average
  and by 0.10 °C at most. PSL's own 1971–2000 `anom` differs by +0.07 °C on
  average and by 0.23 °C at most. The baseline is 1991–2020, the same as CPC's
  weekly indices. The 1971–2000 text is inherited metadata.
- The climatology has 365 days, numbered in the Julian calendar, with no 29
  February. 29 February uses 28 February. The pipeline places the day from the
  first day of the file, because Python decodes the dates two days early.
- PSL keeps one SST file per year (`sst.day.mean.<year>.nc`). The pipeline asks
  for the last 3 days and keeps the latest. In the first days of January the
  newest day is still in the previous year's file.
- NCSS returns the cells just outside the box too (one row and one column). The
  pipeline keeps the 180 × 240 cells inside it. Land arrives as `NaN`.
- Data less than 15 days old is preliminary and can change.
- The NCEI ERDDAP returns final data as CSV, about two weeks late. It is not
  used. Its timestamp query failed with HTTP 400 on 2026-10-02: only the `last`
  index form works.

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
