"""ENFEN's official monthly Índice Costero El Niño (ICEN) table."""

import math
import os
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

VERSION = "0.1.0"

ID = "enfen-icen"
SOURCE = registry.get(ID)
URL = os.environ.get("ENFEN_ICEN_URL", SOURCE["access"]["url"])
MAX_RECORD_AGE = timedelta(days=180)


def fetch(url: str = URL, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def _year(value: str, line_number: int) -> int:
    try:
        year = int(value)
    except ValueError:
        raise ValidationError(
            f"Line {line_number}: non-numeric row: {value!r}."
        ) from None
    if 0 <= year <= 99:
        return 1900 + year if year >= 50 else 2000 + year
    if 1000 <= year <= 9999:
        return year
    raise ValidationError(f"Line {line_number}: year is out of range: {value!r}.")


def _number(value: str, line_number: int) -> float:
    try:
        number = float(value)
    except ValueError:
        raise ValidationError(
            f"Line {line_number}: non-numeric row: {value!r}."
        ) from None
    if not math.isfinite(number):
        raise ValidationError(f"Line {line_number}: non-numeric row: {value!r}.")
    return number


def parse(text: str, today: date | None = None) -> list[dict]:
    """Parse the official table and require a complete monthly sequence."""
    today = today or date.today()
    records: list[dict] = []
    previous_month: int | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        parts = stripped.split()
        if len(parts) != 3:
            raise ValidationError(
                f"Line {line_number}: expected 3 numeric columns, got {line!r}."
            )
        year = _year(parts[0], line_number)
        try:
            month = int(parts[1])
        except ValueError:
            raise ValidationError(
                f"Line {line_number}: non-numeric row: {line!r}."
            ) from None
        if not 1 <= month <= 12:
            raise ValidationError(
                f"Line {line_number}: month must be between 1 and 12, not {month}."
            )
        value = _number(parts[2], line_number)
        if not -10 <= value <= 10:
            raise ValidationError(
                f"Line {line_number}: ICEN is outside the ±10 range: {value}."
            )

        current_month = year * 12 + month - 1
        if previous_month is not None and current_month != previous_month + 1:
            raise ValidationError(
                f"Line {line_number}: {year:04d}-{month:02d} is not the next month; the table has a gap or duplicate."
            )
        previous_month = current_month
        period = f"{year:04d}-{month:02d}"
        records.append({"start": period, "end": period, "icen": value})

    if not records:
        raise ValidationError("The ICEN file contains no records.")

    last_period = date.fromisoformat(f"{records[-1]['start']}-01")
    if today - last_period > MAX_RECORD_AGE:
        raise ValidationError(
            f"The last ICEN record ({records[-1]['end']}) is older than the configured maximum age of {MAX_RECORD_AGE.days} days."
        )
    return records


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add registry provenance and the ingestion timestamp."""
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
        "reference_period": SOURCE["reference_period"],
        "ingestion_time": ingestion_time.astimezone(UTC).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Fetch, validate and publish the current ICEN table."""
    ingestion_time = ingestion_time or datetime.now(UTC)
    records = parse(fetch(), ingestion_time.date())
    return len(records), publish(build(records, ingestion_time))
