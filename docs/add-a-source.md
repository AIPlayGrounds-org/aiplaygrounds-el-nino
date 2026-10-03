# Add a source

A source is one registry entry, one module, one sample and one test.

1. **Entry.** Add a `[[source]]` to [`sources.toml`](../sources.toml) with the
   fields in [The registry](#the-registry). With the verdict `automatable`,
   every data field is required.
2. **Module.** Create `pipeline/src/wawapacha_pipeline/sources/<module>.py`,
   following
   [`noaa_cpc_oni.py`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py):
   `ID`, `fetch`, `parse`, `run`, and the provenance read with
   `registry.get(ID)`. The CLI discovers the module from the registry id; there
   is no shared dispatcher edit.
3. **Schema.** If the source's records have fields of their own, describe them
   in [`schema/dataset.schema.json`](../schema/dataset.schema.json) and run
   `bun run types` in `web/`.
4. **Sample.** Save a real copy of the original file in
   `pipeline/tests/samples/`.
5. **Test.** Add a test in `pipeline/tests/` that reads the sample, like
   [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py).
6. **Notebook.** Add a notebook in `notebooks/` that imports the module and
   shows each step. A test fails if it defines functions. Open it with
   `uv run marimo edit ../notebooks/<module>.py`, from `pipeline/`.
7. **Catalog and seed data.** From `pipeline/`, run
   `uv run wawapacha-pipeline sources` to add the source to
   [`docs/sources.md`](sources.md), then `uv run wawapacha-pipeline run <id>` to
   publish the first `data/<id>.json` seed. The scheduled workflow later
   publishes fresher JSON to the `data` branch.

[`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py) checks the entry
on load, discovers the module implied by every `automatable` id, and raises a
registry error when that module is missing or incomplete.

## The registry

[`sources.toml`](../sources.toml) is the one place that holds the facts about
each source. Leave out a field you do not know: no "unknown" and no placeholder
values. `notes` holds only what was checked and the quirks of the format.

| Field                                                           | Required      | Values                                                                                     |
| --------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------ |
| `id`                                                            | always        | Lowercase with hyphens. It names `data/<id>.json`.                                         |
| `institution`, `product`                                        | always        | Text.                                                                                      |
| `block`                                                         | always        | `ENSO`, `SST`, `Forecasts`, `Precipitation`, `Territory`, `Rivers`, `Alerts` or `History`. |
| `verdict`                                                       | always        | `automatable`, `manual`, `discard` or `pending`.                                           |
| `delivery`                                                      | always        | `v0.1`, `v0.2`, `v0.3` or `v0.4`.                                                          |
| `reviewed`                                                      | always        | The date the source was last reviewed, as `YYYY-MM-DD`.                                    |
| `page`                                                          | always        | URL of the official page.                                                                  |
| `variable`, `unit`, `spatial_resolution`, `temporal_resolution` | `automatable` | Text, in Spanish. Published as written.                                                    |
| `data_type`                                                     | `automatable` | `observed`, `estimated`, `forecast` or `official`.                                         |
| `access.url`                                                    | `automatable` | Download URL.                                                                              |
| `access.kind`, `access.format`, `access.auth`                   | optional      | Text.                                                                                      |
| `update`                                                        | always        | `daily`, `weekly`, `monthly` or `manual`; the schedule used by due selection.              |
| `history`, `cadence`, `license`                                 | optional      | Text.                                                                                      |
| `reference_period`                                              | optional      | Text, in Spanish. Published as written.                                                    |
| `notes`                                                         | optional      | A list of texts.                                                                           |

The five fields the site prints (`variable`, `unit`, both resolutions and
`reference_period`) stay in Spanish. Everything else in the registry is in
English.

A source with the verdict `automatable` must have its discovered module and gets
a section in [`docs/sources.md`](sources.md). The other entries stay in the
registry only.
