import json
from calendar import month_name
from datetime import UTC, datetime
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish
from wawapacha_pipeline.sources import noaa_cpc_outlook as outlook

SAMPLE_PATH = Path(__file__).parent / "samples" / "outlook.html"
SAMPLE = SAMPLE_PATH.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def test_reads_the_visible_issue_and_all_categories_in_table_order():
    records = outlook.parse(SAMPLE)

    assert [
        (record["season"], record["start"], record["end"]) for record in records
    ] == [
        ("ASO", "2026-08", "2026-10"),
        ("SON", "2026-09", "2026-11"),
        ("OND", "2026-10", "2026-12"),
        ("NDJ", "2026-11", "2027-01"),
        ("DJF", "2026-12", "2027-02"),
        ("JFM", "2027-01", "2027-03"),
        ("FMA", "2027-02", "2027-04"),
        ("MAM", "2027-03", "2027-05"),
        ("AMJ", "2027-04", "2027-06"),
    ]
    assert records[0]["issue_date"] == "2026-09"
    assert records[0]["categories"][0] == {
        "category": "Index ≤ -2.0°C",
        "lower_bound": None,
        "upper_bound": -2.0,
        "probability": 0,
    }
    assert [
        (category["lower_bound"], category["upper_bound"])
        for category in records[0]["categories"]
    ] == [
        (None, -2.0),
        (-2.0, -1.5),
        (-1.5, -1.0),
        (-1.0, -0.5),
        (-0.5, 0.5),
        (0.5, 1.0),
        (1.0, 1.5),
        (1.5, 2.0),
        (2.0, None),
    ]
    assert records[-1]["categories"][-1]["probability"] == 0
    assert all(
        isinstance(category["probability"], int)
        for record in records
        for category in record["categories"]
    )
    assert all(
        sum(category["probability"] for category in record["categories"]) == 100
        for record in records
    )


def test_comments_do_not_override_the_visible_issue_heading():
    records = outlook.parse(SAMPLE)

    assert all(record["issue_date"] != "2026-04" for record in records)


def outlook_with_issue_and_first_season(issue_date: str, first_season: str) -> str:
    seasons = ["ASO", "SON", "OND", "NDJ", "DJF", "JFM", "FMA", "MAM", "AMJ"]
    first_index = [
        "DJF",
        "JFM",
        "FMA",
        "MAM",
        "AMJ",
        "MJJ",
        "JJA",
        "JAS",
        "ASO",
        "SON",
        "OND",
        "NDJ",
    ].index(first_season)
    replacement = [
        [
            "DJF",
            "JFM",
            "FMA",
            "MAM",
            "AMJ",
            "MJJ",
            "JJA",
            "JAS",
            "ASO",
            "SON",
            "OND",
            "NDJ",
        ][(first_index + offset) % 12]
        for offset in range(len(seasons))
    ]
    result = SAMPLE.replace(
        "Issued September 2026",
        f"Issued {month_name[int(issue_date[5:7])]} {issue_date[:4]}",
    )
    for offset, season in enumerate(seasons):
        result = result.replace(f"<abbr>{season} ", f"<abbr>__season_{offset} ")
    for offset, season in enumerate(replacement):
        result = result.replace(f"__season_{offset}", season)
    return result


