import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone

    import marimo as mo
    import plotly.express as px
    import polars as pl

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import noaa_ersst as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA/NCEI ERSSTv5 — índices mensuales Niño

    ERSSTv5 es una reconstrucción estadística mensual de la temperatura superficial
    del mar. Este notebook muestra el índice pequeño que publica NCEI para las cuatro
    regiones Niño, desde enero de 1854.

    La fuente: [`docs/sources.md`](../docs/sources.md#noaa-ersst). Las reglas están en
    [`docs/data-contract.md`](../docs/data-contract.md). El notebook solo descarga,
    valida, visualiza y arma el JSON; nunca escribe en `data/`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    El archivo es texto sin cabecera: `year month NINO3 NINO4 NINO3.4 NINO1.2`.
    """)
    return


@app.cell
def _():
    raw = source.fetch()
    lines = raw.splitlines()
    mo.vstack(
        [
            mo.md(f"Descargados **{len(raw.encode()):,} bytes** y **{len(lines):,} filas** de `{source.URL}`."),
            mo.md("Primeras y últimas filas:"),
            mo.plain_text("\n".join(lines[:4] + ["   ..."] + lines[-4:])),
        ]
    )
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `source.parse()` exige seis columnas, meses válidos, cuatro números finitos dentro
    de −10 a +10 °C, comienzo en 1854-01 y continuidad mensual sin huecos ni duplicados.
    También añade las etiquetas calculadas para las tres ventanas de eventos de la Nota
    Técnica ENFEN 01-2024.
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
        if mo.app_meta().mode == "script":
            raise

    if validation_error:
        _out = mo.callout(mo.md(f"**No pasa la validación.** {validation_error}\n\nNo se publicará nada."), kind="danger")
    else:
        _events = sum("event" in record for record in records)
        _out = mo.callout(mo.md(f"**Validación correcta:** {len(records):,} meses y {_events} meses dentro de ventanas de eventos."), kind="success")
    _out
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 3 · Ver los datos

    La tabla conserva el valor de cada región. Las etiquetas de evento son metadatos
    de contexto, no valores modificados.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))
    table = pl.DataFrame(records)
    table
    return (table,)


@app.cell
def _(table):
    chart_data = table.with_columns(pl.col("start").str.to_date("%Y-%m"))
    figure = px.line(
        chart_data,
        x="start",
        y=["nino12_anomaly", "nino34_anomaly"],
        labels={"start": "Mes", "value": "Anomalía (°C)", "variable": "Región"},
        title="ERSSTv5: anomalías en Niño 1+2 y Niño 3.4",
    )
    figure.update_layout(legend_title_text="")
    mo.ui.plotly(figure)
    return


@app.cell
def _(table):
    _events = table.filter(pl.col("event").is_not_null()) if "event" in table.columns else table
    mo.vstack(
        [
            mo.md(f"**Ventanas de eventos:** {_events.height:,} meses etiquetados."),
            mo.ui.table(_events),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` añade la procedencia declarada en `sources.toml` y la versión del
    procesamiento. Aquí se inspecciona una muestra. La publicación real ocurre con
    `wawapacha-pipeline run noaa-ersst`, después de validar el dataset contra el esquema.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))
    dataset = source.build(records, datetime.now(timezone.utc))
    _preview = {key: value for key, value in dataset.items() if key != "records"}
    _preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(_preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
