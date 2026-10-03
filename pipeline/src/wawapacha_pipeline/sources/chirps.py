"""CHIRPS v3 preliminary pentad rainfall aggregated to Peru's departments."""

from __future__ import annotations

import calendar
import html
import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from shapely.geometry import shape

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT, ValidationError, publish

VERSION = "0.1.0"
ID = "chirps"
SOURCE = registry.get(ID)
INDEX_URL = os.environ.get("CHIRPS_INDEX_URL", SOURCE["access"]["url"])
BASELINE_PATH = Path(
    os.environ.get(
        "CHIRPS_BASELINE_PATH",
        Path(__file__).with_name("chirps_baseline.json"),
    )
)
BOUNDARIES_PATH = Path(
    os.environ.get("CHIRPS_BOUNDARIES_PATH", REPO_ROOT / "data" / "limites-inei-ign.json")
)
MISSING_VALUE = -9999.0
MAX_VALUE = 5000.0
WINDOW_MONTHS = 36
EXPECTED_DEPARTMENTS = 25
EXPECTED_DEPARTMENT_CODES = frozenset(f"PE{index:02d}" for index in range(1, 26))
USER_AGENT = "WawaPacha/0.1"
FILE_PATTERN = re.compile(r"^chirps-v3\.0\.(\d{4})\.(\d{2})\.([1-6])\.tif$")


@dataclass(frozen=True, order=True)
class Pentad:
    """One CHIRPS filename and its calendar period."""

    year: int
    month: int
    number: int
    url: str

    @property
    def start(self) -> date:
        return date(self.year, self.month, 1) + timedelta(days=(self.number - 1) * 5)

    @property
    def end(self) -> date:
        if self.number < 6:
            return date(self.year, self.month, self.number * 5)
        return date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])

    @property
    def key(self) -> str:
        if self.month == 2 and self.number == 6:
            calendar_kind = "leap" if self.end.day == 29 else "common"
            return f"02.6-{calendar_kind}"
        return f"{self.month:02d}.{self.number}"


EXPECTED_BASELINE_KEYS = frozenset(
    Pentad(2025, month, number, "").key
    for month in range(1, 13)
    for number in range(1, 7)
) | frozenset({Pentad(2024, 2, 6, "").key})


def _request(url: str, timeout: int = 60, retries: int = 3) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", None) or 200
                if status != 200:
                    raise ValidationError(f"Unexpected HTTP status: {status}.")
                return response.read()
        except ValidationError:
            raise
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
    raise ValidationError(f"Could not download {url} after {retries} attempts: {last_error}")


def fetch(url: str = INDEX_URL, timeout: int = 60, retries: int = 3) -> bytes:
    """Download an index or a GeoTIFF and require an HTTP success response."""
    return _request(url, timeout=timeout, retries=retries)


def discover(index: str | bytes, base_url: str = INDEX_URL) -> list[Pentad]:
    """Find dated preliminary pentads by parsing the live directory listing."""
    if isinstance(index, bytes):
        try:
            index = index.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValidationError(f"The CHIRPS directory listing is not UTF-8: {error}.") from error

    directory = base_url if base_url.endswith("/") else f"{base_url}/"
    found: dict[tuple[int, int, int], Pentad] = {}
    for href in re.findall(r"(?:href|HREF)=[\"']([^\"']+)[\"']", index):
        name = Path(urllib.parse.urlparse(html.unescape(href)).path).name
        match = FILE_PATTERN.fullmatch(name)
        if not match:
            continue
        year, month, number = (int(part) for part in match.groups())
        url = urllib.parse.urljoin(directory, html.unescape(href))
        key = (year, month, number)
        if key in found:
            raise ValidationError(f"The CHIRPS directory listing repeats {name}.")
        found[key] = Pentad(year, month, number, url)

    if not found:
        raise ValidationError("The CHIRPS directory listing contains no preliminary pentads.")
    return sorted(found.values())


def select_window(pentads: list[Pentad], months: int = WINDOW_MONTHS) -> list[Pentad]:
    """Select the rolling window ending at the newest file in the listing."""
    latest_month = date(pentads[-1].year, pentads[-1].month, 1)
    first_month = _shift_month(latest_month, -(months - 1))
    selected = [p for p in pentads if first_month <= date(p.year, p.month, 1) <= latest_month]
    if not selected:
        raise ValidationError("The CHIRPS listing has no pentads in the rolling window.")
    return selected


