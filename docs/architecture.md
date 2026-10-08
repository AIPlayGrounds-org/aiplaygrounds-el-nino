# Architecture

WawaPacha is a Python ingestion pipeline and a Nuxt static site. They meet at
published JSON files and the schema that describes them. There is no runtime
backend.

```text
public source
  → pipeline source module
  → schema validation
  → data branch/<id>.json
  → deploy overlay
  → web/ Nuxt generate
  → GitHub Pages
```

[`data-workflow.md`](data-workflow.md) covers the scheduled steps in this path.

## Code map

| Path                                                          | Owns                                                                                                           |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`sources.toml`](../sources.toml)                             | The source registry: identity, provenance, update class, source notes and site-page ownership.                 |
| [`schema/dataset.schema.json`](../schema/dataset.schema.json) | The published JSON contract. The pipeline validates against it and the web generates TypeScript types from it. |
| [`pipeline/`](../pipeline/)                                   | The uv package that reads or downloads inputs, validates them and publishes JSON.                              |
| [`notebooks/`](../notebooks/)                                 | marimo notebooks that walk through a source's steps. They import the pipeline and publish nothing.             |
| [`data/`](../data/)                                           | Seed JSON on `main`. Deploy overlays it with the latest JSON from the `data` branch when that branch exists.   |
| [`web/`](../web/)                                             | The Nuxt 4 static site: server-side dataset loader, page shaping, charts and accessible table fallbacks.       |
| [`docs/`](README.md)                                          | This documentation. [`sources.md`](sources.md) is the generated, source-specific reference.                    |
| [`.github/workflows/`](../.github/workflows/)                 | CI, the daily data update, the freshness check and the GitHub Pages deployment.                                |
| [`mise.toml`](../mise.toml)                                   | The Bun and uv versions selected for contributors.                                                             |

### Pipeline

| Path                                                                               | Owns                                                                                                                                                      |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py)                    | Loads and validates `sources.toml`, holds the cadence rules, then imports the module named by each automatable id.                                        |
| [`contract.py`](../pipeline/src/wawapacha_pipeline/contract.py)                    | Validates a dataset against the schema and replaces the destination JSON atomically.                                                                      |
| [`sources/`](../pipeline/src/wawapacha_pipeline/sources/)                          | One module per published source. Most download their input. `enfen_communique.py` and `senamhi_estaciones.py` read checked-in files instead.              |
| [`catalog.py`](../pipeline/src/wawapacha_pipeline/catalog.py)                      | Renders [`sources.md`](sources.md) and [`source-catalog.json`](../web/app/data/source-catalog.json) from the registry.                                    |
| [`cli.py`](../pipeline/src/wawapacha_pipeline/cli.py)                              | The `wawapacha-pipeline` commands `run`, `due`, `freshness` and `sources`.                                                                                |
| [`tests/`](../pipeline/tests/)                                                     | Source behavior, checked against real input samples in `tests/samples/`. No test needs the network.                                                       |
| [`scripts/build_chirps_baseline.py`](../pipeline/scripts/build_chirps_baseline.py) | Builds the checked-in CHIRPS 1991–2020 department climatology, [`chirps_baseline.json`](../pipeline/src/wawapacha_pipeline/sources/chirps_baseline.json). |

A source id maps to its module:
`sources/<id with hyphens replaced by underscores>.py`. Discovery requires the
module to define `ID`, `fetch`, `parse` and `run`, and `ID` must equal the
registry id. The ids are listed in [`sources.md`](sources.md).

