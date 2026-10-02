"""Punto de entrada de producción: `wawapacha-pipeline run <id>`."""

import argparse
import sys
from datetime import datetime, timezone

from wawapacha_pipeline.contract import ValidationError, publish, relative_path
from wawapacha_pipeline.sources import noaa_cpc_oni

SOURCES = {noaa_cpc_oni.ID: noaa_cpc_oni}


def run(source_id: str) -> str:
    """Descarga, valida y publica una fuente. Devuelve la ruta publicada."""
    source = SOURCES[source_id]
    records = source.parse(source.download())
    dataset = source.build(records, datetime.now(timezone.utc))
    path = publish(dataset)
    return f"Publicado {source_id}: {len(records)} registros en {relative_path(path)}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wawapacha-pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="descarga, valida y publica una fuente")
    run_parser.add_argument("source", choices=sorted(SOURCES))
    args = parser.parse_args(argv)

    try:
        print(run(args.source))
    except ValidationError as error:
        # Sin publicar nada: el JSON anterior sigue en data/.
        print(f"{args.source}: no pasa la validación. {error}", file=sys.stderr)
        return 1
    return 0
