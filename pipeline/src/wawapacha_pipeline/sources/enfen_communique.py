"""ENFEN official communiqué: the alert status. Its provenance is in sources.toml.

A person records the newest communiqué in pipeline/inputs/enfen.yaml with
`wawapacha-pipeline enfen-add`. This module validates that file and publishes it.
It does not download anything.
"""

import difflib
import os
import re
from collections.abc import Hashable
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT, ValidationError, publish

# Súbela cuando cambie la lógica: queda en cada JSON publicado.
VERSION = "0.1.0"

ID = "enfen-communique"
SOURCE = registry.get(ID)
INPUT_PATH = REPO_ROOT / "pipeline" / "inputs" / "enfen.yaml"
# ENFEN_COMMUNIQUE_PATH reads another file (for example, in tests).
PATH = Path(os.environ.get("ENFEN_COMMUNIQUE_PATH", INPUT_PATH))

REQUIRED = ("number", "year", "date", "status", "url", "next_due")
OPTIONAL = ("checked_at",)

# The exact phrases ENFEN uses. The sentence around them varies, so only the phrase is stored.
STATUSES = (
    "No Activo",
    "Vigilancia de El Niño Costero",
    "Alerta de El Niño Costero",
    "Vigilancia de La Niña Costera",
    "Alerta de La Niña Costera",
)
URL_PATTERN = re.compile(
    r"https://enfen\.imarpe\.gob\.pe/download/comunicado-oficial-enfen-n-(\d+)-(\d{4})/?"
)
URL_TEMPLATE = (
    "https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-{number}-{year}/"
)
INPUT_TEMPLATE = """\
# Written by `wawapacha-pipeline enfen-add` from the newest communiqué:
# https://enfen.imarpe.gob.pe/downloads/comunicados/
# Dates are unquoted YYYY-MM-DD. `status` is the exact phrase ENFEN uses.
# `next_due` is the date the communiqué says the next one is due.
enfen:
  number: {number}
  year: {year}
  date: {published}
  status: "{status}"
  url: "{url}"
  next_due: {next_due}
  checked_at: {checked_at}
"""

# ENFEN publishes in Lima. Peru has no daylight saving time, so a fixed offset is exact.
LIMA = timezone(timedelta(hours=-5))


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects a repeated key instead of keeping the last one."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if not isinstance(key, Hashable):
                raise ValidationError(
                    f"Key {key!r} must be a single value, not a list or a mapping."
                )
            if key in seen:
                raise ValidationError(
                    f"Repeated key {key!r}: a communiqué appears twice."
                )
            seen.add(key)
        return super().construct_mapping(node, deep)


def fetch(path: Path = PATH) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValidationError(f"Cannot read {path}: {error.strerror}.") from None


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the record count and the path of the published JSON."""
    ingestion_time = ingestion_time or datetime.now(UTC)
    records = parse(fetch(), ingestion_time.astimezone(LIMA).date())
    return len(records), publish(build(records, ingestion_time))


def parse(text: str, today: date | None = None) -> list[dict]:
    """Validate the YAML and return its one communiqué as a record.

    `today` is the date in Lima. It decides whether the communiqué lies in the future
    and whether the record is stale.
    """
    today = today or datetime.now(LIMA).date()
    try:
        document = yaml.load(text, Loader=_UniqueKeyLoader)
    except (
        yaml.YAMLError,
        ValueError,
    ) as error:  # ValueError: a date that does not exist, such as 2026-02-30
        raise ValidationError(f"The YAML cannot be read: {error}") from None
    if not isinstance(document, dict) or set(document) != {"enfen"}:
        raise ValidationError("Expected one top-level key, `enfen`.")
    entry = document["enfen"]
    if not isinstance(entry, dict):
        raise ValidationError("`enfen` must be a mapping.")

    missing = [key for key in REQUIRED if entry.get(key) is None]
    if missing:
        raise ValidationError(f"Missing fields: {missing}.")
    unknown = sorted(set(entry) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        raise ValidationError(f"Unknown fields: {unknown}.")

    number, year = entry["number"], entry["year"]
    if type(number) is not int or number < 1:
        raise ValidationError(f"number must be a positive integer, not {number!r}.")
    if type(year) is not int or not 1000 <= year <= 9999:
        raise ValidationError(f"year must have four digits, not {year!r}.")

    published = read_date(entry, "date")
    next_due = read_date(entry, "next_due")
    if published.year != year:
        raise ValidationError(f"date {published} is not in year {year}.")
    if published > today:
        raise ValidationError(
            f"date {published} is in the future (today is {today} in Lima)."
        )
    if next_due <= published:
        raise ValidationError(f"next_due {next_due} must be after date {published}.")

    status = entry["status"]
    if status not in STATUSES:
        raise ValidationError(f"status {status!r} is not one of {list(STATUSES)}.")

    url = entry["url"]
    match = URL_PATTERN.fullmatch(url) if isinstance(url, str) else None
    if match is None:
        raise ValidationError(
            f"url {url!r} is not an https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-<number>-<year>/ page."
        )
    if (int(match[1]), int(match[2])) != (number, year):
        raise ValidationError(
            f"url {url!r} names a different communiqué than {number}-{year}."
        )

    record = {
        "number": number,
        "year": year,
        "status": status,
        "url": url,
        "start": published.isoformat(),
        "end": next_due.isoformat(),
        "stale": today > next_due,
    }
    if "checked_at" in entry:
        checked_at = read_date(entry, "checked_at")
        if checked_at < published:
            raise ValidationError(
                f"checked_at {checked_at} is before date {published}."
            )
        if checked_at > today:
            raise ValidationError(
                f"checked_at {checked_at} is in the future (today is {today} in Lima)."
            )
        record["checked_at"] = checked_at.isoformat()
    return [record]


def read_date(entry: dict, key: str) -> date:
    """YAML turns an unquoted 2026-09-28 into a date. A quoted one stays text and is rejected."""
    value = entry[key]
    if type(value) is not date:
        raise ValidationError(
            f"{key} must be an unquoted YYYY-MM-DD date, not {value!r}."
        )
    return value


def add(
    number: int,
    published: date,
    status: str,
    next_due: date,
    checked_at: date,
    path: Path | None = None,
    today: date | None = None,
) -> str:
    """Validate and replace the input file for this communiqué.

    Return the diff. The year and detail URL follow from the number and date.
    """
    path = path or PATH
    text = INPUT_TEMPLATE.format(
        number=number,
        published=published.isoformat(),
        status=status,
        url=URL_TEMPLATE.format(number=number, year=published.year),
        next_due=next_due.isoformat(),
        checked_at=checked_at.isoformat(),
        year=published.year,
    )
    parse(text, today)
    previous = fetch(path) if path.exists() else ""
    path.write_text(text, encoding="utf-8", newline="\n")
    return "\n".join(
        difflib.unified_diff(
            previous.splitlines(),
            text.splitlines(),
            fromfile=f"a/{path.name}",
            tofile=f"b/{path.name}",
            lineterm="",
        )
    )


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add to the records the provenance the registry declares, the ingestion time and the version."""
    return {
        "id": ID,
        "source": {
            "institution": SOURCE["institution"],
            "product": SOURCE["product"],
            "url": SOURCE["access"]["url"],
        },
        "variable": SOURCE["variable"],
        "unit": SOURCE["unit"],
        "data_type": SOURCE["data_type"],
        "spatial_resolution": SOURCE["spatial_resolution"],
        "temporal_resolution": SOURCE["temporal_resolution"],
        "ingestion_time": ingestion_time.astimezone(UTC).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }
