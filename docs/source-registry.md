# Source registry

[`sources.toml`](../sources.toml) holds the facts about every source. Source
modules, the published JSON and the generated [source catalog](sources.md) all
read them from this file. An optional field with no known value is omitted.

## Fields

Each `[[source]]` entry has these fields:

| Field                                                           | Required      | Values                                                                                     |
| --------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------ |
| `id`                                                            | always        | Lowercase with hyphens. It names `data/<id>.json`.                                         |
| `institution`, `product`                                        | always        | Text.                                                                                      |
| `block`                                                         | always        | `ENSO`, `SST`, `Forecasts`, `Precipitation`, `Territory`, `Rivers`, `Alerts` or `History`. |
| `verdict`                                                       | always        | `automatable`, `manual`, `discard` or `pending`.                                           |
| `reviewed`                                                      | always        | `YYYY-MM-DD`.                                                                              |
| `page`                                                          | always        | URL of the official page.                                                                  |
| `update`                                                        | always        | `daily`, `weekly`, `monthly` or `manual`. [Freshness](freshness.md) reads it.              |
| `site_pages`                                                    | `automatable` | Non-empty list of site routes that publish this source, such as `/` or `/rios`.            |
| `variable`, `unit`, `spatial_resolution`, `temporal_resolution` | `automatable` | Text, in Spanish. Published as written.                                                    |
| `data_type`                                                     | `automatable` | `observed`, `estimated`, `forecast` or `official`.                                         |
| `access.url`                                                    | `automatable` | Download URL.                                                                              |
| `access.kind`, `access.format`, `access.auth`                   | optional      | Text.                                                                                      |
| `history`, `cadence`, `license`                                 | optional      | Text.                                                                                      |
| `reference_period`                                              | optional      | Text, in Spanish. Published as written.                                                    |
| `notes`                                                         | optional      | A list of checked format quirks and source-specific processing facts.                      |

The `[routes]` table at the top of the file gives the Spanish label of each site
route. Add a route and its label there before you list it in a source's
`site_pages`.

`variable`, `unit`, `temporal_resolution` and `reference_period` appear on every
chart, and `spatial_resolution` appears on the methodology page. They stay in
Spanish. Other registry prose is English.

An `automatable` entry needs its module and gets a section in
[`sources.md`](sources.md) and in the web catalog. A `manual` entry with
`site_pages` has a module too: see [`manual-snapshots.md`](manual-snapshots.md).
`discard` and `pending` entries stay in the registry only.

## Add a source

1. Add a `[[source]]` entry to `sources.toml`. An `automatable` entry needs all
   the data fields in the table above.
2. Create `pipeline/src/wawapacha_pipeline/sources/<module>.py`, where
   `<module>` is the id with hyphens replaced by underscores. Follow
   [`noaa_cpc_oni.py`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py).
   Define `ID`, `fetch`, `parse` and `run`, and read the provenance with
   `registry.get(ID)`. Discovery imports the module by name, so no dispatcher
   needs editing.
3. From `pipeline/`, run `uv run wawapacha-pipeline sources` to regenerate
   [`sources.md`](sources.md) and
   [`source-catalog.json`](../web/app/data/source-catalog.json).
4. If the records have source-specific fields, add a record definition and an
   `allOf` rule for the id to
   [`schema/dataset.schema.json`](../schema/dataset.schema.json). Without a rule
   the records use the generic `DatasetRecord`. Then run `bun run types` in
   `web/`. It reads the ids from the catalog and the record types from the
   schema, so the page code needs no id list.
5. Save a real copy of the original input in `pipeline/tests/samples/`.
6. Add tests in `pipeline/tests/` that read the sample and cover the parser's
   rejection cases. Use
   [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py) as the
   model.
7. Add a notebook in `notebooks/` that imports the module and shows its steps.
   Open it from `pipeline/` with `uv run marimo edit ../notebooks/<module>.py`.
   [`test_notebooks.py`](../pipeline/tests/test_notebooks.py) fails if a
   notebook defines a function or class outside a marimo cell.
8. Run `uv run wawapacha-pipeline run <id>` in `pipeline/` to publish the first
   seed JSON. To show the dataset on a page, call `useDataset('<id>')`. The
   scheduled workflow publishes later updates to the `data` branch.

The registry loader rejects an entry with a missing or unknown field, and
discovery rejects an `automatable` entry whose module is missing or incomplete,
before any command runs. The contract the module publishes is in
[`data-contract.md`](data-contract.md).
