# Web performance budget

The route budget is the generated static output, measured from
`web/.output/public`. For each route, `payloadBytes` is the `_payload.json` byte
count and `entryJsBytes` is the sum of the JavaScript assets referenced by that
route's HTML. The checked limit is the measured value in
[`web/performance-budget.json`](../web/performance-budget.json) plus its 15%
margin. That hand-maintained JSON is the single source of budget numbers.

Run the check after generation:

```sh
cd web
bun run generate
bun run check:budget
```

CI runs the same command. A route fails when either its payload or its
referenced entry JavaScript exceeds the checked limit.

To re-measure after an intentional build change, run `bun run generate` and then
`bun run check:budget`. Copy the measured values on the left side of each
route's output into the matching `payloadBytes` and `entryJsBytes` fields in
`web/performance-budget.json`, review the resulting limits, and run the check
again. Do not change the 15% margin to hide an unplanned regression.
