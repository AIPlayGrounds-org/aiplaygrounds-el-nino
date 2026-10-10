"""Check the weekly Niño claims in evidence/claims.toml against the CPC files.

Fetches wksst9120.for (Weekly OISST.v2.1) with the ingestion module's reader
and rel_wksst9120.txt (Weekly Relative OISST.v2.1) with its fetch, prints their
Last-Modified header and SHA-256, and compares them with the quotes the claims
carry: every data row a claim quotes, and that the highest weekly Niño 1+2
anomaly of each file, and the highest before the year of the record, are among
the quoted rows. CPC rewrites the last weeks of both files, so a difference can
mean the claim needs a new check. Exits 1 when any check differs.

Run from the repository root:
uv run --project pipeline pipeline/scripts/check_weekly_nino.py
"""

import re
import sys
import tomllib
from datetime import date
from pathlib import Path

from wawapacha_pipeline.sources import noaa_cpc_nino_weekly as weekly

REGISTRY = Path(__file__).parents[2] / "evidence" / "claims.toml"
WEEKLY_URL = weekly.URL
RELATIVE_URL = WEEKLY_URL.replace("wksst9120.for", "rel_wksst9120.txt")

# The claims that name the record weeks of each file.
RECORD_CLAIM = "weekly-nino12-record-2026-09-30"
RELATIVE_CLAIM = "cpc-weekly-relative-oisst-is-another-file"

RELATIVE_ROW = re.compile(r" (\d{2}[A-Z]{3}\d{4})\s+(-?\d+\.\d)(?:\s+-?\d+\.\d){3}\s*")

Claims = dict[str, dict]
Series = dict[date, float]


def load_claims(path: Path = REGISTRY) -> Claims:
    with path.open("rb") as handle:
        return {claim["id"]: claim for claim in tomllib.load(handle)["claim"]}


def squeeze(line: str) -> str:
    return " ".join(line.split())


def week_of(row: str) -> date:
    return weekly.parse_date(row.split()[0], 0)


def nino12(text: str) -> Series:
    return {
        date.fromisoformat(record["start"]): record["nino_1_2_anomaly"]
        for record in weekly.parse(text)
    }


def relative_nino12(text: str) -> Series:
    return {
        week_of(match[1]): float(match[2])
        for line in text.splitlines()
        if (match := RELATIVE_ROW.fullmatch(line))
    }


def quoted(claims: Claims, url: str) -> list[str]:
    return [
        squeeze(source["quote"])
        for claim in claims.values()
        for source in claim["source"]
        if source["ref"] == url
    ]


def check_rows(label: str, text: str, rows: list[str]) -> list[str]:
    lines = {squeeze(line) for line in text.splitlines()}
    print(f"\n{label}: {len(rows)} quoted rows")
    return [
        f"{label}: a claim quotes a row the file lacks: {row}"
        for row in rows
        if row not in lines
    ]


def check_highest(
    label: str, series: Series, claim: dict, url: str, before_record: bool
) -> list[str]:
    rows = {
        week_of(source["quote"]) for source in claim["source"] if source["ref"] == url
    }
    week = max(series, key=lambda w: (series[w], -w.toordinal()))
    print(f"  {label}: {len(series)} weeks, highest {series[week]:+.1f} on {week}")
    failures = []
    if week not in rows:
        failures.append(f"{label}: the highest week {week} is not a quoted row")
    earlier = {w: v for w, v in series.items() if w.year < week.year}
    if before_record and earlier:
        prior = max(earlier, key=lambda w: (earlier[w], -w.toordinal()))
        print(f"  {label}: highest before {week.year} {earlier[prior]:+.1f} on {prior}")
        if prior not in rows:
            failures.append(
                f"{label}: the highest week before {week.year} is {prior}, not quoted"
            )
    return failures


def check(weekly_text: str, relative_text: str, claims: Claims) -> list[str]:
    return [
        *check_rows("wksst9120.for", weekly_text, quoted(claims, WEEKLY_URL)),
        *check_rows("rel_wksst9120.txt", relative_text, quoted(claims, RELATIVE_URL)),
        *check_highest(
            "wksst9120.for Niño 1+2",
            nino12(weekly_text),
            claims[RECORD_CLAIM],
            WEEKLY_URL,
            before_record=True,
        ),
        *check_highest(
            "rel_wksst9120.txt Niño 1+2",
            relative_nino12(relative_text),
            claims[RELATIVE_CLAIM],
            RELATIVE_URL,
            before_record=False,
        ),
    ]


def main() -> int:
    fetched = [weekly.fetch(url) for url in (WEEKLY_URL, RELATIVE_URL)]
    for url, result in zip((WEEKLY_URL, RELATIVE_URL), fetched, strict=True):
        print(f"fetched {url}\n  Last-Modified: {result.last_modified}")
        print(f"  sha256: {result.sha256}")
    failures = check(fetched[0].text, fetched[1].text, load_claims())
    print("\nall claims hold" if not failures else "\nDIFFERS:")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
