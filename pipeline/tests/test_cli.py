import json
from datetime import UTC, datetime

from wawapacha_pipeline import cli, registry


def scheduled_ids(*updates: str) -> list[str]:
    sources = registry.load()
    return [i for i in cli.SOURCES if sources[i]["update"] in updates]


def write_published_data(path, ingestion_time: str) -> None:
    path.write_text(json.dumps({"ingestion_time": ingestion_time}), encoding="utf-8")


def test_due_selection_uses_the_registry_update_schedule(tmp_path):
    after_monthly_threshold = datetime(2026, 10, 28, 12, tzinfo=UTC)
    for source_id in cli.SOURCES:
        write_published_data(
            tmp_path / f"{source_id}.json", "2026-10-01T12:00:00+00:00"
        )

    assert cli.due_source_ids(
        datetime(2026, 10, 28, 11, 59, tzinfo=UTC), tmp_path
    ) == scheduled_ids("daily", "weekly")
    assert cli.due_source_ids(after_monthly_threshold, tmp_path) == scheduled_ids(
        "daily", "weekly", "monthly"
    )
    assert cli.due_source_ids(
        datetime(2026, 11, 1, tzinfo=UTC), tmp_path
    ) == scheduled_ids("daily", "weekly", "monthly")
    assert cli.due_source_ids(datetime(2026, 10, 1, 13, tzinfo=UTC), tmp_path) == []


def test_due_selector_handles_every_automatable_registry_cadence(tmp_path):
    for source_id in cli.SOURCES:
        write_published_data(
            tmp_path / f"{source_id}.json", "2026-10-01T12:00:00+00:00"
        )

    expected = [
        source_id
        for source_id, entry in registry.load().items()
        if entry["verdict"] == "automatable" and entry["update"] != "manual"
    ]

    assert (
        cli.due_source_ids(datetime(2026, 10, 28, 12, tzinfo=UTC), tmp_path) == expected
    )


def test_due_thresholds_have_a_cron_safety_margin():
    ingestion = datetime(2026, 10, 1, 12, tzinfo=UTC)

    assert not cli._is_due("daily", ingestion, datetime(2026, 10, 2, 7, 59, tzinfo=UTC))
    assert cli._is_due("daily", ingestion, datetime(2026, 10, 2, 8, tzinfo=UTC))
    assert not cli._is_due(
        "weekly", ingestion, datetime(2026, 10, 7, 11, 59, tzinfo=UTC)
    )
    assert cli._is_due("weekly", ingestion, datetime(2026, 10, 7, 12, tzinfo=UTC))
    assert not cli._is_due(
        "monthly", ingestion, datetime(2026, 10, 28, 11, 59, tzinfo=UTC)
    )
    assert cli._is_due("monthly", ingestion, datetime(2026, 10, 28, 12, tzinfo=UTC))
    assert not cli._is_due("manual", ingestion, datetime(2030, 1, 1, tzinfo=UTC))


def test_due_selection_includes_missing_data_and_excludes_manual_sources(tmp_path):
    assert cli.due_source_ids(
        datetime(2026, 10, 2, tzinfo=UTC), tmp_path
    ) == scheduled_ids("daily", "weekly", "monthly")


def test_due_command_prints_one_source_per_line(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path)

    assert cli.main(["due", "--as-of", "2026-10-02T00:00:00+00:00"]) == 0
    assert capsys.readouterr().out == "".join(
        f"{i}\n" for i in scheduled_ids("daily", "weekly", "monthly")
    )


def test_due_command_honours_an_explicit_data_dir(tmp_path, capsys):
    for source_id in cli.SOURCES:
        write_published_data(
            tmp_path / f"{source_id}.json", "2026-10-01T12:00:00+00:00"
        )

    assert (
        cli.main(
            [
                "due",
                "--data-dir",
                str(tmp_path),
                "--as-of",
                "2026-10-28T12:00:00+00:00",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == "".join(
        f"{i}\n" for i in scheduled_ids("daily", "weekly", "monthly")
    )


def test_freshness_uses_the_newest_ingestion_or_source_update(tmp_path):
    for source_id in cli.SOURCES:
        write_published_data(
            tmp_path / f"{source_id}.json", "2026-10-04T12:00:00+00:00"
        )
    weekly = tmp_path / "noaa-cpc-nino-weekly.json"
    weekly.write_text(
        json.dumps(
            {
                "ingestion_time": "2026-10-01T12:00:00+00:00",
                "source_revision": {"last_modified": "Fri, 02 Oct 2026 12:00:00 GMT"},
            }
        ),
        encoding="utf-8",
    )

    assert cli.freshness_issues(datetime(2026, 10, 4, 12, tzinfo=UTC), tmp_path) == []


def test_freshness_reports_stale_missing_and_invalid_data(tmp_path):
    write_published_data(
        tmp_path / "noaa-cpc-nino-weekly.json", "2026-09-20T12:00:00+00:00"
    )
    issues = cli.freshness_issues(datetime(2026, 10, 4, 12, tzinfo=UTC), tmp_path)

    assert any(
        issue.startswith("noaa-cpc-nino-weekly: last update") for issue in issues
    )
    assert any(issue.startswith("noaa-cpc-oni: missing or invalid") for issue in issues)
    assert any(issue.startswith("noaa-oisst: missing or invalid") for issue in issues)


def test_freshness_command_returns_failure_with_visible_errors(tmp_path, capsys):
    write_published_data(
        tmp_path / "noaa-cpc-nino-weekly.json", "2026-09-20T12:00:00+00:00"
    )

    assert (
        cli.main(
            [
                "freshness",
                "--data-dir",
                str(tmp_path),
                "--as-of",
                "2026-10-04T12:00:00+00:00",
            ]
        )
        == 1
    )
    assert "data freshness" in capsys.readouterr().err
