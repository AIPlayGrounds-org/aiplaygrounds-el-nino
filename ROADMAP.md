# Roadmap

Read the North star before choosing work. It defines the target architecture
while the repository converges on it.

## North star

```text
sources.toml → source module → schema validation → data branch/<id>.json
       └────────────── update-data.yml ──────────────┘
                                      ↓ overlay during deploy
                         main's data/ → Nuxt 4 static site → GitHub Pages
```

- `sources.toml` is the single registry. One module per automatable source is
  discovered from the registry id.
- Every dataset passes `schema/dataset.schema.json` before it is written to the
  published data directory as `<id>.json`. A failure keeps the previous file.
- `update-data.yml` runs daily, asks `wawapacha-pipeline due` against the
  published data directory, runs only due sources with per-source failure
  isolation, commits changed JSON to the `data` branch, then dispatches
  `deploy.yml`.
- The browser never calls an upstream API. The `data` branch keeps published
  JSON off `main`; sub-daily sources may later use a Cloudflare cron writing to
  R2 or KV.
- The web is a Nuxt 4 static site. `/` is the v0.1 one-page essay of panels and
  grows into Territorio, Histórico, Pronósticos, Alertas, Aprende and
  Metodología.
- Each panel reads exactly one dataset through one typed loader and renders in
  one shared chart shell. The shell prints variable, unit, period, data type,
  source and last update from the provenance block.
- The `data_type` to Spanish label map exists once. All Spanish copy sits in one
  messages module prepared for i18n.
- Charts and maps are ECharts. Types are generated from the schema.
- Time series, grids (20°N–25°S and 120°W–60°W, two-decimal rounded JSON served
  gzip) and geometry (simplified GeoJSON) are the three dataset kinds. A new
  kind needs a schema extension in the same PR as its first source.
- Observed, estimated, forecast and official stay visibly apart. A stale source
  keeps its last value and shows its age. Alerts link to the official source.
- WawaPacha makes no home-made index, threshold or traffic light.
- The AI summary, when it ships, cites source, variable, date and value, is
  reviewed by a person, and never invents causes, forecasts, alerts or risk.
- Quality means pytest with real samples and no network; every `data/` file is
  validated against the schema; generated files are checked in CI; the web has a
  build and typecheck; and the site is WCAG 2.1 AA, mobile first, light and
  dark.
- The documentation set is the one in this tree. Every rule lives in one file;
  there is no decision log and no working notes.

## Stages

| Stage                         | Scope                                                                                                                                                                                                                                                                        | Exit criteria                                                            | State                                                                                      | Target            |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ----------------- |
| 0 Foundations                 | Layout, registry, schema, CI, deploy, scheduled ingestion, contract v2                                                                                                                                                                                                       | On `main`                                                                | Done                                                                                       | Done (2026-10-02) |
| 1 Sources wave 1              | `noaa-cpc-nino-weekly`, `noaa-cpc-outlook`, `enfen-communique`, `noaa-oisst`, `noaa-ersst`, `limites-inei-ign`, `open-meteo-glofas`: module, notebook, tests with samples, one real committed `data/<id>.json`, registry entry set to `automatable`                          | Each merged; `update-data.yml` run by hand once with the new sources     | Implemented on `main`; a live scheduled run is not evidenced in this tree                  | 2026-10-09        |
| 2 Web foundation              | Typed dataset loader, shared chart shell with provenance, label map and messages module, test fixtures for every dataset kind                                                                                                                                                | `/` renders the ONI through the shell; no panel reads JSON any other way | Done                                                                                       | 2026-10-09        |
| 3 v0.1 panels                 | Panels 2 to 5 and 7 from the panel table                                                                                                                                                                                                                                     | All seven panels on real data; every number shows its provenance         | Done                                                                                       | 2026-10-16        |
| 4 v0.2 rainfall and territory | `chirps` by department using the boundaries; `open-meteo-era5` as the cross-check; Territorio page with a department choropleth                                                                                                                                              | Page live; both sources scheduled                                        | Done                                                                                       | 2026-10-21        |
| 5 v0.3 rivers and alerts      | GloFAS panel marked model-estimated; alerts as links to SENAMHI and ENFEN (no scraping of avisos unless terms allow it); `senamhi-avisos` stays out                                                                                                                          | Page live                                                                | Done                                                                                       | 2026-10-24        |
| 6 v0.4 history                | Histórico page with the 1982–83, 1997–98 and 2017 events from `noaa-ersst`                                                                                                                                                                                                   | Page live                                                                | Done                                                                                       | 2026-10-24        |
| 7 Content and compliance      | Attribution and reviewed terms for every source; Aprende and Metodología; emails to IGP/ENFEN, SENAMHI, ANA, DHN and INAIGEM; AI summary only if a person reviews it. Open-Meteo says “Weather data by Open-Meteo.com”, credits Copernicus, and remains non-commercial only. | Every published source has attribution on the page                       | Partial: page attribution is implemented; outreach and license confirmation remain pending | 2026-10-27        |
| 8 Hardening and release       | Accessibility, mobile and dark mode, performance, SEO, error and empty states, freshness check, final docs pass                                                                                                                                                              | Freeze 2026-10-28; release 2026-10-31                                    | In progress: gates are implemented; freeze and release are still ahead                     | 2026-10-31        |

