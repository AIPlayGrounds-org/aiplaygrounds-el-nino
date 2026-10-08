"""Peru administrative boundaries from the IGN dataset published by HDX."""

import io
import json
import math
import os
import re
import urllib.request
import zipfile
from datetime import UTC, date, datetime
from pathlib import Path

from shapely import coverage_is_valid, coverage_simplify
from shapely.geometry import mapping, shape
from shapely.validation import explain_validity

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import MAX_GZIP_BYTES, ValidationError, publish

VERSION = "0.2.0"
ID = "limites-inei-ign"
SOURCE = registry.get(ID)
URL = os.environ.get("LIMITES_INEI_IGN_URL", SOURCE["access"]["url"])

EXPECTED_MEMBERS = {"per_admin1.geojson", "per_admin2.geojson"}
EXPECTED_COUNTS = {"per_admin1.geojson": 25, "per_admin2.geojson": 196}
CODE_PATTERNS = {
    "per_admin1.geojson": re.compile(r"^PE\d{2}$"),
    "per_admin2.geojson": re.compile(r"^PE\d{4}$"),
}
LICENSE_URL = "https://creativecommons.org/licenses/by/3.0/igo/legalcode"
SIMPLIFICATION_TOLERANCE = 0.02


def fetch(url: str = URL, timeout: int = 60) -> bytes:
    """Download the upstream ZIP, following redirects and requiring success."""
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None) or 200
            if not 200 <= status < 300:
                raise ValidationError(f"HTTP request failed with status {status}.")
            return response.read()
    except ValidationError:
        raise
    except (OSError, TimeoutError) as error:
        raise ValidationError(
            f"Could not download the boundary ZIP: {error}"
        ) from error


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Validate, simplify and publish the one geometry record."""
    parsed = parse(fetch())
    dataset = build(parsed, ingestion_time or datetime.now(UTC))
    return len(dataset["records"]), publish(dataset, max_gzip_bytes=MAX_GZIP_BYTES)


def parse(payload: bytes) -> dict:
    """Read and validate the expected GeoJSON members from an upstream ZIP."""
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except (TypeError, zipfile.BadZipFile, ValueError) as error:
        raise ValidationError(
            f"The download is not a valid ZIP archive: {error}"
        ) from error

    with archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValidationError("The ZIP archive contains duplicate member names.")
        for name in names:
            _check_member_name(name)
        missing = EXPECTED_MEMBERS - set(names)
        if missing:
            raise ValidationError(
                f"The ZIP archive is missing expected members: {sorted(missing)}."
            )

        layers = {
            name: _read_layer(archive.read(name), name)
            for name in sorted(EXPECTED_MEMBERS)
        }

    departments = _validate_layer(layers["per_admin1.geojson"], "per_admin1.geojson")
    provinces = _validate_layer(layers["per_admin2.geojson"], "per_admin2.geojson")
    metadata = _validate_common_metadata(layers)
    _validate_parent_codes(departments, provinces)

    simplified = {
        "departamentos": _simplify(departments, "departamentos"),
        "provincias": _simplify(provinces, "provincias"),
    }
    for collection in simplified.values():
        for feature in collection["features"]:
            feature["geometry"] = _round_geometry(feature["geometry"])
    _validate_simplified(simplified["departamentos"], "departamentos")
    _validate_simplified(simplified["provincias"], "provincias")
    _validate_cross_feature_geometry(simplified["departamentos"], "departamentos")
    _validate_cross_feature_geometry(simplified["provincias"], "provincias")
    _validate_parent_codes(simplified["departamentos"], simplified["provincias"])
    return {**simplified, **metadata}


def build(parsed: dict, ingestion_time: datetime) -> dict:
    """Add contract provenance and the boundary record to parsed layers."""
    valid_on = parsed["valid_on"]
    attribution = (
        f"Peru administrative boundaries: {SOURCE['institution']}, {SOURCE['license']}. "
        "Adapted and simplified by WawaPacha."
    )
    record = {
        "start": valid_on,
        "end": valid_on,
        "version": parsed["version"],
        "departamentos": parsed["departamentos"],
        "provincias": parsed["provincias"],
        "attribution": attribution,
        "license_url": LICENSE_URL,
    }
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
        "records": [record],
    }


def _check_member_name(name: str) -> None:
    normalized = name.replace("\\", "/")
    parts = normalized.split("/")
    if normalized.startswith("/") or ".." in parts or "\\" in name:
        raise ValidationError(f"Unsafe ZIP member path: {name!r}.")


def _read_layer(raw: bytes, member: str) -> dict:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{member}: GeoJSON is not UTF-8: {error}") from error
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValidationError(f"{member}: malformed JSON: {error.msg}.") from error
    if not isinstance(value, dict):
        raise ValidationError(f"{member}: GeoJSON root must be an object.")
    return value


def _validate_layer(layer: dict, member: str) -> dict:
    if layer.get("type") != "FeatureCollection":
        raise ValidationError(f"{member}: expected a GeoJSON FeatureCollection.")
    features = layer.get("features")
    expected = EXPECTED_COUNTS[member]
    if not isinstance(features, list) or len(features) != expected:
        found = len(features) if isinstance(features, list) else "not a list"
        raise ValidationError(f"{member}: expected {expected} features, found {found}.")

    code_pattern = CODE_PATTERNS[member]
    codes: set[str] = set()
    normalized_features = []
    for index, feature in enumerate(features):
        label = f"{member} feature {index}"
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise ValidationError(f"{label}: expected a GeoJSON Feature.")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise ValidationError(f"{label}: properties must be an object.")
        name_key = "adm1_name" if member == "per_admin1.geojson" else "adm2_name"
        code_key = "adm1_pcode" if member == "per_admin1.geojson" else "adm2_pcode"
        name = properties.get(name_key)
        code = properties.get(code_key)
        if not isinstance(name, str) or not name.strip():
            raise ValidationError(f"{label}: {name_key} must be a non-empty name.")
        if not isinstance(code, str) or not code_pattern.fullmatch(code):
            raise ValidationError(f"{label}: {code_key} has an invalid code {code!r}.")
        if code in codes:
            raise ValidationError(f"{label}: duplicate code {code!r}.")
        codes.add(code)
        _validate_metadata(properties, label)
        _validate_geometry(feature.get("geometry"), label)
        normalized_properties = {"name": name.strip(), "code": code}
        if member == "per_admin2.geojson":
            normalized_properties["parent"] = code[:4]
        normalized_features.append(
            {
                "type": "Feature",
                "properties": normalized_properties,
                "geometry": feature["geometry"],
            }
        )
    return {"type": "FeatureCollection", "features": normalized_features}


def _validate_metadata(properties: dict, label: str) -> None:
    for key in ("valid_on", "version", "lang"):
        if (
            key not in properties
            or not isinstance(properties[key], str)
            or not properties[key].strip()
        ):
            raise ValidationError(f"{label}: {key} must be a non-empty string.")
    try:
        date.fromisoformat(properties["valid_on"])
    except ValueError:
        raise ValidationError(f"{label}: valid_on is not an ISO date.") from None
    if not re.fullmatch(r"v\d+", properties["version"]):
        raise ValidationError(f"{label}: version is not parseable.")
    if not re.fullmatch(r"[a-z]{2}", properties["lang"]):
        raise ValidationError(f"{label}: lang is not a two-letter code.")


def _validate_common_metadata(layers: dict[str, dict]) -> dict:
    values = []
    for member in sorted(layers):
        for feature in layers[member]["features"]:
            properties = feature["properties"]
            values.append(
                (properties["valid_on"], properties["version"], properties["lang"])
            )
    first = values[0]
    if any(value != first for value in values[1:]):
        raise ValidationError(
            "valid_on, version and lang must be consistent across both layers."
        )
    return {"valid_on": first[0], "version": first[1], "lang": first[2]}


def _round_geometry(geometry: dict) -> dict:
    """Keep four decimal places, as specified for the map payload."""

    def round_coordinates(value):
        if (
            isinstance(value, (list, tuple))
            and len(value) >= 2
            and all(
                isinstance(number, (int, float)) and not isinstance(number, bool)
                for number in value[:2]
            )
        ):
            return [
                round(number, 4) if isinstance(number, (int, float)) else number
                for number in value
            ]
        if isinstance(value, (list, tuple)):
            return [round_coordinates(child) for child in value]
        return value

    return {**geometry, "coordinates": round_coordinates(geometry["coordinates"])}


def _validate_parent_codes(departments: dict, provinces: dict) -> None:
    department_codes = {
        feature["properties"]["code"] for feature in departments["features"]
    }
    for feature in provinces["features"]:
        parent = feature["properties"]["parent"]
        if parent not in department_codes:
            raise ValidationError(
                f"Province parent code {parent!r} is not a department code."
            )


def _validate_geometry(geometry: object, label: str) -> None:
    if not isinstance(geometry, dict) or geometry.get("type") not in {
        "Polygon",
        "MultiPolygon",
    }:
        found = geometry.get("type") if isinstance(geometry, dict) else None
        raise ValidationError(
            f"{label}: geometry must be Polygon or MultiPolygon, got {found!r}."
        )
    coordinates = geometry.get("coordinates")
    if not coordinates:
        raise ValidationError(f"{label}: geometry coordinates cannot be empty.")
    _validate_coordinate_structure(geometry, label)
    try:
        parsed = shape(geometry)
    except Exception as error:
        raise ValidationError(
            f"{label}: geometry could not be parsed: {error}."
        ) from error
    if parsed.is_empty or parsed.area <= 0:
        raise ValidationError(f"{label}: geometry must have non-zero area.")

    if not parsed.is_valid:
        raise ValidationError(
            f"{label}: invalid polygon topology ({explain_validity(parsed)})."
        )


def _validate_coordinate_structure(geometry: dict, label: str) -> None:
    polygons = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    if not isinstance(polygons, list) or not polygons:
        raise ValidationError(f"{label}: geometry has no polygons.")
    for polygon in polygons:
        if not isinstance(polygon, list) or not polygon:
            raise ValidationError(f"{label}: polygon has no rings.")
        for ring in polygon:
            _validate_ring(ring, label)


def _validate_ring(ring: object, label: str) -> None:
    if not isinstance(ring, (list, tuple)) or len(ring) < 4:
        raise ValidationError(f"{label}: ring must have at least four positions.")
    points = []
    for point in ring:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            raise ValidationError(
                f"{label}: every position needs longitude and latitude."
            )
        longitude, latitude = point[:2]
        if (
            not isinstance(longitude, (int, float))
            or isinstance(longitude, bool)
            or not isinstance(latitude, (int, float))
            or isinstance(latitude, bool)
        ):
            raise ValidationError(f"{label}: coordinates must be numeric.")
        if not math.isfinite(longitude) or not math.isfinite(latitude):
            raise ValidationError(f"{label}: coordinates must be finite.")
        if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
            raise ValidationError(f"{label}: coordinate is outside WGS84 bounds.")
        points.append((longitude, latitude))
    if points[0] != points[-1]:
        raise ValidationError(f"{label}: ring is not closed.")
    if abs(_ring_area(points)) < 1e-12:
        raise ValidationError(f"{label}: ring has zero area.")


def _ring_area(points: list[tuple[float, float]]) -> float:
    return (
        sum(
            first[0] * second[1] - second[0] * first[1]
            for first, second in zip(points, points[1:], strict=False)
        )
        / 2
    )


def _simplify(collection: dict, label: str) -> dict:
    """Simplify a polygon coverage while preserving shared boundaries."""
    try:
        simplified_geometries = coverage_simplify(
            [shape(feature["geometry"]) for feature in collection["features"]],
            SIMPLIFICATION_TOLERANCE,
        )
    except Exception as error:
        raise ValidationError(
            f"Could not simplify {label} coverage: {error}."
        ) from error

    features = []
    for feature, simplified in zip(
        collection["features"], simplified_geometries, strict=True
    ):
        features.append(
            {
                "type": "Feature",
                "properties": feature["properties"],
                "geometry": mapping(simplified),
            }
        )
    return {"type": "FeatureCollection", "features": features}


def _validate_simplified(collection: dict, label: str) -> None:
    if (
        not isinstance(collection, dict)
        or collection.get("type") != "FeatureCollection"
    ):
        raise ValidationError(f"Simplified {label} is not a FeatureCollection.")
    features = collection.get("features")
    if not isinstance(features, list):
        raise ValidationError(f"Simplified {label} features must be a list.")
    codes: set[str] = set()
    for index, feature in enumerate(features):
        label_at = f"simplified {label} feature {index}"
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise ValidationError(f"{label_at}: expected a Feature.")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise ValidationError(f"{label_at}: properties must be an object.")
        name = properties.get("name")
        code = properties.get("code")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError(f"{label_at}: name must be non-empty.")
        if not isinstance(code, str) or code in codes:
            raise ValidationError(f"{label_at}: code is invalid or duplicated.")
        codes.add(code)
        _validate_geometry(feature.get("geometry"), label_at)


def _validate_cross_feature_geometry(collection: dict, label: str) -> None:
    """Require the simplified features to remain a valid polygon coverage."""
    geometries = [shape(feature["geometry"]) for feature in collection["features"]]
    if not coverage_is_valid(geometries):
        raise ValidationError(
            f"Simplified {label}: features overlap or have mismatched boundaries."
        )
