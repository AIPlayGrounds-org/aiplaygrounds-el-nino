import copy
import gzip
import json
import threading
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError
from wawapacha_pipeline.sources import open_meteo_era5 as era5

SAMPLE_PATH = Path(__file__).parent / "samples" / "era5.json"
SAMPLE_PAYLOAD = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
SAMPLE = SAMPLE_PATH.read_text(encoding="utf-8")
START = date(2026, 7, 6)
END = date(2026, 10, 3)


def as_text(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False)


@contextmanager
def fixture_server(payload: object):
    body = as_text(payload).encode("utf-8")
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/era5", requests
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_loads_25_rounded_points_inside_the_departments():
    assert len(era5.POINTS) == 25
    assert [point["code"] for point in era5.POINTS] == [
        f"PE{number:02d}" for number in range(1, 26)
    ]
    assert all(len(str(point["lat"]).split(".")[-1]) <= 4 for point in era5.POINTS)
    assert all(len(str(point["lon"]).split(".")[-1]) <= 4 for point in era5.POINTS)


def test_builds_one_api_call_with_the_required_query():
    urls = era5.build_urls(date(2026, 7, 6), date(2026, 10, 3))

    assert len(urls) == 1
    query = parse_qs(urlsplit(urls[0]).query)
    assert query["daily"] == ["precipitation_sum"]
    assert query["models"] == ["era5"]
    assert query["timezone"] == ["UTC"]
    assert query["precipitation_unit"] == ["mm"]
    assert query["cell_selection"] == ["nearest"]
    assert len(query["latitude"][0].split(",")) == 25
    assert len(query["longitude"][0].split(",")) == 25


def test_expands_daily_arrays_and_discovers_the_null_tail():
    records = era5.parse(SAMPLE, START, END)

    assert era5.last_non_null_day(records) == date(2026, 9, 27)
    assert len(records) == 25 * 84
    assert records[0] == {
        "region": "Amazonas",
        "code": "PE01",
        "start": "2026-07-06",
        "end": "2026-07-06",
        "precipitation_mm": 0.0,
    }
    assert records[-1] == {
        "region": "Ucayali",
        "code": "PE25",
        "start": "2026-09-27",
        "end": "2026-09-27",
        "precipitation_mm": 0.2,
    }
    assert all(record["end"] <= "2026-09-27" for record in records)


def test_preserves_zero_and_null_values():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0]["daily"]["precipitation_sum"][0] = 0
    payload[0]["daily"]["precipitation_sum"][1] = None

    records = era5.parse(as_text(payload), START, END)

    assert records[0]["precipitation_mm"] == 0
    assert records[1]["precipitation_mm"] is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda payload: payload.pop(), "25 points"),
        (lambda payload: payload[0].pop("daily"), "'daily'"),
        (
            lambda payload: payload[0].__setitem__("latitude", -5.5),
            "unexpected snapped coordinates",
        ),
        (lambda payload: payload[0].__setitem__("latitude", -5.1), "0.25-degree grid"),
        (
            lambda payload: payload[0]["daily_units"].__setitem__(
                "precipitation_sum", "inch"
            ),
            "unit",
        ),
        (
            lambda payload: payload[0]["daily"]["precipitation_sum"].pop(),
            "match daily.time length",
        ),
        (
            lambda payload: payload[0]["daily"]["time"].__setitem__(1, "2026-07-08"),
            "without gaps",
        ),
        (
            lambda payload: payload[0]["daily"]["time"].__setitem__(1, "2026-99-99"),
            "invalid date",
        ),
        (
            lambda payload: payload[0]["daily"]["precipitation_sum"].__setitem__(0, -1),
            "outside 0-2000",
        ),
        (
            lambda payload: payload[0]["daily"]["precipitation_sum"].__setitem__(
                0, 2001
            ),
            "outside 0-2000",
        ),
    ],
)
def test_rejects_each_structural_coordinate_date_or_value_rule(change, message):
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    change(payload)

    with pytest.raises(ValidationError, match=message):
        era5.parse(as_text(payload), START, END)


@pytest.mark.parametrize(
    ("coordinate", "value"),
    [("latitude", -5.25), ("longitude", -78.0)],
)
def test_rejects_a_neighboring_grid_cell(coordinate, value):
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0][coordinate] = value

    with pytest.raises(ValidationError, match="unexpected snapped coordinates"):
        era5.parse(as_text(payload), START, END)


def test_rejects_invalid_json():
    with pytest.raises(ValidationError, match="Invalid JSON"):
        era5.parse("{broken", START, END)


def test_rejects_a_non_finite_value():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0]["daily"]["precipitation_sum"][0] = float("nan")

    with pytest.raises(ValidationError, match="not finite"):
        era5.parse(as_text(payload), START, END)


