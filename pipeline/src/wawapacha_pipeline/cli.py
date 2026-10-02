"""Production entry point: `wawapacha-pipeline run <id>` and `wawapacha-pipeline sources`."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from wawapacha_pipeline import catalog, registry
from wawapacha_pipeline.contract import DATA_DIR, ValidationError, relative_path

SOURCES = registry.discover()


def run(source_id: str) -> str:
    """Download, validate and publish a source. Returns a line that says what was published."""
    count, path = SOURCES[source_id].run(datetime.now(timezone.utc))
    return f"Published {source_id}: {count} records in {relative_path(path)}"


def _ingestion_time(path: Path) -> datetime | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["ingestion_time"]
        ingestion = datetime.fromisoformat(value)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return ingestion if ingestion.tzinfo else ingestion.replace(tzinfo=timezone.utc)


def _is_due(update: str, ingestion: datetime, now: datetime) -> bool:
    if update == "manual":
        return False
    minimum_age = {
        "daily": timedelta(hours=20),
        "weekly": timedelta(days=6),
        "monthly": timedelta(days=27),
    }[update]
    return now - ingestion >= minimum_age


def due_source_ids(
    now: datetime | None = None, data_dir: Path | None = None
) -> list[str]:
    now = now or datetime.now(timezone.utc)
    now = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wawapacha-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="download, validate and publish a source")
    run_parser.add_argument("source", choices=sorted(SOURCES))
    commands.add_parser("sources", help="generate docs/sources.md from sources.toml")
    due_parser = commands.add_parser(
        "due", help="list automatable sources due for an update"
    )
    due_parser.add_argument("--as-of", help="evaluate due dates at this ISO 8601 time")
    args = parser.parse_args(argv)

    if args.command == "sources":
        try:
            print(f"Wrote {relative_path(catalog.write(SOURCES))}")
        except registry.RegistryError as error:
            print(f"sources.toml is not valid. {error}", file=sys.stderr)
            return 1
        return 0

    if args.command == "due":
        try:
            as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
            for source_id in due_source_ids(as_of):
                print(source_id)
        except (ValueError, registry.RegistryError) as error:
            print(f"cannot select due sources. {error}", file=sys.stderr)
            return 1
        return 0

    try:
        print(run(args.source))
    except ValidationError as error:
        # Nothing is published: the previous JSON stays in data/.
        print(f"{args.source}: fails validation. {error}", file=sys.stderr)
        return 1
    return 0
