# Contributing

## Branches and PRs

- `main` is what ships: every push deploys the web.
- Work on a branch named `type/topic` (`docs/…`, `feature/…`) and open a PR to
  `main`.
- A PR does one thing. If it depends on another open PR, branch from that one
  and say so in the description.
- To add a source, follow [`docs/add-a-source.md`](docs/add-a-source.md).
- The data branch and deployment overlay are in
  [`docs/data-workflow.md`](docs/data-workflow.md).
- Manual inputs and their refresh boundaries are in
  [`docs/manual-snapshots.md`](docs/manual-snapshots.md).
- The freshness, SEO and performance gates are in
  [`docs/freshness.md`](docs/freshness.md), [`docs/seo.md`](docs/seo.md) and
  [`docs/performance.md`](docs/performance.md).
- Read [`ROADMAP.md`](ROADMAP.md) before choosing work; it owns the target
  architecture, stages and merge plan.
- Follow the [merge plan](ROADMAP.md#merge-plan): merge commits only, signed,
  never squash.

## Checks

[`ci.yml`](.github/workflows/ci.yml) runs these on every PR. Run them first:

Ruff and oxfmt own formatting; the checks below leave the tree unchanged.

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

If a `git diff` fails, a generated file is stale. Commit it with your change:

| Generated file                                                         | Regenerate with                                     | From                                                       |
| ---------------------------------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------- |
| [`docs/sources.md`](docs/sources.md)                                   | `uv run wawapacha-pipeline sources`, in `pipeline/` | [`sources.toml`](sources.toml)                             |
| [`web/app/data/source-catalog.json`](web/app/data/source-catalog.json) | `uv run wawapacha-pipeline sources`, in `pipeline/` | [`sources.toml`](sources.toml)                             |
| [`web/app/types/dataset.ts`](web/app/types/dataset.ts)                 | `bun run types`, in `web/`                          | [`schema/dataset.schema.json`](schema/dataset.schema.json) |

## Language

Docs, registry and code are in English. Spanish stays in the site's own copy, in
proper names and domain terms (El Niño Costero, ENFEN, SENAMHI), and in the
published values the contract fixes
([`data-contract.md`](docs/data-contract.md)).
