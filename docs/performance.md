# Web performance budget

Each route has a size budget, measured on the generated static output in
`web/.output/public`:

- `payloadBytes`: the size of the route's `_payload.json`.
- `entryJsBytes`: the total size of the JavaScript the route loads, from its
  HTML and its page component's import closure.
- `cssBytes`: the total size of the stylesheets its HTML links.

[`web/performance-budget.json`](../web/performance-budget.json) holds the
measured values per route and a `margin` of 0.15. A route fails when a size
exceeds its measured value plus 15%.

## Check

```sh
cd web
bun run generate
bun run check:budget
```

Each output line shows measured/limit for the three sizes of a route, for
example
`/ payload=585921/673810 ok entry-js=928684/1067987 ok css=1555/1789 ok`. The
command exits with status 1 if any is over its limit. CI runs it for the root
path and for the `/wawapacha/` subpath (`PAGES_BASE_URL=/wawapacha/`). The SEO
check is separate: see [`seo.md`](seo.md).

## Update the budget

After an intentional change to the build, regenerate the site and write the
measured sizes:

```sh
cd web
bun run generate
bun run check:budget --update
```

The command measures every route in [`shared/site.ts`](../web/shared/site.ts)
and rewrites `performance-budget.json`, keeping `margin`. Review the diff and
commit it. `check:budget` fails for a route that has no entry.