### v0.1 panel table

The page `/` keeps asking the seven questions below. Each panel has one dataset
and prints that dataset's provenance.

| Panel | Question                              | Dataset id                                     | Status |
| ----- | ------------------------------------- | ---------------------------------------------- | ------ |
| 1     | ¿Llegó El Niño?                       | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built  |
| 2     | ¿Cómo está el mar frente al Perú?     | `noaa-cpc-nino-weekly`                         | Built  |
| 3     | ¿Qué dice el estado oficial del Perú? | `enfen-communique`                             | Built  |
| 4     | ¿Qué esperan los pronósticos?         | `noaa-cpc-outlook`                             | Built  |
| 5     | ¿Dónde está más caliente el mar?      | `noaa-oisst`                                   | Built  |
| 6     | Explora la serie histórica            | [`noaa-cpc-oni`](docs/sources.md#noaa-cpc-oni) | Built  |
| 7     | Cómo lo hicimos                       | Provenance of each dataset                     | Built  |

### Held sources

These entries remain in `sources.toml` but are not published on a site page or
are still waiting for a verified access decision:

- `copernicus-ostia`: programmatic access needs a Copernicus Marine account and
  the product has no anomaly, so it is not comparable with OISST.
- `ecmwf-seas5`: the dataset, variable and region are not set, and access needs
  a Climate Data Store key.
- `dhn-boletines`: the source is manual monthly PDFs whose variable and base
  period must be read from each edition.
- `iri-enso-pluma` (retired): the page no longer provides forecast values, only
  charts.
- `senamhi-pisco`: the product is manual GeoTIFF precipitation data; its
  geographic aggregation and delivery path are not yet verified.
- `nasa-imerg`: NASA PPS access needs registration and the Early, Late and Final
  products require a choice of latency and calibration.
- `senamhi-hidro`: no download was tested and no series format was verified.
- `ana-snirh` and `ana-alertas`: no verified structured river series or national
  alert feed is available; the institutional reply is pending.
- `inaigem`: there is no uniform national alert product and an open layer
  download was not confirmed.
- `indeci-coen`: the source is manual narrative reports, mostly PDFs, whose
  figures change between preliminary and complementary reports.

The registry also keeps `bom-enso` and `enfen-forecast` as discarded entries.
Their reasons are in the generated [source catalog](docs/sources.md).

## Merge plan

1. Work happens in stacked branches. A task branches from `main`, or from the
   open branch it depends on, and says so in its PR.
2. Before a PR is ready, it is rebased on `main`; generated files are
   regenerated, never hand-merged (take `main`'s version, then run the
   generator); CI is green; and both gates passed on the final head.
3. `main` needs one approving review. Use merge commits only, signed, never
   squash, so every stacked commit keeps its signature.
4. Merge stage 1 by conflict risk: `limites-inei-ign` first (it may extend the
   schema), then `noaa-cpc-nino-weekly`, `noaa-cpc-outlook`, `enfen-communique`,
   `noaa-oisst`, `noaa-ersst`, `open-meteo-glofas`. After each merge the next
   branch is rebased and its generated files regenerated.
5. Merge in batches once approval exists, not one at a time, then run
   `update-data.yml` by hand once and confirm `deploy.yml` follows.
6. Web tasks start from fixtures, so they never wait on a data PR; they merge
   after the dataset they read is on `main`.
7. Ownership: Data owns `sources.toml`, `schema/`, `pipeline/`, `notebooks/`,
   `data/`. Web owns `web/`. Content owns the Spanish copy and the documents.
   Names for the three owners are the one open question.
8. Conflict hotspots: `docs/sources.md` and `web/app/types/dataset.ts`
   (generated), `schema/dataset.schema.json` (one PR at a time), and
   `sources.toml` (one entry per source, so it rebases cleanly).

## Out of scope

Accounts and login, favorites, push notifications, a public API, our own CSV or
JSON downloads, global search, district level, our own predictive models, a
model consensus, and agriculture, fishing, health or infrastructure modules.
