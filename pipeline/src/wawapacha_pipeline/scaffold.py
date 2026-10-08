"""Creates the files a new automatable source starts from."""

import re
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT

SOURCES_DIR = Path(registry.__file__).parent / "sources"
TESTS_DIR = REPO_ROOT / "pipeline" / "tests"
ID_PATTERN = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")

MODULE = '''"""{id}. Its provenance is in sources.toml."""

import os
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

# Increment this when the source logic changes.
VERSION = "0.1.0"

ID = "{id}"
SOURCE = registry.get(ID)
# {env} can point to a local test input. Published JSON keeps the registry URL.
URL = os.environ.get("{env}", SOURCE["access"]["url"])


def fetch(url: str = URL, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={{"User-Agent": "WawaPacha/0.1"}})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the record count and the path of the published JSON."""
    records = parse(fetch())
    dataset = build(records, ingestion_time or datetime.now(UTC))
    return len(records), publish(dataset)


def parse(text: str) -> list[dict]:
    """Convert the input into records and validate it according to docs/data-contract.md."""
    if not text.strip():
        raise ValidationError("The input is empty.")
    raise NotImplementedError


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add to the records the provenance the registry declares, the ingestion time and the version."""
    return {{
        "id": ID,
        "source": {{
            "institution": SOURCE["institution"],
            "product": SOURCE["product"],
            "url": SOURCE["access"]["url"],
        }},
        "variable": SOURCE["variable"],
        "unit": SOURCE["unit"],
        "data_type": SOURCE["data_type"],
        "spatial_resolution": SOURCE["spatial_resolution"],
        "temporal_resolution": SOURCE["temporal_resolution"],
        "ingestion_time": ingestion_time.astimezone(UTC).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }}
'''

TEST = """import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, validate
from wawapacha_pipeline.sources import {module} as source

PIPELINE_DIR = Path(__file__).parents[1]
# A copy of the original input saved on the download date.
SAMPLE_PATH = Path(__file__).parent / "samples" / "{sample}"


def test_the_cli_publishes_the_sample_as_a_valid_dataset(tmp_path):
    env = os.environ | {{
        "{env}": SAMPLE_PATH.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(tmp_path),
    }}

    result = subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", source.ID],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    published = json.loads((tmp_path / f"{{source.ID}}.json").read_text(encoding="utf-8"))
    validate(published)
    entry = registry.get(source.ID)
    assert published["source"]["institution"] == entry["institution"]
    assert published["source"]["url"] == entry["access"]["url"]


def test_parse_rejects_an_empty_input():
    with pytest.raises(ValidationError):
        source.parse("")
"""


def new_source(
    source_id: str, sources_dir: Path = SOURCES_DIR, tests_dir: Path = TESTS_DIR
) -> list[Path]:
    """Write the module and its test for `source_id`. Returns the new paths.

    The id must already be in sources.toml: the module reads its entry on import.
    """
    if not ID_PATTERN.fullmatch(source_id):
        raise ValueError(
            f"{source_id!r} must be lowercase words joined by hyphens, starting with a letter."
        )
    registry.get(source_id)
    module = registry.source_module_name(source_id).rsplit(".", 1)[1]
    values = {
        "id": source_id,
        "module": module,
        "env": f"{module.upper()}_URL",
        "sample": f"{module}.txt",
    }
    files = {
        sources_dir / f"{module}.py": MODULE.format(**values),
        tests_dir / f"test_{module}.py": TEST.format(**values),
    }
    existing = [path for path in files if path.exists()]
    if existing:
        raise FileExistsError(f"{existing[0]} already exists.")
    for path, text in files.items():
        path.write_text(text, encoding="utf-8", newline="\n")
    return list(files)
