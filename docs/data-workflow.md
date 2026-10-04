# Data workflow

The registry selects sources, the pipeline publishes validated JSON, and the web
deploy reads that JSON at build time. The registry's `update` field is the
source of truth for cadence. Source facts and the generated catalog are
documented in [`sources.md`](sources.md).

## Local commands

From `pipeline`, list sources that are due in a data directory:

```sh
uv run wawapacha-pipeline due --data-dir ../data
```

Run a selected source with `uv run wawapacha-pipeline run <id>`. The command
validates the source-specific input and the shared schema before it replaces
`data/<id>.json`. A failed run leaves the previous file in place. The
publication boundary and schema are in [`data-contract.md`](data-contract.md).

## Scheduled update

[`update-data.yml`](../.github/workflows/update-data.yml) runs daily. It checks
out `main` and the `data` branch, asks `due` for missing or old automatable
datasets, and runs each selected source independently. A manual dispatch can
name one source. Manual registry entries are never selected by `due`.

The job commits changed JSON to the `data` branch. It dispatches
[`deploy.yml`](../.github/workflows/deploy.yml) only after that push. A source
failure is reported after the other selected sources finish, and the job fails
without publishing that source's replacement.

## Static deployment

The deploy job checks out `main`. When the `data` branch exists, it overlays its
JSON files onto the seed files in `data/`. When it does not exist, the seed
snapshot stays in use. `bun run generate` then prerenders the Nuxt site and
uploads `web/.output/public` to GitHub Pages. The browser never calls an
upstream source.

The generated source catalogues are refreshed from `sources.toml` with
`uv run wawapacha-pipeline sources` from `pipeline/`. Do not edit
[`sources.md`](sources.md) or the web catalogue by hand.
