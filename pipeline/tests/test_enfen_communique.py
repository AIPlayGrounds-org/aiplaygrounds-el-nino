import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish
from wawapacha_pipeline.sources import enfen_communique as enfen

PIPELINE_DIR = Path(__file__).parents[1]
SAMPLE_PATH = Path(__file__).parent / "samples" / "enfen_17_2026.yaml"
SAMPLE = SAMPLE_PATH.read_text(encoding="utf-8")
TODAY = date(2026, 10, 2)


def replace_line(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def run_cli(source: Path, data_dir: Path) -> subprocess.CompletedProcess:
    """Run the CLI as in production, reading `source` and publishing in `data_dir`."""
    env = os.environ | {
        "ENFEN_COMMUNIQUE_PATH": str(source),
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", "enfen-communique"],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_reads_the_communique():
    assert enfen.parse(SAMPLE, TODAY) == [
        {
            "number": 17,
            "year": 2026,
            "status": "Alerta de El Niño Costero",
            "url": "https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-17-2026/",
            "start": "2026-09-28",
            "end": "2026-10-15",
            "stale": False,
            "checked_at": "2026-10-02",
        }
    ]


def test_the_seeded_input_is_valid():
    records = enfen.parse(enfen.INPUT_PATH.read_text(encoding="utf-8"), TODAY)

    assert (records[0]["number"], records[0]["year"]) == (17, 2026)


@pytest.mark.parametrize("status", enfen.STATUSES)
def test_accepts_every_official_status(status):
    text = replace_line(SAMPLE, "Alerta de El Niño Costero", status)

    assert enfen.parse(text, TODAY)[0]["status"] == status


def test_checked_at_is_optional():
    text = replace_line(SAMPLE, "  checked_at: 2026-10-02\n", "")

    assert "checked_at" not in enfen.parse(text, TODAY)[0]


def test_is_not_stale_on_the_next_due_day():
    assert enfen.parse(SAMPLE, date(2026, 10, 15))[0]["stale"] is False


def test_is_stale_the_day_after_the_next_due_date():
    assert enfen.parse(SAMPLE, date(2026, 10, 16))[0]["stale"] is True


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("enfen:", "communique:", "top-level key"),
        ("  number: 17\n", "", "Missing fields"),
        ("  next_due: 2026-10-15\n", "", "Missing fields"),
        (
            "  checked_at: 2026-10-02\n",
            "  checked_at: 2026-10-02\n  color: red\n",
            "Unknown fields",
        ),
        ("number: 17", "number: 0", "positive integer"),
        ("number: 17", 'number: "17"', "positive integer"),
        ("number: 17", "number: 17.5", "positive integer"),
        ("year: 2026", "year: 26", "four digits"),
        ("date: 2026-09-28", 'date: "2026-09-28"', "unquoted"),
        ("date: 2026-09-28", "date: 2026-02-30", "cannot be read"),
        ("date: 2026-09-28", "date: 2025-09-28", "not in year"),
        ("date: 2026-09-28", "date: 2026-10-03", "in the future"),
        ("next_due: 2026-10-15", "next_due: 2026-09-28", "after date"),
        ("checked_at: 2026-10-02", "checked_at: 2026-09-27", "before date"),
        ("checked_at: 2026-10-02", "checked_at: 2026-10-03", "in the future"),
        ('"Alerta de El Niño Costero"', '"alerta de el niño costero"', "status"),
        ('"Alerta de El Niño Costero"', '"El Niño Costero Alert"', "status"),
        ('"Alerta de El Niño Costero"', "red", "status"),
        ("https://enfen.imarpe", "http://enfen.imarpe", "url"),
        (
            "https://enfen.imarpe.gob.pe",
            "https://enfen.imarpe.gob.pe.evil.example",
            "url",
        ),
        ("https://enfen.imarpe.gob.pe", "https://www.gob.pe", "url"),
        ("-n-17-2026/", "-n-17-2026.pdf", "url"),
        ("-n-17-2026/", "-n-16-2026/", "different communiqué"),
        ("-n-17-2026/", "-n-17-2025/", "different communiqué"),
    ],
)
def test_rejects_an_invalid_input(old, new, message):
    with pytest.raises(ValidationError, match=message):
        enfen.parse(replace_line(SAMPLE, old, new), TODAY)


