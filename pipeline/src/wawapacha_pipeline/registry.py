"""The source registry: loads and validates sources.toml, at the repository root."""

import importlib
import tomllib
from datetime import date
from pathlib import Path

from wawapacha_pipeline.contract import DATA_TYPES, REPO_ROOT

REGISTRY_PATH = REPO_ROOT / "sources.toml"

BLOCKS = (
    "ENSO",
    "SST",
    "Forecasts",
    "Precipitation",
    "Territory",
    "Rivers",
    "Alerts",
    "History",
)
DELIVERIES = ("v0.1", "v0.2", "v0.3", "v0.4")
VERDICTS = ("automatable", "manual", "discard", "pending")
UPDATES = ("daily", "weekly", "monthly", "manual")

REQUIRED = (
    "id",
    "institution",
    "product",
    "block",
    "verdict",
    "delivery",
    "reviewed",
    "page",
    "update",
)
# These fields must be available to `contract.publish()` for an automated source.
REQUIRED_AUTOMATED = (
    "variable",
    "unit",
    "data_type",
    "spatial_resolution",
    "temporal_resolution",
    "site_pages",
)
OPTIONAL = ("history", "cadence", "license", "reference_period", "notes")
ACCESS = ("kind", "url", "format", "auth")
SOURCE_PACKAGE = "wawapacha_pipeline.sources"


class RegistryError(Exception):
    """sources.toml does not follow the registry format."""


def load(path: Path = REGISTRY_PATH) -> dict[str, dict]:
    """Return the sources by id, in file order."""
    with open(path, "rb") as f:
        document = tomllib.load(f)
    routes = document.get("routes", {})
    check_routes(routes)
    entries = document.get("source", [])
    sources = {}
    for entry in entries:
        check(entry, routes)
        if entry["id"] in sources:
            raise RegistryError(f"{entry['id']}: duplicate id.")
        sources[entry["id"]] = entry
    return sources


def load_routes(path: Path = REGISTRY_PATH) -> dict[str, str]:
    """Return the labelled site routes from the registry."""
    with open(path, "rb") as f:
        routes = tomllib.load(f).get("routes", {})
    check_routes(routes)
    return routes


def get(source_id: str) -> dict:
    try:
        return load()[source_id]
    except KeyError:
        raise RegistryError(f"{source_id}: not in {REGISTRY_PATH.name}.") from None


def source_module_name(source_id: str) -> str:
    """Return the module name implied by a source id."""
    return f"{SOURCE_PACKAGE}.{source_id.replace('-', '_')}"


def discover(path: Path = REGISTRY_PATH) -> dict[str, object]:
    """Import the implementation for every automatable registry entry.

    The source id determines each module name, so no dispatcher edit is needed.
    """
    sources = load(path)
    modules = {}
    for source_id, entry in sources.items():
        if entry["verdict"] != "automatable":
            continue
        module_name = source_module_name(source_id)
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name != module_name:
                raise
            raise RegistryError(
                f"{source_id}: automatable source is missing {module_name}.py."
            ) from None
        if getattr(module, "ID", None) != source_id:
            raise RegistryError(
                f"{source_id}: module ID does not match the registry id."
            )
        missing = [
            name
            for name in ("fetch", "parse", "run")
            if not callable(getattr(module, name, None))
        ]
        if missing:
            raise RegistryError(
                f"{source_id}: module is missing callable(s): {missing}."
            )
        modules[source_id] = module
    return modules


def check_routes(routes: object) -> None:
    if (
        not isinstance(routes, dict)
        or not routes
        or not all(
            isinstance(route, str)
            and route.startswith("/")
            and isinstance(label, str)
            and label
            for route, label in routes.items()
        )
    ):
        raise RegistryError("routes must map non-empty paths to labels.")


def check(entry: dict, routes: dict[str, str] | None = None) -> None:
    if routes is None:
        routes = load_routes()
    name = entry.get("id", "(no id)")
    access = entry.get("access", {})

    unknown = (
        set(entry)
        - {"access"}
        - set(REQUIRED)
        - set(REQUIRED_AUTOMATED)
        - set(OPTIONAL)
    )
    unknown_access = set(access) - set(ACCESS)
    if unknown or unknown_access:
        raise RegistryError(
            f"{name}: unknown fields: {sorted(unknown) + sorted(unknown_access)}."
        )

    required = list(REQUIRED)
    if entry.get("verdict") == "automatable":
        required += REQUIRED_AUTOMATED
    missing = [key for key in required if not entry.get(key)]
    if entry.get("verdict") == "automatable" and not access.get("url"):
        missing.append("access.url")
    if missing:
        raise RegistryError(f"{name}: missing fields: {missing}.")

    for key, allowed in (
        ("block", BLOCKS),
        ("delivery", DELIVERIES),
        ("verdict", VERDICTS),
        ("update", UPDATES),
    ):
        if entry[key] not in allowed:
            raise RegistryError(
                f"{name}: {key} {entry[key]!r} is not one of {list(allowed)}."
            )
    if "data_type" in entry and entry["data_type"] not in DATA_TYPES:
        raise RegistryError(
            f"{name}: data_type {entry['data_type']!r} is not one of {DATA_TYPES}."
        )
    try:
        date.fromisoformat(entry["reviewed"])
    except (TypeError, ValueError):
        raise RegistryError(f"{name}: reviewed must be a YYYY-MM-DD date.") from None
    notes = entry.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        raise RegistryError(f"{name}: notes must be a list of strings.")
    if "site_pages" in entry:
        site_pages = entry["site_pages"]
        if (
            not isinstance(site_pages, list)
            or not site_pages
            or not all(
                isinstance(page, str) and page.startswith("/") for page in site_pages
            )
        ):
            raise RegistryError(
                f"{name}: site_pages must be a non-empty list of paths."
            )
        if len(set(site_pages)) != len(site_pages):
            raise RegistryError(f"{name}: site_pages must not repeat a path.")
        unknown_pages = set(site_pages) - set(routes)
        if unknown_pages:
            raise RegistryError(
                f"{name}: site_pages has no label for route(s): {sorted(unknown_pages)}."
            )
