"""NOAA OISST v2.1 — daily SST anomaly over the Peruvian ocean region. Its provenance is in sources.toml."""

import io
import os
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish

# Bump it when the logic changes: it stays in every published JSON.
VERSION = "0.2.0"

ID = "noaa-oisst"
SOURCE = registry.get(ID)
# NOAA_OISST_URL reads another server (for example, in tests). The JSON keeps the registry URL.
URL = os.environ.get("NOAA_OISST_URL", SOURCE["access"]["url"]).rstrip("/")

# The region, in the source's own convention: longitude 0–360 east.
SOUTH, NORTH = -25.0, 20.0
WEST, EAST = 240.0, 300.0
STEP = 0.25  # source grid, in degrees
BLOCK = 2  # source cells per published cell, along each axis

# The newest day is not always the same: ask for the last days and keep the latest.
WINDOW_DAYS = 3

TIME_EPOCH = date(1800, 1, 1)
TIME_UNITS = "days since 1800-01-01 00:00:00"
# The climatology has one year, numbered 1, without a 29 February.
CLIMATOLOGY_YEAR = 1
LEAP_DAY_AS = (2, 28)

# Physically possible values in this region, in °C. Outside them it is a read error.
SST_RANGE = (5.0, 35.0)
ANOMALY_RANGE = (-10.0, 10.0)
# A grid with fewer valid cells than this is not a real file: land alone is about a quarter.
MIN_VALID_SHARE = 0.5


def fetch(now: datetime | None = None, url: str = URL, timeout: int = 120) -> tuple[bytes, bytes]:
    """Download the recent days of SST and the climatology of the latest one.

    PSL keeps one SST file per year, and the NetCDF Subset Service cuts the region on the server.
    The first days of January come from the previous year's file, which is still the newest.
    """
    now = now or datetime.now(timezone.utc)
    start = (now - timedelta(days=WINDOW_DAYS)).date()
    sst = download(
        f"{url}/sst.day.mean.{start.year}.nc",
        time_start=f"{start}T00:00:00Z",
        time_end=f"{now.date()}T00:00:00Z",
        timeout=timeout,
    )
    month, day = climatology_day(days(read_netcdf(sst))[-1])
    climatology = download(
        f"{url}/sst.day.mean.ltm.1991-2020.nc",
        time=f"{CLIMATOLOGY_YEAR:04d}-{month:02d}-{day:02d}T00:00:00Z",
        timeout=timeout,
    )
    return sst, climatology


def download(url: str, timeout: int, **time: str) -> bytes:
    # NCSS has no CSV for grids, and its NetCDF-4 output needs an HDF5 reader. Classic NetCDF is the readable one.
    query = {"var": "sst", "north": NORTH, "south": SOUTH, "west": WEST, "east": EAST, "horizStride": 1, "accept": "netcdf"}
    request = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(query | time)}", headers={"User-Agent": "WawaPacha/0.1"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def run(ingestion_time: datetime | None = None) -> tuple[int, Path]:
    """Return the record count and the path of the published JSON."""
    ingestion_time = ingestion_time or datetime.now(timezone.utc)
    records = parse(*fetch(ingestion_time))
    return len(records), publish(build(records, ingestion_time))


def read_netcdf(data: bytes) -> netcdf_file:
    """Open a NetCDF classic file, the format NCSS returns for accept=netcdf."""
    try:
        return netcdf_file(io.BytesIO(data), mmap=False)
    except (TypeError, ValueError, EOFError, OSError) as error:
        raise ValidationError(f"The file is not a complete NetCDF classic file ({error}).") from None


def attribute(variable, name: str):
    """An attribute of a NetCDF variable, or None. Text comes back as str."""
    value = getattr(variable, name, None)
    return value.decode("latin-1") if isinstance(value, bytes) else value


def parse(sst: bytes, climatology: bytes) -> list[dict]:
    """Turn the two files into the record of the latest day and validate it as docs/data-contract.md requires."""
    return anomaly_record(read_netcdf(sst), read_netcdf(climatology))


def anomaly_record(sst: netcdf_file, climatology: netcdf_file) -> list[dict]:
    """Subtract the climatology from the latest day of SST and average it onto the published grid."""
    for name, nc in (("SST", sst), ("climatology", climatology)):
        for variable in ("lat", "lon", "time", "sst"):
            if variable not in nc.variables:
                raise ValidationError(f"The {name} file has no variable {variable!r}.")
        units = attribute(nc.variables["sst"], "units")
        if units != "degC":
            raise ValidationError(f"The {name} file does not give SST in degC: {units!r}.")

    lat_index, lat = axis(sst, "lat", SOUTH, NORTH)
    lon_index, lon = axis(sst, "lon", WEST, EAST)
    if not (np.array_equal(axis(climatology, "lat", SOUTH, NORTH)[1], lat)
            and np.array_equal(axis(climatology, "lon", WEST, EAST)[1], lon)):
        raise ValidationError("The SST and climatology grids are not the same.")

    sst_days = days(sst)
    day = sst_days[-1]
    check_climatology_day(climatology, day)

    today = cells(sst, len(sst_days) - 1, lat_index, lon_index)
    normal = cells(climatology, 0, lat_index, lon_index)
    anomalies = today - normal

    def place(index: tuple[int, int]) -> str:
        return f"lat {lat[index[0]]}, lon {lon[index[1]] - 360}"

    for what, grid, low, high in (
        ("SST", today, *SST_RANGE),
        ("Climatology", normal, *SST_RANGE),
        ("Anomaly", anomalies, *ANOMALY_RANGE),
    ):
        outside = np.argwhere((grid < low) | (grid > high))
        if len(outside):
            index = tuple(outside[0])
            value = grid[index]
            shown = f"{value:.2f}" if what == "Anomaly" else f"{value}"
            raise ValidationError(f"{what} out of range at {place(index)} ({shown} °C).")

    grid = block_means(anomalies)
    valid = sum(value is not None for row in grid for value in row)
    if valid < MIN_VALID_SHARE * len(grid) * len(grid[0]):
        raise ValidationError(f"Only {valid} of {len(grid) * len(grid[0])} cells have a value.")

    return [{
        "start": day.isoformat(),
        "end": day.isoformat(),
        "lat": [round(float(lat[i : i + BLOCK].mean()), 2) for i in range(0, len(lat), BLOCK)],
        "lon": [round(float(lon[j : j + BLOCK].mean()) - 360, 2) for j in range(0, len(lon), BLOCK)],
        "anomaly": grid,
    }]


