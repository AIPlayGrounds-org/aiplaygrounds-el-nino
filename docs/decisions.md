# Decision log

Each decision has a date, what was decided, why, and what follows from it.
Propose a new one in a pull request.

**Statuses:** 🟡 Proposed · ✅ Accepted · ❌ Rejected · 🔁 Superseded

## D-001 — First goal: the ONI end to end

**Date:** 2026-10-01 · **Status:** ✅ Accepted · **Deadline:** 2026-10-09

**Decision.** The first delivery is a page that charts NOAA's **Oceanic Niño
Index (ONI)** from 1950, with its source, unit (°C of anomaly), date of the last
update and data type, **observed**.

**Why.** It is the world's reference index for El Niño and comes from a public
text file, with no account or permission. It forces the whole path: fetch,
clean, store and show. That path is the template for every other source.

**Consequences.** Other indices, maps, forecasts, alerts and the AI summary are
out of this goal. It is met: a document sets the data rules, a script saves the
ONI as JSON with a test, the web shows the chart, and the work is in `main`
through a reviewed PR.

## D-002 — End-of-month scope: every phase, trimmed

**Date:** 2026-10-01 · **Status:** ✅ Accepted · **Deadline:** 2026-10-31

**Decision.** All four phases of the initial plan (`wawapacha.md` §11, in the
git history) ship before 31 October. Each uses only the sources that can be
fetched without waiting on an institution. The phases are in
[`ROADMAP.md`](../ROADMAP.md).

**Why.** The deadline is fixed, and the sources left out need an institution's
reply, an unapproved account or an unconfirmed license.

**Consequences.**

- The emails to IGP/ENFEN, SENAMHI, ANA, DHN and INAIGEM go out in the first
  week, so the replies can arrive in time for a later phase.
- No source is published without its attribution text and reviewed terms of use.
- Anything outside the scope does not block the deadline.

## D-003 — Team split

**Date:** 2026-10-01 · **Status:** ✅ Accepted

**Decision.** Three people work in parallel, each owning one area. **Data**: the
data protocol, one script per source, tests and the published JSON. **Web**:
pages, charts, maps and deployment. **Content**: texts for Aprende and
Metodología, manual ENFEN entry, emails to institutions and licenses. The owners
are open.

**Why.** Data and Web talk only through the JSON format, so Web can move ahead
with test data while Data finishes each source.

**Consequences.** The JSON format is the only interface between the areas.

## D-004 — The pipeline is written in marimo notebooks

