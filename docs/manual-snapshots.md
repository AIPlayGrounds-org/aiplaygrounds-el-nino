# Manual snapshots

Two sources have no download the pipeline can run on a schedule: the ENFEN
communiqué and the SENAMHI station data. A person copies the input into the
repository, and the pipeline validates it with the same publication boundary as
any download (see [`data-contract.md`](data-contract.md)). Their registry
entries have `update = "manual"`, so `due` never selects them. Refresh one by
running it yourself.

## ENFEN communiqué

1. Open the newest communiqué in the
   [ENFEN archive](https://enfen.imarpe.gob.pe/downloads/comunicados/) and copy
   its values from the detail page HTML, not from the PDF.
2. Edit [`pipeline/inputs/enfen.yaml`](../pipeline/inputs/enfen.yaml). It has
   one `enfen` mapping:

   | Key          | Value                                                                                                                                             |
   | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
   | `number`     | The communiqué number.                                                                                                                            |
   | `year`       | Four digits, the year of `date`.                                                                                                                  |
   | `date`       | The publication date, unquoted `YYYY-MM-DD`. Not in the future.                                                                                   |
   | `status`     | One of `No Activo`, `Vigilancia de El Niño Costero`, `Alerta de El Niño Costero`, `Vigilancia de La Niña Costera` or `Alerta de La Niña Costera`. |
   | `url`        | `https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-<number>-<year>/`.                                                               |
   | `next_due`   | The date the communiqué gives for the next one. After `date`.                                                                                     |
   | `checked_at` | Optional. The day you last checked ENFEN, between `date` and today.                                                                               |

3. From `pipeline/`, publish it:

   ```sh
   uv run wawapacha-pipeline run enfen-communique
   ```

The published record runs from `date` to `next_due`. The pipeline sets its
`stale` field from the Lima date when the source runs, and each web build sets
it again from the build's Lima date, so an old record turns stale without a new
pipeline run. The home page keeps the record visible and marks it stale.

## SENAMHI station snapshot

SENAMHI's public histogram map and station pages have no download. A person
reads them without logging in and without bypassing the bot check, and saves the
daily series as a gzip JSON file named
`pipeline/inputs/senamhi-estaciones-YYYY-MM-DD.json.gz`. The module reads the
file with the newest name and makes no network request.

The file has two top-level objects:

- `snapshot`: the strings `taken` (an ISO date), `by`, `page`, `station_page`
  and `note`. All are required.
- `stations`: one object per station code, with `dep`, `name`, `lat`, `lon`,
  `years` and the daily arrays `precipitation_mm`, `tmax_c` and `tmin_c`.
  `years` is a list of `[year, number of days]` pairs for consecutive years.
  Only the first and last year may be partial. Each daily array has exactly the
  days that `years` sums to, with `null` for a missing day.

The module rejects non-finite coordinates, non-consecutive years, incomplete
interior years, daily arrays of the wrong length and negative precipitation. It
publishes monthly precipitation totals, monthly mean maximum and minimum
temperatures, the day counts behind them and, per calendar month, the median of
the monthly precipitation totals across years. A monthly value is `null` when
fewer than 80% of the month's days are present. Daily arrays never reach
`data/`: the source license is unconfirmed, so the monthly aggregates are the
publication boundary.

To refresh, add the new snapshot file and run, from `pipeline/`:

```sh
uv run wawapacha-pipeline run senamhi-estaciones
uv run pytest tests/test_senamhi_estaciones.py
```

No code changes. The published `ingestion_time` is the snapshot's `taken` date,
not the time of the run. Then run the checks in
[`CONTRIBUTING.md`](../.github/CONTRIBUTING.md#checks).
