"""Open-Meteo Flood API — GloFAS discharge for 11 Peruvian basin points."""

from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

VERSION = "0.3.0"
ID = "open-meteo-glofas"
SOURCE = registry.get(ID)
URL = os.environ.get("OPEN_METEO_GLOFAS_URL", SOURCE["access"]["url"])

DAILY_VARIABLES = (
    "river_discharge",
    "river_discharge_mean",
    "river_discharge_median",
    "river_discharge_max",
    "river_discharge_min",
    "river_discharge_p25",
    "river_discharge_p75",
)
UNIT = "m³/s"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

POINTS = (
    {
        "name": "Piura",
        "lat": -5.19,
        "lon": -80.63,
        "grid_lat": -5.174999,
        "grid_lon": -80.62499,
    },
    {
        "name": "Tumbes",
        "lat": -3.57,
        "lon": -80.45,
        "grid_lat": -3.574997,
        "grid_lon": -80.47499,
    },
    {
        "name": "Chira",
        "lat": -4.90,
        "lon": -80.70,
        "grid_lat": -4.924999,
        "grid_lon": -80.72499,
    },
    {
        "name": "Rimac",
        "lat": -11.99,
        "lon": -76.84,
        "grid_lat": -11.974998,
        "grid_lon": -76.82499,
    },
    {
        "name": "Santa",
        "lat": -8.99,
        "lon": -78.61,
        "grid_lat": -8.974998,
        "grid_lon": -78.62499,
    },
    {
        "name": "Chillon",
        "lat": -11.83,
        "lon": -77.03,
        "grid_lat": -11.824997,
        "grid_lon": -77.024994,
    },
    {
        "name": "Canete",
        "lat": -12.90,
        "lon": -76.30,
        "grid_lat": -12.924999,
        "grid_lon": -76.32499,
    },
    {
        "name": "Ica",
        "lat": -14.07,
        "lon": -75.73,
        "grid_lat": -14.074997,
        "grid_lon": -75.72499,
    },
    {
        "name": "Pisco",
        "lat": -13.71,
        "lon": -76.20,
        "grid_lat": -13.724998,
        "grid_lon": -76.174995,
    },
    {
        "name": "Majes-Colca",
        "lat": -16.23,
        "lon": -72.47,
        "grid_lat": -16.224998,
        "grid_lon": -72.47499,
    },
    {
        "name": "Mantaro",
        "lat": -12.07,
        "lon": -75.20,
        "grid_lat": -12.074997,
        "grid_lon": -75.174995,
    },
)


def fetch(url: str = URL, timeout: int = 60) -> str:
    """Download the API response and reject non-success HTTP responses."""
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is not None and status != 200:
                raise ValidationError(f"HTTP status inesperado: {status}.")
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise ValidationError(f"HTTP status inesperado: {error.code}.") from error
    except urllib.error.URLError as error:
        raise ValidationError(
            f"No se pudo descargar GloFAS: {error.reason}."
        ) from error


