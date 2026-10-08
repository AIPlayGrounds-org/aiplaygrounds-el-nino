"""Generates the source catalogues from the registry."""

import json
import re
from collections.abc import Iterable
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT

CATALOG_PATH = REPO_ROOT / "docs" / "sources.md"
WEB_CATALOG_PATH = REPO_ROOT / "web" / "app" / "data" / "source-catalog.json"
WIDTH = 80
LIST_MARKER = re.compile(r"\d+[.)]$")

INTRO = (
    "The sources the pipeline reads. The rest of the registry is in "
    "[`sources.toml`](../sources.toml). `uv run wawapacha-pipeline sources`, run "
    "from `pipeline/`, generates this file. Do not edit it by hand."
)
VERDICTS = (
    "Verdicts: **automatable** (the pipeline publishes it) and **manual** (a "
    "person loads it)."
)

# Map registry fields to the labels in each source's table.
FACTS = (
    ("institution", "Institution"),
    ("product", "Product"),
    ("variable", "Variable"),
    ("unit", "Unit"),
    ("data_type", "Data type"),
    ("update", "Update"),
    ("spatial_resolution", "Spatial resolution"),
    ("temporal_resolution", "Temporal resolution"),
    ("history", "History"),
    ("cadence", "Cadence"),
    ("reference_period", "Reference period"),
    ("license", "License"),
)
ACCESS_FACTS = (
    ("kind", "Access"),
    ("url", "Download URL"),
    ("format", "Format"),
    ("auth", "Authentication"),
)


def wrap(text: str, indent: str = "") -> list[str]:
    """Split the text into lines of up to 80 columns, as prettier does.

    Code spans and links stay whole. A word that Markdown would read as a list marker
    ("2020.") never starts a line: it takes the word before it along.
    """
    lines, words = [], []
    for word in re.findall(r"(?:`[^`]*`|\[[^\]]*\]\([^)]*\)|\S)+", text):
        if words and len(indent) + len(" ".join([*words, word])) > WIDTH:
            carried = (
                [words.pop()] if LIST_MARKER.match(word) and len(words) > 1 else []
            )
            lines.append(indent + " ".join(words))
            words = carried
        words.append(word)
    lines.append(indent + " ".join(words))
    return lines


def table(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> list[str]:
    cells = [header] + [tuple(cell.replace("|", "\\|") for cell in row) for row in rows]
    widths = [max(3, *(len(row[i]) for row in cells)) for i in range(len(header))]

    def line(row: tuple[str, ...]) -> str:
        return (
            "| "
            + " | ".join(
                cell.ljust(width) for cell, width in zip(row, widths, strict=True)
            )
            + " |"
        )

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    return [line(cells[0]), separator] + [line(row) for row in cells[1:]]


def section(entry: dict) -> list[str]:
    lines = [f"### {entry['id']}", ""]
    lines += wrap(f"Reviewed on {entry['reviewed']}. [Official page]({entry['page']}).")
    lines.append("")
    facts = [(label, entry[key]) for key, label in FACTS if key in entry]
    access = entry.get("access", {})
    facts += [(label, access[key]) for key, label in ACCESS_FACTS if key in access]
    lines += table(("Field", "Value"), facts)
    if entry.get("notes"):
        lines += ["", "Notes:", ""]
        for note in entry["notes"]:
            first, *rest = wrap(note, indent="  ")
            lines += ["- " + first.lstrip()] + rest
    return lines


def render(sources: dict[str, dict], built: Iterable[str]) -> str:
    """The catalog of the sources in `built`, in registry order."""
    entries = [entry for entry in sources.values() if entry["id"] in set(built)]
    inventory = [
        (
            f"[`{entry['id']}`](#{entry['id']})",
            f"{entry['institution']}: {entry['product']}",
            entry["block"],
            entry["verdict"],
        )
        for entry in entries
    ]
    lines = ["# Sources", ""] + wrap(INTRO) + [""] + wrap(VERDICTS) + [""]
    lines += table(("ID", "Source", "Block", "Verdict"), inventory)
    for entry in entries:
        lines += ["", *section(entry)]
    return "\n".join(lines) + "\n"


def render_web(
    sources: dict[str, dict], built: Iterable[str], routes: dict[str, str] | None = None
) -> str:
    """Render the registry facts the web needs as a static JSON catalogue."""
    routes = routes or registry.load_routes()
    built_ids = set(built)
    entries = []
    for entry in sources.values():
        if entry["id"] not in built_ids:
            continue
        source = {
            "id": entry["id"],
            "name": entry["product"],
            "provider": entry["institution"],
            "variable": entry["variable"],
            "unit": entry["unit"],
            "data_type": entry["data_type"],
            "spatial_resolution": entry["spatial_resolution"],
            "temporal_resolution": entry["temporal_resolution"],
            "provider_url": entry["page"],
            "data_url": entry["access"]["url"],
            "site_pages": entry["site_pages"],
        }
        for key in ("reference_period", "license"):
            if key in entry:
                source[key] = entry[key]
        stale_after = registry.stale_after(entry["update"])
        if stale_after is not None:
            source["stale_after_hours"] = int(stale_after.total_seconds() // 3600)
        entries.append(source)
    return (
        json.dumps({"routes": routes, "sources": entries}, ensure_ascii=False, indent=2)
        + "\n"
    )


def write(
    built: Iterable[str], path: Path | None = None, web_path: Path | None = None
) -> Path:
    path = path or CATALOG_PATH
    web_path = web_path or WEB_CATALOG_PATH
    path.write_text(render(registry.load(), built), encoding="utf-8", newline="\n")
    web_path.parent.mkdir(parents=True, exist_ok=True)
    web_path.write_text(
        render_web(registry.load(), built), encoding="utf-8", newline="\n"
    )
    return path
