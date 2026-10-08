# Contributing

Thank you for considering a contribution. If the change is not straightforward,
open an issue first to discuss it.

## The codebase

Read [`docs/architecture.md`](../docs/architecture.md) for the code map and
[`docs/README.md`](../docs/README.md) for the guides. To add a source, follow
[`docs/source-registry.md`](../docs/source-registry.md#add-a-source).

## Set up

Install [mise](https://mise.jdx.dev/getting-started), then follow
[Get started](../README.md#get-started). The pipeline runs with `uv run` from
`pipeline/` and the site with `bun` from `web/`.

## Branches and pull requests

- `main` is what ships: every push deploys the site.
- Work on a branch named `type/topic` (`docs/…`, `feature/…`) and open a pull
  request to `main`.
- A pull request does one thing. If it depends on another open pull request,
  branch from that one and say so in the description.
- Before it is ready, rebase it on `main`, regenerate the generated files and
  get CI green. To resolve a conflict in a generated file, take `main`'s version
  and run its generator.
- The `main` ruleset requires a pull request and blocks force pushes and branch
  deletion. It requires no approving review and allows merge, squash and rebase
  merges.

## Checks

[`ci.yml`](workflows/ci.yml) runs these on every pull request. Run them first.
They leave the tree unchanged:

```sh
cd pipeline
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run wawapacha-pipeline sources
git diff --exit-code ../docs/sources.md
git diff --exit-code ../web/app/data/source-catalog.json

cd ../web
bun install --frozen-lockfile
bun run format:check
bun run types
git diff --exit-code app/types/dataset.ts
bun run generate
bun run check:seo
bun run check:budget
```

CI also runs the last three commands with `PAGES_BASE_URL=/wawapacha/`. See
[`docs/seo.md`](../docs/seo.md) and
[`docs/performance.md`](../docs/performance.md).

To format, run `uv run ruff format .` in `pipeline/` and `bun run format` in
`web/`. Format Markdown with
`bunx prettier --print-width 80 --prose-wrap always --write '**/*.md'`.

If a `git diff` check fails, a generated file is stale. Commit the regenerated
file with your change:

| Generated file                                                            | Regenerate with                                     | From                                                                       |
| ------------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- |
| [`docs/sources.md`](../docs/sources.md)                                   | `uv run wawapacha-pipeline sources`, in `pipeline/` | [`sources.toml`](../sources.toml)                                          |
| [`web/app/data/source-catalog.json`](../web/app/data/source-catalog.json) | `uv run wawapacha-pipeline sources`, in `pipeline/` | [`sources.toml`](../sources.toml)                                          |
| [`web/app/types/dataset.ts`](../web/app/types/dataset.ts)                 | `bun run types`, in `web/`                          | [`dataset.schema.json`](../schema/dataset.schema.json) and the web catalog |

## Language

Docs, registry fields and code are in English. Spanish stays in the site's own
copy, in proper names and domain terms (El Niño Costero, ENFEN, SENAMHI), and in
the published values the [data contract](../docs/data-contract.md) fixes.
