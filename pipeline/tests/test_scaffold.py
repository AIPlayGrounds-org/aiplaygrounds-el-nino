import importlib.util
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from wawapacha_pipeline import registry, scaffold
from wawapacha_pipeline.contract import ValidationError, validate

PIPELINE_DIR = Path(__file__).parents[1]
ENTRY = {
    "id": "example-source",
    "institution": "Institution",
    "product": "Product",
    "variable": "Variable",
    "unit": "°C",
    "data_type": "observed",
    "spatial_resolution": "Global",
    "temporal_resolution": "Monthly",
    "access": {"url": "https://example.org/data.txt"},
}


@pytest.fixture(autouse=True)
def registered_example_source(monkeypatch):
    def get(source_id):
        if source_id != ENTRY["id"]:
            raise registry.RegistryError(f"{source_id}: not in sources.toml.")
        return ENTRY

    monkeypatch.setattr(registry, "get", get)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("example_source", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_new_source_writes_a_module_registry_discovery_accepts(tmp_path):
    sources_dir, tests_dir = tmp_path / "sources", tmp_path / "tests"
    sources_dir.mkdir()
    tests_dir.mkdir()

    created = scaffold.new_source("example-source", sources_dir, tests_dir)

    assert created == [
        sources_dir / "example_source.py",
        tests_dir / "test_example_source.py",
    ]
    module = load_module(created[0])
    assert module.ID == "example-source"
    assert all(callable(getattr(module, name)) for name in ("fetch", "parse", "run"))


def test_the_scaffolded_parse_rejects_empty_input_and_is_unfinished_otherwise(tmp_path):
    module = load_module(scaffold.new_source("example-source", tmp_path, tmp_path)[0])

    with pytest.raises(ValidationError):
        module.parse("")
    with pytest.raises(NotImplementedError):
        module.parse("input")


def test_the_scaffolded_build_matches_the_schema(tmp_path):
    module = load_module(scaffold.new_source("example-source", tmp_path, tmp_path)[0])

    dataset = module.build(
        [{"start": "2026-01", "end": "2026-01"}], datetime(2026, 10, 1, tzinfo=UTC)
    )

    validate(dataset)
    assert dataset["source"]["url"] == ENTRY["access"]["url"]


def test_the_scaffolded_empty_input_test_passes_as_written(tmp_path, monkeypatch):
    module_path, test_path = scaffold.new_source("example-source", tmp_path, tmp_path)
    monkeypatch.setitem(
        sys.modules,
        "wawapacha_pipeline.sources.example_source",
        load_module(module_path),
    )
    namespace = {"__file__": str(test_path)}
    exec(
        compile(test_path.read_text(encoding="utf-8"), str(test_path), "exec"),
        namespace,
    )

    # The other scaffolded test needs the author's sample, so it is not run here.
    namespace["test_parse_rejects_an_empty_input"]()


def test_the_scaffolded_test_reads_the_url_variable_the_module_reads(tmp_path):
    module_path, test_path = scaffold.new_source("example-source", tmp_path, tmp_path)

    assert '"EXAMPLE_SOURCE_URL"' in test_path.read_text(encoding="utf-8")
    assert '"EXAMPLE_SOURCE_URL"' in module_path.read_text(encoding="utf-8")


def test_new_source_refuses_to_overwrite(tmp_path):
    scaffold.new_source("example-source", tmp_path, tmp_path)

    with pytest.raises(FileExistsError):
        scaffold.new_source("example-source", tmp_path, tmp_path)


@pytest.mark.parametrize("bad_id", ["Example_Source", "1example", "-example", "a--b"])
def test_new_source_rejects_an_id_that_is_not_a_module_name(tmp_path, bad_id):
    with pytest.raises(ValueError, match="lowercase words"):
        scaffold.new_source(bad_id, tmp_path, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_new_source_rejects_an_id_missing_from_the_registry(tmp_path):
    with pytest.raises(registry.RegistryError, match="not in sources.toml"):
        scaffold.new_source("unlisted-source", tmp_path, tmp_path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("source_id", "message"),
    [("Bad_ID", "lowercase words"), ("unlisted-source", "not in sources.toml")],
)
def test_new_source_command_reports_why_it_cannot_create(source_id, message):
    result = subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "new-source", source_id],
        cwd=PIPELINE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert message in result.stderr