def parse(text: str, as_of: date | None = None) -> list[dict]:
    """Validate a GloFAS response and expand each daily array into records."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValidationError(f"JSON inválido: {error.msg}.") from None

    if not isinstance(payload, list):
        raise ValidationError(
            f"Se esperaban {len(POINTS)} puntos y llegaron una respuesta parcial."
        )
    points = payload
    if len(points) != len(POINTS):
        raise ValidationError(
            f"Se esperaban {len(POINTS)} puntos y llegaron {len(points)}."
        )
    expected_points = POINTS

    as_of = as_of or datetime.now(UTC).date()
    if isinstance(as_of, datetime):
        as_of = as_of.date()

    records = []
    dates: list[date] | None = None
    for index, (payload_point, expected_point) in enumerate(
        zip(points, expected_points, strict=True), start=1
    ):
        daily, grid_lat, grid_lon = validate_point(payload_point, expected_point, index)
        point_dates = validate_daily_arrays(daily, index)
        if dates is None:
            dates = point_dates
        elif point_dates != dates:
            raise ValidationError(
                f"Punto {index}: las fechas no coinciden con el primer punto."
            )

        for offset, current_date in enumerate(point_dates):
            records.append(
                {
                    "point": expected_point["name"],
                    "lat": expected_point["lat"],
                    "lon": expected_point["lon"],
                    "grid_lat": grid_lat,
                    "grid_lon": grid_lon,
                    "start": current_date.isoformat(),
                    "end": current_date.isoformat(),
                    "data_type": "estimated" if current_date <= as_of else "forecast",
                    **{
                        variable: daily[variable][offset]
                        for variable in DAILY_VARIABLES
                    },
                }
            )
    return records


def validate_point(
    payload: object, expected: dict, number: int
) -> tuple[dict, float, float]:
    """Validate one named point and preserve its snapped model coordinates."""
    if not isinstance(payload, dict):
        raise ValidationError(f"Punto {number}: se esperaba un objeto.")
    try:
        grid_lat = payload["latitude"]
        grid_lon = payload["longitude"]
        daily_units = payload["daily_units"]
        daily = payload["daily"]
    except KeyError as error:
        raise ValidationError(
            f"Punto {number}: falta el campo {error.args[0]!r}."
        ) from None
    if not finite_number(grid_lat) or not finite_number(grid_lon):
        raise ValidationError(
            f"Punto {number}: coordenadas de la cuadrícula no válidas."
        )
    if grid_lat != expected["grid_lat"] or grid_lon != expected["grid_lon"]:
        raise ValidationError(
            f"Punto {number} ({expected['name']}): coordenadas snapped inesperadas."
        )
    if not isinstance(daily_units, dict):
        raise ValidationError(f"Punto {number}: daily_units no es un objeto.")
    if daily_units.get("time") != "iso8601":
        raise ValidationError(f"Punto {number}: la unidad de tiempo debe ser iso8601.")
    for variable in DAILY_VARIABLES:
        if daily_units.get(variable) != UNIT:
            raise ValidationError(
                f"Punto {number}: unidad inesperada para {variable!r}."
            )
    if not isinstance(daily, dict):
        raise ValidationError(f"Punto {number}: daily no es un objeto.")
    return daily, float(grid_lat), float(grid_lon)


def validate_daily_arrays(daily: dict, number: int) -> list[date]:
    """Validate dates, aligned arrays, missing values and physical ranges."""
    if "time" not in daily or not isinstance(daily["time"], list):
        raise ValidationError(f"Punto {number}: falta daily.time.")
    dates = []
    for position, text in enumerate(daily["time"], start=1):
        if not isinstance(text, str) or not DATE_PATTERN.fullmatch(text):
            raise ValidationError(
                f"Punto {number}, fecha {position}: fecha no ISO YYYY-MM-DD."
            )
        try:
            dates.append(date.fromisoformat(text))
        except ValueError:
            raise ValidationError(
                f"Punto {number}, fecha {position}: fecha inválida."
            ) from None
    if not dates:
        raise ValidationError(f"Punto {number}: daily.time está vacío.")
    for previous, current in zip(dates, dates[1:], strict=False):
        if current != previous + timedelta(days=1):
            raise ValidationError(
                f"Punto {number}: fechas fuera de orden o con huecos."
            )

    length = len(dates)
    for variable in DAILY_VARIABLES:
        values = daily.get(variable)
        if not isinstance(values, list) or len(values) != length:
            raise ValidationError(
                f"Punto {number}: {variable} no tiene la misma longitud que time."
            )
        for position, value in enumerate(values, start=1):
            if value is not None and (not finite_number(value) or value < 0):
                raise ValidationError(
                    f"Punto {number}, {variable} {position}: valor negativo o no finito."
                )
    return dates


def finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add the registry provenance, ingestion time and processing version."""
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
        "ingestion_time": ingestion_time.astimezone(UTC).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }
    if "reference_period" in SOURCE:
        dataset["reference_period"] = SOURCE["reference_period"]
    return dataset


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Download, validate and publish the source atomically."""
    ingestion_time = ingestion_time or datetime.now(UTC)
    records = parse(fetch(), ingestion_time.astimezone(UTC).date())
    return len(records), publish(build(records, ingestion_time))
