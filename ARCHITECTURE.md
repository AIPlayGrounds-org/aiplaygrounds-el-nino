# Architecture

A data pipeline and a static site. There is no backend. This document is the
code map: what each directory does and which boundaries the code keeps. The
target architecture and unbuilt work live in [`ROADMAP.md`](ROADMAP.md).

```text
public source
  → pipeline/        downloads, validates and publishes (wawapacha-pipeline run <id>)
  → data/<id>.json   data and provenance
  → web/             nuxt generate reads data/ at build time
  → GitHub Pages
```

## Code map

| Path                                                       | Job                                                                                                                         |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [`sources.toml`](sources.toml)                             | The registry. Holds the facts about each source: institution, URL, variable, unit, verdict. It is the only place they live. |
| [`schema/dataset.schema.json`](schema/dataset.schema.json) | The contract of the published JSON. The pipeline validates against it and the web generates its types from it.              |
| [`pipeline/`](pipeline/)                                   | A Python package (uv). Downloads, validates and publishes.                                                                  |
| [`notebooks/`](notebooks/)                                 | One marimo notebook per source. Imports the package and shows each step. Never writes to `data/`.                           |
| [`data/`](data/)                                           | One JSON per source. If a download fails validation, the previous file stays.                                               |
| [`web/`](web/)                                             | The web app: Nuxt 4 and Vue, with Bun. The current ONI chart uses ECharts (`vue-echarts`).                                  |
| [`docs/`](docs/README.md)                                  | Chart rules, data contract, concepts, source workflow and the source catalog.                                               |
| [`.github/workflows/`](.github/workflows/)                 | `ci.yml` checks every PR. `deploy.yml` publishes `web/` to GitHub Pages on every push to `main`.                            |
| [`mise.toml`](mise.toml)                                   | Pins the Bun and uv versions.                                                                                               |

### `pipeline/src/wawapacha_pipeline/`

| Module                                                       | Job                                                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| [`registry.py`](pipeline/src/wawapacha_pipeline/registry.py) | Loads and validates `sources.toml`. The only loader of the registry.                 |
| [`contract.py`](pipeline/src/wawapacha_pipeline/contract.py) | Validates a dataset against the schema and publishes it to `data/` atomically.       |
| [`sources/`](pipeline/src/wawapacha_pipeline/sources/)       | One module per source. Downloads, parses and builds the dataset from registry facts. |
| [`catalog.py`](pipeline/src/wawapacha_pipeline/catalog.py)   | Generates [`docs/sources.md`](docs/sources.md) from the registry.                    |
| [`cli.py`](pipeline/src/wawapacha_pipeline/cli.py)           | `wawapacha-pipeline run <id>`, `due` and `sources`.                                  |

### `web/app/`

| Path                                           | Job                                                     |
| ---------------------------------------------- | ------------------------------------------------------- |
| [`pages/index.vue`](web/app/pages/index.vue)   | The `/` page. Reads the ONI JSON and builds the panels. |
| [`components/`](web/app/components/)           | The ONI charts.                                         |
| [`utils/enso.ts`](web/app/utils/enso.ts)       | ENSO phases and ONI dates.                              |
| [`types/dataset.ts`](web/app/types/dataset.ts) | Types for the JSON. **Generated**: do not edit.         |

## Boundaries

- **`pipeline/` and `web/` meet only at `data/` and the schema.** The web does
  not import pipeline code, and the pipeline does not import web code. Whoever
  works on the web can use test data that satisfies the schema while the
  pipeline finishes a source. The JSON contract lets the Data and Web
  workstreams move independently.
- **A source's facts live only in `sources.toml`.** A module in `sources/` reads
  them from the registry and does not repeat them. A test checks that the
  published JSON matches its entry.
- **One module per automatable source.** Discovery maps each automatable
  registry id to `sources/<id with hyphens replaced by underscores>.py`. A
  registry check fails when the module is missing or does not expose `ID`,
  `fetch`, `parse` and `run`. Discovery keeps source work isolated and avoids a
  shared dispatcher that every source branch must edit.
- **Nothing is published without passing the schema.** `contract.publish()`
  validates before it writes. If validation fails, the previous JSON stays in
  `data/`.
- **Notebooks hold no logic.** They import the package. A test fails if a
  notebook defines a function or a class. Production does not depend on marimo,
  while contributors can still inspect each pipeline step.
- **Two files are generated, and CI fails when they are stale:**
  `docs/sources.md` (`uv run wawapacha-pipeline sources`, from `pipeline/`) and
  `web/app/types/dataset.ts` (`bun run types`, from `web/`).
- **A failing source does not hide its data.** The previous JSON stays, with its
  ingestion time, and the page shows its age
  ([`web/app/pages/index.vue`](web/app/pages/index.vue)).
- **No backend.** There are no accounts, no public API and no downloads of our
  own. Static JSON keeps visitor traffic independent of upstream availability
  and rate limits.
- **The browser loads only our JSON.** Scheduled ingestion fetches upstream
  sources and publishes due datasets before the static site build, so visitor
  traffic never calls an upstream API.
- **ECharts is the current chart renderer.** The planned v0.1 map's grid and
  serving rules are in [`ROADMAP.md`](ROADMAP.md), not duplicated here.
