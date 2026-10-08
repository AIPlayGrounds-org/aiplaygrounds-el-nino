import gzip
import json
import subprocess
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).parents[1]
SNAPSHOT = PIPELINE_DIR / "inputs" / "senamhi-estaciones-2026-10-04.json.gz"


def snapshot_check(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "snapshot-check", str(path)],
        cwd=PIPELINE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_snapshot_check_summarises_a_valid_snapshot():
    result = snapshot_check(SNAPSHOT)

    assert result.returncode == 0, result.stderr
    assert "42 stations" in result.stdout
    assert "taken 2026-10-04" in result.stdout


def test_snapshot_check_names_the_station_and_field_that_fail(tmp_path):
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as stream:
        payload = json.load(stream)
    code, station = next(iter(payload["stations"].items()))
    station["precipitation_mm"].pop()
    broken = tmp_path / "senamhi-estaciones-2026-10-05.json.gz"
    with gzip.open(broken, "wt", encoding="utf-8") as stream:
        json.dump(payload, stream)

    result = snapshot_check(broken)

    assert result.returncode == 1
    assert f"Station {code}: precipitation_mm has" in result.stderr


def test_snapshot_check_rejects_a_file_that_is_not_gzip(tmp_path):
    plain = tmp_path / "snapshot.json.gz"
    plain.write_text("{}", encoding="utf-8")

    result = snapshot_check(plain)

    assert result.returncode == 1
    assert "Could not read SENAMHI snapshot" in result.stderr