@pytest.mark.parametrize(
    ("issue_date", "first_season", "expected_first", "expected_last"),
    [
        ("2026-11", "OND", ("2026-10", "2026-12"), ("2027-06", "2027-08")),
        ("2026-12", "NDJ", ("2026-11", "2027-01"), ("2027-07", "2027-09")),
        ("2027-01", "DJF", ("2026-12", "2027-02"), ("2027-08", "2027-10")),
    ],
)
def test_issue_month_year_boundaries(
    issue_date: str,
    first_season: str,
    expected_first: tuple[str, str],
    expected_last: tuple[str, str],
):
    records = outlook.parse(
        outlook_with_issue_and_first_season(issue_date, first_season)
    )

    assert (records[0]["start"], records[0]["end"]) == expected_first
    assert (records[-1]["start"], records[-1]["end"]) == expected_last


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (
            SAMPLE.replace('id="probabilities-table"', 'id="wrong-table"'),
            "probabilities-table",
        ),
        (
            replace_once(SAMPLE, "Index &le; -2.0&deg;C", "Index &lt; -2.0&deg;C"),
            "Cabecera",
        ),
        (
            SAMPLE.replace("Issued September 2026", "Published September 2026"),
            "encabezado visible",
        ),
        (
            SAMPLE.replace(
                "<h2>Issued September 2026</h2>",
                "<h2>Issued September 2026</h2><h2>Issued October 2026</h2>",
            ),
            "encabezado visible",
        ),
        (replace_once(SAMPLE, "<abbr>SON", "<abbr>ASO"), "repetida"),
        (replace_once(SAMPLE, "<abbr>SON", "<abbr>OND"), "secuencia"),
        (replace_once(SAMPLE, ">23</td>", ">23.0</td>"), "no entero"),
        (replace_once(SAMPLE, ">23</td>", ">101</td>"), "fuera de rango"),
        (replace_once(SAMPLE, ">23</td>", ">22</td>"), "suman 99"),
    ],
)
def test_rejects_each_structural_or_probability_rule(broken: str, message: str):
    with pytest.raises(ValidationError, match=message):
        outlook.parse(broken)


def test_rejects_a_table_with_the_wrong_number_of_rows():
    broken = SAMPLE.replace("<tr><th><abbr>AMJ", "<tr><th><abbr>AMJ", 1)
    broken = broken.replace(
        "<tr><th><abbr>AMJ <span>Apr May Jun</span></abbr>",
        "",
        1,
    )

    with pytest.raises(ValidationError, match="cabecera y 9 filas"):
        outlook.parse(broken)


def test_rejects_a_table_row_with_the_wrong_number_of_cells():
    broken = replace_once(SAMPLE, "<tr><th><abbr>AMJ", "<tr><th><abbr>AMJ")
    broken = broken.replace(
        "<td>0</td></tr>\n      </tbody>", "</tr>\n      </tbody>", 1
    )

    with pytest.raises(ValidationError, match="10 celdas"):
        outlook.parse(broken)


def test_rejects_a_missing_probability():
    broken = replace_once(SAMPLE, ">23</td>", "></td>")

    with pytest.raises(ValidationError, match="no entero"):
        outlook.parse(broken)


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


def test_build_adds_registry_provenance():
    dataset = outlook.build(
        outlook.parse(SAMPLE), datetime(2026, 10, 1, 12, tzinfo=UTC)
    )

    assert dataset["id"] == "noaa-cpc-outlook"
    assert dataset["ingestion_time"] == "2026-10-01T12:00:00+00:00"
    assert dataset["processing_version"] == outlook.VERSION
    assert_matches_registry(dataset)


def test_run_publishes_valid_data_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(outlook, "fetch", lambda: SAMPLE)
    monkeypatch.setattr(outlook, "publish", lambda dataset: publish(dataset, tmp_path))

    count, path = outlook.run(datetime(2026, 10, 1, 12, tzinfo=UTC))

    assert count == 9
    assert path == tmp_path / "noaa-cpc-outlook.json"
    published = json.loads(path.read_text(encoding="utf-8"))
    assert published["records"][-1]["categories"][7]["probability"] == 0
    assert_matches_registry(published)


def test_run_keeps_the_previous_json_when_validation_fails(tmp_path, monkeypatch):
    previous = tmp_path / "noaa-cpc-outlook.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")
    monkeypatch.setattr(outlook, "fetch", lambda: "broken")

    with pytest.raises(ValidationError, match="encabezado visible"):
        outlook.run(datetime(2026, 10, 1, 12, tzinfo=UTC))

    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'
