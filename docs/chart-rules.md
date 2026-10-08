# Chart rules

Rules for every chart and data table on the site. Product copy is in Spanish.

## Provenance

Every chart gets its dataset from `useDataset(id, shape?)`. The server loader
validates the JSON against the schema, an optional `shape` function reduces it
before the page payload is serialized, and
[`ChartShell.vue`](../web/app/components/ChartShell.vue) prints the provenance
block from the result. The fields come from the
[data contract](data-contract.md).

| Question                                         | Dataset fields                                                   |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| What does it show, and in which unit?            | `variable`, `unit`                                               |
| What period does it cover?                       | First and last record, `temporal_resolution`, `reference_period` |
| Is it observed, estimated, forecast or official? | `data_type`                                                      |
| Where does it come from?                         | `source.institution`, `source.product`, `source.url`             |
| When was it last updated?                        | `ingestion_time` and the last record's date                      |

`ChartShell` also prints the accessible summary and the age of the data. It
shows a stale-source notice when `ingestion_time` is older than the source's
limit from the [freshness check](freshness.md#on-the-site) or the newest record
ended 90 days ago or more.

## Display

- Keep observed, estimated, forecast and official data visibly distinct.
- Put the definition, resolution, reference period and method below the chart.
- State both direction and size for a trend. An arrow alone is not enough.
- Keep the last valid value visible when a source stops updating, and show its
  age.
- Render the update date and data period in static HTML. Add the current age
  after mount.
- Give empty and error states a useful next action.
- Link alerts to the official source.
- Link to the original dataset.

## Attribution

[`DatasetAttribution.vue`](../web/app/components/DatasetAttribution.vue) adds
the Open-Meteo credit that the ERA5 and GloFAS pages require and names their
Copernicus products. `/territorio` also prints the attribution and license of
the boundary dataset from its geometry record. Source-specific facts and license
notes are in [`sources.md`](sources.md).