def test_rejects_a_repeated_communique():
    with pytest.raises(ValidationError, match="appears twice"):
        enfen.parse(SAMPLE + SAMPLE, TODAY)


@pytest.mark.parametrize("key", ["[a, b]", "{a: b}"])
def test_rejects_a_key_that_is_a_list_or_a_mapping(key):
    # YAML allows `? [a, b]` as a key. It cannot be a field name, and must not crash the run.
    text = replace_line(SAMPLE, "  number: 17\n", f"  ? {key}\n  : 17\n")

    with pytest.raises(ValidationError, match="single value"):
        enfen.parse(text, TODAY)


def test_cli_reports_a_key_that_is_a_list_without_a_traceback(tmp_path):
    broken = tmp_path / "broken.yaml"
    broken.write_text("enfen:\n  ? [a, b]\n  : 1\n", encoding="utf-8")

    result = run_cli(broken, tmp_path)

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "single value" in result.stderr


@pytest.mark.parametrize(
    "text", ["", "enfen:\n", "enfen: 17\n", "- enfen\n", "enfen: [unclosed\n"]
)
def test_rejects_a_file_that_is_not_one_enfen_mapping(text):
    with pytest.raises(ValidationError):
        enfen.parse(text, TODAY)


def test_fetch_reports_a_missing_file(tmp_path):
    with pytest.raises(ValidationError, match="Cannot read"):
        enfen.fetch(tmp_path / "absent.yaml")


def test_run_stamps_the_lima_date(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "wawapacha_pipeline.sources.enfen_communique.publish",
        lambda dataset: publish(dataset, tmp_path),
    )
    monkeypatch.setattr(enfen, "PATH", SAMPLE_PATH)
    # 2026-10-16 03:00 UTC is still 2026-10-15 22:00 in Lima: not stale yet.
    count, path = enfen.run(datetime(2026, 10, 16, 3, tzinfo=UTC))

    assert count == 1
    assert json.loads(path.read_text(encoding="utf-8"))["records"][0]["stale"] is False


def assert_matches_registry(dataset: dict) -> None:
    entry = registry.get(dataset["id"])

    assert dataset["source"] == {
        "institution": entry["institution"],
        "product": entry["product"],
        "url": entry["access"]["url"],
    }
    assert dataset["variable"] == entry["variable"]
    assert dataset["unit"] == entry["unit"]
    assert dataset["data_type"] == entry["data_type"] == "official"
    assert dataset["spatial_resolution"] == entry["spatial_resolution"]
    assert dataset["temporal_resolution"] == entry["temporal_resolution"]


def test_build_adds_provenance_metadata():
    dataset = enfen.build(
        enfen.parse(SAMPLE, TODAY), datetime(2026, 10, 2, 12, tzinfo=UTC)
    )

    assert dataset["id"] == "enfen-communique"
    assert dataset["ingestion_time"] == "2026-10-02T12:00:00+00:00"
    assert dataset["processing_version"] == enfen.VERSION
    assert len(dataset["records"]) == 1
    assert_matches_registry(dataset)


