import copy
import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish
from wawapacha_pipeline.sources import open_meteo_glofas as glofas

PIPELINE_DIR = Path(__file__).parents[1]
SAMPLE_PATH = Path(__file__).parent / "samples" / "glofas.json"
SAMPLE_PAYLOAD = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
SAMPLE = SAMPLE_PATH.read_text(encoding="utf-8")


def as_text(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False)


def test_reads_the_point_list_and_expands_daily_arrays():
    records = glofas.parse(SAMPLE, date(2026, 9, 26))

    assert len(records) == 33
    assert records[0] == {
        "point": "Piura",
        "lat": -5.19,
        "lon": -80.63,
        "grid_lat": -5.174999,
        "grid_lon": -80.62499,
        "start": "2026-09-25",
        "end": "2026-09-25",
        "data_type": "estimated",
        "river_discharge": 0.06,
        "river_discharge_mean": 0.06,
        "river_discharge_median": 0.06,
        "river_discharge_max": 0.08,
        "river_discharge_min": 0.06,
        "river_discharge_p25": 0.06,
        "river_discharge_p75": 0.06,
    }
    assert records[2]["data_type"] == "forecast"
    assert records[-1]["point"] == "Mantaro"
    assert records[-1]["grid_lon"] == -75.174995


def test_rejects_a_partial_single_object_response():
    with pytest.raises(ValidationError, match="11 puntos"):
        glofas.parse(as_text(SAMPLE_PAYLOAD[0]), date(2026, 9, 26))


def test_rejects_a_basin_moved_by_one_grid_cell():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[6]["longitude"] += 0.05

    with pytest.raises(ValidationError, match="coordenadas snapped inesperadas"):
        glofas.parse(as_text(payload), date(2026, 9, 26))


def test_preserves_zero_and_null_values():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0]["daily"]["river_discharge"][0] = 0
    payload[0]["daily"]["river_discharge"][1] = None

    records = glofas.parse(as_text(payload), date(2026, 9, 26))

    assert records[0]["river_discharge"] == 0
    assert records[1]["river_discharge"] is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda payload: payload.pop(), "11 puntos"),
        (lambda payload: payload[0].pop("daily"), "'daily'"),
        (
            lambda payload: payload[0].__setitem__("latitude", -5.50),
            "coordenadas snapped inesperadas",
        ),
        (
            lambda payload: payload[0]["daily_units"].__setitem__(
                "river_discharge", "m3/s"
            ),
            "unidad inesperada",
        ),
        (lambda payload: payload[0]["daily"].pop("river_discharge"), "river_discharge"),
        (
            lambda payload: payload[0]["daily"]["river_discharge"].pop(),
            "misma longitud",
        ),
        (
            lambda payload: payload[0]["daily"]["time"].__setitem__(1, "2026-09-24"),
            "huecos",
        ),
        (
            lambda payload: payload[0]["daily"]["time"].__setitem__(1, "2026-09-99"),
            "fecha inválida",
        ),
        (
            lambda payload: payload[0]["daily"]["river_discharge"].__setitem__(0, -1),
            "negativo o no finito",
        ),
    ],
)
def test_rejects_each_structural_or_value_rule(change, message):
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    change(payload)
    broken = as_text(payload)

    with pytest.raises(ValidationError, match=message):
        glofas.parse(broken, date(2026, 9, 26))


def test_rejects_a_scalar_root():
    with pytest.raises(ValidationError, match="11 puntos"):
        glofas.parse('"not a point"', date(2026, 9, 26))


def test_rejects_invalid_json():
    with pytest.raises(ValidationError, match="JSON inválido"):
        glofas.parse("{roto", date(2026, 9, 26))


def test_rejects_a_non_finite_value():
    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload[0]["daily"]["river_discharge"][0] = float("nan")

    with pytest.raises(ValidationError, match="no finito"):
        glofas.parse(as_text(payload), date(2026, 9, 26))


def test_fetch_rejects_a_non_200_response(monkeypatch):
    response = MagicMock()
    response.status = 503
    response.__enter__.return_value = response
    monkeypatch.setattr(
        glofas.urllib.request, "urlopen", lambda request, timeout: response
    )

    with pytest.raises(ValidationError, match="503"):
        glofas.fetch("https://example.org/glofas")


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
    records = glofas.parse(SAMPLE, date(2026, 9, 26))
    dataset = glofas.build(records, datetime(2026, 10, 1, 12, 0, tzinfo=UTC))

    assert dataset["id"] == "open-meteo-glofas"
    assert dataset["ingestion_time"] == "2026-10-01T12:00:00+00:00"
    assert dataset["processing_version"] == glofas.VERSION
    assert_matches_registry(dataset)


def test_publish_validates_and_writes_typed_records(tmp_path):
    dataset = glofas.build(
        glofas.parse(SAMPLE, date(2026, 9, 26)),
        datetime(2026, 10, 1, 12, 0, tzinfo=UTC),
    )

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "open-meteo-glofas.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


def run_cli(source: Path, data_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ | {
        "OPEN_METEO_GLOFAS_URL": source.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", "open-meteo-glofas"],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_publishes_the_fixture(tmp_path):
    result = run_cli(SAMPLE_PATH, tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published open-meteo-glofas: 33 records in ")
    published = json.loads(
        (tmp_path / "open-meteo-glofas.json").read_text(encoding="utf-8")
    )
    assert len(published["records"]) == 33
    assert_matches_registry(published)


def test_cli_keeps_the_previous_json_when_validation_fails(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text(as_text(SAMPLE_PAYLOAD[0]), encoding="utf-8")
    previous = tmp_path / "open-meteo-glofas.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")

    result = run_cli(broken, tmp_path)

    assert result.returncode == 1
    assert "11 puntos" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'
