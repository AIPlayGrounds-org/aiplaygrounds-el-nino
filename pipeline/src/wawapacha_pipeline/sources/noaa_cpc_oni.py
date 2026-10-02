"""NOAA CPC — Oceanic Niño Index (ONI). Ficha: docs/fuentes/noaa-cpc-oni.md."""

import os
import urllib.request
from datetime import datetime, timezone

from wawapacha_pipeline.contract import ValidationError

# Versión de esta fuente. Súbela cuando cambie la lógica: queda en cada JSON publicado.
VERSION = "0.1.0"

ID = "noaa-cpc-oni"
# NOAA_CPC_ONI_URL permite leer otro archivo (por ejemplo, en los tests).
URL = os.environ.get("NOAA_CPC_ONI_URL", "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt")

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
    """Convierte el archivo en registros y lo valida según docs/datos.md."""
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
    """Añade a los registros los metadatos de procedencia (docs/datos.md §4)."""
    return {
        "id": ID,
        "source": {
            "institution": "NOAA Climate Prediction Center (CPC)",
            "product": "Oceanic Niño Index (ONI)",
            "url": URL,
        },
        "variable": "Anomalía de la temperatura superficial del mar en Niño 3.4, media móvil de tres meses",
        "unit": "°C",
        "data_type": "observado",
        "spatial_resolution": "Región Niño 3.4 (5°N–5°S, 170°W–120°W)",
        "temporal_resolution": "Trimestral móvil",
        "reference_period": "Periodos de 30 años que CPC actualiza cada 5 años",
        "ingestion_time": ingestion_time.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "processing_version": VERSION,
        "records": records,
    }
