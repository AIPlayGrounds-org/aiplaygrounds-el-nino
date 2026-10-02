# Data contract

The rules every WawaPacha dataset follows, from download to the page. The
concepts (anomaly, base period…) are in [`concepts.md`](concepts.md). The code
that applies them is mapped in [`ARCHITECTURE.md`](../ARCHITECTURE.md).

## 1. Origin

- A source is automated only if it has an entry in
  [`sources.toml`](../sources.toml) with the verdict `automatable`.
- The pipeline downloads from the `access.url` of that entry, never from copies
  or intermediate pages.
- A source module does not repeat what the registry says. It reads the
  institution, product, URL, variable and unit from it.

## 2. Validation

Every download is checked before it is published. **If anything fails, nothing
is published and the previous JSON stays.** The site keeps showing the last
valid data, with its date.

Each source checks at least:

| Check                                                        | Why                                     |
| ------------------------------------------------------------ | --------------------------------------- |
| The file has the expected structure (header, columns)        | Catches format changes in the source.   |
| Every value is inside a physically possible range            | Catches read errors and corrupt values. |
| Dates are in order, with no gaps and no duplicates           | Catches truncated or misread downloads. |
| The resulting JSON matches the [schema](#4-published-format) | Catches data the web could not read.    |

Missing values are stored as `null`, never as `0` and never as the source's own
code (for example `-99.9`).

## 3. Transformation

- **Source values are not modified.** Only their format changes.
- If the source publishes the anomaly, use theirs. Do not recompute it.
- If something has to be computed (an average, an anomaly), the method and the
  base period go in the `notes` of the source's registry entry.

## 4. Published format

One JSON file per source, at `data/<id>.json`. It carries the provenance of the
data (institution, product and URL; what is measured and in which unit; whether
it is observed, estimated or forecast; its resolution and base period), when it
was downloaded, the version of the code that produced it, and the records.

The contract is [`schema/dataset.schema.json`](../schema/dataset.schema.json).
It is the only definition of the fields:

- `contract.publish()` validates every JSON against it before writing.
- `bun run types`, in `web/`, generates the web's TypeScript types from it.

The fields of a record depend on the source. Every record states the period it
describes (`start`, `end`). Dates follow ISO 8601: `2026-08` for a month,
`2026-08-31` for a day.

`data_type` takes one of three Spanish values. They are part of the contract, so
they stay as they are:

| Value        | Meaning                                                     |
| ------------ | ----------------------------------------------------------- |
| `observado`  | Observed: measured directly, or computed from measurements. |
| `estimado`   | Estimated: modeled from satellites and measurements.        |
| `pronóstico` | Forecast: what is expected to happen.                       |

The text fields the site prints (`variable`, `unit`, both resolutions and
`reference_period`) come from the registry as written, so they are in Spanish.
[`add-a-source.md`](add-a-source.md#the-registry) lists them.

A real example: [`data/noaa-cpc-oni.json`](../data/noaa-cpc-oni.json).

## 5. Comparability

- Never mix anomalies with different base periods in one chart without saying
  so.
- Never mix observed, estimated and forecast data without telling them apart.

## 6. Tests

Each source has a test that reads a real copy of the original file, kept in the
repository. If the source changes its format, the sample still shows what it
used to look like. The samples are in `pipeline/tests/samples/`.

Other tests check that the published JSON matches its registry entry and that
every JSON in `data/` matches the schema.
