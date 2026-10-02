# Product

_Monitoreando el Fenómeno El Niño en el Perú_

What WawaPacha is, who it is for and the rules every chart follows. The code is
mapped in [`ARCHITECTURE.md`](../ARCHITECTURE.md).

## What it is

A scientific, public-facing web observatory that tracks the signals of El Niño
in Peru. Every number shows where it comes from and when it was last updated.

The guiding principle is **simple first, technical on demand.** The user's path
is: observe → put in context → compare → go deeper → check the source.

## Who it is for

| Audience                     | Needs                                                                                                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| **General public**           | To understand in under a minute what is happening, what stands out, where, and whether there are alerts. |
| **Students and researchers** | Historical series, units, climatological references, method, and a link to the original source.          |

Technical users can identify the variable, unit, source, reference, method,
update date and original link of every number.

## Principles

1. Clarity over density.
2. Scientific rigor without needless jargon.
3. Source and update date are always visible.
4. **Observed**, **estimated**, **forecast** and **official** data stay clearly
   apart.
5. An anomaly is not a danger.
6. Thresholds are official or scientific, never our own.
7. The site does not infer causes.
8. No traffic light and no home-made index: each signal shows on its own.

## Rules for every chart

Every chart answers five questions. The answers come from the dataset's
provenance block, never from text written by hand
([the contract](data-contract.md#4-published-format)):

| Question                                              | Field                                                |
| ----------------------------------------------------- | ---------------------------------------------------- |
| What does it show, and in which unit?                 | `variable`, `unit`                                   |
| What period does it cover, and what is its reference? | first and last record, `reference_period`            |
| Observed, estimated, forecast or official?            | `data_type`                                          |
| Where does it come from?                              | `source.institution`, `source.product`, `source.url` |
| When was it last updated?                             | `ingestion_time` and the date of the last record     |

It also follows these rules:

- **Technical details** sit in a collapsible section under the chart, with the
  definition, resolution, base period and method.
- **Trends** show direction and size (`↑ +0,8 °C`), never the arrow alone.
- **A source that stops updating** keeps its last value on screen, with its age.
  It is never hidden.
- **Empty and error states** carry a useful message.
- **The site offers no downloads of its own.** It links to the original dataset.
