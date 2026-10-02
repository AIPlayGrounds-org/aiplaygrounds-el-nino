import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    import json
    import os
    import tempfile
    import urllib.request
    from datetime import datetime, timezone
    from pathlib import Path

    import marimo as mo
    import plotly.express as px
    import polars as pl

    REPO_ROOT = Path(__file__).resolve().parents[1]
    # Carpeta donde se publican los JSON: data/ en la raíz del repositorio.
    # WAWAPACHA_DATA_DIR permite usar otra carpeta (por ejemplo, en los tests).
    DATA_DIR = Path(os.environ.get("WAWAPACHA_DATA_DIR", REPO_ROOT / "data"))

    # Versión de este notebook. Súbela cuando cambie la lógica: queda en cada JSON publicado.
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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA CPC — Oceanic Niño Index (ONI)

    El índice de referencia internacional de El Niño: la anomalía de la temperatura del mar
    en la región Niño 3.4, promediada en trimestres móviles.

    - Ficha de la fuente: [`docs/fuentes/noaa-cpc-oni.md`](../docs/fuentes/noaa-cpc-oni.md)
    - Reglas que sigue este notebook: [`docs/datos.md`](../docs/datos.md)
    - Conceptos: [`docs/conceptos.md`](../docs/conceptos.md)

    Se ejecuta de arriba abajo en cinco pasos: **descargar → leer y validar → ver → armar el JSON → publicar**.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    El archivo es texto en columnas, una fila por trimestre.
    """)
    return


@app.function
def download(url: str = URL, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "WawaPacha/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("ascii")


@app.cell
def _():
    raw = download()

    _lines = raw.splitlines()
    mo.vstack([
        mo.md(f"Descargados **{len(raw.encode()):,} bytes** y **{len(_lines)} líneas** de `{URL}`."),
        mo.md("Primeras y últimas líneas:"),
        mo.plain_text("\n".join(_lines[:4] + ["   ..."] + _lines[-4:])),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `parse()` convierte cada línea en un registro y comprueba lo que exige el protocolo:

    - la cabecera es `SEAS YR TOTAL ANOM`;
    - cada línea tiene 4 columnas numéricas y un trimestre conocido;
    - la temperatura y la anomalía están en rangos posibles;
    - la serie empieza en DJF 1950 y no falta ni se repite ningún trimestre.

    Cada trimestre se guarda con los meses que cubre (`start` y `end`): `DJF 1950` va de
    diciembre de 1949 a febrero de 1950.
    """)
    return


@app.class_definition
class ValidationError(Exception):
    """La descarga no cumple el protocolo de datos y no debe publicarse."""


@app.function
def parse(text: str) -> list[dict]:
    """Convierte el archivo en registros y lo valida según el protocolo de datos."""
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


@app.function
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


@app.function
def month_iso(index: int) -> str:
    """Convierte «meses desde el año 0» en AAAA-MM."""
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


@app.cell
def _(raw):
    try:
        records = parse(raw)
        validation_error = None
    except ValidationError as error:
        records = None
        validation_error = str(error)
        # Sin interfaz (producción), un error debe detener la ejecución.
        if mo.app_meta().mode == "script":
            raise

    if validation_error:
        _out = mo.callout(mo.md(f"**No pasa la validación.** {validation_error}\n\nNo se publicará nada."), kind="danger")
    else:
        _out = mo.callout(mo.md(f"**Validación correcta:** {len(records)} trimestres, de {records[0]['start']} a {records[-1]['end']}."), kind="success")
    _out
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 3 · Ver los datos

    Los registros válidos pasan a una tabla de polars. Para dibujar cada trimestre se usa su mes central
    (`center`): JJA 2026 se dibuja en julio de 2026.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    oni = pl.DataFrame(records).with_columns(
        pl.col("start").str.to_date("%Y-%m"),
        pl.col("end").str.to_date("%Y-%m"),
    ).with_columns(
        center=pl.col("start").dt.offset_by("1mo"),
    )
    oni
    return (oni,)


