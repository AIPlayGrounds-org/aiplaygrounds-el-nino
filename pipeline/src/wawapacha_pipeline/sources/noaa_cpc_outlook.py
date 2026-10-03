"""NOAA CPC ENSO strength probabilities. Provenance lives in sources.toml."""

import os
import re
import urllib.request
from calendar import month_name
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

VERSION = "0.1.0"

ID = "noaa-cpc-outlook"
SOURCE = registry.get(ID)
URL = os.environ.get("NOAA_CPC_OUTLOOK_URL", SOURCE["access"]["url"])

SEASON_START_MONTH = {
    "DJF": 12,
    "JFM": 1,
    "FMA": 2,
    "MAM": 3,
    "AMJ": 4,
    "MJJ": 5,
    "JJA": 6,
    "JAS": 7,
    "ASO": 8,
    "SON": 9,
    "OND": 10,
    "NDJ": 11,
}
SEASON_CENTER_MONTH = {
    season: start_month % 12 + 1
    for season, start_month in SEASON_START_MONTH.items()
}
MONTHS = {name.lower(): number for number, name in enumerate(month_name) if name}

CATEGORY_HEADINGS = [
    "Index ≤ -2.0°C",
    "-1.5°C ≥ Index > -2.0°C",
    "-1.0°C ≥ Index > -1.5°C",
    "-0.5°C ≥ Index > -1.0°C",
    "−0.5°C < Index < 0.5°C",
    "0.5°C ≤ Index < 1.0°C",
    "1.0°C ≤ Index < 1.5°C",
    "1.5°C ≤ Index < 2.0°C",
    "Index ≥ 2.0°C",
]
CATEGORY_BOUNDS = [
    (None, -2.0),
    (-2.0, -1.5),
    (-1.5, -1.0),
    (-1.0, -0.5),
    (-0.5, 0.5),
    (0.5, 1.0),
    (1.0, 1.5),
    (1.5, 2.0),
    (2.0, None),
]
EXPECTED_HEADER = ["Season", *CATEGORY_HEADINGS]
ISSUE_RE = re.compile(r"Issued\s+([A-Za-z]+)\s+(\d{4})\Z")
SEASON_RE = re.compile(r"([A-Z]{3})\b")
INTEGER_RE = re.compile(r"\d+\Z")


class _PageParser(HTMLParser):
    """Collect only visible headings and rows from the named HTML table."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.issue_headings: list[str] = []
        self.table_count = 0
        self.rows: list[list[str]] = []
        self._in_h2 = False
        self._h2_parts: list[str] = []
        self._in_target_table = False
        self._table_depth = 0
        self._row: list[str] | None = None
        self._cell_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "h2":
            self._in_h2 = True
            self._h2_parts = []
        elif tag == "table" and attributes.get("id") == "probabilities-table":
            self.table_count += 1
            if self.table_count == 1:
                self._in_target_table = True
                self._table_depth = 1
        elif self._in_target_table and tag == "table":
            self._table_depth += 1
        elif self._in_target_table and tag == "tr":
            self._row = []
        elif self._in_target_table and tag in {"th", "td"} and self._row is not None:
            self._cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self._in_h2:
            heading = _clean_text("".join(self._h2_parts))
            if heading:
                self.issue_headings.append(heading)
            self._in_h2 = False
            self._h2_parts = []
        elif self._in_target_table and tag in {"th", "td"} and self._cell_parts is not None:
            self._row.append(_clean_text("".join(self._cell_parts)))
            self._cell_parts = None
        elif self._in_target_table and tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif self._in_target_table and tag == "table":
            self._table_depth -= 1
            if self._table_depth == 0:
                self._in_target_table = False

    def handle_data(self, data: str) -> None:
        if self._in_h2:
            self._h2_parts.append(data)
        if self._cell_parts is not None:
            self._cell_parts.append(data)


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def fetch(url: str = URL, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = response.read()
        encoding = response.headers.get_content_charset() or "utf-8"
        return content.decode(encoding)


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the season count and path of the published JSON."""
    records = parse(fetch())
    dataset = build(records, ingestion_time or datetime.now(timezone.utc))
    return len(records), publish(dataset)


