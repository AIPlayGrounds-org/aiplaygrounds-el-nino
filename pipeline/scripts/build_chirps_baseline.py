"""Build the checked-in CHIRPS v3 department climatology once."""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from wawapacha_pipeline.sources import chirps

FINAL_TEMPLATE = (
    "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/pentads/latam/tifs/"
    "chirps-v3.0.{year:04d}.{month:02d}.{number}.tif"
)
FIRST_YEAR = 1991
LAST_YEAR = 2020
OUTPUT = (
    Path(__file__).parents[1]
    / "src"
    / "wawapacha_pipeline"
    / "sources"
    / "chirps_baseline.json"
)


def final_url(year: int, month: int, number: int) -> str:
    return FINAL_TEMPLATE.format(year=year, month=month, number=number)


def years_for(month: int, number: int, calendar_kind: str | None) -> range | list[int]:
    years = range(FIRST_YEAR, LAST_YEAR + 1)
    if month == 2 and number == 6:
        return [year for year in years if (year % 4 == 0) == (calendar_kind == "leap")]
    return years


def build_row(
    month: int,
    number: int,
    key: str,
    calendar_kind: str | None,
    boundaries: list[dict],
) -> dict:
    totals = {boundary["code"]: 0.0 for boundary in boundaries}
    counts = {boundary["code"]: 0 for boundary in boundaries}
    years = years_for(month, number, calendar_kind)
    with ProcessPoolExecutor(max_workers=8) as executor:
        jobs = {
            executor.submit(chirps.fetch, final_url(year, month, number), 120): year
            for year in years
        }
        weights = None
        for job in as_completed(jobs):
            year = jobs[job]
            period = date(year, month, (number - 1) * 5 + 1)
            raw = job.result()
            if weights is None:
                weights = chirps.overlap_weights(raw, boundaries)
            aggregated_values = chirps.aggregate(raw, boundaries, weights)
            print(f"read {key} {period}", flush=True)
            for code, value in aggregated_values.items():
                if value is not None:
                    totals[code] += value
                    counts[code] += 1
    values = {
        code: None if counts[code] == 0 else round(totals[code] / counts[code], 3)
        for code in totals
    }
    return {"key": key, "values": values}


def main() -> None:
    boundaries = chirps.load_boundaries()
    rows = []
    for month in range(1, 13):
        for number in range(1, 7):
            if month == 2 and number == 6:
                for sample_year, calendar_kind in ((2025, "common"), (2024, "leap")):
                    key = chirps.Pentad(sample_year, month, number, "").key
                    rows.append(
                        build_row(month, number, key, calendar_kind, boundaries)
                    )
            else:
                key = chirps.Pentad(2025, month, number, "").key
                rows.append(build_row(month, number, key, None, boundaries))
    payload = {
        "base_period": "1991-2020",
        "product": "CHIRPS v3 final pentads",
        "method": (
            "Exact overlap mean of 1991–2020 CHC v3 final pentad GeoTIFFs, "
            "weighted by overlap area and cos(latitude) in WGS84; February P6 "
            "is split into common and leap years."
        ),
        "data_url": "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/pentads/latam/tifs/",
        "boundary_source": "data/limites-inei-ign.json",
        "records": rows,
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(rows)} pentads x {len(boundaries)} departments to {OUTPUT}")


if __name__ == "__main__":
    main()
