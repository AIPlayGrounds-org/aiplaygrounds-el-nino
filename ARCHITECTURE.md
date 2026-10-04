# Architecture

WawaPacha is a Python ingestion pipeline and a Nuxt static site. There is no
runtime backend. The target architecture and work that is not built yet live in
[`ROADMAP.md`](ROADMAP.md).

```text
public source
  → pipeline source module
  → schema validation
  → data branch/<id>.json
  → deploy overlay
  → web/ Nuxt generate
  → GitHub Pages
```

## Code map

| Path                                                       | Owns                                                                                                                         |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [`sources.toml`](sources.toml)                             | The source registry: identity, provenance, update class, delivery stage, source notes and site-page ownership.               |
| [`schema/dataset.schema.json`](schema/dataset.schema.json) | The published JSON contract. The pipeline validates against it and the web generates TypeScript types from it.               |
| [`pipeline/`](pipeline/)                                   | The uv package that discovers source modules, downloads or reads inputs, validates source-specific rules and publishes JSON. |
| [`notebooks/`](notebooks/)                                 | One inspection notebook per automatable source. Notebooks import the pipeline and do not publish data themselves.            |
| [`data/`](data/)                                           | Seed JSON on `main`. Deploy overlays it with the latest JSON from the `data` branch when that branch exists.                 |
| [`web/`](web/)                                             | The Nuxt 4 static site, its server-side dataset loader, page-specific shaping, charts and accessible fallbacks.              |
| [`docs/`](docs/README.md)                                  | The documentation set. The generated source catalog is the source-specific reference.                                        |
| [`.github/workflows/`](.github/workflows/)                 | CI, the daily data update, and the GitHub Pages deployment.                                                                  |
| [`mise.toml`](mise.toml)                                   | The pinned Bun and uv versions used by contributors.                                                                         |

### Pipeline

| Path                                                         | Owns                                                                                                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [`registry.py`](pipeline/src/wawapacha_pipeline/registry.py) | Loads and validates `sources.toml`, then discovers the module named by each automatable id.                                                |
| [`contract.py`](pipeline/src/wawapacha_pipeline/contract.py) | Validates a dataset against the schema and replaces the destination JSON atomically after validation succeeds.                             |
| [`sources/`](pipeline/src/wawapacha_pipeline/sources/)       | One module per automatable source. Each module fetches, parses, builds and publishes its dataset; [`enfen_icen.py`](pipeline/src/wawapacha_pipeline/sources/enfen_icen.py) publishes the official monthly ICEN table. |
| [`catalog.py`](pipeline/src/wawapacha_pipeline/catalog.py)   | Renders [`docs/sources.md`](docs/sources.md) and [`web/app/data/source-catalog.json`](web/app/data/source-catalog.json) from the registry. |
| [`cli.py`](pipeline/src/wawapacha_pipeline/cli.py)           | Provides `run`, `due`, `freshness` and `sources`. `due` and `freshness` apply the registry update class to published JSON timestamps.      |

The scheduled [`update-data.yml`](.github/workflows/update-data.yml) runs once a
day. It asks `due` for missing or old daily, weekly and monthly datasets, skips
manual entries, runs selected sources independently, and publishes changed JSON
to the `data` branch. Only when changed JSON is committed and pushed does the
workflow dispatch [`deploy.yml`](.github/workflows/deploy.yml). The registry's
`update` field and the generated [source catalog](docs/sources.md) own each
source's cadence and cadence notes.

The scheduled [`freshness.yml`](.github/workflows/freshness.yml) runs the
`wawapacha-pipeline freshness` command against the published files. It reuses
the registry cadence schedule, but its independent tolerance is two nominal
cadence intervals plus slack: 52 hours for daily, 15 days for weekly, and 63
days for monthly. Those values live with the due thresholds in
`pipeline/src/wawapacha_pipeline/cli.py`. It compares the published file's
`ingestion_time`; a stale result fails this separate workflow and
therefore does not block deploys.

### Web

