# Add a source

A source is one registry entry, one module, one sample and one test.

1. **Entry.** Add a `[[source]]` to [`sources.toml`](../sources.toml) with the
   fields in [The registry](#the-registry). With the verdict `automatable`,
   every data field is required.
2. **Module.** Create `pipeline/src/wawapacha_pipeline/sources/<module>.py`,
   following
   [`noaa_cpc_oni.py`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py):
   `ID`, `parse`, `build`, and the provenance read with `registry.get(ID)`.
   Register it in `SOURCES`, in
   [`cli.py`](../pipeline/src/wawapacha_pipeline/cli.py).
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
7. **Catalog and data.** From `pipeline/`, run
   `uv run wawapacha-pipeline sources` to add the source to
   [`docs/sources.md`](sources.md), then `uv run wawapacha-pipeline run <id>` to
   publish `data/<id>.json`.

[`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py) checks the entry
on load, and a test checks that every module in `SOURCES` has an `automatable`
entry.

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
| `data_type`                                                     | `automatable` | One of the values in [the contract](data-contract.md#4-published-format).                  |
| `access.url`                                                    | `automatable` | Download URL.                                                                              |
| `access.kind`, `access.format`, `access.auth`                   | optional      | Text.                                                                                      |
| `history`, `cadence`, `license`                                 | optional      | Text.                                                                                      |
| `reference_period`                                              | optional      | Text, in Spanish. Published as written.                                                    |
| `notes`                                                         | optional      | A list of texts.                                                                           |

The five fields the site prints (`variable`, `unit`, both resolutions and
`reference_period`) stay in Spanish. Everything else in the registry is in
English.

A source with the verdict `automatable` and a module in `SOURCES` gets a section
in [`docs/sources.md`](sources.md). The other entries stay in the registry only.
