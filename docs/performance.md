# Web performance budget

The route budget is the generated static output, measured from
`web/.output/public`. For each route, `payloadBytes` is the `_payload.json` byte
count and `entryJsBytes` is the sum of the JavaScript assets referenced by that
route's HTML and its page-component import closure. `cssBytes` is the sum of the
stylesheet files linked by the route's HTML. The checked limits are the measured
values in [`web/performance-budget.json`](../web/performance-budget.json) plus
its 15% margin. That hand-maintained JSON is the single source of budget
numbers.

The SEO output gate is separate. Its route, metadata and crawler checks are in
[`seo.md`](seo.md).

Run the check after generation:

```sh
cd web
bun run generate
bun run check:budget
```

CI runs the same command, including a build under the GitHub Pages `/wawapacha/`
base path. A route fails when its payload, loaded JavaScript, or linked CSS
exceeds the checked limit.

To re-measure after an intentional build change, run `bun run generate` and then
`bun run check:budget`. Copy the measured values on the left side of each
route's output into the matching `payloadBytes`, `entryJsBytes`, and `cssBytes`
fields in `web/performance-budget.json`, review the resulting limits, and run
the check again. Do not change the 15% margin to hide an unplanned regression.

## Social image

Social metadata uses the committed `web/public/og-image.png`, a 1200x630 PNG
because crawlers do not reliably render SVG images. The source artwork is
`web/public/og-image.svg`. The SEO document owns the generated-output check.