def parse(text: str) -> list[dict]:
    """Read the visible issue and the complete nine-category probability table."""
    parser = _PageParser()
    try:
        parser.feed(text)
        parser.close()
    except (AssertionError, ValueError) as error:
        raise ValidationError(f"HTML inválido: {error}") from None

    issue_date = read_issue_date(parser.issue_headings)
    if parser.table_count != 1:
        raise ValidationError(
            f"Se esperaba exactamente una tabla #probabilities-table, se encontraron {parser.table_count}."
        )
    if len(parser.rows) != 10:
        raise ValidationError(f"La tabla debía tener una cabecera y 9 filas, tiene {len(parser.rows)}.")
    if parser.rows[0] != EXPECTED_HEADER:
        raise ValidationError(f"Cabecera inesperada: {parser.rows[0]!r}.")

    issue_year, issue_month = (int(part) for part in issue_date.split("-"))
    issue_index = issue_year * 12 + issue_month - 1
    records = []
    previous_start = None
    first_start_index = None
    seen_seasons = set()
    for row_number, row in enumerate(parser.rows[1:], start=2):
        if len(row) != 10:
            raise ValidationError(f"Fila {row_number}: se esperaban 10 celdas, tiene {len(row)}.")
        season_match = SEASON_RE.fullmatch(row[0].split()[0]) if row[0].split() else None
        if season_match is None or season_match.group(1) not in SEASON_START_MONTH:
            raise ValidationError(f"Fila {row_number}: temporada desconocida {row[0]!r}.")
        season = season_match.group(1)
        if season in seen_seasons:
            raise ValidationError(f"Fila {row_number}: temporada repetida {season!r}.")
        seen_seasons.add(season)

        start_month = SEASON_START_MONTH[season]
        if previous_start is not None and start_month != previous_start % 12 + 1:
            raise ValidationError(f"Fila {row_number}: {season} rompe la secuencia de temporadas.")
        previous_start = start_month

        if first_start_index is None:
            if SEASON_CENTER_MONTH[season] != issue_month:
                raise ValidationError(
                    f"Fila {row_number}: la temporada {season} no está centrada en el mes de emisión."
                )
            first_start_index = issue_index - 1
            start_index = first_start_index
        else:
            start_index = first_start_index + len(records)
        start = month_iso(start_index)
        end = month_iso(start_index + 2)
        categories = []
        probabilities = []
        for column, (heading, bounds, value) in enumerate(
            zip(CATEGORY_HEADINGS, CATEGORY_BOUNDS, row[1:], strict=True), start=2
        ):
            if not INTEGER_RE.fullmatch(value):
                raise ValidationError(f"Fila {row_number}, columna {column}: porcentaje no entero {value!r}.")
            probability = int(value)
            if not 0 <= probability <= 100:
                raise ValidationError(f"Fila {row_number}, columna {column}: porcentaje fuera de rango ({probability}).")
            probabilities.append(probability)
            categories.append(
                {
                    "category": heading,
                    "lower_bound": bounds[0],
                    "upper_bound": bounds[1],
                    "probability": probability,
                }
            )
        if sum(probabilities) != 100:
            raise ValidationError(f"Fila {row_number}: los porcentajes suman {sum(probabilities)}, no 100.")
        records.append(
            {
                "issue_date": issue_date,
                "season": season,
                "start": start,
                "end": end,
                "categories": categories,
            }
        )

    if len(seen_seasons) != 9:
        raise ValidationError(f"Se esperaban 9 temporadas únicas, se encontraron {len(seen_seasons)}.")
    return records


def read_issue_date(headings: list[str]) -> str:
    """Return the single visible `Issued Month Year` heading as YYYY-MM."""
    matches = []
    for heading in headings:
        match = ISSUE_RE.fullmatch(heading)
        if match:
            month = MONTHS.get(match.group(1).lower())
            if month is None:
                raise ValidationError(f"Mes de emisión desconocido: {match.group(1)!r}.")
            matches.append(f"{match.group(2)}-{month:02d}")
    if len(matches) != 1:
        raise ValidationError(f"Se esperaba un único encabezado visible Issued, se encontraron {len(matches)}.")
    return matches[0]


def month_iso(index: int) -> str:
    """Convert zero-based months to the contract's YYYY-MM representation."""
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add registry provenance, ingestion time and processing version."""
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
        "ingestion_time": ingestion_time.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }
