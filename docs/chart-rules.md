# Chart rules

These rules apply to every chart and data table. The product's scope and
non-goals are in [`README.md`](../README.md). This document owns chart
behavior.

## Provenance

Every chart receives a dataset from `useDataset(id, shape?)`. The server loader
validates the source JSON against the shared schema, and an optional shape
function can reduce it before the page payload is serialized. The chart shell
prints the provenance block from the returned dataset.

| Question                                         | Dataset fields                                                   |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| What does it show, and in which unit?            | `variable`, `unit`                                               |
| What period does it cover?                       | First and last record, `temporal_resolution`, `reference_period` |
| Is it observed, estimated, forecast or official? | `data_type`                                                      |
| Where does it come from?                         | `source.institution`, `source.product`, `source.url`             |
| When was it last updated?                        | `ingestion_time` and the last record's date                      |

[`ChartShell.vue`](../web/app/components/ChartShell.vue) owns the common
provenance block, accessible summary, latest-data age and stale-source notice.
The dataset contract that supplies its fields is
[`data-contract.md`](data-contract.md).

## Display

- Keep observed, estimated, forecast and official data visibly distinct.
- Put the definition, resolution, reference period and method below the chart.
- State both direction and size for a trend. An arrow alone is not enough.
- Keep the last valid value visible when a source stops updating, and show its
  age.
- Render the update date and data period in static HTML. Add the current age
  after mount.
- Give empty and error states a useful next action.
- Link alerts to the official source. WawaPacha does not invent a threshold,
  index or traffic light.
- Link to the original dataset. WawaPacha does not offer a first-party data
  download.

## Attribution

`DatasetAttribution.vue` adds the required Open-Meteo credit for the ERA5 and
GloFAS pages and names their Copernicus products. Territory also prints the
boundary dataset's attribution and license from its geometry record. The
source-specific facts and license notes live in the generated
[`sources.md`](sources.md).