@app.cell
def _(oni):
    _last = oni.row(-1, named=True)

    _fig = px.line(
        oni,
        x="center",
        y="anomaly",
        markers=True,
        hover_data=["season", "sst"],
        labels={"center": "Trimestre (mes central)", "anomaly": "Anomalía (°C)", "sst": "Temperatura (°C)", "season": "Trimestre"},
        title="ONI: anomalía de la temperatura del mar en Niño 3.4",
    )
    _fig.update_traces(marker_size=3)
    _fig.add_hline(y=THRESHOLD, line_dash="dash", line_color="firebrick", annotation_text=f"+{THRESHOLD} °C · El Niño")
    _fig.add_hline(y=-THRESHOLD, line_dash="dash", line_color="steelblue", annotation_text=f"−{THRESHOLD} °C · La Niña", annotation_position="bottom right")
    _fig.add_scatter(
        x=[_last["center"]],
        y=[_last["anomaly"]],
        mode="markers",
        marker=dict(size=11, color="firebrick"),
        name=f"Último: {_last['season']} {_last['center'].year} ({_last['anomaly']:+.2f} °C)",
    )
    _fig.update_layout(dragmode="select", legend=dict(orientation="h", y=-0.2))

    chart = mo.ui.plotly(_fig)
    mo.vstack([mo.md("Arrastra sobre el gráfico para seleccionar un periodo; la tabla de abajo mostrará esos trimestres."), chart])
    return (chart,)


@app.cell
def _(chart, oni):
    _dates = [p["x"] for p in chart.value if "x" in p]
    if _dates:
        _from, _to = min(_dates)[:10], max(_dates)[:10]
        _selection = oni.filter(pl.col("center").is_between(pl.lit(_from).str.to_date(), pl.lit(_to).str.to_date()))
        _out = mo.vstack([mo.md(f"**Selección:** {_selection.height} trimestres, de {_from} a {_to}."), mo.ui.table(_selection)])
    else:
        _out = mo.md("_Ningún periodo seleccionado._")
    _out
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Resumen

    Calculado con expresiones de polars. La racha cuenta los trimestres seguidos con anomalía
    ≥ +0,5 °C hasta el último dato; NOAA exige al menos cinco para hablar de un episodio El Niño.
    """)
    return


@app.cell
def _(oni):
    _max = oni.sort("anomaly").row(-1, named=True)
    _min = oni.sort("anomaly").row(0, named=True)

    # Recorre la serie desde el final: cum_min se queda en 0 en cuanto un trimestre no supera el umbral.
    streak = oni.select((pl.col("anomaly").reverse() >= THRESHOLD).cast(pl.Int32).cum_min().sum()).item()

    mo.hstack([
        mo.stat(f"{_max['anomaly']:+.2f} °C", label="Máximo", caption=f"{_max['season']} {_max['center'].year}"),
        mo.stat(f"{_min['anomaly']:+.2f} °C", label="Mínimo", caption=f"{_min['season']} {_min['center'].year}"),
        mo.stat(str(streak), label="Trimestres seguidos ≥ +0,5 °C", caption="hasta el último dato"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Explorar la tabla

    Añade filtros, ordena o agrupa sin escribir código. La pestaña **Python code** muestra el código
    polars equivalente.
    """)
    return


@app.cell
def _(oni):
    explorer = mo.ui.dataframe(oni)
    explorer
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    Se añaden a los registros los metadatos de procedencia que exige el protocolo (§4).
    """)
    return


@app.function
def build(records: list[dict], ingestion_time: datetime) -> dict:
    """Añade a los registros los metadatos de procedencia (protocolo §4)."""
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


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    dataset = build(records, datetime.now(timezone.utc))

    _preview = {k: v for k, v in dataset.items() if k != "records"}
    _preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(_preview)
    return (dataset,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 5 · Publicar

    Al ejecutar el notebook como script (`uv run python noaa_cpc_oni.py`) se publica automáticamente.
    Al abrirlo en marimo hay que pulsar el botón, para no reescribir `data/` sin querer.
    """)
    return


@app.function
def publish(dataset: dict, data_dir: Path = DATA_DIR) -> Path:
    """Guarda el dataset en data/<id>.json.

    Escribe primero en un archivo temporal y luego lo renombra. Así, si algo
    falla a mitad de camino, el JSON anterior queda intacto.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / f"{dataset['id']}.json"
    fd, tmp = tempfile.mkstemp(dir=data_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, target)
    except BaseException:
        os.unlink(tmp)
        raise
    return target


@app.function
def relative_path(path: Path) -> str:
    """Ruta relativa a la raíz del repositorio, con «/»: se lee igual en Windows, Linux y Mac."""
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


@app.cell
def _():
    publish_button = mo.ui.run_button(label="Publicar en data/")
    return (publish_button,)


@app.cell
def _(dataset, publish_button):
    if mo.app_meta().mode == "script" or publish_button.value:
        _path = publish(dataset)
        print(f"Publicado {ID}: {len(dataset['records'])} registros en {relative_path(_path)}")
        _out = mo.callout(mo.md(f"Publicado en `{relative_path(_path)}`."), kind="success")
    else:
        _out = publish_button
    _out
    return


if __name__ == "__main__":
    app.run()
