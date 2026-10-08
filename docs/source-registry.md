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
2. From `pipeline/`, create the module and its test:

   ```sh
   uv run wawapacha-pipeline new-source <id>
   ```

   It writes `sources/<module>.py` and `tests/test_<module>.py`, where
   `<module>` is the id with hyphens replaced by underscores. It reads the
   provenance with `registry.get(ID)` and leaves `parse` to write. Follow
   [`noaa_cpc_oni.py`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py).
   Discovery imports the module by name, so no dispatcher needs editing.

3. From `pipeline/`, run `uv run wawapacha-pipeline sources` to regenerate
   [`sources.md`](sources.md) and
   [`source-catalog.json`](../web/app/data/source-catalog.json).
4. If the records have source-specific fields, add a record definition and an
   `allOf` rule for the id to
   [`schema/dataset.schema.json`](../schema/dataset.schema.json). Without a rule
   the records use the generic `DatasetRecord`. Then run `bun run types` in
   `web/`. It reads the ids from the catalog and the record types from the
   schema, so the page code needs no id list.
5. Save a real copy of the original input as
   `pipeline/tests/samples/<module>.txt`, the path the generated test reads.
6. Complete `tests/test_<module>.py`: add the parser's rejection cases. Use
   [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py) as the
   model.
7. Add a notebook in `notebooks/` that imports the module and shows its steps.
   Open it from `pipeline/` with `uv run marimo edit ../notebooks/<module>.py`.
   [`test_notebooks.py`](../pipeline/tests/test_notebooks.py) fails if a
   notebook defines a function or class outside a marimo cell, and it fails if
   no test runs the notebook. `ENVIRONMENTS` there maps a notebook stem to the
   environment variables that point its source at a sample, so add your
   notebook's entry. `open_meteo_era5` is the special case: its test runs the
   notebook against a local server. A source that needs a fixture of its own
   lists its id in `RUN_BY_SOURCE_TEST` and runs the notebook in a
   `test_notebook_runs_to_the_end_without_publishing` test in its own test file,
   as [`test_noaa_oisst.py`](../pipeline/tests/test_noaa_oisst.py) does.
8. Run `uv run wawapacha-pipeline run <id>` in `pipeline/` to publish the first
   seed JSON. To show the dataset on a page, call `useDataset('<id>')`. The
   scheduled workflow publishes later updates to the `data` branch.

The registry loader rejects an entry with a missing or unknown field, and
discovery rejects an `automatable` entry whose module is missing or incomplete,
before any command runs. The contract the module publishes is in
[`data-contract.md`](data-contract.md).
