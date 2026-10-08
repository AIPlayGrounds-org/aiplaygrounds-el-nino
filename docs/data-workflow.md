# Data workflow

How a source's data gets from its upstream to the site. The registry selects the
sources, the pipeline publishes validated JSON to the `data` branch, and the
deploy builds the site from that JSON. The `update` field of each entry in
[`sources.toml`](../sources.toml) sets the cadence. The shape of the JSON is in
[`data-contract.md`](data-contract.md).

## Run a source locally

Run these from `pipeline/`. List the sources that are due:

```sh
uv run wawapacha-pipeline due --data-dir ../data
```

A source is due when its `data/<id>.json` is missing or invalid, or when the
file's `ingestion_time` is at least this old:

| `update`  | Due after |
| --------- | --------- |
| `daily`   | 20 hours  |
| `weekly`  | 6 days    |
| `monthly` | 27 days   |

A `manual` source is never due. `--as-of <ISO-8601 time>` evaluates the rule at
another time. The thresholds are `CADENCE_RULES` in
[`registry.py`](../pipeline/src/wawapacha_pipeline/registry.py).

Run one source:

```sh
uv run wawapacha-pipeline run <id>
```

The command validates the source's input and then the shared schema, and
replaces `data/<id>.json` only if both pass. Set `WAWAPACHA_DATA_DIR` to publish
to another directory.

## Scheduled update

[`update-data.yml`](../.github/workflows/update-data.yml) runs daily at 14:17
UTC. It checks out `main` and the `data` branch, creating the branch when it
does not exist, asks `due` for the sources to run, and runs each one
independently. A manual dispatch can name one source to run instead.

The job commits changed JSON to the `data` branch with the message
`data: update <ids>`, then dispatches
[`deploy.yml`](../.github/workflows/deploy.yml). If a source fails, the job runs
the others, publishes their results and then fails. The failed source keeps its
previous JSON.

[`freshness.yml`](../.github/workflows/freshness.yml) checks the published files
separately. See [`freshness.md`](freshness.md).

## Static deployment

[`deploy.yml`](../.github/workflows/deploy.yml) runs on every push to `main` and
when dispatched. It checks out `main`. If the `data` branch exists, it copies
that branch's `*.json` files over the seed files in `data/`. Otherwise the seed
files stay. `bun run generate` then prerenders the Nuxt site with
`PAGES_BASE_URL` set to the repository subpath, and the job uploads
`web/.output/public` to GitHub Pages.