def test_rejects_a_huge_integer_as_a_validation_error():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0]["daily"]["precipitation_sum"][0] = 10**1000

    with pytest.raises(ValidationError, match="outside 0-2000"):
        era5.parse(as_text(payload), START, END)


def test_fetch_rejects_a_non_200_response(monkeypatch):
    response = MagicMock()
    response.status = 503
    response.__enter__.return_value = response
    monkeypatch.setattr(
        era5.urllib.request, "urlopen", lambda request, timeout: response
    )

    with pytest.raises(ValidationError, match="503"):
        era5.fetch("https://example.org/era5")


def assert_matches_registry(dataset: dict) -> None:
    entry = registry.get(dataset["id"])

    assert dataset["source"] == {
        "institution": entry["institution"],
        "product": entry["product"],
        "url": entry["access"]["url"],
    }
    for field in (
        "variable",
        "unit",
        "data_type",
        "spatial_resolution",
        "temporal_resolution",
    ):
        assert dataset[field] == entry[field]


def test_build_adds_provenance_metadata():
    records = era5.parse(SAMPLE, START, END)
    dataset = era5.build(records, datetime(2026, 10, 3, 12, 0, tzinfo=UTC))

    assert dataset["id"] == "open-meteo-era5"
    assert dataset["ingestion_time"] == "2026-10-03T12:00:00+00:00"
    assert dataset["processing_version"] == era5.VERSION
    assert_matches_registry(dataset)


def test_publish_validates_and_keeps_the_compressed_payload_under_200_kib(tmp_path):
    dataset = era5.build(
        era5.parse(SAMPLE, START, END),
        datetime(2026, 10, 3, 12, 0, tzinfo=UTC),
    )

    path = era5.publish(dataset, tmp_path)

    assert path == tmp_path / "open-meteo-era5.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset
    assert len(gzip.compress(path.read_bytes(), compresslevel=9, mtime=0)) < 200 * 1024


def test_run_publishes_the_fixture(monkeypatch, tmp_path):
    monkeypatch.setattr(era5, "DATA_DIR", tmp_path)

    with fixture_server(SAMPLE_PAYLOAD) as (url, requests):
        monkeypatch.setattr(era5, "URL", url)
        count, path = era5.run(datetime(2026, 10, 3, 12, 0, tzinfo=UTC))

    assert count == 2100
    assert path == tmp_path / "open-meteo-era5.json"
    assert len(requests) == 1
    request_query = parse_qs(urlsplit(requests[0]).query)
    assert request_query["start_date"] == ["2026-07-06"]
    assert request_query["end_date"] == ["2026-10-03"]
    published = json.loads(path.read_text(encoding="utf-8"))
    assert len(published["records"]) == 2100
    assert_matches_registry(published)


def test_run_rejects_a_shifted_response_without_publishing(monkeypatch, tmp_path):
    shifted = copy.deepcopy(SAMPLE_PAYLOAD)
    for point in shifted:
        point["daily"]["time"] = [
            (date.fromisoformat(day) + timedelta(days=1)).isoformat()
            for day in point["daily"]["time"]
        ]

    monkeypatch.setattr(era5, "DATA_DIR", tmp_path)
    with fixture_server(shifted) as (url, _requests):
        monkeypatch.setattr(era5, "URL", url)
        with pytest.raises(ValidationError, match="response starts"):
            era5.run(datetime(2026, 10, 3, 12, 0, tzinfo=UTC))

    assert not (tmp_path / "open-meteo-era5.json").exists()


def test_run_rejects_a_shortened_response_without_publishing(monkeypatch, tmp_path):
    shortened = copy.deepcopy(SAMPLE_PAYLOAD)
    for point in shortened:
        point["daily"]["time"].pop()
        point["daily"]["precipitation_sum"].pop()

    monkeypatch.setattr(era5, "DATA_DIR", tmp_path)
    with fixture_server(shortened) as (url, _requests):
        monkeypatch.setattr(era5, "URL", url)
        with pytest.raises(ValidationError, match="response ends"):
            era5.run(datetime(2026, 10, 3, 12, 0, tzinfo=UTC))

    assert not (tmp_path / "open-meteo-era5.json").exists()


def test_run_keeps_the_previous_json_when_validation_fails(monkeypatch, tmp_path):
    previous = tmp_path / "open-meteo-era5.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")
    monkeypatch.setattr(era5, "DATA_DIR", tmp_path)

    with fixture_server(SAMPLE_PAYLOAD[:-1]) as (url, _requests):
        monkeypatch.setattr(era5, "URL", url)
        with pytest.raises(ValidationError, match="25 points"):
            era5.run(datetime(2026, 10, 3, 12, 0, tzinfo=UTC))
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'