def axis(nc: netcdf_file, name: str, low: float, high: float) -> tuple[np.ndarray, np.ndarray]:
    """Indices and values of a coordinate inside the region, checked against the regular grid.

    NCSS adds the cells just outside the box, so the indices pick the exact ones.
    """
    values = nc.variables[name][:].astype(float)
    indices = np.flatnonzero((values >= low) & (values <= high))
    chosen = values[indices]
    expected = low + STEP / 2 + np.arange(round((high - low) / STEP)) * STEP
    if len(chosen) != len(expected) or not np.allclose(chosen, expected, rtol=0, atol=1e-4):
        raise ValidationError(
            f"{name} is not the expected grid: {len(chosen)} cells from {chosen[:1].tolist()} to {chosen[-1:].tolist()}, "
            f"expected {len(expected)} from {expected[0]} to {expected[-1]} in steps of {STEP}."
        )
    return indices, chosen


def day_numbers(nc: netcdf_file) -> list[int]:
    """The time axis as whole days since TIME_EPOCH."""
    time = nc.variables["time"]
    if attribute(time, "units") != TIME_UNITS:
        raise ValidationError(f"Unexpected time units: {attribute(time, 'units')!r}. Expected {TIME_UNITS!r}.")
    values = time[:].astype(float)
    if not len(values) or np.any(values != np.floor(values)):
        raise ValidationError("The time axis is empty or has values that are not whole days.")
    return values.astype(int).tolist()


def days(nc: netcdf_file) -> list[date]:
    """The days of the SST time axis. They must be in order, with no gap and no duplicate."""
    result = [TIME_EPOCH + timedelta(days=value) for value in day_numbers(nc)]
    if any(later - earlier != timedelta(days=1) for earlier, later in zip(result, result[1:])):
        raise ValidationError(f"The days are not consecutive: {[d.isoformat() for d in result]}.")
    return result


def check_climatology_day(climatology: netcdf_file, day: date) -> None:
    """Check that the climatology holds the day of the year that applies to `day`.

    The file numbers its days in the Julian calendar, which Python lacks: decoded as Gregorian,
    the dates come out two days early. The day is placed from the first day of the file instead.
    """
    month, day_of_month = climatology_day(day)
    expected = (date(2001, month, day_of_month) - date(2001, 1, 1)).days
    numbers = day_numbers(climatology)
    actual_range = attribute(climatology.variables["time"], "actual_range")
    first = None if actual_range is None or np.size(actual_range) == 0 else np.ravel(actual_range)[0]
    if len(numbers) != 1 or first is None or numbers[0] - first != expected:
        raise ValidationError(f"The climatology is not the one for {month:02d}-{day_of_month:02d}.")


def climatology_day(day: date) -> tuple[int, int]:
    """Month and day of the climatology that applies to a day."""
    return LEAP_DAY_AS if (day.month, day.day) == (2, 29) else (day.month, day.day)


def cells(nc: netcdf_file, time_index: int, lat_index: np.ndarray, lon_index: np.ndarray) -> np.ndarray:
    """The SST of one day over the region, rows from the south. Missing cells are NaN."""
    variable = nc.variables["sst"]
    if variable.dimensions != ("time", "lat", "lon"):
        raise ValidationError(f"Unexpected dimensions of sst: {list(variable.dimensions)}.")
    values = variable[time_index][np.ix_(lat_index, lon_index)].astype(float)
    fill = attribute(variable, "missing_value")
    if fill is not None:
        values[values == float(np.ravel(fill)[0])] = np.nan
    return values


def block_means(values: np.ndarray) -> list[list[float | None]]:
    """Average each block of BLOCK × BLOCK cells, ignoring the missing ones, rounded to 2 decimals."""
    rows, columns = values.shape
    blocks = values.reshape(rows // BLOCK, BLOCK, columns // BLOCK, BLOCK)
    counts = np.sum(~np.isnan(blocks), axis=(1, 3))
    totals = np.nansum(blocks, axis=(1, 3))
    means = totals / np.where(counts, counts, 1)
    # Adding 0.0 turns -0.0 into 0.0.
    return [
        [round(float(mean), 2) + 0.0 if count else None for mean, count in zip(mean_row, count_row)]
        for mean_row, count_row in zip(means, counts)
    ]


def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Add to the records the provenance the registry declares, the ingestion time and the version."""
    return {
        "id": ID,
        "source": {
            "institution": SOURCE["institution"],
            "product": SOURCE["product"],
            "url": SOURCE["access"]["url"],
        },
        "variable": SOURCE["variable"],
        "unit": SOURCE["unit"],
        "data_type": SOURCE["data_type"],
        "spatial_resolution": SOURCE["spatial_resolution"],
        "temporal_resolution": SOURCE["temporal_resolution"],
        "reference_period": SOURCE["reference_period"],
        "ingestion_time": ingestion_time.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }
