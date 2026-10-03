import json
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from wawapacha_pipeline.contract import ValidationError, validate
from wawapacha_pipeline.sources import chirps

SAMPLES = Path(__file__).parent / "samples"


def boundaries(count: int = 25) -> list[dict]:
    result = []
    for index in range(count):
        column, row = index % 5, index // 5
        west, north = column * 0.05, 1 - row * 0.05
        result.append(
            {
                "name": f"Departamento {index + 1}",
                "code": f"PE{index + 1:02d}",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [west, north],
                            [west + 0.05, north],
                            [west + 0.05, north - 0.05],
                            [west, north - 0.05],
                            [west, north],
                        ]
                    ],
                },
            }
        )
    return result


def geotiff(values: np.ndarray) -> bytes:
    with rasterio.io.MemoryFile() as memory:
        with memory.open(
            driver="GTiff",
            width=values.shape[1],
            height=values.shape[0],
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=from_origin(0, 1, 0.05, 0.05),
        ) as dataset:
            dataset.write(values.astype("float32"), 1)
        return memory.read()


def test_discover_reads_live_shaped_names_and_select_window():
    links = []
    for year, month in ((2023, 10), (2024, 2), (2026, 9)):
        for number in range(1, 7):
            links.append(f'<a href="chirps-v3.0.{year}.{month:02d}.{number}.tif">x</a>')
    index = "\n".join(links)

    found = chirps.discover(index, "https://example.test/pentads/")

    assert found[0].url.endswith("2023.10.1.tif")
    assert found[-1].url.endswith("2026.09.6.tif")
    assert chirps.Pentad(2024, 2, 6, "").start == date(2024, 2, 26)
    assert chirps.Pentad(2024, 2, 6, "").end == date(2024, 2, 29)

    all_links = []
    year, month = 2023, 10
    for _ in range(36):
        for number in range(1, 7):
            all_links.append(f'<a href="chirps-v3.0.{year}.{month:02d}.{number}.tif">x</a>')
        month += 1
        if month == 13:
            year, month = year + 1, 1
    selected = chirps.select_window(chirps.discover("\n".join(all_links), "https://x/"))
    assert len(selected) == 216
    assert selected[0].start == date(2023, 10, 1)
    assert selected[-1].end == date(2026, 9, 30)


def test_aggregate_masks_cells_and_maps_missing_to_none():
    values = np.arange(1, 26, dtype=float).reshape(5, 5)
    values[0, 0] = chirps.MISSING_VALUE

    result = chirps.aggregate(geotiff(values), boundaries())

    assert result["PE01"] is None
    assert result["PE02"] == 2
    assert result["PE25"] == 25


@pytest.mark.parametrize("bad", [-0.1, 5000.1])
def test_aggregate_rejects_out_of_range_rainfall(bad):
    values = np.ones((5, 5), dtype=float)
    values[0, 0] = bad

    with pytest.raises(ValidationError, match="between 0 and 5,000"):
        chirps.aggregate(geotiff(values), boundaries())


def test_parse_builds_records_and_calculates_anomaly():
    values = np.full((5, 5), 12.34)
    period = chirps.Pentad(2026, 9, 6, "fixture.tif")
    normal = {boundary["code"]: 10.0 for boundary in boundaries()}
    baseline = {"09.6": normal}

    records = chirps.parse([(period, geotiff(values))], boundaries(), baseline)

    assert records[0] == {
        "region": "Departamento 1",
        "code": "PE01",
        "start": "2026-09-26",
        "end": "2026-09-30",
        "precipitation_mm": 12.3,
        "anomaly_mm": 2.3,
    }
    assert all(record["anomaly_mm"] == 2.3 for record in records)

    dataset = chirps.build(records, datetime(2026, 10, 3, 12, tzinfo=timezone.utc))
    validate(dataset)
    assert dataset["reference_period"] == "1991–2020"


def test_parse_keeps_input_missing_as_null():
    values = np.full((5, 5), chirps.MISSING_VALUE)
    period = chirps.Pentad(2026, 9, 6, "fixture.tif")
    baseline = {"09.6": {boundary["code"]: 10.0 for boundary in boundaries()}}

    records = chirps.parse([(period, geotiff(values))], boundaries(), baseline)

    assert all(record["precipitation_mm"] is None for record in records)
    assert all(record["anomaly_mm"] is None for record in records)


def test_sample_point_reads_native_cell():
    raw = geotiff(np.arange(1, 26, dtype=float).reshape(5, 5))

    assert chirps.sample_point(raw, 0.025, 0.975) == 1
    assert chirps.sample_point(raw, 2, 2) is None


def test_load_boundaries_reads_the_real_shaped_published_fixture():
    loaded = chirps.load_boundaries(Path(__file__).parents[2] / "data" / "limites-inei-ign.json")

    assert len(loaded) == 25
    assert loaded[0]["code"] == "PE01"
    assert loaded[0]["geometry"]["type"] in {"Polygon", "MultiPolygon"}


def test_select_window_keeps_only_files_present_in_the_listing():
    index = (SAMPLES / "chirps_index.html").read_text(encoding="utf-8")

    selected = chirps.select_window(chirps.discover(index, "https://example.test/"))

    assert [pentad.number for pentad in selected] == [1, 3]


def test_baseline_shape_is_static_and_complete():
    baseline = chirps.load_baseline()

    assert len(baseline) == 73
    assert all(len(values) == 25 for values in baseline.values())
    expected = {f"{month:02d}.{number}" for month in range(1, 13) for number in range(1, 7)}
    expected.remove("02.6")
    expected.update({"02.6-common", "02.6-leap"})
    assert set(baseline) == expected


def test_load_baseline_rejects_noncanonical_february_key(tmp_path):
    payload = json.loads(chirps.BASELINE_PATH.read_text(encoding="utf-8"))
    next(row for row in payload["records"] if row["key"] == "02.6-common")["key"] = "02.6"
    path = tmp_path / "invalid-baseline.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError, match="exact 73 calendar keys"):
        chirps.load_baseline(path)


def test_parse_uses_real_baseline_for_common_and_leap_february_pentad_six():
    baseline = chirps.load_baseline()
    raw = geotiff(np.full((5, 5), 12.34))
    periods = [
        chirps.Pentad(2025, 2, 6, "common.tif"),
        chirps.Pentad(2024, 2, 6, "leap.tif"),
    ]

    records = chirps.parse([(period, raw) for period in periods], boundaries(), baseline)

    assert periods[0].key == "02.6-common"
    assert periods[1].key == "02.6-leap"
    assert all(record["anomaly_mm"] is not None for record in records)
