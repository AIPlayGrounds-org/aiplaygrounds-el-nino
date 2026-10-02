import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone

    import marimo as mo
    import plotly.express as px
    import polars as pl

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import noaa_cpc_oni as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA CPC — Oceanic Niño Index (ONI)

    El índice de referencia internacional de El Niño: la anomalía de la temperatura del mar
    en la región Niño 3.4, promediada en trimestres móviles.

    - La fuente: [`docs/sources.md`](../docs/sources.md#noaa-cpc-oni)
    - Reglas de los datos: [`docs/data-contract.md`](../docs/data-contract.md)
    - Conceptos: [`docs/concepts.md`](../docs/concepts.md)

    Este notebook muestra paso a paso lo que hace [`pipeline/`](../pipeline/src/wawapacha_pipeline/sources/noaa_cpc_oni.py): **descargar → leer y validar → ver → armar el JSON**. No define lógica de la fuente y no escribe en `data/`; para publicar, usa `wawapacha-pipeline run noaa-cpc-oni`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    El archivo es texto en columnas, una fila por trimestre.
    """)
    return


@app.cell
def _():
    raw = source.download()

    _lines = raw.splitlines()
    mo.vstack([
        mo.md(f"Descargados **{len(raw.encode()):,} bytes** y **{len(_lines)} líneas** de `{source.URL}`."),
        mo.md("Primeras y últimas líneas:"),
        mo.plain_text("\n".join(_lines[:4] + ["   ..."] + _lines[-4:])),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `source.parse()` convierte cada línea en un registro y comprueba lo que exige el protocolo:

    - la cabecera es `SEAS YR TOTAL ANOM`;
    - cada línea tiene 4 columnas numéricas y un trimestre conocido;
    - la temperatura y la anomalía están en rangos posibles;
    - la serie empieza en DJF 1950 y no falta ni se repite ningún trimestre.

    Cada trimestre se guarda con los meses que cubre (`start` y `end`): `DJF 1950` va de
    diciembre de 1949 a febrero de 1950.
    """)
    return


@app.cell
def _(raw):
    try:
        records = source.parse(raw)
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
    _fig.add_hline(y=source.THRESHOLD, line_dash="dash", line_color="firebrick", annotation_text=f"+{source.THRESHOLD} °C · El Niño")
    _fig.add_hline(y=-source.THRESHOLD, line_dash="dash", line_color="steelblue", annotation_text=f"−{source.THRESHOLD} °C · La Niña", annotation_position="bottom right")
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
    streak = oni.select((pl.col("anomaly").reverse() >= source.THRESHOLD).cast(pl.Int32).cum_min().sum()).item()

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

    `source.build()` añade a los registros la procedencia que declara [`sources.toml`](../sources.toml), según el [esquema](../schema/dataset.schema.json). Aquí solo se muestra: el JSON no se guarda.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    dataset = source.build(records, datetime.now(timezone.utc))

    _preview = {k: v for k, v in dataset.items() if k != "records"}
    _preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(_preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