| Path                                                                             | Owns                                                                                                                              |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`pages/index.vue`](web/app/pages/index.vue)                                     | The home page: ONI, weekly Niño indices, the ENFEN communiqué, CPC probabilities and the OISST map.                               |
| [`pages/territorio.vue`](web/app/pages/territorio.vue)                           | The department rainfall map and its ERA5 cross-check.                                                                             |
| [`pages/historico.vue`](web/app/pages/historico.vue)                             | The comparison of current and tagged historical events.                                                                           |
| [`pages/rios.vue`](web/app/pages/rios.vue)                                       | The modeled river-discharge series and official alert links.                                                                      |
| [`pages/aprende.vue`](web/app/pages/aprende.vue)                                 | The Spanish explainer for ENSO, Niño regions, ONI and the Peruvian coast.                                                         |
| [`pages/metodologia.vue`](web/app/pages/metodologia.vue)                         | The generated source catalogue and data-type explanations.                                                                        |
| [`server/utils/loadDataset.ts`](web/server/utils/loadDataset.ts)                 | The static dataset catalog and server-side schema validation.                                                                     |
| [`composables/useDataset.ts`](web/app/composables/useDataset.ts)                 | The page-facing loader. `useDataset(id, shape?)` hydrates from the Nuxt payload; `shape` runs on the server before serialization. |
| [`composables/useSourceCatalog.ts`](web/app/composables/useSourceCatalog.ts)     | Reads the generated source catalogue and gets each source's `ingestion_time` through the dataset loader.                          |
| [`data/source-catalog.json`](web/app/data/source-catalog.json)                   | Generated registry facts and labelled page ownership for the methodology catalogue.                                               |
| [`composables/useChartTheme.ts`](web/app/composables/useChartTheme.ts)           | Reads chart colors and font from CSS variables and refreshes them when the system color scheme changes.                           |
| [`utils/format.ts`](web/app/utils/format.ts)                                     | Shared Spanish number and date formatting, including Lima time and river-discharge precision.                                     |
| [`utils/sourceCatalog.ts`](web/app/utils/sourceCatalog.ts)                       | Validates and shapes the generated source catalogue used by Metodología.                                                          |
| [`composables/useSiteSeo.ts`](web/app/composables/useSiteSeo.ts)                 | Shared canonical, Open Graph and Twitter metadata, using page copy from `messages.ts`.                                            |
| [`server/routes/sitemap.xml.ts`](web/server/routes/sitemap.xml.ts)               | Generates the sitemap from the public route list during static generation.                                                        |
| [`server/routes/robots.txt.ts`](web/server/routes/robots.txt.ts)                 | Generates crawler rules and links the generated sitemap.                                                                          |
| [`components/ChartShell.vue`](web/app/components/ChartShell.vue)                 | The shared chart frame, accessible summary, provenance fields, data age and stale-source notice.                                  |
| [`components/DatasetAttribution.vue`](web/app/components/DatasetAttribution.vue) | The Open-Meteo credit and the required ERA5 or GloFAS attribution.                                                                |
| [`messages.ts`](web/app/messages.ts)                                             | Spanish product copy and the single `data_type` label map.                                                                        |
| [`types/dataset.ts`](web/app/types/dataset.ts)                                   | Schema-generated TypeScript types. **Generated:** run `bun run types` in `web/`; do not edit by hand.                             |
| [`types/datasets.ts`](web/app/types/datasets.ts)                                 | The id-to-record type map used by the loader and page shapes.                                                                     |
| [`test/`](web/test/)                                                             | Behavior and type tests for the loader, shaping functions, chart shell and page data.                                             |

## Dataset loading and page payloads

The browser receives only the static JSON that Nuxt puts in the page payload. It
does not call an upstream source. The server loader imports one dataset by id,
validates it against [`dataset.schema.json`](schema/dataset.schema.json), and
then `useDataset` optionally reduces the returned value before hydration.

| Route         | Server-side shaping                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `/`           | Crops the OISST grid to the map window. The ONI, weekly indices, communiqué and outlook use the records their panels read.             |
| `/territorio` | Keeps department geometry, the latest CHIRPS record per department, and ERA5 department totals plus the first and last source records. |
| `/historico`  | Keeps tagged ERSST event records and the current year, then keeps the matching ONI windows.                                            |
| `/rios`       | Keeps the river fields used by the chart and orders records by point and date.                                                         |

The route's shaped return value is what Nuxt serializes into its
`_payload.json`. The route byte budget and generated-output check live in
[`docs/performance.md`](docs/performance.md) and
[`web/performance-budget.json`](web/performance-budget.json). It also has
relative shaping assertions in
[`web/test/territorio.test.ts`](web/test/territorio.test.ts) and
[`web/test/rios.test.ts`](web/test/rios.test.ts). The separate 200 KiB gzip
limits enforced by some pipeline sources are source-payload limits, not route
payload limits; their current values are in the generated
[source catalog](docs/sources.md).

## Boundaries

- **Pipeline and web meet at published JSON and the schema.** Neither package
  imports the other. Deploy overlays the `data` branch before `nuxt generate`.
- **Source facts have one home.** `sources.toml` owns registry facts. Source
  modules read them through `registry.get()` and add only source-specific
  parsing and validation. Its top-level `[routes]` table owns the label for each
  site route used by `site_pages`.
- **Automatable source discovery is registry-driven.** A source id maps to
  `sources/<id with hyphens replaced by underscores>.py`; discovery requires
  `ID`, `fetch`, `parse` and `run`.
- **Notebooks hold no pipeline logic.** They import the source modules and show
  their steps. [`test_notebooks.py`](pipeline/tests/test_notebooks.py) rejects
  functions and classes outside marimo cells and checks that a notebook can run
  without publishing data.
- **Invalid data is not published.** Schema validation runs before the atomic
  replacement, so a failed run leaves the previous JSON in place.
- **The methodology catalogue is generated.** `catalog.py` writes the registry
  facts and labelled page ownership to `web/app/data/source-catalog.json`; the
  web validates it and reads each published dataset through `loadDataset` for
  its last update.
- **The web has one dataset entry point.** Pages call `useDataset`; components
  receive datasets as props and do not import `data/` directly.
- **Charts use one provenance frame.** `ChartShell` owns the variable, unit,
  period, data type, source and update age. Chart-specific controls and
  explanations stay in the page or panel.
- **Stale data remains visible.** The shell shows the latest valid record and
  its age, then links to the source when its update or record age crosses the
  current stale threshold.
- **There is no backend.** Static JSON makes visitor traffic independent of
  upstream availability and rate limits. Accounts, a public API and first-party
  downloads are outside the product boundary; the complete non-goals list is in
  [`README.md`](README.md#non-goals).

## Verification

CI runs these pipeline commands from `pipeline`:

- Ruff format check: `uv run ruff format --check .`
- Ruff lint: `uv run ruff check .`
- Tests: `uv run pytest`

It then generates `docs/sources.md` and `web/app/data/source-catalog.json` and
checks their clean diff. From `web/`, the oxfmt check is `oxfmt --check .`, also
exposed to contributors as the exact script command `bun run format:check`. CI
then regenerates the schema types, checks their clean diff and runs
`bun run generate`. The contributor-facing working-directory details are in
[`CONTRIBUTING.md`](CONTRIBUTING.md#checks).
