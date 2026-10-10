import importlib.util
from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "scripts"

ICEN_URL = "http://met.igp.gob.pe/datos/ICEN.txt"
WEEKLY_URL = "https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for"
RELATIVE_URL = "https://www.cpc.ncep.noaa.gov/data/indices/rel_wksst9120.txt"

WEEKLY = "\n".join(
    [
        " Weekly SST data starts week centered on 2Sept1981",
        "",
        "                Nino1+2      Nino3        Nino34        Nino4",
        " Week          SST SSTA     SST SSTA     SST SSTA     SST SSTA",
        " 02SEP1981     24.3-0.3     26.3 0.1     26.9 0.1     28.4 0.1",
        " 09SEP1981     24.5 0.1     26.5 0.2     27.1 0.2     28.5 0.2",
        " 16SEP1981     24.5 4.5     26.5 0.2     27.1 0.2     28.5 0.2",
        " 23SEP1981     24.5 5.3     26.5 0.2     27.1 0.2     28.5-0.2",
    ]
)
RELATIVE = "\n".join(
    [
        " Weekly Relative SST data starts week centered on 9Sept1981",
        "",
        "                Nino1+2    Nino3    Nino34    Nino4",
        " 09SEP1981         0.1        0.2        0.2       -0.1",
        " 16SEP1981         4.6        1.3        0.1       -0.2",
    ]
)


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def icen():
    return load("check_icen")


@pytest.fixture
def weekly():
    return load("check_weekly_nino")


def claim(*sources: tuple[str, str]) -> dict:
    return {"source": [{"ref": ref, "quote": quote} for ref, quote in sources]}


def series(*rows: tuple[int, int, float]) -> dict[tuple[int, int], float]:
    return {(year, month): value for year, month, value in rows}


def test_a_warm_run_needs_three_months_and_takes_the_magnitude_of_its_maximum(icen):
    values = series(
        (2019, 10, 0.2),
        (2019, 11, 0.9),
        (2019, 12, 1.4),
        (2020, 1, 0.6),
        (2020, 2, 0.1),
        (2020, 3, 0.8),
        (2020, 4, 1.0),
        (2020, 5, 0.0),
    )

    assert icen.events(values) == [((2019, 11), (2020, 1), 3, "Moderada")]


def test_the_threshold_is_strict(icen):
    values = series((2012, 4, 0.51), (2012, 5, 0.6), (2012, 6, 0.55), (2012, 7, 0.5))

    assert icen.events(values) == [((2012, 4), (2012, 6), 3, "Débil")]


def test_icen_rows_are_read_from_the_quotes_of_the_claims(icen):
    claims = {
        "a": claim((ICEN_URL, "1983   6    4.32"), (ICEN_URL, "1997  11    4.08"))
    }

    assert icen.check_quoted_rows({(1983, 6): 4.32, (1997, 11): 4.08}, claims) == []


def test_icen_reports_a_quoted_row_the_file_no_longer_has(icen):
    claims = {"a": claim((ICEN_URL, "1983   6    4.32"))}

    failures = icen.check_quoted_rows({(1983, 6): 4.30}, claims)

    assert failures == ["ICEN.txt has 4.3 for (1983, 6), a claim quotes 4.32"]


def test_a_peak_claim_fails_when_a_higher_month_is_in_the_event(icen):
    claims = {
        "icen-peak-2017": claim(
            (ICEN_URL, "2017   3    1.31"),
            ("https://enfen.example/nota", "2017 1 2017 4 4 Niño Moderado"),
        )
    }
    file = series((2017, 1, 0.8), (2017, 2, 1.0), (2017, 3, 1.31), (2017, 4, 0.9))
    higher = {**file, (2017, 4): 1.4}
    claims["icen-peak-1982-83"] = claims["icen-peak-1997-98"] = claims["icen-peak-2017"]

    assert icen.check_peaks(file, claims) == []
    assert len(icen.check_peaks(higher, claims)) == 3


def test_the_latest_claim_follows_the_end_of_the_file_and_the_rank(icen):
    claims = {
        "icen-2026-07": claim((ICEN_URL, "2026   7    3.38")),
        "icen-2026-07-rank": claim(
            (ICEN_URL, "2026   7    3.38"), (ICEN_URL, "1983   6    4.32")
        ),
    }
    file = series((1983, 6, 4.32), (2026, 6, 2.66), (2026, 7, 3.38))

    assert icen.check_latest(file, claims) == []

    revised = {**file, (2026, 8): 3.9}
    assert icen.check_latest(revised, claims) != []


def test_a_flat_file_differs_from_the_registry(icen, monkeypatch, capsys):
    flat = "".join(
        f"{year} {month:3d} 0.00\n"
        for year in range(1950, 2027)
        for month in range(1, 13)
        if (year, month) <= (2026, 7)
    )
    monkeypatch.setattr(icen.enfen_icen, "fetch", lambda: flat)

    assert icen.main() == 1
    assert "DIFFERS" in capsys.readouterr().out


def test_the_relative_file_is_read_by_its_nino12_column(weekly):
    assert weekly.relative_nino12(RELATIVE) == {
        date(1981, 9, 9): 0.1,
        date(1981, 9, 16): 4.6,
    }


RECORD_ROW = "23SEP1981     24.5 5.3     26.5 0.2     27.1 0.2     28.5-0.2"
RELATIVE_ROW = "16SEP1981         4.6        1.3        0.1       -0.2"


def weekly_claims(weekly, *weekly_rows: str, relative_rows=(RELATIVE_ROW,)) -> dict:
    return {
        weekly.RECORD_CLAIM: claim(*((WEEKLY_URL, row) for row in weekly_rows)),
        weekly.RELATIVE_CLAIM: claim(*((RELATIVE_URL, row) for row in relative_rows)),
    }


def test_weekly_files_that_match_the_quoted_rows_pass(weekly):
    claims = weekly_claims(weekly, RECORD_ROW)

    assert weekly.check(WEEKLY, RELATIVE, claims) == []


def test_a_higher_week_than_the_quoted_record_is_reported(weekly):
    higher = WEEKLY.replace("24.5 4.5", "24.5 5.4")
    claims = weekly_claims(weekly, RECORD_ROW)

    failures = weekly.check(higher, RELATIVE, claims)

    assert any("is not a quoted row" in failure for failure in failures)


def test_a_week_that_cpc_dropped_is_reported_not_raised(weekly):
    dropped = "30SEP2026     26.1 5.3     29.0 4.0     29.9 3.2     29.9 1.2"
    claims = weekly_claims(weekly, dropped)

    failures = weekly.check(WEEKLY, RELATIVE, claims)

    assert any("quotes a row the file lacks" in failure for failure in failures)
