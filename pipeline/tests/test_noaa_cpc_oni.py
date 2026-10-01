import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

import noaa_cpc_oni as oni
from noaa_cpc_oni import REPO_ROOT, ValidationError, publish, relative_path

PIPELINE_DIR = Path(__file__).parents[1]
SAMPLE_PATH = Path(__file__).parent / "samples" / "oni.ascii.txt"
# Copia real del archivo de NOAA descargada el 2026-10-01.
SAMPLE = SAMPLE_PATH.read_text(encoding="ascii")


def replace_line(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def run_notebook(source: Path, data_dir: Path) -> subprocess.CompletedProcess:
    """Ejecuta el notebook como script, igual que en producción, leyendo `source`."""
    env = os.environ | {"NOAA_CPC_ONI_URL": source.resolve().as_uri(), "WAWAPACHA_DATA_DIR": str(data_dir)}
    return subprocess.run(
        [sys.executable, "noaa_cpc_oni.py"], cwd=PIPELINE_DIR, env=env, capture_output=True, text=True, encoding="utf-8"
    )


def test_reads_the_whole_real_file():
    records = oni.parse(SAMPLE)

    assert len(records) == 919
    assert records[0] == {"season": "DJF", "start": "1949-12", "end": "1950-02", "sst": 25.01, "anomaly": -1.32}
    assert records[-1] == {"season": "JJA", "start": "2026-06", "end": "2026-08", "sst": 29.09, "anomaly": 1.80}


def test_ndj_ends_in_january_of_the_next_year():
    ndj_1950 = next(r for r in oni.parse(SAMPLE) if r["season"] == "NDJ" and r["start"] == "1950-11")

    assert ndj_1950["end"] == "1951-01"


def test_rejects_unexpected_header():
    with pytest.raises(ValidationError, match="Cabecera"):
        oni.parse(SAMPLE.replace("SEAS", "SEASON", 1))


def test_rejects_a_missing_season():
    with pytest.raises(ValidationError, match="hueco o duplicado"):
        oni.parse(replace_line(SAMPLE, "  NDJ 1950  25.41  -0.79\n", ""))


def test_rejects_a_duplicated_season():
    line = "  NDJ 1950  25.41  -0.79\n"
    with pytest.raises(ValidationError, match="hueco o duplicado"):
        oni.parse(replace_line(SAMPLE, line, line + line))


def test_rejects_an_anomaly_out_of_range():
    with pytest.raises(ValidationError, match="anomalía fuera de rango"):
        oni.parse(replace_line(SAMPLE, "29.09   1.80", "29.09   9.80"))


def test_rejects_a_non_numeric_value():
    with pytest.raises(ValidationError, match="no numérico"):
        oni.parse(replace_line(SAMPLE, "29.09   1.80", "29.09   n/a"))


def test_build_adds_provenance_metadata():
    dataset = oni.build(oni.parse(SAMPLE), datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc))

    assert dataset["id"] == "noaa-cpc-oni"
    assert dataset["source"]["url"] == oni.URL
    assert dataset["unit"] == "°C"
    assert dataset["data_type"] == "observado"
    assert dataset["ingestion_time"] == "2026-10-01T12:00:00+00:00"
    assert len(dataset["records"]) == 919


def test_publish_writes_the_json(tmp_path):
    dataset = oni.build(oni.parse(SAMPLE), datetime(2026, 10, 1, tzinfo=timezone.utc))

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "noaa-cpc-oni.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


def test_relative_path_inside_the_repo_uses_forward_slashes():
    assert relative_path(REPO_ROOT / "data" / "noaa-cpc-oni.json") == "data/noaa-cpc-oni.json"


def test_relative_path_outside_the_repo_keeps_the_full_path(tmp_path):
    path = tmp_path / "noaa-cpc-oni.json"

    assert relative_path(path) == Path(path).as_posix()


def test_notebook_as_script_publishes_the_json(tmp_path):
    result = run_notebook(SAMPLE_PATH, tmp_path)

    assert result.returncode == 0, result.stderr
    published = json.loads((tmp_path / "noaa-cpc-oni.json").read_text(encoding="utf-8"))
    assert len(published["records"]) == 919
    assert published["records"][-1]["anomaly"] == 1.80


def test_notebook_as_script_keeps_the_previous_json_when_validation_fails(tmp_path):
    broken = tmp_path / "roto.txt"
    broken.write_text("contenido roto\n", encoding="ascii")
    previous = tmp_path / "noaa-cpc-oni.json"
    previous.write_text('{"versión": "anterior"}', encoding="utf-8")

    result = run_notebook(broken, tmp_path)

    assert result.returncode != 0
    assert "Cabecera inesperada" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"versión": "anterior"}'
