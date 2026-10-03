import json
import os
import subprocess
import sys
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish
from wawapacha_pipeline.sources import noaa_ersst as ersst

PIPELINE_DIR = Path(__file__).parents[1]
SAMPLE_PATH = Path(__file__).parent / "samples" / "ersst.v5.el_nino.dat"
SAMPLE = SAMPLE_PATH.read_text(encoding="ascii")
FIRST_LINE = SAMPLE.splitlines()[0]


def replace_line(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def run_cli(source: Path, data_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ | {
        "NOAA_ERSST_URL": source.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", "noaa-ersst"],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_reads_the_whole_real_file_and_maps_columns():
    records = ersst.parse(SAMPLE)

    assert len(records) == 2072
    assert records[0] == {
        "start": "1854-01",
        "end": "1854-01",
        "nino3_anomaly": -0.27,
        "nino4_anomaly": -0.46,
        "nino34_anomaly": -0.70,
        "nino12_anomaly": -0.59,
    }
    assert records[-1] == {
        "start": "2026-08",
        "end": "2026-08",
        "nino3_anomaly": 3.04,
        "nino4_anomaly": 1.42,
        "nino34_anomaly": 2.53,
        "nino12_anomaly": 3.67,
    }


def test_accepts_whitespace_delimited_rows():
    first = "\t1854\t1\t-0.27\t-0.46\t-0.70\t-0.59  "

    assert ersst.parse(replace_line(SAMPLE, FIRST_LINE, first))[0]["start"] == "1854-01"


def test_marks_the_three_inclusive_event_windows():
    records = ersst.parse(SAMPLE)
    events = {
        name: [record["start"] for record in records if record.get("event") == name]
        for name in ("1982-83", "1997-98", "2017")
    }

    assert events == {
        "1982-83": [f"1982-{month:02d}" for month in range(7, 13)]
        + [f"1983-{month:02d}" for month in range(1, 12)],
        "1997-98": [f"1997-{month:02d}" for month in range(4, 13)]
        + [f"1998-{month:02d}" for month in range(1, 9)],
        "2017": [f"2017-{month:02d}" for month in range(1, 5)],
    }


def test_rejects_an_unexpected_header_or_extra_column():
    with pytest.raises(ValidationError, match="no numérico"):
        ersst.parse("year month NINO3 NINO4 NINO3.4 NINO1.2\n" + SAMPLE)

    with pytest.raises(ValidationError, match="6 columnas"):
        ersst.parse(replace_line(SAMPLE, FIRST_LINE, FIRST_LINE + " 0"))


def test_rejects_a_short_row():
    with pytest.raises(ValidationError, match="6 columnas"):
        ersst.parse(replace_line(SAMPLE, FIRST_LINE, "1854 1 -0.27 -0.46 -0.70"))


def test_rejects_a_series_that_does_not_start_in_1854():
    with pytest.raises(ValidationError, match="empezar en 1854-01"):
        ersst.parse(replace_line(SAMPLE, FIRST_LINE, "1853 12 -0.27 -0.46 -0.70 -0.59"))


def test_rejects_an_invalid_month():
    with pytest.raises(ValidationError, match="mes fuera de rango"):
        ersst.parse(replace_line(SAMPLE, FIRST_LINE, "1854 13 -0.27 -0.46 -0.70 -0.59"))


def test_rejects_a_missing_month():
    second_line = SAMPLE.splitlines()[1]

    with pytest.raises(ValidationError, match="no contiguo"):
        ersst.parse(replace_line(SAMPLE, second_line + "\n", ""))


def test_rejects_a_duplicated_month():
    second_line = SAMPLE.splitlines()[1]

    with pytest.raises(ValidationError, match="no contiguo"):
        ersst.parse(replace_line(SAMPLE, second_line + "\n", second_line + "\n" + second_line + "\n"))


@pytest.mark.parametrize("bad_value", ["not-a-number", "NaN", "inf", "-Infinity"])
def test_rejects_non_finite_or_non_numeric_values(bad_value):
    broken = replace_line(SAMPLE, "-0.27", bad_value)
    message = "no numérico" if bad_value == "not-a-number" else "números finitos"

    with pytest.raises(ValidationError, match=message):
        ersst.parse(broken)


def test_rejects_an_anomaly_outside_the_conservative_range():
    with pytest.raises(ValidationError, match="anomalía fuera de rango"):
        ersst.parse(replace_line(SAMPLE, "3.67", "10.01"))


def test_fetch_sends_a_user_agent_and_requires_http_200(monkeypatch):
    class Headers:
        def get_content_type(self):
            return "text/plain"

    class Response:
        status = 200
        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return SAMPLE.encode("ascii")

    requests = []

    def urlopen(request, timeout):
        requests.append((request, timeout))
        return Response()

    monkeypatch.setattr(ersst.urllib.request, "urlopen", urlopen)

    assert ersst.fetch("https://example.test/index", timeout=7, retries=1) == SAMPLE
    assert requests[0][0].get_header("User-agent") == "WawaPacha/0.1"
    assert requests[0][1] == 7

    class NotFound(Response):
        status = 404

    monkeypatch.setattr(ersst.urllib.request, "urlopen", lambda request, timeout: NotFound())
    with pytest.raises(ValidationError, match="HTTP status inesperado: 404"):
        ersst.fetch("https://example.test/index", retries=1)


def test_fetch_rejects_html_and_retries_transient_errors(monkeypatch):
    class Headers:
        def get_content_type(self):
            return "text/html"

    class HtmlResponse:
        status = 200
        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"<html>error</html>"

    monkeypatch.setattr(ersst.urllib.request, "urlopen", lambda request, timeout: HtmlResponse())
    with pytest.raises(ValidationError, match="parece HTML"):
        ersst.fetch("https://example.test/index", retries=1)

    calls = 0

    def eventually_works(request, timeout):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise urllib.error.URLError("temporary failure")

        class Response:
            status = 200
            headers = type("Headers", (), {"get_content_type": lambda self: "text/plain"})()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return SAMPLE.encode("ascii")

        return Response()

    monkeypatch.setattr(ersst.urllib.request, "urlopen", eventually_works)
    assert ersst.fetch("https://example.test/index", retries=2) == SAMPLE
    assert calls == 2


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


def test_build_adds_provenance_metadata():
    dataset = ersst.build(ersst.parse(SAMPLE), datetime(2026, 10, 2, 12, tzinfo=timezone.utc))

    assert dataset["id"] == "noaa-ersst"
    assert dataset["ingestion_time"] == "2026-10-02T12:00:00+00:00"
    assert dataset["processing_version"] == ersst.VERSION
    assert len(dataset["records"]) == 2072
    assert_matches_registry(dataset)


def test_publish_writes_typed_records(tmp_path):
    dataset = ersst.build(ersst.parse(SAMPLE), datetime(2026, 10, 2, 12, tzinfo=timezone.utc))

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "noaa-ersst.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


def test_cli_publishes_the_json_without_network(tmp_path):
    result = run_cli(SAMPLE_PATH, tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published noaa-ersst: 2072 records in ")
    published = json.loads((tmp_path / "noaa-ersst.json").read_text(encoding="utf-8"))
    assert published["records"][-1]["nino12_anomaly"] == 3.67
    assert_matches_registry(published)


def test_cli_keeps_the_previous_json_when_validation_fails(tmp_path):
    broken = tmp_path / "broken.txt"
    broken.write_text("1854 1 NaN -0.46 -0.70 -0.59\n", encoding="ascii")
    previous = tmp_path / "noaa-ersst.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")

    result = run_cli(broken, tmp_path)

    assert result.returncode == 1
    assert "números finitos" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'


def test_notebook_runs_to_the_end_without_publishing(tmp_path):
    notebook = Path(__file__).parents[2] / "notebooks" / "noaa_ersst.py"
    env = os.environ | {
        "NOAA_ERSST_URL": SAMPLE_PATH.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(tmp_path),
    }

    result = subprocess.run(
        [sys.executable, str(notebook)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []
