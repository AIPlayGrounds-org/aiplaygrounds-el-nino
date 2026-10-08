# Data freshness

The freshness check reports published JSON that is missing, unreadable or older
than its registry cadence allows. It is separate from due selection and never
blocks a deploy.

Run it from `pipeline/`:

```sh
uv run wawapacha-pipeline freshness --data-dir ../data
```

A passing run prints `Published datasets are within their registry cadence.` A
failing run prints one `::error title=data freshness::...` line per dataset on
stderr and exits with status 1. `--as-of <ISO-8601 time>` evaluates the check at
another time, which makes a result reproducible.

The command reads `ingestion_time` from the file of each automatable source and
skips `manual` sources. A dataset is stale when its age exceeds twice the
cadence interval plus a slack:

| `update`  | Interval | Slack   | Stale after |
| --------- | -------- | ------- | ----------- |
| `daily`   | 1 day    | 4 hours | 52 hours    |
| `weekly`  | 7 days   | 1 day   | 15 days     |
| `monthly` | 31 days  | 1 day   | 63 days     |

The values are `CADENCE_RULES` in
[`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py), and
[`test_cli.py`](../pipeline/tests/test_cli.py) covers them.

[`freshness.yml`](../.github/workflows/freshness.yml) runs the same command
daily at 14:47 UTC against a worktree of the `data` branch.

## On the site

The site applies the same limit. `wawapacha-pipeline sources` writes each
non-manual source's limit, in hours, to the
[web catalog](../web/app/data/source-catalog.json) as `stale_after_hours`.
During the build, `loadDataset` adds it to the dataset, so the browser receives
one number and not the catalog. A chart shows a stale notice when:

- its `ingestion_time` is older than `stale_after_hours`, or
- its newest record ended 90 days ago or more, whatever the last run was.

A `manual` source has no `stale_after_hours`, so only the second condition
applies. The site keeps showing the last valid record and its age. The display
rule is in [`chart-rules.md`](chart-rules.md).
