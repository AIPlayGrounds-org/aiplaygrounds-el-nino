# Chart rules

The audience, purpose and product principles are in
[`PRODUCT.md`](../PRODUCT.md). These are the rules every chart follows.

## Provenance

Every chart answers five questions from the dataset's provenance block, never
from hand-written chart text. `useDataset(id)` is the only web data loader. It
validates the static catalog against the shared schema, and the shared chart
shell prints these fields with the chart.

| Question                                              | Provenance fields                                                |
| ----------------------------------------------------- | ---------------------------------------------------------------- |
| What does it show, and in which unit?                 | `variable`, `unit`                                               |
| What period does it cover, and what is its reference? | First and last record, `temporal_resolution`, `reference_period` |
| Is it observed, estimated, forecast or official?      | `data_type`                                                      |
| Where does it come from?                              | `source.institution`, `source.product`, `source.url`             |
| When was it last updated?                             | `ingestion_time` and the date of the last record                 |

## Display rules

- Observed, estimated, forecast and official data stay visibly distinct.
- Technical details sit below the chart: definition, resolution, reference
  period and method.
- A trend includes direction and size, never an arrow alone.
- A source that stops updating keeps its last value and shows its age.
- The update date and age come from `ingestion_time`; the latest data period
  comes from the last record. The date and period are in static HTML; the
  browser adds the current age after mount.
- Empty and error states explain what the reader can do next.
- Alerts link to the official source. WawaPacha does not invent a threshold,
  index or traffic light.
- The site links to the original dataset; it does not provide its own download.

The contract that defines these fields is
[`data-contract.md`](data-contract.md).
