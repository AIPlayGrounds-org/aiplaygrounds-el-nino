# Documentation

This directory is the reference set for the repository. Each document owns one
kind of rule. Start with the map below, then follow links instead of copying a
rule into another document.

| Document                                     | Owns                                                                         |
| -------------------------------------------- | ---------------------------------------------------------------------------- |
| [`chart-rules.md`](chart-rules.md)           | Chart provenance, attribution and display behavior.                          |
| [`data-contract.md`](data-contract.md)       | The published dataset shape and validation boundary.                         |
| [`add-a-source.md`](add-a-source.md)         | The contributor workflow for adding a registry source.                       |
| [`concepts.md`](concepts.md)                 | The domain glossary for interpreting the data.                               |
| [`sources.md`](sources.md)                   | The generated catalog of automatable and snapshot sources shown on the site. |
| [`performance.md`](performance.md)           | The web payload and entry-JavaScript budget and its check command.           |
| [`data-workflow.md`](data-workflow.md)       | Due selection, data-branch publication and the static deployment overlay.    |
| [`manual-snapshots.md`](manual-snapshots.md) | Human-maintained inputs and their publication boundary.                      |
| [`freshness.md`](freshness.md)               | The independent published-data freshness check.                              |
| [`seo.md`](seo.md)                           | Generated metadata, sitemap, robots file and their check.                    |

The repository map is [`ARCHITECTURE.md`](../ARCHITECTURE.md). Contributor
branches, checks and merges are in [`CONTRIBUTING.md`](../CONTRIBUTING.md). The
source catalog is generated with `uv run wawapacha-pipeline sources` from
`pipeline/`; do not edit it by hand. Edit [`sources.toml`](../sources.toml) and
regenerate the catalog when source facts change.
