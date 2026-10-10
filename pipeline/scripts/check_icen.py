"""Check the ICEN claims in evidence/claims.toml against the live IGP file.

Fetches ICEN.txt with the ingestion module's reader and compares it with the
quotes the claims carry: every ICEN.txt row a claim quotes, the maximum of each
event whose peak a claim names, the last month and rank of the latest value,
the January to July 2026 values the ENFEN report prints, and the chronology of
Nota Técnica ENFEN 01-2024 (Tabla 3) rebuilt with its thresholds (Tabla 2) and
its rule of three consecutive warm months. Exits 1 when any check differs.

Run from the repository root: uv run --project pipeline pipeline/scripts/check_icen.py
"""

import hashlib
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

from wawapacha_pipeline.sources import enfen_icen

REGISTRY = Path(__file__).parents[2] / "evidence" / "claims.toml"
ICEN_URL = enfen_icen.SOURCE["access"]["url"]

# Nota Técnica ENFEN 01-2024, Tabla 2 (PDF p. 3): warm categories, strict ">".
WEAK, MODERATE, STRONG, EXTRAORDINARY = 0.5, 1.3, 2.1, 3.5

# Nota Técnica ENFEN 01-2024, Tabla 3 (PDF p. 5):
# (start year, start month, end year, end month, months, magnitude).
TABLE_3 = [
    (1951, 5, 1951, 12, 8, "Fuerte"),
    (1953, 2, 1953, 10, 9, "Moderada"),
    (1957, 3, 1958, 7, 17, "Fuerte"),
    (1963, 8, 1963, 10, 3, "Débil"),
    (1965, 3, 1966, 1, 11, "Moderada"),
    (1968, 9, 1968, 11, 3, "Débil"),
    (1969, 3, 1970, 1, 11, "Moderada"),
    (1972, 2, 1973, 2, 13, "Fuerte"),
    (1976, 4, 1976, 12, 9, "Moderada"),
    (1982, 7, 1983, 11, 17, "Extraordinaria"),
    (1986, 12, 1987, 12, 13, "Moderada"),
    (1991, 8, 1992, 6, 11, "Moderada"),
    (1993, 3, 1993, 9, 7, "Débil"),
    (1994, 11, 1995, 1, 3, "Débil"),
    (1997, 4, 1998, 8, 17, "Extraordinaria"),
    (2002, 3, 2002, 5, 3, "Débil"),
    (2006, 8, 2006, 12, 5, "Débil"),
    (2008, 6, 2008, 9, 4, "Débil"),
    (2009, 6, 2009, 9, 4, "Débil"),
    (2012, 4, 2012, 7, 4, "Débil"),
    (2014, 5, 2014, 11, 7, "Débil"),
    (2015, 4, 2016, 5, 14, "Fuerte"),
    (2017, 1, 2017, 4, 4, "Moderada"),
    (2018, 11, 2019, 1, 3, "Débil"),
    (2023, 3, 2024, 2, 12, "Fuerte"),
]

# The claims whose ICEN.txt row is the maximum of the Tabla 3 event they quote.
PEAK_CLAIMS = ("icen-peak-1982-83", "icen-peak-1997-98", "icen-peak-2017")

SPANISH_MONTHS = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep")
SPANISH_MONTHS += ("Oct", "Nov", "Dic")
ICEN_ROW = re.compile(r"(\d{4})\s+(\d{1,2})\s+(-?\d+\.\d+)")
TABLE_3_ROW = re.compile(r"(\d{4}) (\d{1,2}) (\d{4}) (\d{1,2}) (\d+) Niño (\w+)")
ENFEN_ROW = re.compile(rf"({'|'.join(SPANISH_MONTHS)})-(\d{{2}}) ([-–]?\d+\.\d+)")

Month = tuple[int, int]
Claims = dict[str, dict]
Event = tuple[int, int, int, int, int, str]


def load_claims(path: Path = REGISTRY) -> Claims:
    with path.open("rb") as handle:
        return {claim["id"]: claim for claim in tomllib.load(handle)["claim"]}


def quotes(claim: dict, icen: bool) -> list[str]:
    """The quotes of a claim that come from ICEN.txt, or from any other source."""
    return [
        source["quote"]
        for source in claim["source"]
        if (source["ref"] == ICEN_URL) == icen
    ]


def rows(quote_list: list[str]) -> list[tuple[Month, float]]:
    return [
        ((int(year), int(month)), float(value))
        for quote in quote_list
        for year, month, value in ICEN_ROW.findall(quote)
    ]


def table_3_events(quote_list: list[str]) -> list[Event]:
    return [
        (*(int(n) for n in match[:5]), match[5])
        for quote in quote_list
        for match in TABLE_3_ROW.findall(quote)
    ]


def category(value: float) -> str | None:
    if value > EXTRAORDINARY:
        return "Extraordinaria"
    if value > STRONG:
        return "Fuerte"
    if value > MODERATE:
        return "Moderada"
    if value > WEAK:
        return "Débil"
    return None


def following(month: Month) -> Month:
    year, number = month
    return (year + 1, 1) if number == 12 else (year, number + 1)


