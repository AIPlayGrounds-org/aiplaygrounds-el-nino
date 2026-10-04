# Add a source

A source consists of one registry entry, one discovered module, a checked-in
sample, tests and a notebook. The contract and generated-file rules are in
[`data-contract.md`](data-contract.md).

1. Add a `[[source]]` entry to [`sources.toml`](../sources.toml). Use the fields
   in [The registry](#the-registry), and provide all data fields for an
   `automatable` source.
2. Create `pipeline/src/wawapacha_pipeline/sources/<module>.py`, following
   [`noaa_cpc_oni.py`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py).
   Expose `ID`, `fetch`, `parse` and `run`, and read registry provenance with
   `registry.get(ID)`. Discovery derives the module name from the id, so no
   shared dispatcher needs editing.
3. If the records need source-specific fields, add them to
   [`schema/dataset.schema.json`](../schema/dataset.schema.json), then run
   `bun run types` from `web/` to regenerate the TypeScript types.
4. Save a real copy of the original input in `pipeline/tests/samples/`.
5. Add behavior tests in `pipeline/tests/` that read the sample and cover the
   parser's rejection cases. Use
   [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py) as the
   example.
6. Add a notebook in `notebooks/` that imports the module and shows its steps.
   Open it with `uv run marimo edit ../notebooks/<module>.py` from `pipeline/`.
   [`test_notebooks.py`](../pipeline/tests/test_notebooks.py) checks that
   notebooks define no pipeline functions or classes and that the example runs
   to completion without publishing.
7. From `pipeline/`, run `uv run wawapacha-pipeline sources` to regenerate
   [`docs/sources.md`](sources.md). Run `uv run wawapacha-pipeline run <id>` to
   publish the first seed JSON. The scheduled workflow later publishes newer
   JSON to the `data` branch.

The registry loader checks the entry, discovers every automatable module and
rejects a missing or incomplete module before the CLI starts.

## The registry

[`sources.toml`](../sources.toml) is the one place for source facts. Leave out a
field you do not know. Do not use `unknown` or placeholder values. `notes` is
for checked format quirks and source-specific processing facts.

| Field                                                           | Required    | Values                                                                                     |
| --------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------ |
| `id`                                                            | always      | Lowercase with hyphens. It names `data/<id>.json`.                                         |
| `institution`, `product`                                        | always      | Text.                                                                                      |
| `block`                                                         | always      | `ENSO`, `SST`, `Forecasts`, `Precipitation`, `Territory`, `Rivers`, `Alerts` or `History`. |
| `verdict`                                                       | always      | `automatable`, `manual`, `discard` or `pending`.                                           |
| `delivery`                                                      | always      | `v0.1`, `v0.2`, `v0.3` or `v0.4`.                                                          |
| `reviewed`                                                      | always      | `YYYY-MM-DD`.                                                                              |
| `page`                                                          | always      | URL of the official page.                                                                  |
| `variable`, `unit`, `spatial_resolution`, `temporal_resolution` | automatable | Text, in Spanish. Published as written.                                                    |
| `data_type`                                                     | automatable | `observed`, `estimated`, `forecast` or `official`.                                         |
| `access.url`                                                    | automatable | Download URL.                                                                              |
| `access.kind`, `access.format`, `access.auth`                   | optional    | Text.                                                                                      |
| `update`                                                        | always      | `daily`, `weekly`, `monthly` or `manual`; used by due selection.                           |
| `history`, `cadence`, `license`                                 | optional    | Text.                                                                                      |
| `reference_period`                                              | optional    | Text, in Spanish. Published as written.                                                    |
| `notes`                                                         | optional    | A list of checked facts.                                                                   |

The fields that the site prints (`variable`, `unit`, `temporal_resolution` and
`reference_period`) remain in Spanish. `spatial_resolution` is part of the
published contract but is not printed by `ChartShell`. Other registry prose is
in English.

An automatable entry must have its discovered module and receives a section in
the generated [source catalog](sources.md). Manual, discarded and pending
entries remain in the registry without a generated dataset section.
