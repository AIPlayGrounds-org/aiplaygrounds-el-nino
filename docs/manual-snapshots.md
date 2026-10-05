# Manual snapshots

Manual inputs are checked-in evidence. They are validated by the same pipeline
publication boundary as downloaded inputs, but due selection never refreshes
them. The registry marks a manual source with `update = "manual"`.

## ENFEN communiqué

An operator reads the newest communiqué HTML in the
[ENFEN archive](https://enfen.imarpe.gob.pe/downloads/comunicados/) and edits
[`pipeline/inputs/enfen.yaml`](../pipeline/inputs/enfen.yaml). The file has one
`enfen` mapping with the communiqué number, year, date, exact status, matching
detail URL, next due date and optional check date. Dates are unquoted ISO dates.
The parser accepts only ENFEN's five status phrases and the matching IMARPE
detail URL.

From `pipeline`, run the source after editing the input:

```sh
uv run wawapacha-pipeline run enfen-communique
```

The published record ends on the stated next due date. The parser computes its
`stale` field using Lima time when the source runs. Each web build recomputes
the field from the build's Lima date and the record's `end`, so an old record
turns stale without a new pipeline run. The page keeps it visible with a clear
notice.

## SENAMHI station snapshot

An operator takes a snapshot from SENAMHI's public histogram map and station
pages. Access uses no login and does not bypass the bot check. The snapshot is
saved unchanged as `pipeline/inputs/senamhi-estaciones-YYYY-MM-DD.json.gz`. Its
metadata records the date, operator, source pages and note. The module chooses
the newest file by filename.

The module validates station coordinates, consecutive years, partial first and
last years, aligned daily arrays and non-negative precipitation. It publishes
monthly precipitation totals and temperature means. A monthly value is null when
fewer than 80% of its calendar days are present. Daily arrays never cross into
`data/`. The source license is unconfirmed, so the monthly aggregates are the
publication boundary.

Due selection never runs this source. From `pipeline`, publish the newest
snapshot and run its behavior tests:

```sh
uv run wawapacha-pipeline run senamhi-estaciones
uv run pytest tests/test_senamhi_estaciones.py
```

The refresh needs no code edit. The published `ingestion_time` is the snapshot's
date, not the time of the run. After publication, run the web generation and the
checks in [`CONTRIBUTING.md`](../CONTRIBUTING.md#checks).
