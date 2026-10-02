# Contributing

## Branches and PRs

- `main` is what ships: every push deploys the web.
- Work on a branch named `type/topic` (`docs/…`, `feature/…`) and open a PR to
  `main`.
- A PR does one thing. If it depends on another open PR, branch from that one
  and say so in the description.
- To add a source, follow [`docs/add-a-source.md`](docs/add-a-source.md).
- A decision goes in [`docs/decisions.md`](docs/decisions.md), in the same PR
  that applies it.

## Checks

[`ci.yml`](.github/workflows/ci.yml) runs these on every PR. Run them first:

```sh
cd pipeline
uv run pytest
uv run wawapacha-pipeline sources
git diff --exit-code ../docs/sources.md

cd ../web
bun install --frozen-lockfile
bun run types
git diff --exit-code app/types/dataset.ts
bun run generate
```

If a `git diff` fails, a generated file is stale. Commit it with your change:

| Generated file                                         | Regenerate with                                     | From                                                       |
| ------------------------------------------------------ | --------------------------------------------------- | ---------------------------------------------------------- |
| [`docs/sources.md`](docs/sources.md)                   | `uv run wawapacha-pipeline sources`, in `pipeline/` | [`sources.toml`](sources.toml)                             |
| [`web/app/types/dataset.ts`](web/app/types/dataset.ts) | `bun run types`, in `web/`                          | [`schema/dataset.schema.json`](schema/dataset.schema.json) |

## Language

Docs, registry and code are in English. Spanish stays in the site's own copy, in
proper names and domain terms (El Niño Costero, ENFEN, SENAMHI), and in the
published values the contract fixes
([`data-contract.md`](docs/data-contract.md)).
