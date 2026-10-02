# Roadmap

Everything that is not built yet lives here, and only here. The other documents
describe what exists. [`sources.toml`](sources.toml) holds every source with its
verdict.

## Milestones

All four ship by **2026-10-31**
([D-002](docs/decisions.md#d-002--end-of-month-scope-every-phase-trimmed)). Each
uses only the sources that can be fetched without waiting on an institution.

**v0.1 ENSO and sea**

- [x] The ONI end to end, due 2026-10-09
      ([D-001](docs/decisions.md#d-001--first-goal-the-oni-end-to-end))
- [ ] [`noaa-cpc-nino-semanal`](sources.toml): weekly Niño indices
- [ ] [`noaa-oisst`](sources.toml): the OISST map
- [ ] [`noaa-cpc-outlook`](sources.toml): NOAA CPC probabilities
- [ ] [`enfen-comunicado`](sources.toml): the ENFEN status, entered by hand

**v0.2 Rainfall and territory**

- [ ] [`chirps`](sources.toml)
- [ ] [`open-meteo-era5`](sources.toml): daily rainfall by region
      ([D-005](docs/decisions.md#d-005--free-apis-for-rainfall-and-rivers))
- [ ] [`limites-inei-ign`](sources.toml): region and province boundaries

**v0.3 Rivers and alerts**

- [ ] [`senamhi-avisos`](sources.toml): SENAMHI notices
- [ ] [`open-meteo-glofas`](sources.toml): simulated discharge, shown as
      model-estimated
- [ ] Links to the official alerts

**v0.4 History**

- [ ] [`noaa-ersst`](sources.toml), with the 1982–83, 1997–98 and 2017 events

**Before the deadline**

- [ ] Emails to IGP/ENFEN, SENAMHI, ANA, DHN and INAIGEM, so the replies arrive
      in time for a later phase
- [ ] Attribution text and reviewed terms of use for every source

## v0.1 panels

The page `/` keeps asking "¿Llegó El Niño?" and is made of seven panels
([D-007](docs/decisions.md#d-007--v01-is-one-page-made-of-panels)). Each reads a
single dataset.

| #   | Panel                                 | Data id                                        | Status                 |
| --- | ------------------------------------- | ---------------------------------------------- | ---------------------- |
| 1   | ¿Llegó El Niño?                       | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built                  |
| 2   | ¿Cómo está el mar frente al Perú?     | [`noaa-cpc-nino-semanal`](sources.toml)        | Pipeline missing       |
| 3   | ¿Qué dice el estado oficial del Perú? | [`enfen-comunicado`](sources.toml)             | Pipeline missing       |
| 4   | ¿Qué esperan los pronósticos?         | [`noaa-cpc-outlook`](sources.toml)             | Pipeline missing       |
| 5   | ¿Dónde está más caliente el mar?      | [`noaa-oisst`](sources.toml)                   | Map spike missing      |
| 6   | Explora la serie histórica            | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built                  |
| 7   | Cómo lo hicimos                       | the provenance of each dataset                 | Built for the ONI only |

## Later sources

Each one needs an institution's reply, an account or a confirmed license. A
source leaves this list when it has a module and a section in
[`docs/sources.md`](docs/sources.md).

- [ ] [`enfen-icen`](sources.toml), [`enfen-icen-historico`](sources.toml)
- [ ] [`copernicus-ostia`](sources.toml), [`ecmwf-seas5`](sources.toml)
- [ ] [`dhn-boletines`](sources.toml), [`iri-enso-pluma`](sources.toml): manual
- [ ] [`senamhi-pisco`](sources.toml), [`senamhi-estaciones`](sources.toml),
      [`nasa-imerg`](sources.toml)
- [ ] [`senamhi-hidro`](sources.toml), [`ana-snirh`](sources.toml),
      [`ana-alertas`](sources.toml), [`inaigem`](sources.toml)
- [ ] [`indeci-coen`](sources.toml): manual

Decided against: `bom-enso` and `enfen-pronostico`.

## Product sections

The site is one page today. After the milestones:

- **Dashboard:** what is happening now (SST, ENSO, rainfall, rivers, forecasts,
  alerts, news), in a fixed order until there is a fair way to rank very
  different variables by anomaly.
- **Territorio:** a map-led view by region and province, with a card for each.
- **Histórico:** series, anomalies and past events, with 2017 labeled **Niño
  Costero**.
- **Pronósticos:** one chart per institution, with no average.
- **Alertas:** meteorological, hydrological, and avalanche and debris-flow
  alerts, linked to the official source until ingestion is reliable.
- **Aprende** and **Metodología:** a plain-language guide, and the sources,
  processing, base periods and limits.
- **AI summary**, "Qué está pasando ahora": written from normalized data. It
  never infers causes, forecasts, invents alerts or assigns risk levels, and
  every statement links to its source, variable, date and value. A person
  reviews the first ones.

## Infrastructure

- [ ] Scheduled data refresh: GitHub Actions with cron, one source at a time.
- [ ] Maps with MapLibre GL JS.
- [ ] Tailwind. The web uses its own stylesheets.
- [ ] A global time range (24 h · 7 d · 30 d · 12 m), where ENSO and the
      forecasts keep their own window.
- [ ] English and Quechua, on top of the Spanish i18n.
- [ ] Search-engine indexing for Aprende, Histórico and Territorio.

## Out of scope for now

Accounts and login, favorites, push notifications, a public API, our own CSV or
JSON downloads, global search, district level, our own predictive models, a
model consensus, and agriculture, fishing, health or infrastructure modules.

## Open questions

1. **The type of the ENFEN status.** `data_type` accepts `observado`, `estimado`
   and `pronóstico`; the status is none of them. Proposal: add `oficial` to the
   [schema](schema/dataset.schema.json).
2. **How to show the forecast.** CPC gives nine categories per season, and
   grouping them is a sum of our own. Proposal: show CPC's categories as they
   are, with a legend of their ranges.
3. **The map.** Whether it fits in v0.1 without MapLibre. A spike measures how
   heavy a grid cut to Peru's region is.
4. **The Niño region of panel 2.** Proposal: Niño 1+2 as the main series, Niño
   3.4 as the reference, the other two in the technical details.
5. **Owners.** Data, Web and Content have none
   ([D-003](docs/decisions.md#d-003--team-split)).

## Decisions awaiting acceptance

All eight are 🟡 Proposed in [`docs/decisions.md`](docs/decisions.md).

- [ ] D-001 first goal: the ONI
- [ ] D-002 end-of-month scope
- [ ] D-003 team split
- [ ] D-004 marimo notebooks (partly superseded by D-006)
- [ ] D-005 free APIs for rainfall and rivers
- [ ] D-006 the pipeline is a package
- [ ] D-007 v0.1 is one page made of panels
- [ ] D-008 registry and schema
