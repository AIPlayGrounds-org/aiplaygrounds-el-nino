# Roadmap

Everything not built yet lives here. The other documents describe what exists.
[`sources.toml`](sources.toml) holds every source with its verdict.

## Milestones

All four ship by **2026-10-31**
([D-002](docs/decisions.md#d-002--end-of-month-scope-every-phase-trimmed)).

**v0.1 ENSO and sea**

- [x] The ONI end to end, due 2026-10-09
      ([D-001](docs/decisions.md#d-001--first-goal-the-oni-end-to-end))
- [ ] [`noaa-cpc-nino-weekly`](sources.toml): weekly Niño indices; Niño 1+2 is
      the main series, Niño 3.4 the reference, and Niño 3 and 4 are details
- [ ] [`noaa-oisst`](sources.toml): an ECharts canvas map on the 0.5° grid from
      20°N–25°S and 120°W–60°W, with rounded JSON coordinates
- [ ] [`noaa-cpc-outlook`](sources.toml): CPC's nine strength categories in
      published table order, with bounds stored as data
- [ ] [`enfen-communique`](sources.toml): the official status from hand-filled
      `pipeline/inputs/enfen.yaml`, validated and published by the source task

**v0.2 Rainfall and territory**

- [ ] [`chirps`](sources.toml)
- [ ] [`open-meteo-era5`](sources.toml): daily rainfall by region
- [ ] [`limites-inei-ign`](sources.toml): region and province boundaries

**v0.3 Rivers and alerts**

- [ ] [`senamhi-avisos`](sources.toml): SENAMHI notices
- [ ] [`open-meteo-glofas`](sources.toml): simulated discharge, shown as
      model-estimated
- [ ] Links to the official alerts

**v0.4 History**

- [ ] [`noaa-ersst`](sources.toml), with the 1982–83, 1997–98 and 2017 events

**Before the deadline**

- [ ] Emails to IGP/ENFEN, SENAMHI, ANA, DHN and INAIGEM
- [ ] Attribution text and reviewed terms of use for every source

## v0.1 panels

The page `/` keeps asking "¿Llegó El Niño?" and has seven panels
([D-007](docs/decisions.md#d-007--v01-is-one-page-made-of-panels)).

| #   | Panel                                 | Data id                                        | Status                 |
| --- | ------------------------------------- | ---------------------------------------------- | ---------------------- |
| 1   | ¿Llegó El Niño?                       | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built                  |
| 2   | ¿Cómo está el mar frente al Perú?     | [`noaa-cpc-nino-weekly`](sources.toml)         | Pipeline missing       |
| 3   | ¿Qué dice el estado oficial del Perú? | [`enfen-communique`](sources.toml)             | Pipeline missing       |
| 4   | ¿Qué esperan las previsiones?         | [`noaa-cpc-outlook`](sources.toml)             | Pipeline missing       |
| 5   | ¿Dónde está más caliente el mar?      | [`noaa-oisst`](sources.toml)                   | Map spike missing      |
| 6   | Explora la serie histórica            | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built                  |
| 7   | Cómo lo hicimos                       | provenance of each dataset                     | Built for the ONI only |

## Later sources

Each source leaves this list when it has a module and a section in
[`docs/sources.md`](docs/sources.md).

- [ ] [`enfen-icen`](sources.toml), [`enfen-icen-history`](sources.toml): later;
      SIOFEN is behind a Cloudflare challenge and IGP times out, so Niño 1+2
      weekly stands in for v0.1
- [ ] [`copernicus-ostia`](sources.toml), [`ecmwf-seas5`](sources.toml)
- [ ] [`dhn-boletines`](sources.toml), [`iri-enso-pluma`](sources.toml): manual
- [ ] [`senamhi-pisco`](sources.toml), [`senamhi-estaciones`](sources.toml),
      [`nasa-imerg`](sources.toml)
- [ ] [`senamhi-hidro`](sources.toml), [`ana-snirh`](sources.toml),
      [`ana-alertas`](sources.toml), [`inaigem`](sources.toml)
- [ ] [`indeci-coen`](sources.toml): manual

Decided against: `bom-enso` and `enfen-forecast`.

## Product sections

The site is one page today. Later sections are **Dashboard**, **Territorio**,
**Histórico**, **Pronósticos**, **Alertas**, **Aprende**, **Metodología** and an
AI summary that cites its source, variable, date and value and never invents
causes, forecasts, alerts or risk levels.

## Infrastructure

- [ ] Scheduled refresh: `update-data.yml` asks `wawapacha-pipeline due` and
      runs only due sources.
- [ ] Keep the browser on our static JSON; upstream traffic comes from
      ingestion, not visitors.
- [ ] Revisit sub-daily rain and river sources: move data off `main`, probably a
      Cloudflare cron job writing to R2 or KV.
- [ ] Tailwind, a global time range, English and Quechua, and search indexing
      for Aprende, Histórico and Territorio.

## Open question

Names are still needed for the Data, Web and Content owners
([D-003](docs/decisions.md#d-003--team-split)).

## Out of scope for now

Accounts and login, favorites, push notifications, a public API, our own CSV or
JSON downloads, global search, district level, our own predictive models, a
model consensus, and agriculture, fishing, health or infrastructure modules.
