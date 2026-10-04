from datetime import UTC, date, datetime

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError
from wawapacha_pipeline.sources import enfen_icen as icen

SAMPLE = """\
% Índice Costero El Niño (ICEN; ENFEN, 2024)
% yy   mm   ICEN
99 11 -0.75
99 12 -1.07
00 01 -1.25
00 02 0.50
"""


def test_parse_skips_comments_converts_two_digit_years_and_keeps_months_contiguous():
    records = icen.parse(SAMPLE, date(2000, 3, 1))

    assert records == [
        {"start": "1999-11", "end": "1999-11", "icen": -0.75},
        {"start": "1999-12", "end": "1999-12", "icen": -1.07},
        {"start": "2000-01", "end": "2000-01", "icen": -1.25},
        {"start": "2000-02", "end": "2000-02", "icen": 0.5},
    ]


@pytest.mark.parametrize(
    ("text", "today", "message"),
    [
        ("2026 1 nope", date(2026, 2, 1), "non-numeric"),
        ("2026 13 1.0", date(2026, 2, 1), "between 1 and 12"),
        ("2026 1 1.0\n2026 3 1.0", date(2026, 4, 1), "gap or duplicate"),
        ("2026 1 10.1", date(2026, 2, 1), "outside the ±10 range"),
        ("2025 1 1.0", date(2026, 10, 1), "older than the configured maximum age"),
    ],
)
def test_parse_rejects_each_required_validation_failure(text, today, message):
    with pytest.raises(ValidationError, match=message):
        icen.parse(text, today)


def test_build_uses_the_registry_provenance():
    dataset = icen.build(
        icen.parse(SAMPLE, date(2000, 3, 1)), datetime(2000, 3, 1, tzinfo=UTC)
    )

    entry = registry.get("enfen-icen")
    assert dataset["source"]["url"] == "http://met.igp.gob.pe/datos/ICEN.txt"
    assert dataset["reference_period"] == entry["reference_period"]
    assert dataset["records"][-1]["start"] == "2000-02"
