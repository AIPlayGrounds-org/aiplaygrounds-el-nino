# Data freshness

Freshness is a reporting gate for published JSON. It is separate from due
selection and does not block a site deploy. The `freshness` command reads each
automatable source's `ingestion_time`, skips manual sources, and reports a
missing, invalid or over-age file. Its cadence thresholds are implemented in
[`cli.py`](../pipeline/src/wawapacha_pipeline/cli.py) and covered by
[`test_cli.py`](../pipeline/tests/test_cli.py).

Run the check from `pipeline`:

```sh
uv run wawapacha-pipeline freshness --data-dir ../data
```

Use `--as-of <ISO-8601 time>` to make a local result reproducible. A passing run
prints `Published datasets are within their registry cadence.`. A failing run
prints one `::error title=data freshness::...` line per issue and returns
status 1.

[`freshness.yml`](../.github/workflows/freshness.yml) runs the same check daily
against a worktree of the `data` branch. It reports stale data without blocking
[`deploy.yml`](../.github/workflows/deploy.yml). The site keeps showing the last
valid record and its age; the chart shell's display rule is in
[`chart-rules.md`](chart-rules.md).
