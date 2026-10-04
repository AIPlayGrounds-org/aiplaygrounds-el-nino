"""Production entry point: `wawapacha-pipeline run <id>` and `wawapacha-pipeline sources`."""

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

from wawapacha_pipeline import catalog, registry
from wawapacha_pipeline.contract import DATA_DIR, ValidationError, relative_path

SOURCES = registry.discover()
CADENCE_RULES = {
    "daily": {
        "interval": timedelta(days=1),
        "due_after": timedelta(hours=20),
        "slack": timedelta(hours=4),
        "stale_label": "2 × 24 hours + 4 hours slack",
    },
    "weekly": {
        "interval": timedelta(days=7),
        "due_after": timedelta(days=6),
        "slack": timedelta(days=1),
        "stale_label": "2 × 7 days + 1 day slack",
    },
    "monthly": {
        "interval": timedelta(days=31),
        "due_after": timedelta(days=27),
        "slack": timedelta(days=1),
        "stale_label": "2 × 31 days + 1 day slack",
    },
}


def run(source_id: str) -> str:
    """Download, validate and publish a source. Returns a line that says what was published."""
    count, path = SOURCES[source_id].run(datetime.now(UTC))
    return f"Published {source_id}: {count} records in {relative_path(path)}"


def _ingestion_time(path: Path) -> datetime | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["ingestion_time"]
        ingestion = datetime.fromisoformat(value)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return ingestion if ingestion.tzinfo else ingestion.replace(tzinfo=UTC)


def _parse_update_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _published_update_times(path: Path) -> list[datetime]:
    try:
        dataset = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    times = [_parse_update_time(dataset.get("ingestion_time"))]
    revision = dataset.get("source_revision")
    if isinstance(revision, dict):
        times.append(_parse_update_time(revision.get("last_modified")))
    return [time for time in times if time is not None]


def _is_due(update: str, ingestion: datetime, now: datetime) -> bool:
    if update == "manual":
        return False
    return now - ingestion >= CADENCE_RULES[update]["due_after"]


def _is_stale(update: str, last_update: datetime, now: datetime) -> bool:
    if update == "manual":
        return False
    return now - last_update > _freshness_tolerance(update)


def _freshness_tolerance(update: str) -> timedelta:
    rule = CADENCE_RULES[update]
    return rule["interval"] * 2 + rule["slack"]


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
    """Return stale or missing published datasets using cadence tolerances.

    Ingestion is the publication timestamp. When an HTTP Last-Modified value is
    present, the newest of those two timestamps is used so a source revision is
    not reported stale merely because the file was checked later.
    """
    now = now or datetime.now(UTC)
    now = now if now.tzinfo else now.replace(tzinfo=UTC)
    data_dir = data_dir or DATA_DIR
    sources = registry.load()
    issues = []
    for source_id in SOURCES:
        update = sources[source_id]["update"]
        if update == "manual":
            continue
        path = data_dir / f"{source_id}.json"
        times = _published_update_times(path)
        if not times:
            issues.append(f"{source_id}: missing or invalid ingestion/update timestamp")
            continue
        latest = max(times)
        if _is_stale(update, latest, now):
            age = now - latest
            issues.append(
                f"{source_id}: last update {latest.isoformat()} is {age} old; "
                f"{update} freshness tolerance is "
                f"{_freshness_tolerance(update)} "
                f"({CADENCE_RULES[update]['stale_label']})"
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wawapacha-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser(
        "run", help="download, validate and publish a source"
    )
    run_parser.add_argument("source", choices=sorted(SOURCES))
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
    args = parser.parse_args(argv)

    if args.command == "sources":
        try:
            catalog.write(SOURCES)
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
