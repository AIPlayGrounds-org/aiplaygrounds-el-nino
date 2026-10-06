# WawaPacha

![The home page: "¿Llegó El Niño?" with the latest ONI reading and the stripes of the series since 1950](docs/assets/site.png)

WawaPacha is a public web observatory for signals of El Niño in Peru. It is a
static site built with [Nuxt 4](https://nuxt.com/) and Bun, fed by a Python
pipeline managed with uv. The browser receives published JSON from this
repository; there is no runtime backend, account system or upstream API call.
Live at <https://aiplaygrounds-org.github.io/wawapacha/>.

## Boundary

The pipeline reads registered public sources, validates each dataset and
publishes `data/<id>.json`. Deployment overlays newer JSON from the `data`
branch onto the seed files on `main`, then `nuxt generate` builds the static
site for GitHub Pages. The architecture map is
[`ARCHITECTURE.md`](ARCHITECTURE.md).

## Install and run

You need [Git](https://git-scm.com/) and
[mise](https://mise.jdx.dev/getting-started). mise installs the Bun and uv
versions selected in [`mise.toml`](mise.toml).

```sh
mise install
cd web
mise exec -- bun install
mise exec -- bun run dev
```

Open <http://localhost:3100>. If mise is active in your shell, omit
`mise exec --`.

To generate the source catalogues, use `pipeline/`:

```sh
cd pipeline
uv run wawapacha-pipeline sources
```

To run one source and publish its JSON, use `pipeline/`:

```sh
cd pipeline
uv run wawapacha-pipeline run noaa-cpc-oni
```

The seed file is [`data/noaa-cpc-oni.json`](data/noaa-cpc-oni.json). The
scheduled data workflow publishes newer files to the `data` branch; see the
[`data workflow`](docs/data-workflow.md) for the branch and failure behavior.

If validation fails, the previous JSON remains in place.

## Smallest example

The web loads a typed dataset by id. A page can pass a server-side shaping
function when it needs only part of the published records:

```ts
const oni = await useDataset("noaa-cpc-oni");
const oisst = await useDataset("noaa-oisst", cropOisst);
```

`useDataset` validates on the server and hydrates the shaped result from the
Nuxt payload. See [`chart-rules.md`](docs/chart-rules.md) for the display
contract and
[`ARCHITECTURE.md`](ARCHITECTURE.md#dataset-loading-and-page-payloads) for the
current page shapes.

## Features

- `/` explains the current ONI signal with a history chart, weekly Niño indices,
  the ENFEN status, CPC probabilities and an OISST anomaly map.
- `/territorio` maps recent CHIRPS rainfall and anomalies by department, with an
  ERA5 cross-check.
- `/historico` compares the current year with tagged 1982–83, 1997–98 and 2017
  events, the official ICEN series and a SENAMHI station snapshot.
- `/rios` shows modeled discharge for selected Peruvian basins and links to
  official alerts.
- Every chart exposes its variable, unit, period, data type, source and update
  age. The UI keeps observed, estimated, forecast and official data distinct.
- The pipeline keeps source facts in one registry and generates the source
  catalog and schema-derived TypeScript types.

## Links

- [Documentation index](docs/README.md)
- [Contributing](CONTRIBUTING.md)