**Date:** 2026-10-01 · **Status:** 🔁 Superseded by
[D-006](#d-006--the-pipeline-is-a-package-and-the-notebooks-show-it).

**Decision.** Each source is a [marimo](https://marimo.io) notebook that does
the whole path: download, validate, display and publish. Tables use **polars**
and charts use **plotly**. The file opens in the browser to review each step
(`marimo edit`) and runs headless in production.

**Why.** Anyone on the team sees what the code does at each step. A marimo
notebook is a plain `.py` file: it versions in Git, is tested with pytest and
runs in GitHub Actions.

**Consequences.** A notebook with polars per source replaces "one script per
source" with pandas. xarray joins with the gridded sources that need it. The
notebook no longer runs in production (D-006).

## D-005 — Free APIs for rainfall and rivers

**Date:** 2026-10-01 · **Status:** ✅ Accepted

**Decision.** Open-Meteo's free API serves two sources in the scope of D-002:
`open-meteo-era5` (v0.2, daily rainfall by region) and `open-meteo-glofas`
(v0.3, **simulated** river discharge, until SENAMHI or ANA observed discharge is
available). OISST (v0.1) uses NCEI's ERDDAP, which returns CSV cut to the area.

**Why.** They are free, need no account and were tested with real data for
Piura. They give rainfall by region without processing grids, and are the only
route found to show rivers in v0.3 without waiting on the institutions.

**Consequences.** Non-commercial use only, with the CC BY 4.0 attribution:
"Weather data by Open-Meteo.com" and credit to Copernicus. GloFAS discharge is
always shown as **model-estimated**, never as official data or a basis for
alerts. Each river point is validated against a known flood first.

## D-006 — The pipeline is a package and the notebooks show it

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** The code for each source (download, parse, validate, build the
JSON) lives in the package [`pipeline/`](../pipeline/). The notebooks live in
[`notebooks/`](../notebooks/), import it and show each step. They define no
functions or classes and never write to `data/`. Production runs
`wawapacha-pipeline run <id>`, the only path that writes to `data/`.

**Why.** Production does not depend on marimo. There is a single way to publish,
and tests call the functions directly. The notebooks keep what D-004 asked for:
anyone on the team can see each step.

**Consequences.** A test fails if a notebook defines a function or a class.
marimo, plotly and polars are in the `notebooks` group of
`pipeline/pyproject.toml`, and the package does not depend on them.

## D-007 — v0.1 is one page made of panels

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** v0.1 is one page, `/`, built around the question "¿Llegó El
Niño?". It is made of seven panels, listed in [`ROADMAP.md`](../ROADMAP.md).
Each panel reads a single dataset and shows its provenance from the JSON.

**Why.** It is what the ONI site already does, extended with the v0.1 sources.
One panel per dataset lets a source be added without touching the others. It
avoids the crowded dashboard that [`product.md`](product.md) rules out.

**Consequences.** The Dashboard with dynamic ordering, Territorio and the other
sections are outside this decision.

## D-008 — The repository is organized around a registry and a schema

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** Each source's facts live in one entry of
[`sources.toml`](../sources.toml), not in `docs/fuentes/`. The JSON contract is
[`schema/dataset.schema.json`](../schema/dataset.schema.json), not a table in
`docs/datos.md`. The web app is in [`web/`](../web/). The docs are in English,
and `docs/arquitectura.md` is now [`ARCHITECTURE.md`](../ARCHITECTURE.md).

**Why.** A source's URL and unit had two copies that could drift. The cards ran
to about 2,800 lines, mostly "Desconocido" (unknown); the registry keeps only
what was checked. Data that breaks the contract is not published.

**Consequences.** CI fails if `docs/sources.md` or `web/app/types/dataset.ts` is
stale. Registry discovery checks that every `automatable` entry has its source
module, and the published JSON matches its registry entry.

## D-009 — Contract values are English

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** The published contract uses `observed`, `estimated`, `forecast`
and `official` for `data_type`. Spanish labels belong to product UI copy, not to
machine-readable JSON, registry values or generated types.

**Why.** English contract values are unambiguous across the pipeline and web
code, while the UI can translate them in one place without changing data.

**Consequences.** The schema, registry, published data, tests and generated
types use the four English values. `official` identifies institutional
statements such as ENFEN's alert status.

## D-010 — The map uses an ECharts canvas

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** The v0.1 map uses an ECharts canvas. Its grid covers 20°N–25°S and
120°W–60°W at 0.5-degree spacing. Coordinates are rounded to two decimals,
stored as JSON and served gzip-compressed by the host.

**Why.** ECharts is already the web charting system and a regular grid is enough
for the first map. This keeps the map asset and rendering path small.

**Consequences.** The map spike builds the grid JSON and ECharts layer. ECharts
is the only map renderer in the architecture and roadmap.

## D-011 — Static site with scheduled ingestion

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** The browser loads only our own JSON. Each source declares an
`update` cadence of `daily`, `weekly`, `monthly` or `manual` in `sources.toml`.
The scheduled workflow asks the pipeline's `due` selection for sources whose
published data is due, then runs only those sources.

**Why.** Visitor traffic must not depend on the availability, rate limits or
credentials of any upstream API. Source-specific schedules avoid needless
downloads while keeping the static build reproducible.

**Consequences.** The registry check validates the English cadence values, and
the workflow can publish a source independently. Sub-daily sources such as rain
and river levels trigger a later move off `main`, probably to a Cloudflare cron
job that writes to R2 or KV. Until then, scheduled ingestion remains a checked
repository change.

## D-012 — English source ids and discovered source modules

**Date:** 2026-10-02 · **Status:** ✅ Accepted

**Decision.** Source ids are English: `noaa-cpc-nino-weekly`,
`enfen-communique`, `enfen-forecast` and `enfen-icen-history`. An automatable
registry entry maps to
`pipeline/src/wawapacha_pipeline/sources/<id with hyphens replaced by underscores>.py`.
The module exposes `ID`, `fetch`, `parse` and `run`; the pipeline discovers it
from the registry rather than maintaining a shared source dictionary.

**Why.** English ids keep filenames, JSON ids and links consistent with the
English contract. Discovery lets parallel source work add one registry entry and
one module without editing a conflict-prone dispatcher.

**Consequences.** A missing or incomplete module is a registry-check error.
Sources that are planned but do not yet have a module remain `pending` until
their source task adds the implementation and changes the verdict to
`automatable`.
