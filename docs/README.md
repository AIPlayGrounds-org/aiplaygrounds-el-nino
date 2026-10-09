# Documentation

Read in this order. Each document owns one subject and links to the others
instead of repeating them.

1. [`architecture.md`](architecture.md): the code map, the data flow and the
   boundaries between packages.
2. [`data-workflow.md`](data-workflow.md): due selection, the `data` branch and
   the static deployment.
3. [`data-contract.md`](data-contract.md): the shape of `data/<id>.json` and the
   rules that gate publication.
4. [`source-registry.md`](source-registry.md): the fields of `sources.toml` and
   the steps to add a source.
5. [`sources.md`](sources.md): the generated catalog of every source.
6. [`manual-snapshots.md`](manual-snapshots.md): the inputs a person refreshes.
7. [`freshness.md`](freshness.md): the check that reports stale published data.
8. [`chart-rules.md`](chart-rules.md): provenance, attribution and display rules
   for every chart.
9. [`seo.md`](seo.md): page metadata, sitemap, robots file and their check.
10. [`performance.md`](performance.md): the per-route size budget and its check.
11. [`concepts.md`](concepts.md): the climate terms the data uses.
12. [`story.md`](story.md): the reading path from the central-Pacific signal to
    the coast, state, observations, expectations and past events.

To change code, start with [`CONTRIBUTING.md`](../.github/CONTRIBUTING.md).
