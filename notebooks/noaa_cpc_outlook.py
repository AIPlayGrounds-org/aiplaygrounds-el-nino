import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone

    import marimo as mo
    import polars as pl

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import noaa_cpc_outlook as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA CPC — ENSO strength probabilities

    La fuente publica nueve categorías de intensidad para nueve temporadas
    móviles de tres meses. Este notebook muestra **descargar → leer y validar →
    explorar → armar el JSON** usando el módulo de la fuente. No escribe en
    `data/`; la publicación de producción la hace `wawapacha-pipeline run
    noaa-cpc-outlook`.

    - [Fuente en `sources.toml`](../sources.toml)
    - [Contrato de datos](../docs/data-contract.md)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md("## Paso 1 · Descargar")
    return


@app.cell
def _():
    raw = source.fetch()
    mo.vstack([
        mo.md(f"Descargados **{len(raw.encode()):,} bytes** de `{source.URL}`."),
        mo.plain_text(raw[:500] + "\n…"),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `source.parse()` selecciona la tabla `#probabilities-table`, toma el
    encabezado `Issued` visible, comprueba las nueve categorías exactas y valida
    que las nueve probabilidades enteras de cada temporada sumen 100.
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
        output = mo.callout(mo.md(f"**No pasa la validación.** {validation_error}"), kind="danger")
    else:
        output = mo.callout(
            mo.md(f"**Validación correcta:** {len(records)} temporadas y 9 categorías por temporada."),
            kind="success",
        )
    output
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md("## Paso 3 · Ver las probabilidades")
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))
    table = pl.DataFrame(
        [
            {
                "issue_date": record["issue_date"],
                "season": record["season"],
                "start": record["start"],
                "end": record["end"],
                **category,
            }
            for record in records
            for category in record["categories"]
        ]
    )
    mo.ui.table(table)
    return (table,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` añade la procedencia del registro, la fecha de ingestión y
    la versión del procesamiento. Aquí se inspecciona el resultado, pero no se
    llama a `publish()` y no se guarda ningún archivo.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))
    dataset = source.build(records, datetime.now(timezone.utc))
    preview = {key: value for key, value in dataset.items() if key != "records"}
    preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
