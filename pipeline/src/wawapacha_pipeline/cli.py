"""Production entry point: `wawapacha-pipeline run <id>` and `wawapacha-pipeline sources`."""

import argparse
import importlib
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from wawapacha_pipeline import catalog, registry, scaffold
from wawapacha_pipeline.contract import DATA_DIR, ValidationError, relative_path
from wawapacha_pipeline.sources import enfen_communique, senamhi_estaciones

SOURCES = registry.discover()
SNAPSHOT_IDS = tuple(
    source_id
    for source_id, entry in registry.load().items()
    if entry["verdict"] == "manual" and entry.get("site_pages")
)
# Snapshot sources publish from a checked-in file, so due selection never sees them.
SNAPSHOTS = {
    source_id: importlib.import_module(registry.source_module_name(source_id))
    for source_id in SNAPSHOT_IDS
}
CATALOG_SOURCES = tuple(SOURCES) + SNAPSHOT_IDS


def run(source_id: str) -> str:
    """Download or read, validate and publish a source. Returns a line that says what was published."""
    if source_id in SNAPSHOTS:
        count, path = SNAPSHOTS[source_id].run()
    else:
        count, path = SOURCES[source_id].run(datetime.now(UTC))
    return f"Published {source_id}: {count} records in {relative_path(path)}"


def _ingestion_time(path: Path) -> datetime | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["ingestion_time"]
        ingestion = datetime.fromisoformat(value)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return ingestion if ingestion.tzinfo else ingestion.replace(tzinfo=UTC)


def _is_due(update: str, ingestion: datetime, now: datetime) -> bool:
    if update == "manual":
        return False
    return now - ingestion >= registry.CADENCE_RULES[update]["due_after"]


def due_source_ids(
    now: datetime | None = None, data_dir: Path | None = None
) -> list[str]:
    now = now or datetime.now(UTC)
    now = now if now.tzinfo else now.replace(tzinfo=UTC)
    data_dir = data_dir or DATA_DIR
    sources = registry.load()
    return [
        source_id
        for source_id in SOURCES
        if (
            (ingestion := _ingestion_time(data_dir / f"{source_id}.json")) is None
            and sources[source_id]["update"] != "manual"
        )
        or (
            ingestion is not None
            and _is_due(sources[source_id]["update"], ingestion, now)
        )
    ]


def freshness_issues(
    now: datetime | None = None, data_dir: Path | None = None
) -> list[str]:
    """Return stale or missing published datasets using cadence tolerances."""
    now = now or datetime.now(UTC)
    now = now if now.tzinfo else now.replace(tzinfo=UTC)
    data_dir = data_dir or DATA_DIR
    sources = registry.load()
    issues = []
    for source_id in SOURCES:
        update = sources[source_id]["update"]
        tolerance = registry.stale_after(update)
        if tolerance is None:
            continue
        path = data_dir / f"{source_id}.json"
        last_update = _ingestion_time(path)
        if last_update is None:
            issues.append(f"{source_id}: missing or invalid ingestion/update timestamp")
            continue
        if now - last_update > tolerance:
            issues.append(
                f"{source_id}: last update {last_update.isoformat()} is "
                f"{now - last_update} old; {update} freshness tolerance is {tolerance}"
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wawapacha-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser(
        "run", help="download or read, validate and publish a source"
    )
    run_parser.add_argument("source", choices=sorted((*SOURCES, *SNAPSHOTS)))
    commands.add_parser(
        "sources", help="generate the source catalogues from sources.toml"
    )
    due_parser = commands.add_parser(
        "due", help="list automatable sources due for an update"
    )
    due_parser.add_argument("--as-of", help="evaluate due dates at this ISO 8601 time")
    due_parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="directory containing published source JSON",
    )
    freshness_parser = commands.add_parser(
        "freshness", help="fail when published datasets exceed their registry cadence"
    )
    freshness_parser.add_argument(
        "--as-of", help="evaluate freshness at this ISO 8601 time"
    )
    freshness_parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="directory containing published source JSON",
    )
    new_source_parser = commands.add_parser(
        "new-source", help="create the module and test for a new automatable source"
    )
    new_source_parser.add_argument("source", help="the new source id")
    snapshot_parser = commands.add_parser(
        "snapshot-check", help="validate a SENAMHI station snapshot before it is run"
    )
    snapshot_parser.add_argument("file", type=Path)
    enfen_parser = commands.add_parser(
        "enfen-add",
        help="record the newest ENFEN communiqué in pipeline/inputs/enfen.yaml",
    )
    enfen_parser.add_argument("number", type=int, help="communiqué number")
    enfen_parser.add_argument(
        "--date", type=date.fromisoformat, required=True, help="communiqué date"
    )
    enfen_parser.add_argument(
        "--status", choices=enfen_communique.STATUSES, required=True
    )
    enfen_parser.add_argument(
        "--next-due",
        type=date.fromisoformat,
        required=True,
        help="date the communiqué gives for the next one",
    )
    enfen_parser.add_argument(
        "--checked-at",
        type=date.fromisoformat,
        help="day the ENFEN archive was read (default: today in Lima)",
    )
    args = parser.parse_args(argv)

    if args.command == "new-source":
        try:
            created = scaffold.new_source(args.source)
        except (ValueError, FileExistsError, registry.RegistryError) as error:
            print(f"cannot create the source. {error}", file=sys.stderr)
            return 1
        for path in created:
            print(f"Created {relative_path(path)}")
        return 0

    if args.command == "snapshot-check":
        try:
            snapshot = senamhi_estaciones.load_snapshot(args.file)
        except ValidationError as error:
            print(f"{args.file}: fails validation. {error}", file=sys.stderr)
            return 1
        stations = snapshot["stations"]
        years = [
            int(year) for station in stations.values() for year, _ in station["years"]
        ]
        print(
            f"{args.file}: {len(stations)} stations, {min(years)}-{max(years)}, "
            f"taken {snapshot['snapshot']['taken']}"
        )
        return 0

    if args.command == "enfen-add":
        try:
            print(
                enfen_communique.add(
                    args.number,
                    args.date,
                    args.status,
                    args.next_due,
                    args.checked_at or datetime.now(enfen_communique.LIMA).date(),
                )
            )
        except ValidationError as error:
            print(f"cannot record the communiqué. {error}", file=sys.stderr)
            return 1
        return 0

    if args.command == "sources":
        try:
            catalog.write(CATALOG_SOURCES)
            print(
                f"Wrote {relative_path(catalog.CATALOG_PATH)} and "
                f"{relative_path(catalog.WEB_CATALOG_PATH)}"
            )
        except registry.RegistryError as error:
            print(f"sources.toml is not valid. {error}", file=sys.stderr)
            return 1
        return 0

    if args.command == "due":
        try:
            as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
            for source_id in due_source_ids(as_of, args.data_dir):
                print(source_id)
        except (ValueError, registry.RegistryError) as error:
            print(f"cannot select due sources. {error}", file=sys.stderr)
            return 1
        return 0

    if args.command == "freshness":
        try:
            as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
            issues = freshness_issues(as_of, args.data_dir)
        except (ValueError, registry.RegistryError) as error:
            print(f"cannot check data freshness. {error}", file=sys.stderr)
            return 1
        if issues:
            for issue in issues:
                print(f"::error title=data freshness::{issue}", file=sys.stderr)
            return 1
        print("Published datasets are within their registry cadence.")
        return 0

    try:
        print(run(args.source))
    except ValidationError as error:
        # Nothing is published: the previous JSON stays in data/.
        print(f"{args.source}: fails validation. {error}", file=sys.stderr)
        return 1
    return 0
