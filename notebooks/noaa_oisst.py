import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    import gzip
    import tempfile
    from datetime import datetime, timezone
    from pathlib import Path

    import marimo as mo
    import plotly.express as px
    import polars as pl

    from wawapacha_pipeline.contract import ValidationError, publish
    from wawapacha_pipeline.sources import noaa_oisst as source

    # El límite de docs/data-contract.md: 20 KB comprimido con gzip.
    LIMIT = 20 * 1024


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA OISST — anomalía diaria de la temperatura del mar

    El mapa del panel 5: cuánto se aparta la temperatura del mar de lo normal, día a día, entre
    20°N–25°S y 120°W–60°W.

    - La fuente: [`docs/sources.md`](../docs/sources.md#noaa-oisst)
    - Reglas de los datos: [`docs/data-contract.md`](../docs/data-contract.md)
    - Conceptos: [`docs/concepts.md`](../docs/concepts.md)

    Este notebook muestra paso a paso lo que hace [`pipeline/`](../pipeline/src/wawapacha_pipeline/sources/noaa_oisst.py): **descargar → leer y validar → ver → armar el JSON**. No define lógica de la fuente y no escribe en `data/`; para publicar, usa `wawapacha-pipeline run noaa-oisst`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    NOAA PSL guarda un archivo de temperatura por año y otro con la climatología diaria 1991–2020.
    El servicio NCSS recorta la región en el servidor, así que solo se bajan unos cientos de kilobytes:

    1. la temperatura de los últimos días (se queda con el más reciente);
    2. la climatología de ese mismo día del año.
    """)
    return


@app.cell
def _():
    sst_file, climatology_file = source.fetch()

    _days = source.days(source.read_netcdf(sst_file))
    mo.md(f"Descargados **{len(sst_file):,} bytes** de temperatura (días {_days[0]} a {_days[-1]}) y **{len(climatology_file):,} bytes** de climatología, de `{source.URL}`.")
    return climatology_file, sst_file


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `source.parse()` lee los dos archivos NetCDF, resta la climatología al día más reciente y promedia
    cada bloque de 2 × 2 celdas de 0,25° en una celda de 0,5°. Comprueba lo que exige el protocolo:

    - los archivos son NetCDF clásico, con `lat`, `lon`, `time` y `sst` en °C;
    - los ejes son exactamente la malla de 180 × 240 celdas de la región (el servidor añade una fila y una columna fuera de ella; se descartan);
    - los días van en orden, sin huecos ni repetidos, y la climatología es la del mismo día del año (el 29 de febrero usa el 28);
    - la temperatura (5–35 °C) y la anomalía (±10 °C) están en rangos posibles;
    - al menos la mitad de las celdas tiene valor. El resto son tierra y quedan en `null`.
    """)
    return


@app.cell
def _(climatology_file, sst_file):
    try:
        records = source.parse(sst_file, climatology_file)
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
        _grid = records[0]["anomaly"]
        _valid = sum(value is not None for row in _grid for value in row)
        _out = mo.callout(mo.md(f"**Validación correcta:** {records[0]['start']}, malla de {len(_grid)} × {len(_grid[0])} celdas, {_valid:,} con valor y {len(_grid) * len(_grid[0]) - _valid:,} nulas."), kind="success")
    _out
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 3 · Ver los datos

    La anomalía es la temperatura del día menos la normal 1991–2020 de ese día: rojo es más cálido
    que lo normal y azul, más frío. Los huecos son tierra.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    _record = records[0]
    # polars guarda los `null` como NaN al pasar a numpy, que es lo que el mapa deja en blanco.
    _fig = px.imshow(
        pl.DataFrame(_record["anomaly"], orient="row").to_numpy(),
        x=_record["lon"],
        y=_record["lat"],
        origin="lower",
        aspect="equal",
        color_continuous_scale="RdBu_r",
        color_continuous_midpoint=0,
        labels={"x": "Longitud (°E)", "y": "Latitud (°N)", "color": "Anomalía (°C)"},
        title=f"Anomalía de la temperatura del mar, {_record['start']} (base 1991–2020)",
    )
    mo.ui.plotly(_fig)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Resumen

    Calculado con expresiones de polars sobre las celdas con valor.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    _record = records[0]
    cells = (
        pl.DataFrame({"lat": _record["lat"], "anomaly": _record["anomaly"]})
        .explode("anomaly", empty_as_null=True)
        .with_columns(lon=pl.Series(_record["lon"] * len(_record["lat"])))
        .drop_nulls("anomaly")
    )
    _hottest = cells.sort("anomaly").row(-1, named=True)
    _coldest = cells.sort("anomaly").row(0, named=True)

    mo.hstack([
        mo.stat(f"{_hottest['anomaly']:+.2f} °C", label="Más cálida", caption=f"{_hottest['lat']}°, {_hottest['lon']}°"),
        mo.stat(f"{_coldest['anomaly']:+.2f} °C", label="Más fría", caption=f"{_coldest['lat']}°, {_coldest['lon']}°"),
        mo.stat(f"{cells['anomaly'].mean():+.2f} °C", label="Media de la región", caption="celdas con valor"),
    ], justify="start", gap=2)
    return (cells,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Explorar las celdas

    Filtra, ordena o agrupa sin escribir código. La pestaña **Python code** muestra el código polars equivalente.
    """)
    return


@app.cell
def _(cells):
    explorer = mo.ui.dataframe(cells)
    explorer
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` añade a la malla la procedencia que declara [`sources.toml`](../sources.toml), según el [esquema](../schema/dataset.schema.json). `publish()` valida el JSON contra el esquema; aquí lo escribe en una carpeta temporal, solo para medir los bytes reales. Nada llega a `data/`. El límite es de 20 KB comprimido con gzip.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    dataset = source.build(records, datetime.now(timezone.utc))

    _record = dataset["records"][0]
    _preview = {k: v for k, v in dataset.items() if k != "records"}
    _preview["records"] = [{
        "start": _record["start"],
        "end": _record["end"],
        "lat": f"{len(_record['lat'])} valores, de {_record['lat'][0]} a {_record['lat'][-1]}",
        "lon": f"{len(_record['lon'])} valores, de {_record['lon'][0]} a {_record['lon'][-1]}",
        "anomaly": f"{len(_record['anomaly'])} filas de {len(_record['anomaly'][0])} valores",
    }]
    # El mismo `publish` que usa la producción, en una carpeta temporal: valida contra el esquema y da los bytes reales.
    with tempfile.TemporaryDirectory() as _folder:
        _published = publish(dataset, Path(_folder)).read_bytes()
    _gzipped = len(gzip.compress(_published))
    mo.vstack([
        mo.md(f"El JSON publicado pesa **{len(_published):,} bytes**, **{_gzipped:,}** comprimido con gzip ({_gzipped / LIMIT:.0%} del límite de {LIMIT:,})."),
        mo.tree(_preview),
    ])
    return (dataset,)


if __name__ == "__main__":
    app.run()