def test_publish_writes_the_json(tmp_path):
    dataset = enfen.build(enfen.parse(SAMPLE, TODAY), datetime(2026, 10, 2, tzinfo=UTC))

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "enfen-communique.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "red"),
        ("stale", "no"),
        ("start", "2026-9-28"),
        ("url", "https://example.org/communique"),
        ("number", 0),
        ("extra", 1),
    ],
)
def test_the_schema_rejects_a_bad_record(tmp_path, field, value):
    dataset = enfen.build(enfen.parse(SAMPLE, TODAY), datetime(2026, 10, 2, tzinfo=UTC))
    dataset["records"][0][field] = value

    with pytest.raises(ValidationError, match="schema"):
        publish(dataset, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_cli_publishes_the_json(tmp_path):
    result = run_cli(SAMPLE_PATH, tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published enfen-communique: 1 records in ")
    published = json.loads(
        (tmp_path / "enfen-communique.json").read_text(encoding="utf-8")
    )
    assert published["records"][0]["status"] == "Alerta de El Niño Costero"
    assert_matches_registry(published)


def test_cli_keeps_the_previous_json_when_validation_fails(tmp_path):
    broken = tmp_path / "broken.yaml"
    broken.write_text(
        replace_line(SAMPLE, "Alerta de El Niño Costero", "red"), encoding="utf-8"
    )
    previous = tmp_path / "enfen-communique.json"
    previous.write_text('{"previous": true}', encoding="utf-8")

    result = run_cli(broken, tmp_path)

    assert result.returncode == 1
    assert "status" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"previous": true}'


def test_add_writes_an_input_the_parser_reads_and_shows_the_diff(tmp_path):
    path = tmp_path / "enfen.yaml"
    path.write_text(SAMPLE, encoding="utf-8")

    diff = enfen.add(
        18,
        date(2026, 10, 15),
        "Vigilancia de El Niño Costero",
        date(2026, 10, 29),
        date(2026, 10, 16),
        path,
        today=date(2026, 10, 16),
    )

    record = enfen.parse(path.read_text(encoding="utf-8"), date(2026, 10, 16))[0]
    assert record["number"] == 18
    assert record["url"].endswith("comunicado-oficial-enfen-n-18-2026/")
    assert record["end"] == "2026-10-29"
    assert "-  number: 17" in diff
    assert "+  number: 18" in diff
    assert '+  status: "Vigilancia de El Niño Costero"' in diff


def test_add_leaves_the_input_unchanged_when_the_communique_is_invalid(tmp_path):
    path = tmp_path / "enfen.yaml"
    path.write_text(SAMPLE, encoding="utf-8")

    with pytest.raises(ValidationError, match="status"):
        enfen.add(
            18, date(2026, 10, 1), "red", date(2026, 10, 29), TODAY, path, today=TODAY
        )
    with pytest.raises(ValidationError, match="in the future"):
        enfen.add(
            18,
            date(2026, 11, 15),
            "No Activo",
            date(2026, 11, 29),
            TODAY,
            path,
            today=TODAY,
        )

    assert path.read_text(encoding="utf-8") == SAMPLE


def test_the_committed_input_is_what_enfen_add_writes(tmp_path):
    path = tmp_path / "enfen.yaml"
    committed = enfen.INPUT_PATH.read_text(encoding="utf-8")
    record = enfen.parse(committed, TODAY)[0]

    enfen.add(
        record["number"],
        date.fromisoformat(record["start"]),
        record["status"],
        date.fromisoformat(record["end"]),
        date.fromisoformat(record["checked_at"]),
        path,
        today=TODAY,
    )

    assert path.read_text(encoding="utf-8") == committed


def test_enfen_add_command_records_the_communique(tmp_path):
    path = tmp_path / "enfen.yaml"
    env = os.environ | {"ENFEN_COMMUNIQUE_PATH": str(path)}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "wawapacha_pipeline",
            "enfen-add",
            "17",
            "--date",
            "2026-09-28",
            "--status",
            "Alerta de El Niño Costero",
            "--next-due",
            "2026-10-15",
            "--checked-at",
            "2026-10-02",
        ],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert "+  number: 17" in result.stdout
    assert enfen.parse(path.read_text(encoding="utf-8"), TODAY)[0]["number"] == 17
