"""Production entry point: `wawapacha-pipeline run <id>` and `wawapacha-pipeline sources`."""

import argparse
import sys
from datetime import datetime, timezone

from wawapacha_pipeline import catalog, registry
from wawapacha_pipeline.contract import ValidationError, publish, relative_path
from wawapacha_pipeline.sources import noaa_cpc_oni

SOURCES = {noaa_cpc_oni.ID: noaa_cpc_oni}


def run(source_id: str) -> str:
    """Download, validate and publish a source. Returns a line that says what was published."""
    source = SOURCES[source_id]
    records = source.parse(source.download())
    dataset = source.build(records, datetime.now(timezone.utc))
    path = publish(dataset)
    return f"Published {source_id}: {len(records)} records in {relative_path(path)}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wawapacha-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="download, validate and publish a source")
    run_parser.add_argument("source", choices=sorted(SOURCES))
    commands.add_parser("sources", help="generate docs/sources.md from sources.toml")
    args = parser.parse_args(argv)

    if args.command == "sources":
        try:
            print(f"Wrote {relative_path(catalog.write(SOURCES))}")
        except registry.RegistryError as error:
            print(f"sources.toml is not valid. {error}", file=sys.stderr)
            return 1
        return 0

    try:
        print(run(args.source))
    except ValidationError as error:
        # Nothing is published: the previous JSON stays in data/.
        print(f"{args.source}: fails validation. {error}", file=sys.stderr)
        return 1
    return 0