`CADENCE_RULES` in
[`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py) are the cadence
rules. `due` and `freshness` apply them to published timestamps, and the web
catalog carries each source's stale limit, and the server loader adds it to the
dataset, so the site applies the same rule.
[`data-workflow.md`](data-workflow.md) and [`freshness.md`](freshness.md)
describe what runs them.

### Web

| Path                                                                            | Owns                                                                                                                                               |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`pages/`](../web/app/pages/)                                                   | One file per public route. The route list is [`shared/site.ts`](../web/shared/site.ts).                                                            |
| [`server/utils/loadDataset.ts`](../web/server/utils/loadDataset.ts)             | Loads the datasets listed in the source catalog, validates them against the schema and adds each source's stale limit.                             |
| [`composables/useDataset.ts`](../web/app/composables/useDataset.ts)             | The page-facing loader. `useDataset(id, shape?)` hydrates from the Nuxt payload. `shape` runs on the server before serialization.                  |
| [`composables/useSourceCatalog.ts`](../web/app/composables/useSourceCatalog.ts) | Reads the generated source catalog and gets each source's `ingestion_time` through the dataset loader.                                             |
| [`data/source-catalog.json`](../web/app/data/source-catalog.json)               | Generated registry facts, labelled page ownership and each source's stale limit.                                                                   |
| [`utils/freshness.ts`](../web/app/utils/freshness.ts)                           | Decides whether a dataset is stale, from its `ingestion_time`, the stale limit the loader added and the date of its last record.                   |
| [`utils/sourceCatalog.ts`](../web/app/utils/sourceCatalog.ts)                   | Validates and shapes the generated source catalog.                                                                                                 |
| [`components/ChartShell.vue`](../web/app/components/ChartShell.vue)             | The shared chart frame. See [`chart-rules.md`](chart-rules.md).                                                                                    |
| [`composables/useChartTheme.ts`](../web/app/composables/useChartTheme.ts)       | Reads chart colors and font from CSS variables and refreshes them when the system color scheme changes.                                            |
| [`composables/useSiteSeo.ts`](../web/app/composables/useSiteSeo.ts)             | Canonical, Open Graph and Twitter metadata. See [`seo.md`](seo.md).                                                                                |
| [`messages.ts`](../web/app/messages.ts)                                         | Spanish product copy and the `data_type` label map.                                                                                                |
| [`utils/format.ts`](../web/app/utils/format.ts)                                 | Shared Spanish number and date formatting, including Lima time and river-discharge precision.                                                      |
| [`types/dataset.ts`](../web/app/types/dataset.ts)                               | TypeScript types generated from the schema, plus the id-to-record map built from the source catalog. Regenerate it with `bun run types` in `web/`. |
| [`types/datasets.ts`](../web/app/types/datasets.ts)                             | The dataset types the loader and page shapes use, built on the generated map.                                                                      |
| [`scripts/`](../web/scripts/)                                                   | The `check:seo`, `check:budget` and `update:budget` commands. See [`seo.md`](seo.md) and [`performance.md`](performance.md).                       |
| [`test/`](../web/test/)                                                         | Behavior and type tests for the loader, shaping functions, chart shell and page data.                                                              |

## Dataset loading and page payloads

The browser receives only the static JSON that Nuxt puts in the page payload.
The server loader reads one dataset by id from `data/`, validates it against
[`dataset.schema.json`](../schema/dataset.schema.json), and `useDataset` can
reduce it before hydration:

```ts
const oni = await useDataset("noaa-cpc-oni");
const oisst = await useDataset("noaa-oisst", cropOisst);
```

The shaped value is what Nuxt serializes into `_payload.json`. These routes
shape their datasets:

| Route         | Server-side shaping                                                                                                                             |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `/`           | Crops the OISST grid to the map window. The ONI, weekly indices, communiqué and outlook use the records their panels read.                      |
| `/territorio` | Keeps department geometry, the latest CHIRPS record per department, and ERA5 department totals plus the first and last source records.          |
| `/historico`  | Keeps tagged ERSST event records and the current year, matching ONI windows, the two SENAMHI rain event windows and each station's latest year. |
| `/rios`       | Keeps the river fields used by the chart and orders records by point and date.                                                                  |

[`performance.md`](performance.md) covers the route size budget. It is separate
from the 200 KiB gzip limit (`MAX_GZIP_BYTES`) that
[`limites_inei_ign.py`](../pipeline/src/wawapacha_pipeline/sources/limites_inei_ign.py)
and
[`open_meteo_era5.py`](../pipeline/src/wawapacha_pipeline/sources/open_meteo_era5.py)
apply to their published JSON.

## Boundaries

- **Pipeline and web meet at published JSON and the schema.** Neither imports
  the other. Deploy overlays the `data` branch before `nuxt generate`.
- **The registry holds source facts.** Source modules read them through
  `registry.get()` and add only source-specific parsing and validation. The
  `[routes]` table in `sources.toml` holds the label of each site route that
  `site_pages` uses.
- **Notebooks hold no pipeline logic.**
  [`test_notebooks.py`](../pipeline/tests/test_notebooks.py) rejects functions
  and classes outside marimo cells and runs the ONI notebook against a sample
  without publishing.
- **Invalid data is not published.** Schema validation runs before the atomic
  replacement, so a failed run leaves the previous JSON in place.
- **The web has one dataset entry point.** Pages call `useDataset`. Components
  receive datasets as props.
- **Charts share one provenance frame.** `ChartShell` prints the variable, unit,
  period, data type, source and update age. Chart-specific controls and
  explanations stay in the page or panel.
