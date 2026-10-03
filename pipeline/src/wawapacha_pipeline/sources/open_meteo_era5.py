"""Open-Meteo ERA5 daily precipitation for representative department points."""

from __future__ import annotations

import gzip
import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from shapely.geometry import Point, shape

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import DATA_DIR, ValidationError, publish as contract_publish

VERSION = "0.2.0"
ID = "open-meteo-era5"
SOURCE = registry.get(ID)
URL = os.environ.get("OPEN_METEO_ERA5_URL", "https://archive-api.open-meteo.com/v1/archive")
DAILY_VARIABLE = "precipitation_sum"
UNIT = "mm"
WINDOW_DAYS = 90
MAX_COORDINATES_PER_REQUEST = 100
MAX_DAILY_PRECIPITATION_MM = 2_000
MAX_GZIP_BYTES = 200 * 1024
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BOUNDARIES_PATH = Path(__file__).resolve().parents[4] / "data" / "limites-inei-ign.json"


def _load_points() -> tuple[dict[str, str | float], ...]:
    """Load one rounded Shapely representative point for each department."""
    try:
        payload = json.loads(BOUNDARIES_PATH.read_text(encoding="utf-8"))
        features = payload["records"][0]["departamentos"]["features"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, OSError) as error:
        raise ValidationError(f"Could not read department boundaries: {error}.") from error
    if not isinstance(features, list) or len(features) != 25:
        found = len(features) if isinstance(features, list) else "not a list"
        raise ValidationError(f"Expected 25 department boundaries, found {found}.")

    points = []
    seen_codes: set[str] = set()
    for feature in features:
        try:
            properties = feature["properties"]
            code = properties["code"]
            region = properties["name"]
            geometry = shape(feature["geometry"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValidationError(f"Invalid department boundary feature: {error}.") from error
        if not isinstance(code, str) or not re.fullmatch(r"PE\d{2}", code):
            raise ValidationError(f"Invalid department code: {code!r}.")
        if code in seen_codes:
            raise ValidationError(f"Duplicate department code: {code}.")
        seen_codes.add(code)
        representative = geometry.representative_point()
        longitude = round(representative.x, 4)
        latitude = round(representative.y, 4)
        if not geometry.covers(Point(longitude, latitude)):
            raise ValidationError(f"Rounded representative point is outside department {code}.")
        points.append({"region": region, "code": code, "lat": latitude, "lon": longitude})

    expected_codes = {f"PE{number:02d}" for number in range(1, 26)}
    if seen_codes != expected_codes:
        raise ValidationError("Department boundaries must contain PE01 through PE25.")
    return tuple(sorted(points, key=lambda point: point["code"]))


POINTS = _load_points()


def request_window(as_of: date) -> tuple[date, date]:
    """Return the inclusive 90-day window ending on the UTC ingestion date."""
    return as_of - timedelta(days=WINDOW_DAYS - 1), as_of


def build_urls(start: date, end: date, url: str = URL) -> list[str]:
    """Build the bounded coordinate requests for one inclusive date window."""
    if start > end:
        raise ValidationError("The request start date must not be after the end date.")
    urls = []
    for offset in range(0, len(POINTS), MAX_COORDINATES_PER_REQUEST):
        batch = POINTS[offset : offset + MAX_COORDINATES_PER_REQUEST]
        query = urllib.parse.urlencode(
            {
                "latitude": ",".join(str(point["lat"]) for point in batch),
                "longitude": ",".join(str(point["lon"]) for point in batch),
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": DAILY_VARIABLE,
                "models": "era5",
                "timezone": "UTC",
                "precipitation_unit": UNIT,
            }
        )
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme == "file":
            urls.append(url)
        else:
            separator = "&" if parsed.query else "?"
            urls.append(f"{url}{separator}{query}")
    return urls


def fetch(url: str = URL, timeout: int = 60) -> str:
    """Download one API response and reject non-success HTTP responses."""
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is not None and status != 200:
                raise ValidationError(f"HTTP request failed with status {status}.")
            return response.read().decode("utf-8")
    except ValidationError:
        raise
    except urllib.error.HTTPError as error:
        raise ValidationError(f"HTTP request failed with status {error.code}.") from error
    except (urllib.error.URLError, OSError, TimeoutError) as error:
        raise ValidationError(f"Could not download ERA5 data: {error}.") from error


def parse(
    text: str,
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    """Validate point responses and expand available daily precipitation values."""
    payload = _decode(text)
    if not isinstance(payload, list) or len(payload) != len(POINTS):
        found = len(payload) if isinstance(payload, list) else "a non-list response"
        raise ValidationError(f"Expected {len(POINTS)} points, found {found}.")

    point_data = []
    latest_non_null: date | None = None
    dates: list[date] | None = None
    for number, (payload_point, expected_point) in enumerate(zip(payload, POINTS), start=1):
        daily = _validate_point(payload_point, expected_point, number)
        point_dates, values = _validate_daily(daily, number)
        if start is not None and point_dates[0] != start:
            raise ValidationError(f"Point {number}: response starts on {point_dates[0]}, expected {start}.")
        if end is not None and point_dates[-1] != end:
            raise ValidationError(f"Point {number}: response ends on {point_dates[-1]}, expected {end}.")
        if dates is None:
            dates = point_dates
        elif point_dates != dates:
            raise ValidationError(f"Point {number}: dates do not match the first point.")
        for current_date, value in zip(point_dates, values):
            if value is not None and (latest_non_null is None or current_date > latest_non_null):
                latest_non_null = current_date
        point_data.append((expected_point, values))

    if dates is None or latest_non_null is None:
        raise ValidationError("Every precipitation value is null; no publishable day was found.")

    records = []
    for point, values in point_data:
        for offset, current_date in enumerate(dates):
            if current_date > latest_non_null:
                break
            records.append(
                {
                    "region": point["region"],
                    "code": point["code"],
                    "start": current_date.isoformat(),
                    "end": current_date.isoformat(),
                    "precipitation_mm": values[offset],
                }
            )
    return records


def last_non_null_day(text: str) -> date:
    """Return the latest day with at least one non-null precipitation value."""
    payload = _decode(text)
    if not isinstance(payload, list) or len(payload) != len(POINTS):
        found = len(payload) if isinstance(payload, list) else "a non-list response"
        raise ValidationError(f"Expected {len(POINTS)} points, found {found}.")
    latest: date | None = None
    for number, (payload_point, expected_point) in enumerate(zip(payload, POINTS), start=1):
        daily = _validate_point(payload_point, expected_point, number)
        dates, values = _validate_daily(daily, number)
        for current_date, value in zip(dates, values):
            if value is not None and (latest is None or current_date > latest):
                latest = current_date
    if latest is None:
        raise ValidationError("Every precipitation value is null; no latest day was found.")
    return latest


def _decode(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValidationError(f"Invalid JSON: {error.msg}.") from None


def _validate_point(payload: object, expected: dict, number: int) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError(f"Point {number}: expected an object.")
    try:
        latitude = payload["latitude"]
        longitude = payload["longitude"]
        daily_units = payload["daily_units"]
        daily = payload["daily"]
    except KeyError as error:
        raise ValidationError(f"Point {number}: missing field {error.args[0]!r}.") from None
    if not finite_number(latitude) or not finite_number(longitude):
        raise ValidationError(f"Point {number}: snapped coordinates are not finite numbers.")
    if not _on_grid(latitude) or not _on_grid(longitude):
        raise ValidationError(f"Point {number}: snapped coordinates are not on the 0.25-degree grid.")
    if abs(latitude - expected["lat"]) > 0.25 or abs(longitude - expected["lon"]) > 0.25:
        raise ValidationError(f"Point {number} ({expected['code']}): unexpected snapped coordinates.")
    if not isinstance(daily_units, dict):
        raise ValidationError(f"Point {number}: daily_units is not an object.")
    if daily_units.get("time") != "iso8601":
        raise ValidationError(f"Point {number}: time unit must be iso8601.")
    if daily_units.get(DAILY_VARIABLE) != UNIT:
        raise ValidationError(f"Point {number}: precipitation unit must be {UNIT}.")
    if not isinstance(daily, dict):
        raise ValidationError(f"Point {number}: daily is not an object.")
    return daily


def _validate_daily(daily: dict, number: int) -> tuple[list[date], list[float | None]]:
    times = daily.get("time")
    values = daily.get(DAILY_VARIABLE)
    if not isinstance(times, list):
        raise ValidationError(f"Point {number}: daily.time is missing or not a list.")
    if not isinstance(values, list) or len(values) != len(times):
        raise ValidationError(f"Point {number}: precipitation_sum must match daily.time length.")
    dates = []
    for position, text in enumerate(times, start=1):
        if not isinstance(text, str) or not DATE_PATTERN.fullmatch(text):
            raise ValidationError(f"Point {number}, date {position}: expected ISO YYYY-MM-DD.")
        try:
            dates.append(date.fromisoformat(text))
        except ValueError:
            raise ValidationError(f"Point {number}, date {position}: invalid date.") from None
    if not dates:
        raise ValidationError(f"Point {number}: daily.time is empty.")
    for previous, current in zip(dates, dates[1:]):
        if current != previous + timedelta(days=1):
            raise ValidationError(f"Point {number}: dates are not strictly ascending without gaps.")

    checked_values: list[float | None] = []
    for position, value in enumerate(values, start=1):
        if value is not None and (
            not finite_number(value) or value < 0 or value > MAX_DAILY_PRECIPITATION_MM
        ):
            raise ValidationError(
                f"Point {number}, precipitation_sum {position}: value is outside 0-{MAX_DAILY_PRECIPITATION_MM} mm or not finite."
            )
        checked_values.append(None if value is None else float(value))
    return dates, checked_values


def _on_grid(value: float) -> bool:
    return math.isclose(value, round(value * 4) / 4, abs_tol=1e-5)


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


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
        "ingestion_time": ingestion_time.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }


def publish(dataset: dict, data_dir: Path = DATA_DIR) -> Path:
    """Reject an oversized compressed payload before publishing atomically."""
    encoded = (json.dumps(dataset, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    compressed_size = len(gzip.compress(encoded, compresslevel=9, mtime=0))
    if compressed_size > MAX_GZIP_BYTES:
        raise ValidationError(
            f"The published JSON is {compressed_size} gzip bytes; the limit is {MAX_GZIP_BYTES}."
        )
    return contract_publish(dataset, data_dir)


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Fetch the last 90-day window, discover its lag, and publish available days."""
    ingestion_time = ingestion_time or datetime.now(timezone.utc)
    start, end = request_window(ingestion_time.astimezone(timezone.utc).date())
    responses = [fetch(url) for url in build_urls(start, end)]
    records = []
    for response in responses:
        records.extend(parse(response))
    return len(records), publish(build(records, ingestion_time), DATA_DIR)
