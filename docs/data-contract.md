# Data contract

The shape of `data/<id>.json` and the rules a dataset passes before the pipeline
publishes it. The schema is
[`schema/dataset.schema.json`](../schema/dataset.schema.json). Source-specific
access and transformation notes are in [`sources.md`](sources.md). Domain terms
are in [`concepts.md`](concepts.md).

## Published format

Each file holds one source's provenance and at least one record:

| Field                                       | Meaning                                                                                                                                                                                                     |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                        | The lowercase hyphenated id from `sources.toml`.                                                                                                                                                            |
| `source`                                    | Institution, product and download URL.                                                                                                                                                                      |
| `variable`, `unit`                          | What the data measures and its unit.                                                                                                                                                                        |
| `data_type`                                 | One of `observed` (measured or reported observation), `estimated` (model or analysis estimate), `forecast` (prediction of a future period) or `official` (an institution's official status or declaration). |
| `spatial_resolution`, `temporal_resolution` | The source's spatial and temporal resolution.                                                                                                                                                               |
| `reference_period`                          | The anomaly base period, when applicable.                                                                                                                                                                   |
| `ingestion_time`                            | The UTC or offset-aware ISO 8601 download time.                                                                                                                                                             |
| `processing_version`                        | The code version that produced the file.                                                                                                                                                                    |
| `source_revision`                           | Optional object with the upstream SHA-256 and a required `last_modified` key. `last_modified` is the HTTP `Last-Modified` value, or `null` when the upstream sends no header.                               |
| `records`                                   | A non-empty array. Every record has `start`. Interval records also have `end`. The other fields depend on the dataset id.                                                                                   |

Record dates are ISO 8601 strings: `YYYY-MM` for months and `YYYY-MM-DD` for
days. The schema defines the record fields of each dataset id, including time
series, grids, boundaries and forecast records. A new record kind needs a schema
extension in the same change as its first source.

The web labels the four `data_type` values in Spanish. Registry text fields that
the site prints stay Spanish. Code, schema keys and contract values are English.

## Provenance

An automatable dataset has an entry in [`sources.toml`](../sources.toml) and a
module under
[`pipeline/src/wawapacha_pipeline/sources/`](../pipeline/src/wawapacha_pipeline/sources/).
The module reads the entry with `registry.get()`, and the published dataset
copies the institution, product, access URL, variable, unit, data type and
resolutions from it. The entry's fields are in
[`source-registry.md`](source-registry.md).

## Publication

Source modules check the format and domain rules of their own input. Then
`contract.publish()` validates the whole dataset against the schema, writes a
temporary file in the destination directory and atomically replaces
`data/<id>.json`. A failed run leaves the previous JSON in place.

The tests run without network access. They validate the seed files, the registry
provenance and each source's failure cases against checked-in samples.

## Validation rules

Source parsers enforce these rules. Each source's tests are in
`pipeline/tests/test_<module>.py`. The names below are examples.

- **Missing values stay `null`.** An upstream sentinel such as the `-9999` of
  CHIRPS is published as `null`. A real zero is a value. See
  `test_parse_keeps_input_missing_as_null` in
  [`test_chirps.py`](../pipeline/tests/test_chirps.py) and
  `test_preserves_zero_and_null_values` in
  [`test_open_meteo_era5.py`](../pipeline/tests/test_open_meteo_era5.py) and
  [`test_open_meteo_glofas.py`](../pipeline/tests/test_open_meteo_glofas.py).
- **Time series are ordered, without gaps or duplicates.** Tests include
  `test_rejects_a_missing_month` in
  [`test_noaa_ersst.py`](../pipeline/tests/test_noaa_ersst.py),
  `test_rejects_a_missing_season` in
  [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py),
  `test_rejects_days_with_a_gap` in
  [`test_noaa_oisst.py`](../pipeline/tests/test_noaa_oisst.py) and
  `test_rejects_a_gap` in
  [`test_noaa_cpc_nino_weekly.py`](../pipeline/tests/test_noaa_cpc_nino_weekly.py).
- **Every non-null value is physically possible for its source.** Tests include
  `test_rejects_an_anomaly_out_of_range` in
  [`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py) and
  `test_aggregate_rejects_out_of_range_rainfall` in
  [`test_chirps.py`](../pipeline/tests/test_chirps.py).

## Transformation

A source module publishes source values as the upstream gives them. It may
change the file format or add an explicitly derived field, and the method goes
in the registry `notes`. If the upstream publishes an anomaly, the module uses
it as published. When the module computes a value, its method and base period go
in the registry `notes`, and `reference_period` carries the base period into the
published file. `test_build_adds_provenance_metadata` in
[`test_noaa_cpc_oni.py`](../pipeline/tests/test_noaa_cpc_oni.py) and
`test_parse_builds_records_and_calculates_anomaly` in
[`test_chirps.py`](../pipeline/tests/test_chirps.py) check this.

## Comparability

Anomalies with different base periods are comparable once the difference is
named. Observed, estimated, forecast and official values are combined with their
types labeled. [`chart-rules.md`](chart-rules.md) holds the display rules.

## Generated consumers

The web generates [`web/app/types/dataset.ts`](../web/app/types/dataset.ts) from
the schema and the source catalog. The schema's `allOf` rules assign a record
type to each id, and the catalog lists the ids. CI fails when the file is stale.
The command is in [`CONTRIBUTING.md`](../.github/CONTRIBUTING.md#checks).
