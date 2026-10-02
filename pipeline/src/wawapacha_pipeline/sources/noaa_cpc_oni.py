"""NOAA CPC — Oceanic Niño Index (ONI). Its provenance is in sources.toml."""

import os
import urllib.request
from datetime import datetime, timezone

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError

# Versión de esta fuente. Súbela cuando cambie la lógica: queda en cada JSON publicado.
VERSION = "0.1.0"

ID = "noaa-cpc-oni"
SOURCE = registry.get(ID)
# NOAA_CPC_ONI_URL reads another file (for example, in tests). The JSON keeps the registry URL.
URL = os.environ.get("NOAA_CPC_ONI_URL", SOURCE["access"]["url"])

HEADER = ["SEAS", "YR", "TOTAL", "ANOM"]
# Trimestres en orden. La posición es el mes central: DJF (0) está centrado en enero.
SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
FIRST_SEASON = ("DJF", 1950)

# Rangos físicamente posibles en Niño 3.4. Un valor fuera de ellos es un error de lectura.
SST_RANGE = (20.0, 32.0)
ANOMALY_RANGE = (-5.0, 5.0)

# Umbral oficial de NOAA para El Niño (+) y La Niña (−).
THRESHOLD = 0.5


def download(url: str = URL, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("ascii")


def parse(text: str) -> list[dict]:
    """Convierte el archivo en registros y lo valida según docs/data-contract.md."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or lines[0].split() != HEADER:
        found = lines[0] if lines else "(archivo vacío)"
        raise ValidationError(f"Cabecera inesperada: {found!r}. Se esperaba {' '.join(HEADER)!r}.")

    records = []
    previous = None
    for number, line in enumerate(lines[1:], start=2):
        season, year, sst, anomaly = read_line(line, number)
        center = year * 12 + SEASONS.index(season)  # meses desde el año 0; 0 = enero

        if previous is None and (season, year) != FIRST_SEASON:
            raise ValidationError(f"Línea {number}: la serie debería empezar en DJF 1950, empieza en {season} {year}.")
        if previous is not None and center != previous + 1:
            raise ValidationError(f"Línea {number}: {season} {year} no sigue al trimestre anterior (hueco o duplicado).")
        previous = center

        records.append({
            "season": season,
            "start": month_iso(center - 1),
            "end": month_iso(center + 1),
            "sst": sst,
            "anomaly": anomaly,
        })

    if not records:
        raise ValidationError("El archivo no contiene registros.")
    return records


def read_line(line: str, number: int) -> tuple[str, int, float, float]:
    """Lee y valida una línea: trimestre, año, temperatura y anomalía."""
    parts = line.split()
    if len(parts) != 4:
        raise ValidationError(f"Línea {number}: se esperaban 4 columnas: {line!r}")
    season, year, sst, anomaly = parts
    if season not in SEASONS:
        raise ValidationError(f"Línea {number}: trimestre desconocido {season!r}.")
    try:
        year, sst, anomaly = int(year), float(sst), float(anomaly)
    except ValueError:
        raise ValidationError(f"Línea {number}: valor no numérico: {line!r}") from None
    if not SST_RANGE[0] <= sst <= SST_RANGE[1]:
        raise ValidationError(f"Línea {number}: temperatura fuera de rango ({sst} °C).")
    if not ANOMALY_RANGE[0] <= anomaly <= ANOMALY_RANGE[1]:
        raise ValidationError(f"Línea {number}: anomalía fuera de rango ({anomaly} °C).")
    return season, year, sst, anomaly


def month_iso(index: int) -> str:
    """Convierte «meses desde el año 0» en AAAA-MM."""
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


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
