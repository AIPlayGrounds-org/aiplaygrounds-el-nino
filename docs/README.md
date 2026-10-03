# Documentation

| Document                               | Owns                                                |
| -------------------------------------- | --------------------------------------------------- |
| [`chart-rules.md`](chart-rules.md)     | The provenance and display rules for every chart.   |
| [`data-contract.md`](data-contract.md) | The published dataset format and validation rules.  |
| [`add-a-source.md`](add-a-source.md)   | The workflow for adding a registry source.          |
| [`concepts.md`](concepts.md)           | The glossary for reading the data.                  |
| [`sources.md`](sources.md)             | The generated catalog of sources in `sources.toml`. |

The web's data boundary and chart provenance contract are described in
[`ARCHITECTURE.md`](../ARCHITECTURE.md) and [`chart-rules.md`](chart-rules.md).
Web behavior tests live in `web/test/` and run with `bun run test` from `web/`;
type checking runs with `bun run typecheck`. Formatting and lint checks are
documented with the CI commands in
[`CONTRIBUTING.md`](../CONTRIBUTING.md#checks).

The product audience and principles are in [`PRODUCT.md`](../PRODUCT.md). The
existing code map is in [`ARCHITECTURE.md`](../ARCHITECTURE.md), and unbuilt
work is in [`ROADMAP.md`](../ROADMAP.md). Branches, checks and merges are in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).
