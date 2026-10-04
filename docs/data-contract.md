# Data contract

This document owns the shape and publication boundary of `data/<id>.json`.
Source-specific access and transformation notes live in the generated
[`sources.md`](sources.md). Domain terms are in [`concepts.md`](concepts.md).

## Registry and provenance

An automatable dataset has a matching entry in [`sources.toml`](../sources.toml)
and a discovered module under
[`pipeline/src/wawapacha_pipeline/sources/`](../pipeline/src/wawapacha_pipeline/sources/).
The module reads registry provenance through `registry.get()` and the published
dataset copies the institution, product, access URL, variable, unit, data type
and resolutions from that entry.

The registry's `update` value is one of `daily`, `weekly`, `monthly` or
`manual`. The daily workflow uses it to select due automatable datasets. The
current cadence text belongs in the generated [source catalog](sources.md).

## Validation and publication

Source modules validate the format and domain rules that are specific to their
upstream input. The shared `contract.publish()` then validates the complete
dataset against [`schema/dataset.schema.json`](../schema/dataset.schema.json),
writes a temporary file in the destination directory and atomically replaces
`data/<id>.json` only after validation succeeds. A failed run therefore leaves
the previous published JSON intact.

The test suite validates the seed files, registry provenance and source-specific
failure cases. It runs without network access by using checked-in samples.

## Validation rules

Source parsers preserve missing values as `null`. They never turn a missing
value into `0` or leave the upstream sentinel in the published record. A real
zero is still a value. The behavior is covered by
[`test_parse_keeps_input_missing_as_null`](../pipeline/tests/test_chirps.py),
[`test_preserves_zero_and_null_values`](../pipeline/tests/test_open_meteo_era5.py)
and the corresponding
[`test_preserves_zero_and_null_values`](../pipeline/tests/test_open_meteo_glofas.py).

Time-series validators require records in order with no gaps or duplicates.
Examples include
[`test_rejects_a_missing_month`](../pipeline/tests/test_noaa_ersst.py) and
[`test_rejects_a_duplicated_month`](../pipeline/tests/test_noaa_ersst.py), the
ONI parser's
[`test_rejects_a_missing_season`](../pipeline/tests/test_noaa_cpc_oni.py) and
[`test_rejects_a_duplicated_season`](../pipeline/tests/test_noaa_cpc_oni.py),
the ERA5
[`test_rejects_each_structural_coordinate_date_or_value_rule`](../pipeline/tests/test_open_meteo_era5.py),
and the GloFAS
[`test_rejects_each_structural_or_value_rule`](../pipeline/tests/test_open_meteo_glofas.py).
Daily OISST checks include
[`test_rejects_days_with_a_gap`](../pipeline/tests/test_noaa_oisst.py),
[`test_rejects_a_duplicated_day`](../pipeline/tests/test_noaa_oisst.py) and
[`test_rejects_days_out_of_order`](../pipeline/tests/test_noaa_oisst.py). The
weekly Niño parser checks the same rules with
[`test_rejects_a_gap`](../pipeline/tests/test_noaa_cpc_nino_weekly.py) and
[`test_rejects_a_duplicated_week`](../pipeline/tests/test_noaa_cpc_nino_weekly.py).

Every non-null value must stay within the physically possible range for its
source. The source validators reject out-of-range ONI anomalies in
[`test_rejects_an_anomaly_out_of_range`](../pipeline/tests/test_noaa_cpc_oni.py),
ERSST anomalies in
[`test_rejects_an_anomaly_outside_the_conservative_range`](../pipeline/tests/test_noaa_ersst.py),
OISST SST, climatology and anomaly values in
[`test_rejects_an_sst_out_of_range`](../pipeline/tests/test_noaa_oisst.py),
[`test_rejects_a_climatology_out_of_range`](../pipeline/tests/test_noaa_oisst.py)
and
[`test_rejects_an_anomaly_out_of_range`](../pipeline/tests/test_noaa_oisst.py),
weekly Niño SST and anomalies in
[`test_rejects_an_sst_out_of_range`](../pipeline/tests/test_noaa_cpc_nino_weekly.py)
and
[`test_rejects_an_anomaly_out_of_range`](../pipeline/tests/test_noaa_cpc_nino_weekly.py),
and rainfall in
[`test_aggregate_rejects_out_of_range_rainfall`](../pipeline/tests/test_chirps.py).

## Transformation

Source values are not silently modified. A source module may change the file
format or add an explicitly derived field, but the method must be visible in the
source notes. If the upstream publishes an anomaly, use that anomaly as
published rather than recomputing it. When a value is computed here, its method
and base period belong in the registry `notes`; `reference_period` carries the
base period into the published contract when applicable. Registry provenance and
published values are checked by
[`test_reads_the_whole_real_file_and_maps_columns`](../pipeline/tests/test_noaa_ersst.py),
[`test_build_adds_provenance_metadata`](../pipeline/tests/test_noaa_cpc_oni.py)
and
[`test_parse_builds_records_and_calculates_anomaly`](../pipeline/tests/test_chirps.py).

## Published format

Each published file contains one source's provenance and at least one record:

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
| `source_revision`                           | Optional object with the upstream SHA-256 and required `last_modified` key; `last_modified` is the HTTP `Last-Modified` value or `null` when the upstream supplies no header.                               |
| `records`                                   | A non-empty array. Every record has `start`; interval records also have `end`. Fields beyond those depend on the dataset id.                                                                                |

Record dates use ISO 8601 strings: `YYYY-MM` for months and `YYYY-MM-DD` for
days. The schema adds the record fields for each current dataset id, including
time series, grids, boundaries and forecast records. A new record kind requires
a schema extension in the same change as its first source.

The product translates the four `data_type` values into Spanish labels at the UI
boundary. Registry text fields printed by the site remain Spanish; code, schema
keys and contract values remain English.

## Comparability

Do not combine anomalies with different base periods without naming the
difference. Do not combine observed, estimated, forecast and official values
without labeling their types. The chart presentation rules live in
[`chart-rules.md`](chart-rules.md).

## Generated consumers

The pipeline generates [`docs/sources.md`](sources.md) from the registry. The
web generates [`web/app/types/dataset.ts`](../web/app/types/dataset.ts) from the
schema with `bun run types` in `web/`. CI fails when either generated file is
stale.
