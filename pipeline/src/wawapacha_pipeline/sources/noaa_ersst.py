"""NOAA/NCEI ERSSTv5 monthly Niño indices."""

import math
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

VERSION = "0.1.0"
ID = "noaa-ersst"
SOURCE = registry.get(ID)
URL = os.environ.get("NOAA_ERSST_URL", SOURCE["access"]["url"])

ANOMALY_RANGE = (-10.0, 10.0)
EVENT_WINDOWS = (
    ("1982-83", "1982-07", "1983-11"),
    ("1997-98", "1997-04", "1998-08"),
    ("2017", "2017-01", "2017-04"),
)


def fetch(url: str = URL, timeout: int = 60, retries: int = 3) -> str:
    """Download the plain-text index, retrying transient HTTP failures."""
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", None)
                if status is None and urllib.parse.urlparse(url).scheme == "file":
                    status = 200
                if status != 200:
                    raise ValidationError(f"HTTP status inesperado: {status}.")
                content_type = response.headers.get_content_type()
                raw = response.read()
                if content_type == "text/html" or raw.lstrip().lower().startswith(
                    (b"<html", b"<!doctype", b"<head", b"<body")
                ):
                    raise ValidationError(
                        "La respuesta parece HTML, no el índice de ERSSTv5."
                    )
                try:
                    return raw.decode("ascii")
                except UnicodeDecodeError:
                    raise ValidationError(
                        "La respuesta no es texto ASCII válido."
                    ) from None
        except ValidationError:
            raise
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
            last_error = error

    raise ValidationError(
        f"No se pudo descargar el índice de ERSSTv5 tras {retries} intentos: {last_error}"
    )


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the record count and the path of the published JSON."""
    records = parse(fetch())
    dataset = build(records, ingestion_time or datetime.now(UTC))
    return len(records), publish(dataset)


def parse(text: str) -> list[dict]:
    """Parse and validate the six-column ERSSTv5 index file."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValidationError("El archivo está vacío.")

    records = []
    previous = None
    for number, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 6:
            raise ValidationError(f"Línea {number}: se esperaban 6 columnas: {line!r}")
        year_text, month_text, *values_text = parts
        try:
            year = int(year_text)
            month = int(month_text)
            values = [float(value) for value in values_text]
        except ValueError:
            raise ValidationError(
                f"Línea {number}: valor no numérico: {line!r}"
            ) from None
        if not 1 <= month <= 12:
            raise ValidationError(f"Línea {number}: mes fuera de rango ({month}).")
        if not all(math.isfinite(value) for value in values):
            raise ValidationError(
                f"Línea {number}: las anomalías deben ser números finitos."
            )
        if not all(ANOMALY_RANGE[0] <= value <= ANOMALY_RANGE[1] for value in values):
            raise ValidationError(
                f"Línea {number}: anomalía fuera de rango ({line!r})."
            )

        index = year * 12 + month - 1
        if previous is None and (year, month) != (1854, 1):
            raise ValidationError(
                f"Línea {number}: la serie debería empezar en 1854-01."
            )
        if previous is not None and index != previous + 1:
            raise ValidationError(
                f"Línea {number}: mes no contiguo, hay un hueco o duplicado."
            )
        previous = index

        month_iso = f"{year:04d}-{month:02d}"
        record = {
            "start": month_iso,
            "end": month_iso,
            "nino3_anomaly": values[0],
            "nino4_anomaly": values[1],
            "nino34_anomaly": values[2],
            "nino12_anomaly": values[3],
        }
        if event := event_for_month(month_iso):
            record["event"] = event
        records.append(record)

    return records


def event_for_month(month: str) -> str | None:
    """Return the current chronology label for an event-window month."""
    for name, start, end in EVENT_WINDOWS:
        if start <= month <= end:
            return name
    return None


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add registry provenance and publication metadata to validated records."""
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
