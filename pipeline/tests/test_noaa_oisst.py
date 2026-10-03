import gzip
import json
import os
import subprocess
import sys
import threading
from datetime import UTC, date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np
import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import REPO_ROOT, ValidationError, publish
from wawapacha_pipeline.sources import noaa_oisst as oisst

PIPELINE_DIR = Path(__file__).parents[1]
NOTEBOOK = REPO_ROOT / "notebooks" / "noaa_oisst.py"
SAMPLES = Path(__file__).parent / "samples"
# Real copies of what PSL returned on 2026-10-02: SST for 2026-09-30 and 2026-10-01, and the
# climatology for 1 October.
SST = (SAMPLES / "oisst.sst.day.mean.2026.nc").read_bytes()
CLIMATOLOGY = (SAMPLES / "oisst.sst.day.mean.ltm.1991-2020.nc").read_bytes()
NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)

OCEAN = (0.125, 260.125)  # a cell in the open Pacific, in the source's own axes
LIMIT = 20 * 1024


def cell(nc, day: int, lat: float, lon: float) -> tuple[int, int, int]:
    """The index of a cell in the sst array."""
    return (
        day,
        int(np.flatnonzero(nc.variables["lat"][:] == lat)[0]),
        int(np.flatnonzero(nc.variables["lon"][:] == lon)[0]),
    )


def anomaly_record(sst, climatology) -> dict:
    return oisst.anomaly_record(sst, climatology)[0]


@pytest.fixture
def sst():
    return oisst.read_netcdf(SST)


@pytest.fixture
def climatology():
    return oisst.read_netcdf(CLIMATOLOGY)


class Upstream:
    """A local server that answers like PSL's NCSS, with the sample files, and keeps the requests it got."""

    def __init__(self):
        self.files = {"sst": SST, "climatology": CLIMATOLOGY}
        self.requests = []
        upstream = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                upstream.requests.append(self.path)
                name = urlsplit(self.path).path.rsplit("/", 1)[-1]
                kind = "climatology" if "ltm" in name else "sst"
                body = upstream.files[kind]
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}/thredds/ncss/grid/Datasets/noaa.oisst.v2.highres"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def query(self, number: int) -> dict[str, str]:
        return {
            key: values[0]
            for key, values in parse_qs(urlsplit(self.requests[number]).query).items()
        }


@pytest.fixture
def upstream():
    server = Upstream()
    yield server
    server.server.shutdown()
    server.server.server_close()


def run_cli(upstream: Upstream, data_dir: Path) -> subprocess.CompletedProcess:
    """Run the CLI as in production, reading from `upstream` and publishing to `data_dir`."""
    env = os.environ | {
        "NOAA_OISST_URL": upstream.url,
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", "noaa-oisst"],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_reads_the_real_files(sst, climatology):
    record = anomaly_record(sst, climatology)

    assert record["start"] == record["end"] == "2026-10-01"
    assert len(record["lat"]) == 90 and len(record["lon"]) == 120
    assert (record["lat"][0], record["lat"][-1]) == (-24.75, 19.75)
    assert (record["lon"][0], record["lon"][-1]) == (-119.75, -60.25)
    assert len(record["anomaly"]) == 90 and all(
        len(row) == 120 for row in record["anomaly"]
    )
    assert record["anomaly"][0][:5] == [-0.65, -0.68, -0.67, -0.51, -0.23]
    assert record["anomaly"][45][60] == 5.47


def test_the_grid_matches_an_independent_count_of_the_native_cells(sst, climatology):
    """On 2026-10-01 the scout measured 10,812 missing 0.25° cells, a mean of +2.3352 °C and a range of -1.95 to +7.786 °C."""
    lat_index, _ = oisst.axis(sst, "lat", oisst.SOUTH, oisst.NORTH)
    lon_index, _ = oisst.axis(sst, "lon", oisst.WEST, oisst.EAST)
    today = oisst.cells(sst, 1, lat_index, lon_index)
    normal = oisst.cells(climatology, 0, lat_index, lon_index)
    anomalies = (today - normal)[~np.isnan(today - normal)]

    assert today.size - anomalies.size == 10812
    assert anomalies.mean() == pytest.approx(2.3352, abs=1e-3)
    assert (anomalies.min(), anomalies.max()) == pytest.approx((-1.95, 7.786), abs=1e-3)


def test_land_is_null_and_ocean_has_a_value(sst, climatology):
    record = anomaly_record(sst, climatology)
    row, column = (record["lat"].index(-10.25), record["lon"].index(-75.25))

    assert record["anomaly"][row][column] is None
    assert (
        record["anomaly"][record["lat"].index(-0.25)][record["lon"].index(-100.25)]
        is not None
    )
    assert sum(value is None for line in record["anomaly"] for value in line) == 2594


def test_the_file_has_cells_outside_the_box_that_are_dropped(sst):
    assert len(sst.variables["lat"][:]) == 181 and len(sst.variables["lon"][:]) == 241

    assert len(oisst.axis(sst, "lat", oisst.SOUTH, oisst.NORTH)[0]) == 180
    assert len(oisst.axis(sst, "lon", oisst.WEST, oisst.EAST)[0]) == 240


def test_block_means_ignore_missing_cells():
    nan = float("nan")

    grid = oisst.block_means(np.array([[1.0, 3.0, nan, nan], [nan, nan, nan, nan]]))

    assert grid == [[2.0, None]]


def test_block_means_are_rounded_to_two_decimals_and_never_negative_zero():
    nan = float("nan")

    grid = oisst.block_means(
        np.array([[0.123, 0.123, -0.001, nan], [0.124, 0.123, nan, nan]])
    )

    assert grid == [[0.12, 0.0]]
    assert str(grid[0][1]) == "0.0"


def test_a_missing_value_in_either_file_gives_null(sst, climatology):
    sst.variables["sst"][cell(sst, 1, *OCEAN)] = np.nan
    climatology.variables["sst"][cell(climatology, 0, 0.125, 260.375)] = np.nan

    kept = [
        float(sst.variables["sst"][cell(sst, 1, 0.375, lon)])
        - float(climatology.variables["sst"][cell(climatology, 0, 0.375, lon)])
        for lon in (260.125, 260.375)
    ]

    record = anomaly_record(sst, climatology)

    # The 2 × 2 block of lat 0.25, lon -99.75 has two missing cells: it is the mean of the other two.
    assert record["anomaly"][record["lat"].index(0.25)][
        record["lon"].index(-99.75)
    ] == round(sum(kept) / 2, 2)


def test_a_fill_value_counts_as_missing(sst, climatology):
    fill = sst.variables["sst"].missing_value
    for lat in (0.125, 0.375):
        for lon in (260.125, 260.375):
            sst.variables["sst"][cell(sst, 1, lat, lon)] = fill

    record = anomaly_record(sst, climatology)

    assert (
        record["anomaly"][record["lat"].index(0.25)][record["lon"].index(-99.75)]
        is None
    )


def test_rejects_a_file_that_is_not_netcdf():
    with pytest.raises(ValidationError, match="not a complete NetCDF classic file"):
        oisst.read_netcdf(b"<html>Service unavailable</html>")


def test_rejects_a_truncated_file():
    with pytest.raises(ValidationError, match="not a complete NetCDF classic file"):
        oisst.read_netcdf(SST[:100_000])


def test_rejects_a_missing_variable(sst, climatology):
    del sst.variables["sst"]

    with pytest.raises(ValidationError, match="no variable 'sst'"):
        anomaly_record(sst, climatology)


def test_rejects_other_units(sst, climatology):
    sst.variables["sst"].units = b"degF"

    with pytest.raises(ValidationError, match="degC"):
        anomaly_record(sst, climatology)


def test_rejects_a_changed_grid(sst, climatology):
    sst.variables["lon"][100] += 0.25

    with pytest.raises(ValidationError, match="lon is not the expected grid"):
        anomaly_record(sst, climatology)


def test_rejects_climatology_on_another_grid(sst, climatology):
    climatology.variables["lat"][100] += 0.25

    with pytest.raises(ValidationError, match="lat is not the expected grid"):
        anomaly_record(sst, climatology)


@pytest.mark.parametrize("actual_range", [None, np.array([])], ids=["missing", "empty"])
def test_rejects_a_climatology_without_an_actual_range(sst, climatology, actual_range):
    climatology.variables["time"].actual_range = actual_range

    with pytest.raises(ValidationError, match="not the one for"):
        anomaly_record(sst, climatology)


def test_rejects_days_with_a_gap(sst, climatology):
    sst.variables["time"][1] += 1

    with pytest.raises(ValidationError, match="not consecutive"):
        anomaly_record(sst, climatology)


def test_rejects_a_duplicated_day(sst, climatology):
    sst.variables["time"][1] = sst.variables["time"][0]

    with pytest.raises(ValidationError, match="not consecutive"):
        anomaly_record(sst, climatology)


def test_rejects_days_out_of_order(sst, climatology):
    sst.variables["time"][:] = sst.variables["time"][::-1].copy()

    with pytest.raises(ValidationError, match="not consecutive"):
        anomaly_record(sst, climatology)


def test_rejects_other_time_units(sst, climatology):
    sst.variables["time"].units = b"hours since 1800-01-01 00:00:00"

    with pytest.raises(ValidationError, match="Unexpected time units"):
        anomaly_record(sst, climatology)


def test_rejects_a_climatology_of_another_day(sst, climatology):
    climatology.variables["time"][0] += 1

    with pytest.raises(ValidationError, match="climatology is not the one for 10-01"):
        anomaly_record(sst, climatology)


def test_the_climatology_day_is_placed_from_the_first_day_of_the_file(climatology):
    oisst.check_climatology_day(climatology, date(2026, 10, 1))
    with pytest.raises(ValidationError):
        oisst.check_climatology_day(climatology, date(2026, 10, 2))


def test_29_february_uses_the_climatology_of_28_february(climatology):
    first = climatology.variables["time"].actual_range[0]
    climatology.variables["time"][0] = first + 31 + 27

    oisst.check_climatology_day(climatology, date(2028, 2, 29))
    oisst.check_climatology_day(climatology, date(2026, 2, 28))
    with pytest.raises(ValidationError):
        oisst.check_climatology_day(climatology, date(2026, 3, 1))


def test_rejects_an_sst_out_of_range(sst, climatology):
    sst.variables["sst"][cell(sst, 1, *OCEAN)] = 50.0

    with pytest.raises(
        ValidationError, match=r"SST out of range at lat 0.125, lon -99.875 \(50.0 °C\)"
    ):
        anomaly_record(sst, climatology)


def test_rejects_a_climatology_out_of_range(sst, climatology):
    climatology.variables["sst"][cell(climatology, 0, *OCEAN)] = -20.0

    with pytest.raises(ValidationError, match="Climatology out of range"):
        anomaly_record(sst, climatology)


def test_rejects_an_anomaly_out_of_range(sst, climatology):
    sst.variables["sst"][cell(sst, 1, *OCEAN)] = 34.0
    climatology.variables["sst"][cell(climatology, 0, *OCEAN)] = 20.0

    with pytest.raises(ValidationError, match="Anomaly out of range"):
        anomaly_record(sst, climatology)


def test_rejects_a_grid_with_almost_no_values(sst, climatology):
    sst.variables["sst"][:] = np.nan

    with pytest.raises(ValidationError, match="Only 0 of 10800 cells have a value"):
        anomaly_record(sst, climatology)


def assert_matches_registry(dataset: dict) -> None:
    entry = registry.get(dataset["id"])

    assert dataset["source"] == {
        "institution": entry["institution"],
        "product": entry["product"],
        "url": entry["access"]["url"],
    }
    assert dataset["variable"] == entry["variable"]
    assert dataset["unit"] == entry["unit"]
    assert dataset["data_type"] == entry["data_type"]
    assert dataset["spatial_resolution"] == entry["spatial_resolution"]
    assert dataset["temporal_resolution"] == entry["temporal_resolution"]
    assert dataset["reference_period"] == entry["reference_period"]


def test_build_adds_provenance_metadata():
    dataset = oisst.build(oisst.parse(SST, CLIMATOLOGY), NOW)

    assert dataset["id"] == "noaa-oisst"
    assert dataset["ingestion_time"] == "2026-10-02T12:00:00+00:00"
    assert dataset["processing_version"] == oisst.VERSION
    assert len(dataset["records"]) == 1
    assert_matches_registry(dataset)


def test_publish_writes_the_json_under_the_size_limit(tmp_path):
    dataset = oisst.build(oisst.parse(SST, CLIMATOLOGY), NOW)

    path = publish(dataset, tmp_path)

    assert json.loads(path.read_text(encoding="utf-8")) == dataset
    assert len(gzip.compress(path.read_bytes())) < LIMIT


@pytest.mark.parametrize(
    ("change", "where"),
    [
        (lambda record: record.pop("lat"), "lat"),
        (lambda record: record["anomaly"][0].__setitem__(0, "warm"), "anomaly/0/0"),
        (lambda record: record.update(start="2026-10"), "start"),
        (lambda record: record["lon"].__setitem__(0, 240.25), "lon/0"),
        (lambda record: record["anomaly"].pop(), "anomaly"),
        (lambda record: record["anomaly"][0].pop(), "anomaly/0"),
    ],
    ids=[
        "no-lat",
        "text-cell",
        "month-instead-of-day",
        "longitude-in-0-360",
        "missing-row",
        "short-row",
    ],
)
def test_publish_rejects_a_grid_that_breaks_the_grid_schema(tmp_path, change, where):
    dataset = oisst.build(oisst.parse(SST, CLIMATOLOGY), NOW)
    change(dataset["records"][0])

    with pytest.raises(ValidationError, match=where):
        publish(dataset, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_fetch_asks_for_the_region_the_last_days_and_the_climatology_of_the_latest_day(
    upstream,
):
    sst, climatology = oisst.fetch(NOW, upstream.url)

    assert (sst, climatology) == (SST, CLIMATOLOGY)
    assert [
        urlsplit(request).path.rsplit("/", 1)[-1] for request in upstream.requests
    ] == [
        "sst.day.mean.2026.nc",
        "sst.day.mean.ltm.1991-2020.nc",
    ]
    assert upstream.query(0) == {
        "var": "sst",
        "north": "20.0",
        "south": "-25.0",
        "west": "240.0",
        "east": "300.0",
        "horizStride": "1",
        "accept": "netcdf",
        "time_start": "2026-09-29T00:00:00Z",
        "time_end": "2026-10-02T00:00:00Z",
    }
    assert upstream.query(1)["time"] == "0001-10-01T00:00:00Z"


def test_in_early_january_fetch_reads_the_previous_years_file(upstream):
    oisst.fetch(datetime(2027, 1, 2, tzinfo=UTC), upstream.url)

    assert urlsplit(upstream.requests[0]).path.endswith("/sst.day.mean.2026.nc")
    assert upstream.query(0)["time_start"] == "2026-12-30T00:00:00Z"


def test_cli_publishes_the_json(upstream, tmp_path):
    result = run_cli(upstream, tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published noaa-oisst: 1 records in ")
    published = json.loads((tmp_path / "noaa-oisst.json").read_text(encoding="utf-8"))
    assert published["records"][0]["start"] == "2026-10-01"
    assert published["records"][0]["anomaly"][45][60] == 5.47
    assert_matches_registry(published)
    assert len(gzip.compress((tmp_path / "noaa-oisst.json").read_bytes())) < LIMIT


@pytest.mark.parametrize("broken", ["sst", "climatology"])
def test_cli_keeps_the_previous_json_when_validation_fails(upstream, tmp_path, broken):
    upstream.files[broken] = b"<html>Service unavailable</html>"
    previous = tmp_path / "noaa-oisst.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")

    result = run_cli(upstream, tmp_path)

    assert result.returncode == 1
    assert "not a complete NetCDF classic file" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'


def test_the_published_json_is_the_registered_source_and_under_the_size_limit():
    path = REPO_ROOT / "data" / "noaa-oisst.json"
    published = json.loads(path.read_text(encoding="utf-8"))

    assert_matches_registry(published)
    assert len(published["records"]) == 1
    assert len(gzip.compress(path.read_bytes())) < LIMIT


def test_notebook_runs_to_the_end_without_publishing(upstream, tmp_path):
    env = os.environ | {
        "NOAA_OISST_URL": upstream.url,
        "WAWAPACHA_DATA_DIR": str(tmp_path),
    }

    result = subprocess.run(
        [sys.executable, str(NOTEBOOK)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []
