"""NOAA CPC weekly Niño-region SST and anomaly indices."""

import hashlib
import os
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

VERSION = "0.1.0"

ID = "noaa-cpc-nino-weekly"
SOURCE = registry.get(ID)
URL = os.environ.get("NOAA_CPC_NINO_WEEKLY_URL", SOURCE["access"]["url"])

PREAMBLE = (
    " Weekly SST data starts week centered on 2Sept1981",
    "",
    "                Nino1+2      Nino3        Nino34        Nino4",
    " Week          SST SSTA     SST SSTA     SST SSTA     SST SSTA",
)
FIRST_DATE = date(1981, 9, 2)
ROW_WIDTH = 62
DATE_PATTERN = re.compile(r"\d{2}[A-Z]{3}\d{4}")
PAIR_PATTERN = re.compile(
    r"(?P<sst>\d{2}\.\d)(?:(?P<negative>-\d\.\d)| (?P<positive>\d\.\d))"
)
MONTHS = {
    name: number
    for number, name in enumerate(
        (
            "JAN",
            "FEB",
            "MAR",
            "APR",
            "MAY",
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV",
            "DEC",
        ),
        start=1,
    )
}
PAIR_STARTS = (15, 28, 41, 54)
REGIONS = ("nino_1_2", "nino_3", "nino_3_4", "nino_4")
SST_RANGE = (15.0, 35.0)
ANOMALY_RANGE = (-8.0, 8.0)


@dataclass(frozen=True)
class FetchResult:
    """Downloaded bytes and the upstream metadata needed for revision checks."""

    text: str
    sha256: str
    last_modified: str | None
    retrieved_at: str

    @property
    def ingestion_metadata(self) -> dict[str, str | None]:
        return {
            "sha256": self.sha256,
            "last_modified": self.last_modified,
            "retrieved_at": self.retrieved_at,
        }


def fetch(url: str = URL, timeout: int = 60) -> FetchResult:
    """Download the source and retain its revision and retrieval metadata."""
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    retrieved_at = datetime.now(UTC)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = response.read()
        last_modified = response.headers.get("Last-Modified")
    return FetchResult(
        text=content.decode("ascii"),
        sha256=hashlib.sha256(content).hexdigest(),
        last_modified=last_modified,
        retrieved_at=retrieved_at.isoformat(timespec="seconds"),
    )


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the record count and the path of the published JSON."""
    fetched = fetch()
    metadata = fetched.ingestion_metadata
    records = parse(fetched.text)
    dataset = build(
        records,
        ingestion_time or datetime.fromisoformat(metadata["retrieved_at"]),
        {key: metadata[key] for key in ("sha256", "last_modified")},
    )
    return len(records), publish(dataset)


def parse(text: str) -> list[dict]:
    """Parse and validate the fixed-width CPC weekly file."""
    lines = text.splitlines()
    if len(lines) < len(PREAMBLE) + 1 or tuple(lines[:4]) != PREAMBLE:
        found = lines[:4] if lines else "(archivo vacío)"
        raise ValidationError(f"Preamble inesperado: {found!r}.")

    records = []
    previous = None
    data_started = False
    for number, line in enumerate(lines[4:], start=5):
        if not line.strip():
            if data_started:
                if any(remaining.strip() for remaining in lines[number:]):
                    raise ValidationError(
                        f"Línea {number}: línea vacía inesperada entre los datos."
                    )
                break
            raise ValidationError(
                f"Línea {number}: línea vacía inesperada antes de los datos."
            )
        data_started = True
        records.append(read_line(line, number, previous))
        previous = date.fromisoformat(records[-1]["start"])

    if not records:
        raise ValidationError("El archivo no contiene registros.")
    return records


def read_line(line: str, number: int, previous: date | None = None) -> dict:
    """Read one 62-character row using the source's fixed offsets."""
    token = line[1:10]
    if DATE_PATTERN.fullmatch(token) is None:
        raise ValidationError(f"Línea {number}: fecha inesperada {token!r}.")
    if len(line) != ROW_WIDTH:
        raise ValidationError(
            f"Línea {number}: se esperaban 62 caracteres, hay {len(line)}."
        )

    current = parse_date(token, number)
    if current.weekday() != 2:
        raise ValidationError(
            f"Línea {number}: la fecha no cae en miércoles ({token})."
        )
    if previous is None:
        if current != FIRST_DATE:
            raise ValidationError(
                f"Línea {number}: la serie debería empezar en 1981-09-02, empieza en {current}."
            )
    elif current != previous + timedelta(days=7):
        raise ValidationError(
            f"Línea {number}: {current} no sigue a la semana anterior (hueco o duplicado)."
        )

    values = {}
    for region, start in zip(REGIONS, PAIR_STARTS, strict=True):
        pair = line[start : start + 8]
        match = PAIR_PATTERN.fullmatch(pair)
        if match is None:
            raise ValidationError(
                f"Línea {number}: par SST/anomalía inesperado {pair!r}."
            )
        sst = float(match["sst"])
        anomaly = float(match["negative"] or match["positive"])
        if not SST_RANGE[0] <= sst <= SST_RANGE[1]:
            raise ValidationError(f"Línea {number}: SST fuera de rango ({sst} °C).")
        if not ANOMALY_RANGE[0] <= anomaly <= ANOMALY_RANGE[1]:
            raise ValidationError(
                f"Línea {number}: anomalía fuera de rango ({anomaly} °C)."
            )
        values[f"{region}_sst"] = sst
        values[f"{region}_anomaly"] = anomaly

    iso_date = current.isoformat()
    return {"start": iso_date, "end": iso_date, **values}


def parse_date(token: str, number: int) -> date:
    """Parse CPC's uppercase DDMMMYYYY date without depending on locale."""
    try:
        return date(int(token[5:9]), MONTHS[token[2:5]], int(token[:2]))
    except (KeyError, ValueError):
        raise ValidationError(f"Línea {number}: fecha inválida {token!r}.") from None


def build(
    records: list[dict],
    ingestion_time: datetime,
    source_revision: dict[str, str | None] | None = None,
) -> dict:
    """Add registry provenance, ingestion time and an optional source revision."""
    dataset = {
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
    }
    if source_revision is not None:
        dataset["source_revision"] = source_revision
    dataset["records"] = records
    return dataset
