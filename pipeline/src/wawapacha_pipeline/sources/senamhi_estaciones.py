"""SENAMHI station observations reduced to publishable monthly aggregates.

The input is a manual snapshot of the public histogram pages. Daily values
are deliberately consumed only inside this module: the published dataset has
monthly precipitation totals and temperature means, never the daily series.
"""

from __future__ import annotations

import gzip
import json
import math
from calendar import monthrange
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from statistics import median

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT, ValidationError, publish

VERSION = "0.1.0"
ID = "senamhi-estaciones"
SOURCE = registry.get(ID)
INPUT_DIRECTORY = REPO_ROOT / "pipeline" / "inputs"
MISSING_FRACTION = 0.20
VARIABLE = "Monthly station precipitation and temperature aggregates"
UNIT = "mm; °C"
DATA_TYPE = "observed"
SPATIAL_RESOLUTION = "Station point"
TEMPORAL_RESOLUTION = "Monthly"


def input_path() -> Path:
    candidates = sorted(INPUT_DIRECTORY.glob(f"{ID}-*.json.gz"))
    if not candidates:
        raise ValidationError(
            f"Expected at least one {ID}-*.json.gz input, found none."
        )
    return max(candidates, key=lambda candidate: candidate.name)


def load_snapshot(path: Path | None = None) -> dict:
    """Read the checked-in gzip snapshot without making a network request."""
    path = path or input_path()
    try:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            payload = json.load(stream)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError(
            f"Could not read SENAMHI snapshot {path}: {error}."
        ) from error
    validate_snapshot(payload)
    return payload


def validate_snapshot(payload: object) -> None:
    """Validate the snapshot envelope and all aligned daily arrays."""
    if not isinstance(payload, dict):
        raise ValidationError("SENAMHI snapshot must be an object.")
    snapshot = payload.get("snapshot")
    stations = payload.get("stations")
    if not isinstance(snapshot, dict) or not isinstance(stations, dict) or not stations:
        raise ValidationError(
            "SENAMHI snapshot needs snapshot and non-empty stations objects."
        )
    for key in ("taken", "by", "page", "station_page", "note"):
        if not isinstance(snapshot.get(key), str) or not snapshot[key]:
            raise ValidationError(f"SENAMHI snapshot metadata {key!r} is required.")
    try:
        date.fromisoformat(snapshot["taken"])
    except ValueError:
        raise ValidationError(
            f"SENAMHI snapshot taken date is invalid: {snapshot['taken']!r}."
        ) from None
    for code, station in stations.items():
        if not isinstance(code, str) or not code:
            raise ValidationError("SENAMHI station codes must be non-empty strings.")
        _validate_station(code, station)


def _validate_station(code: str, station: object) -> None:
    if not isinstance(station, dict):
        raise ValidationError(f"Station {code}: expected an object.")
    required = (
        "dep",
        "name",
        "lat",
        "lon",
        "years",
        "precipitation_mm",
        "tmax_c",
        "tmin_c",
    )
    missing = [key for key in required if key not in station]
    if missing:
        raise ValidationError(f"Station {code}: missing {missing}.")
    if not isinstance(station["dep"], str) or not station["dep"]:
        raise ValidationError(f"Station {code}: department must be a non-empty string.")
    if not isinstance(station["name"], str) or not station["name"]:
        raise ValidationError(f"Station {code}: name must be a non-empty string.")
    for key in ("lat", "lon"):
        if not finite_number(station[key]):
            raise ValidationError(f"Station {code}: {key} must be finite.")

    years = station["years"]
    if not isinstance(years, list) or not years:
        raise ValidationError(f"Station {code}: years must be a non-empty list.")
    normalized_years: list[tuple[int, int]] = []
    for position, item in enumerate(years, start=1):
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], int)
        ):
            raise ValidationError(f"Station {code}: years item {position} is invalid.")
        try:
            year = int(item[0])
            date(year, 1, 1)
        except (TypeError, ValueError):
            raise ValidationError(
                f"Station {code}: invalid year {item[0]!r}."
            ) from None
        normalized_years.append((year, item[1]))
    for previous, current in zip(normalized_years, normalized_years[1:], strict=False):
        if current[0] != previous[0] + 1:
            raise ValidationError(f"Station {code}: years are not consecutive.")
    for position, (year, days) in enumerate(normalized_years):
        calendar_days = 366 if _is_leap(year) else 365
        if not 1 <= days <= calendar_days:
            raise ValidationError(
                f"Station {code}: {year} has invalid day count {days}."
            )
        if position not in (0, len(normalized_years) - 1) and days != calendar_days:
            raise ValidationError(
                f"Station {code}: {year} has {days} days; complete interior years are required."
            )

    expected = sum(days for _, days in normalized_years)
    for key in ("precipitation_mm", "tmax_c", "tmin_c"):
        values = station[key]
        if not isinstance(values, list) or len(values) != expected:
            found = len(values) if isinstance(values, list) else "not a list"
            raise ValidationError(
                f"Station {code}: {key} has {found} values; expected {expected}."
            )
        for position, value in enumerate(values, start=1):
            if value is not None and not finite_number(value):
                raise ValidationError(
                    f"Station {code}: {key} value {position} is invalid."
                )
            if key == "precipitation_mm" and value is not None and value < 0:
                raise ValidationError(
                    f"Station {code}: precipitation cannot be negative."
                )


def finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _daily_values(station: dict, key: str) -> list[tuple[date, float | None]]:
    result: list[tuple[date, float | None]] = []
    offset = 0
    for year_text, days in station["years"]:
        first = date(int(year_text), 1, 1)
        values = station[key][offset : offset + days]
        result.extend(
            (first + timedelta(days=day_offset), value)
            for day_offset, value in enumerate(values)
        )
        offset += days
    return result


def _monthly_value(
    values: dict[tuple[int, int], list[float | None]], month: date, kind: str
) -> tuple[float | None, int]:
    month_days = monthrange(month.year, month.month)[1]
    in_month = values.get((month.year, month.month), [])
    observed = [value for value in in_month if value is not None]
    if len(observed) / month_days < 1 - MISSING_FRACTION:
        return None, len(observed)
    if kind == "sum":
        return round(sum(observed), 1), len(observed)
    return round(sum(observed) / len(observed), 1), len(observed)


def _monthly_buckets(
    values: list[tuple[date, float | None]],
) -> dict[tuple[int, int], list[float | None]]:
    buckets: dict[tuple[int, int], list[float | None]] = {}
    for day, value in values:
        buckets.setdefault((day.year, day.month), []).append(value)
    return buckets


def _month_range(station: dict) -> list[date]:
    first_year = int(station["years"][0][0])
    last_year = int(station["years"][-1][0])
    return [
        date(year, month, 1)
        for year in range(first_year, last_year + 1)
        for month in range(1, 13)
    ]


def aggregate_station(code: str, station: dict) -> list[dict]:
    """Aggregate one station and add its calendar-month precipitation median."""
    precipitation = _monthly_buckets(_daily_values(station, "precipitation_mm"))
    tmax = _monthly_buckets(_daily_values(station, "tmax_c"))
    tmin = _monthly_buckets(_daily_values(station, "tmin_c"))
    rows = []
    for month in _month_range(station):
        precipitation_mm, precipitation_days = _monthly_value(
            precipitation, month, "sum"
        )
        tmax_c, tmax_days = _monthly_value(tmax, month, "mean")
        tmin_c, tmin_days = _monthly_value(tmin, month, "mean")
        rows.append(
            {
                "station": code,
                "region": normalise_station_name(station["name"]),
                "department": station["dep"],
                "lat": round(station["lat"], 5),
                "lon": round(station["lon"], 5),
                "start": month.strftime("%Y-%m"),
                "end": month.strftime("%Y-%m"),
                "precipitation_mm": precipitation_mm,
                "precipitation_days": precipitation_days,
                "tmax_c": tmax_c,
                "tmax_days": tmax_days,
                "tmin_c": tmin_c,
                "tmin_days": tmin_days,
                "precipitation_median_mm": None,
            }
        )
    values_by_month: dict[int, list[float]] = {}
    for row in rows:
        value = row["precipitation_mm"]
        if value is not None:
            values_by_month.setdefault(int(row["start"][5:7]), []).append(value)
    medians = {
        month: round(median(values), 1) for month, values in values_by_month.items()
    }
    for row in rows:
        row["precipitation_median_mm"] = medians.get(int(row["start"][5:7]))
    return rows


def parse(payload: dict) -> list[dict]:
    """Aggregate every station from a snapshot already validated at load."""
    records = [
        record
        for code, station in payload["stations"].items()
        for record in aggregate_station(code, station)
    ]
    if not records:
        raise ValidationError("SENAMHI snapshot produced no monthly records.")
    return records


def normalise_station_name(name: str) -> str:
    # The snapshot's replacement character represents the station's ñ.
    return name.replace("\ufffd", "Ñ")


def snapshot_time(payload: dict) -> datetime:
    return datetime.fromisoformat(payload["snapshot"]["taken"]).replace(tzinfo=UTC)


def build(records: list[dict], snapshot: dict) -> dict:
    """Add the standard envelope while preserving manual-snapshot provenance."""
    access = SOURCE.get("access", {})
    snapshot_metadata = snapshot["snapshot"]
    return {
        "id": ID,
        "source": {
            "institution": SOURCE["institution"],
            "product": f"{SOURCE['product']} (manual snapshot {snapshot_metadata['taken']})",
            "url": snapshot_metadata["page"] or access.get("url"),
        },
        "variable": SOURCE.get("variable", VARIABLE),
        "unit": SOURCE.get("unit", UNIT),
        "data_type": SOURCE.get("data_type", DATA_TYPE),
        "spatial_resolution": SOURCE.get("spatial_resolution", SPATIAL_RESOLUTION),
        "temporal_resolution": SOURCE.get("temporal_resolution", TEMPORAL_RESOLUTION),
        "ingestion_time": snapshot_time(snapshot).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }


def run() -> tuple[int, Path]:
    """Publish aggregates from the checked-in snapshot; no network is used."""
    payload = load_snapshot()
    records = parse(payload)
    dataset = build(records, payload)
    return len(records), publish(dataset)
