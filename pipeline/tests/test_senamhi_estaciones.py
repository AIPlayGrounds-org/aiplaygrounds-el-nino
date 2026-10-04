import gzip
import json
from pathlib import Path

import pytest

from wawapacha_pipeline.contract import ValidationError, validate
from wawapacha_pipeline.sources import senamhi_estaciones

INPUT = Path(__file__).parents[1] / "inputs" / "senamhi-estaciones-2026-10-04.json.gz"


def load_fixture() -> dict:
    with gzip.open(INPUT, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def test_snapshot_aggregates_to_months_and_keeps_daily_values_out():
    payload = load_fixture()
    records = senamhi_estaciones.parse(payload)

    assert len(payload["stations"]) == 42
    assert len(records) > 20_000
    first = records[0]
    assert first.keys() == {
        "station",
        "region",
        "department",
        "lat",
        "lon",
        "start",
        "precipitation_mm",
        "precipitation_days",
        "tmax_c",
        "tmax_days",
        "tmin_c",
        "tmin_days",
        "precipitation_median_mm",
    }
    assert len(first["start"]) == 7
    assert all("precipitation_daily" not in record for record in records)
    assert any(record["region"] == "JAYANCA (LA VIÑA)" for record in records)


def test_monthly_quality_gate_is_independent_per_variable():
    station = {
        "dep": "TEST",
        "name": "TEST",
        "lat": 0,
        "lon": 0,
        "years": [["2000", 366]],
        "precipitation_mm": [1] * 366,
        "tmax_c": [10] * 366,
        "tmin_c": [5] * 366,
    }
    station["precipitation_mm"][0:7] = [None] * 7
    station["tmax_c"][0:7] = [None] * 7
    station["tmin_c"][0:6] = [None] * 6

    january = senamhi_estaciones.aggregate_station("test", station)[0]

    assert january["precipitation_mm"] is None
    assert january["precipitation_days"] == 24
    assert january["tmax_c"] is None
    assert january["tmax_days"] == 24
    assert january["tmin_c"] == 5
    assert january["tmin_days"] == 25


def test_partial_first_year_is_the_sep_to_dec_tail():
    station = {
        "dep": "TEST",
        "name": "TEST",
        "lat": 0,
        "lon": 0,
        "years": [["2000", 122], ["2001", 365]],
        "precipitation_mm": [1] * (122 + 365),
        "tmax_c": [10] * (122 + 365),
        "tmin_c": [5] * (122 + 365),
    }

    rows = senamhi_estaciones.aggregate_station("test", station)
    tail = {row["start"]: row for row in rows if row["start"].startswith("2000-")}

    assert set(tail) == {"2000-09", "2000-10", "2000-11", "2000-12"}
    assert [tail[month]["precipitation_mm"] for month in sorted(tail)] == [
        30,
        31,
        30,
        31,
    ]
    assert [tail[month]["precipitation_days"] for month in sorted(tail)] == [
        30,
        31,
        30,
        31,
    ]


def test_interior_year_must_be_complete():
    payload = load_fixture()
    station = next(iter(payload["stations"].values()))
    station["years"][1][1] -= 1
    station["precipitation_mm"] = station["precipitation_mm"][:-1]
    station["tmax_c"] = station["tmax_c"][:-1]
    station["tmin_c"] = station["tmin_c"][:-1]

    with pytest.raises(ValidationError, match="complete interior years"):
        senamhi_estaciones.validate_snapshot(payload)


def test_build_uses_the_snapshot_date_and_valid_standard_envelope():
    payload = load_fixture()
    records = senamhi_estaciones.parse(payload)
    dataset = senamhi_estaciones.build(records, payload)

    validate(dataset)
    assert dataset["ingestion_time"] == "2026-10-04T00:00:00+00:00"
    assert "manual snapshot 2026-10-04" in dataset["source"]["product"]


def test_input_path_uses_the_newest_snapshot_name(monkeypatch, tmp_path):
    for name in (
        "senamhi-estaciones-2025-01-01.json.gz",
        "senamhi-estaciones-2026-10-04.json.gz",
    ):
        (tmp_path / name).write_bytes(b"")
    monkeypatch.setattr(senamhi_estaciones, "INPUT_DIRECTORY", tmp_path)

    assert (
        senamhi_estaciones.input_path().name == "senamhi-estaciones-2026-10-04.json.gz"
    )