def events(series: dict[Month, float]) -> list[tuple[Month, Month, int, str]]:
    """Runs of at least three consecutive warm months, rated by their maximum."""
    found, run = [], []
    for month in sorted(series) + [None]:
        if month is not None and series[month] > WEAK:
            if run and following(run[-1]) != month:
                found.append(run)
                run = []
            run.append(month)
        else:
            found.append(run)
            run = []
    return [
        (r[0], r[-1], len(r), category(max(series[m] for m in r)))
        for r in found
        if len(r) >= 3
    ]


def check_quoted_rows(series: dict[Month, float], claims: Claims) -> list[str]:
    quoted = [
        row for claim in claims.values() for row in rows(quotes(claim, icen=True))
    ]
    print(f"\nrows quoted by the claims: {len(quoted)}")
    return [
        f"ICEN.txt has {series.get(month)} for {month}, a claim quotes {value}"
        for month, value in quoted
        if series.get(month) != value
    ]


def check_peaks(series: dict[Month, float], claims: Claims) -> list[str]:
    failures = []
    print("\npeaks")
    for claim_id in PEAK_CLAIMS:
        [(month, value)] = rows(quotes(claims[claim_id], icen=True))
        [(sy, sm, ey, em, _, _)] = table_3_events(quotes(claims[claim_id], icen=False))
        window = [m for m in sorted(series) if (sy, sm) <= m <= (ey, em)]
        peak = max(window, key=series.__getitem__)
        print(
            f"  {claim_id}: file {series[peak]:.2f} in {peak}; claim {value} in {month}"
        )
        if series[peak] != value or series[month] != value:
            failures.append(
                f"{claim_id}: the peak of {(sy, sm)}..{(ey, em)} is not the quoted row"
            )
    return failures


def check_latest(series: dict[Month, float], claims: Claims) -> list[str]:
    last = max(series)
    value = series[last]
    higher = {m for m in series if series[m] > value}
    ties = [m for m in series if series[m] == value and m != last]
    print(f"\nlatest: {last} = {value:.2f} ({category(value)})")
    print(f"  rank {len(higher) + 1} of {len(series)} months; equal elsewhere: {ties}")
    failures = []
    [(latest_month, latest_value)] = rows(quotes(claims["icen-2026-07"], icen=True))
    if (latest_month, latest_value) != (last, value):
        failures.append(f"icen-2026-07 quotes {latest_month}, the file ends at {last}")
    quoted = {m for m, _ in rows(quotes(claims["icen-2026-07-rank"], icen=True))}
    if quoted != higher | {last} or ties:
        failures.append(
            "icen-2026-07-rank: the quoted higher months are not the file's"
        )
    return failures


def check_enfen_table(series: dict[Month, float], claims: Claims) -> list[str]:
    claim = claims["icen-file-matches-enfen-table"]
    printed = {
        (2000 + int(year), SPANISH_MONTHS.index(name) + 1): float(
            value.replace("–", "-")
        )
        for quote in quotes(claim, icen=False)
        for name, year, value in ENFEN_ROW.findall(quote)
    }
    months = [m for m, _ in rows(quotes(claim, icen=True))]
    print(f"\nENFEN report months compared with the file: {len(printed)}")
    return [
        f"ENFEN prints {printed.get(month)} for {month}, the file has {series.get(month)}"
        for month in months
        if printed.get(month) != series.get(month)
    ] or ([] if printed else ["icen-file-matches-enfen-table quotes no ENFEN row"])


def check_chronology(series: dict[Month, float], claims: Claims) -> list[str]:
    found = {
        (*start, *end, months, magnitude)
        for start, end, months, magnitude in events(series)
        if end <= (2024, 2)
    }
    table = set(TABLE_3)
    explained = set(
        table_3_events(quotes(claims["icen-chronology-reproduced"], icen=False))
    )
    unmatched = table - found
    extra = found - table
    print(f"\nchronology: {len(found)} events up to 2024-02 from the file")
    print(f"  {len(table & found)} of {len(table)} table rows match exactly")
    for row in sorted(unmatched):
        print(f"  table row without a match: {row}")
    for row in sorted(extra):
        print(f"  file event without a table row: {row}")
    failures = [
        f"table row {row} differs and the claim does not quote it"
        for row in sorted(unmatched - explained)
    ]
    starts = {row[:2] for row in unmatched}
    failures += [
        f"file event {row} has no table row"
        for row in sorted(extra)
        if row[:2] not in starts
    ]
    return failures


def check(series: dict[Month, float], claims: Claims) -> list[str]:
    return [
        *check_quoted_rows(series, claims),
        *check_peaks(series, claims),
        *check_latest(series, claims),
        *check_enfen_table(series, claims),
        *check_chronology(series, claims),
    ]


def main() -> int:
    text = enfen_icen.fetch()
    print(f"fetched {ICEN_URL}")
    print(f"  sha256: {hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    # Staleness is the freshness check's concern, not this script's.
    records = enfen_icen.parse(text, today=date.min)
    series = {
        (int(record["start"][:4]), int(record["start"][5:])): record["icen"]
        for record in records
    }
    print(f"{len(series)} months, {min(series)} to {max(series)}")
    failures = check(series, load_claims())
    print("\nall claims hold" if not failures else "\nDIFFERS:")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
