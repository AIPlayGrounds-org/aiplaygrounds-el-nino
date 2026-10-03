"""ENFEN official communiqué: the alert status. Its provenance is in sources.toml.

A person copies the newest communiqué into pipeline/inputs/enfen.yaml. This module
validates that file and publishes it; nothing is downloaded.
"""

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