def _shift_month(value: date, offset: int) -> date:
    index = value.year * 12 + value.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def load_boundaries(path: Path = BOUNDARIES_PATH) -> list[dict]:
    """Read the published departamento geometries used as the spatial mask."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        features = payload["records"][0]["departamentos"]["features"]
    except (OSError, KeyError, TypeError, IndexError, json.JSONDecodeError) as error:
        raise ValidationError(f"Could not read departamento boundaries from {path}: {error}") from error
    if not isinstance(features, list) or len(features) != EXPECTED_DEPARTMENTS:
        raise ValidationError(f"Expected {EXPECTED_DEPARTMENTS} departamento boundaries, found {len(features) if isinstance(features, list) else 'invalid'}.")
    normalized = []
    codes = set()
    for feature in features:
        try:
            properties = feature["properties"]
            name = properties["name"]
            code = properties["code"]
            geometry = feature["geometry"]
            parsed = shape(geometry)
        except (KeyError, TypeError, ValueError) as error:
            raise ValidationError(f"Invalid departamento boundary: {error}") from error
        if not isinstance(name, str) or not isinstance(code, str) or code in codes:
            raise ValidationError("Departamento boundaries need unique names and codes.")
        if parsed.is_empty or not parsed.is_valid:
            raise ValidationError(f"Invalid geometry for departamento {code}.")
        codes.add(code)
        normalized.append({"name": name, "code": code, "geometry": geometry})
    return normalized


def aggregate(raw: bytes, boundaries: list[dict]) -> dict[str, float | None]:
    """Mask valid raster cells by each department and return the cell mean."""
    with MemoryFile(raw) as memory:
        try:
            with memory.open() as source:
                _validate_raster(source)
                data = source.read(1, masked=False).astype(float)
                valid = np.isfinite(data) & (data != MISSING_VALUE)
                values = data[valid]
                if values.size and (float(values.min()) < 0 or float(values.max()) > MAX_VALUE):
                    raise ValidationError("CHIRPS rainfall must be between 0 and 5,000 mm per pentad.")
                result = {}
                for boundary in boundaries:
                    mask = geometry_mask(
                        [boundary["geometry"]],
                        out_shape=data.shape,
                        transform=source.transform,
                        invert=True,
                        all_touched=True,
                    )
                    selected = data[valid & mask]
                    result[boundary["code"]] = (
                        float(np.mean(selected)) if selected.size else None
                    )
                return result
        except rasterio.errors.RasterioIOError as error:
            raise ValidationError(f"The CHIRPS download is not a readable GeoTIFF: {error}") from error


def _validate_raster(source: rasterio.DatasetReader) -> None:
    if source.driver != "GTiff" or source.count != 1:
        raise ValidationError("CHIRPS files must be single-band GeoTIFFs.")
    if source.crs is None or source.crs.to_epsg() != 4326:
        raise ValidationError("CHIRPS GeoTIFFs must use EPSG:4326.")
    if not np.isclose(source.res[0], 0.05, atol=0.0001) or not np.isclose(source.res[1], 0.05, atol=0.0001):
        raise ValidationError("CHIRPS GeoTIFFs must have 0.05 degree cells.")
    if source.width < 1 or source.height < 1 or not all(math.isfinite(v) for v in source.bounds):
        raise ValidationError("CHIRPS GeoTIFF has invalid dimensions or bounds.")


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, dict[str, float | None]]:
    """Load the one-time department climatology and verify its calendar shape."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload["records"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValidationError(f"Could not read CHIRPS baseline from {path}: {error}") from error
    baseline = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValidationError("The CHIRPS baseline contains a non-object row.")
        key = row.get("key")
        values = row.get("values")
        if not isinstance(key, str) or not isinstance(values, dict) or key in baseline:
            raise ValidationError("The CHIRPS baseline has invalid or duplicate keys.")
        if set(values) != EXPECTED_DEPARTMENT_CODES:
            missing = sorted(EXPECTED_DEPARTMENT_CODES - set(values))
            unexpected = sorted(set(values) - EXPECTED_DEPARTMENT_CODES)
            raise ValidationError(
                f"Baseline {key} must contain exactly the 25 departments; "
                f"missing={missing}, unexpected={unexpected}."
            )
        for code, value in values.items():
            if not re.fullmatch(r"PE\d{2}", code):
                raise ValidationError(f"Baseline {key} has an invalid department code {code!r}.")
            if value is not None and (
                not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0 <= value <= MAX_VALUE
            ):
                raise ValidationError(f"Baseline {key} has an invalid rainfall value for {code}.")
        baseline[key] = values
    if set(baseline) != EXPECTED_BASELINE_KEYS:
        missing = sorted(EXPECTED_BASELINE_KEYS - set(baseline))
        unexpected = sorted(set(baseline) - EXPECTED_BASELINE_KEYS)
        raise ValidationError(
            "The CHIRPS baseline must contain the exact 73 calendar keys; "
            f"missing={missing}, unexpected={unexpected}."
        )
    return baseline


def parse(
    files: list[tuple[Pentad, bytes]],
    boundaries: list[dict],
    baseline: dict[str, dict[str, float | None]],
) -> list[dict]:
    """Aggregate downloaded pentads and calculate anomalies from the static baseline."""
    if not files:
        raise ValidationError("No CHIRPS pentads were supplied.")
    if len(boundaries) != EXPECTED_DEPARTMENTS:
        raise ValidationError(f"Expected 25 department boundaries, found {len(boundaries)}.")
    records = []
    for pentad, raw in files:
        values = aggregate(raw, boundaries)
        for boundary in boundaries:
            code = boundary["code"]
            value = values[code]
            normal = baseline.get(pentad.key, {}).get(code)
            anomaly = None if value is None or normal is None else round(value - normal, 1)
            records.append(
                {
                    "region": boundary["name"],
                    "code": code,
                    "start": pentad.start.isoformat(),
                    "end": pentad.end.isoformat(),
                    "precipitation_mm": None if value is None else round(value, 1),
                    "anomaly_mm": anomaly,
                }
            )
    return records


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add registry provenance and publication metadata."""
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


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Discover, download, aggregate and publish the rolling CHIRPS window."""
    pentads = discover(fetch(INDEX_URL), INDEX_URL)
    selected = select_window(pentads)
    boundaries = load_boundaries()
    baseline = load_baseline()
    files = [(pentad, fetch(pentad.url)) for pentad in selected]
    records = parse(files, boundaries, baseline)
    dataset = build(records, ingestion_time or datetime.now(timezone.utc))
    return len(records), publish(dataset)


def sample_point(raw: bytes, longitude: float, latitude: float) -> float | None:
    """Read the native cell containing a WGS84 point for an independent check."""
    with MemoryFile(raw) as memory:
        with memory.open() as source:
            _validate_raster(source)
            row, column = source.index(longitude, latitude)
            if not (0 <= row < source.height and 0 <= column < source.width):
                return None
            value = float(source.read(1)[row, column])
            return None if value == MISSING_VALUE or not math.isfinite(value) else value
