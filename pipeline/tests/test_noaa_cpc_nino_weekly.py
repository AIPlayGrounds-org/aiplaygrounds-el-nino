import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish
from wawapacha_pipeline.sources import noaa_cpc_nino_weekly as weekly

PIPELINE_DIR = Path(__file__).parents[1]
NOTEBOOK_PATH = Path(__file__).parents[2] / "notebooks" / "noaa_cpc_nino_weekly.py"
SAMPLE_PATH = Path(__file__).parent / "samples" / "nino_weekly.for"
SAMPLE = SAMPLE_PATH.read_text(encoding="ascii")


def replace_line(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def run_cli(source: Path, data_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ | {
        "NOAA_CPC_NINO_WEEKLY_URL": source.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", weekly.ID],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_reads_the_whole_real_file_and_preserves_glued_and_spaced_values():
    records = weekly.parse(SAMPLE)

    assert len(records) == 60
    assert records[0] == {
        "start": "1981-09-02",
        "end": "1981-09-02",
        "nino_1_2_sst": 20.6,
        "nino_1_2_anomaly": -0.1,
        "nino_3_sst": 24.8,
        "nino_3_anomaly": -0.1,
        "nino_3_4_sst": 26.5,
        "nino_3_4_anomaly": -0.2,
        "nino_4_sst": 28.3,
        "nino_4_anomaly": -0.3,
    }
    assert records[9]["nino_3_4_anomaly"] == -1.0
    assert records[-1]["nino_1_2_anomaly"] == 1.9
    assert records[-1]["start"] == "1982-10-20"


def test_rejects_an_unexpected_preamble():
    with pytest.raises(ValidationError, match="Preamble"):
        weekly.parse(SAMPLE.replace("Nino1+2", "Nino1+3", 1))


def test_rejects_an_unexpected_nonempty_line_after_data():
    with pytest.raises(ValidationError, match="fecha inesperada"):
        weekly.parse(SAMPLE + "unexpected footer\n")


def test_rejects_a_blank_line_between_data_rows():
    first, second = SAMPLE.splitlines()[4:6]
    with pytest.raises(ValidationError, match="vacía inesperada entre los datos"):
        weekly.parse(SAMPLE.replace(first + "\n" + second, first + "\n\n" + second, 1))


def test_rejects_a_row_with_the_wrong_width():
    line = " 02SEP1981     20.6-0.1     24.8-0.1     26.5-0.2     28.3-0."
    with pytest.raises(ValidationError, match="62 caracteres"):
        weekly.parse(replace_line(SAMPLE, SAMPLE.splitlines()[4], line))


def test_rejects_a_pair_that_is_not_fixed_width_numeric():
    with pytest.raises(ValidationError, match="par SST/anomalía"):
        weekly.parse(replace_line(SAMPLE, "20.6-0.1", "20.6+0.1"))


def test_rejects_an_sst_out_of_range():
    with pytest.raises(ValidationError, match="SST fuera de rango"):
        weekly.parse(replace_line(SAMPLE, "20.6-0.1", "40.6-0.1"))


def test_rejects_an_anomaly_out_of_range():
    with pytest.raises(ValidationError, match="anomalía fuera de rango"):
        weekly.parse(replace_line(SAMPLE, "22.3 1.5", "22.3 9.5"))


def test_rejects_a_non_wednesday_date():
    with pytest.raises(ValidationError, match="miércoles"):
        weekly.parse(replace_line(SAMPLE, "02SEP1981", "03SEP1981"))


def test_rejects_a_gap():
    with pytest.raises(ValidationError, match="hueco o duplicado"):
        weekly.parse(replace_line(SAMPLE, " 09SEP1981", " 16SEP1981"))


def test_rejects_a_duplicated_week():
    first, second = SAMPLE.splitlines()[4:6]
    duplicate = SAMPLE.replace(first + "\n" + second, first + "\n" + first, 1)
    with pytest.raises(ValidationError, match="hueco o duplicado"):
        weekly.parse(duplicate)


def test_rejects_a_series_that_does_not_start_at_the_documented_date():
    with pytest.raises(ValidationError, match="1981-09-02"):
        weekly.parse(replace_line(SAMPLE, "02SEP1981", "09SEP1981"))


def test_rejects_an_empty_file():
    with pytest.raises(ValidationError, match="Preamble"):
        weekly.parse("")


class HTTPResponse:
    def __init__(self, content: bytes, headers: dict[str, str]):
        self.content = content
        self.headers = headers

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self):
        return self.content


def test_fetch_keeps_the_revision_metadata_from_an_http_header(monkeypatch):
    content = SAMPLE.encode("ascii")
    response = HTTPResponse(content, {"Last-Modified": "Wed, 02 Oct 2026 07:00:12 GMT"})

    def open_url(request, timeout):
        assert request.full_url == "https://example.test/weekly.for"
        assert timeout == 60
        return response

    monkeypatch.setattr(weekly.urllib.request, "urlopen", open_url)
    fetched = weekly.fetch("https://example.test/weekly.for")

    assert fetched.sha256 == hashlib.sha256(content).hexdigest()
    assert fetched.last_modified == "Wed, 02 Oct 2026 07:00:12 GMT"
    assert fetched.retrieved_at.endswith("+00:00")
    assert fetched.ingestion_metadata == {
        "sha256": fetched.sha256,
        "last_modified": fetched.last_modified,
        "retrieved_at": fetched.retrieved_at,
    }


def test_fetch_keeps_the_hash_when_http_has_no_last_modified(monkeypatch):
    content = SAMPLE.encode("ascii")
    monkeypatch.setattr(
        weekly.urllib.request,
        "urlopen",
        lambda request, timeout: HTTPResponse(content, {}),
    )

    fetched = weekly.fetch("https://example.test/weekly.for")

    assert fetched.sha256 == hashlib.sha256(content).hexdigest()
    assert fetched.last_modified is None


def assert_matches_registry(dataset: dict) -> None:
    entry = registry.get(dataset["id"])
    assert dataset["source"] == {
        "institution": entry["institution"],
        "product": entry["product"],
        "url": entry["access"]["url"],
    }
    for key in (
        "variable",
        "unit",
        "data_type",
        "spatial_resolution",
        "temporal_resolution",
        "reference_period",
    ):
        assert dataset[key] == entry[key]


def test_build_adds_contract_provenance():
    dataset = weekly.build(
        weekly.parse(SAMPLE),
        datetime(2026, 10, 2, 12, tzinfo=UTC),
        {"sha256": "a" * 64, "last_modified": None},
    )

    assert dataset["id"] == weekly.ID
    assert dataset["ingestion_time"] == "2026-10-02T12:00:00+00:00"
    assert dataset["processing_version"] == weekly.VERSION
    assert dataset["source_revision"] == {"sha256": "a" * 64, "last_modified": None}
    assert len(dataset["records"]) == 60
    assert_matches_registry(dataset)


def test_publish_writes_the_json(tmp_path):
    dataset = weekly.build(weekly.parse(SAMPLE), datetime(2026, 10, 2, 12, tzinfo=UTC))

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "noaa-cpc-nino-weekly.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


def test_cli_publishes_the_json(tmp_path):
    result = run_cli(SAMPLE_PATH, tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published noaa-cpc-nino-weekly: 60 records in ")
    published = json.loads(
        (tmp_path / "noaa-cpc-nino-weekly.json").read_text(encoding="utf-8")
    )
    assert published["records"][-1]["nino_1_2_anomaly"] == 1.9
    assert (
        published["source_revision"]["sha256"]
        == hashlib.sha256(SAMPLE_PATH.read_bytes()).hexdigest()
    )
    assert_matches_registry(published)


def test_nino_notebook_runs_to_the_end_without_publishing(tmp_path):
    env = os.environ | {
        "NOAA_CPC_NINO_WEEKLY_URL": SAMPLE_PATH.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(tmp_path),
    }

    result = subprocess.run(
        [sys.executable, str(NOTEBOOK_PATH)],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []


def test_cli_keeps_the_previous_json_when_validation_fails(tmp_path):
    broken = tmp_path / "broken.for"
    broken.write_text("contenido roto\n", encoding="ascii")
    previous = tmp_path / "noaa-cpc-nino-weekly.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")

    result = run_cli(broken, tmp_path)

    assert result.returncode == 1
    assert "Preamble inesperado" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'
