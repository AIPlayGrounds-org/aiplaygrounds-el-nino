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

## Published format

Each published file contains one source's provenance and at least one record:

| Field                                       | Meaning                                                                                              |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `id`                                        | The lowercase hyphenated id from `sources.toml`.                                                     |
| `source`                                    | Institution, product and download URL.                                                               |
| `variable`, `unit`                          | What the data measures and its unit.                                                                 |
| `data_type`                                 | `observed`, `estimated`, `forecast` or `official`.                                                   |
| `spatial_resolution`, `temporal_resolution` | The source's spatial and temporal resolution.                                                        |
| `reference_period`                          | The anomaly base period, when applicable.                                                            |
| `ingestion_time`                            | The UTC or offset-aware ISO 8601 download time.                                                      |
| `processing_version`                        | The code version that produced the file.                                                             |
| `source_revision`                           | The upstream SHA-256 and optional `Last-Modified` value, when supplied.                              |
| `records`                                   | A non-empty array. Every record has `start` and `end`; fields beyond those depend on the dataset id. |

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
