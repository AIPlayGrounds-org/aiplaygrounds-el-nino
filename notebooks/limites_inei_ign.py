import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone

    import marimo as mo

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import limites_inei_ign as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Límites administrativos del Perú — INEI/IGN

    Este notebook muestra el flujo de la fuente que alimenta el mapa de Territorio:
    **descargar → leer el ZIP → validar → simplificar → armar el JSON**.

    - Fuente y atribución: [`sources.toml`](../sources.toml)
    - Reglas: [`docs/data-contract.md`](../docs/data-contract.md)
    - El notebook no escribe en `data/`; la publicación usa `wawapacha-pipeline run limites-inei-ign`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    HDX entrega un ZIP con las capas `per_admin1.geojson` y `per_admin2.geojson`.
    El módulo sigue redirecciones y solo acepta una respuesta HTTP exitosa.
    """)
    return


@app.cell
def _():
    raw = source.fetch()
    mo.md(f"Descargados **{len(raw):,} bytes** desde `{source.URL}`.")
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Leer y validar

    `source.parse()` comprueba el formato ZIP, los nombres seguros, el UTF-8 y el
    JSON. Después exige 25 departamentos y 196 provincias, códigos y nombres no
    vacíos, geometría Polygon/MultiPolygon WGS84 válida, y `valid_on`, `version` y
    `lang` comunes a las dos capas.
    """)
    return


@app.cell
def _(raw):
    try:
        parsed = source.parse(raw)
        validation_error = None
    except ValidationError as error:
        parsed = None
        validation_error = str(error)
        if mo.app_meta().mode == "script":
            raise

    if validation_error:
        _out = mo.callout(
            mo.md(f"**No pasa la validación.** {validation_error}\n\nNo se publicará nada."),
            kind="danger",
        )
    else:
        _out = mo.callout(
            mo.md(
                f"**Validación correcta:** {len(parsed['departamentos']['features'])} departamentos "
                f"y {len(parsed['provincias']['features'])} provincias."
            ),
            kind="success",
        )
    _out
    return (parsed,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 3 · Ver las capas simplificadas

    Se conservan solo `name`, `code` y, en provincias, `parent`. La geometría se
    simplifica con Shapely (0,02 grados, preservando la topología) y vuelve a pasar
    las comprobaciones de conteo, códigos y topología antes de continuar.
    """)
    return


@app.cell
def _(parsed):
    mo.stop(parsed is None, mo.md("_Sin capas válidas._"))

    _summary = [
        {
            "capa": "departamentos",
            "features": len(parsed["departamentos"]["features"]),
            "primer elemento": parsed["departamentos"]["features"][0]["properties"],
        },
        {
            "capa": "provincias",
            "features": len(parsed["provincias"]["features"]),
            "primer elemento": parsed["provincias"]["features"][0]["properties"],
        },
    ]
    mo.ui.table(_summary)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` agrega la procedencia declarada en el registro, la versión de
    procesamiento y una única medición geométrica fechada con `valid_on`. Aquí solo
    se muestra una vista resumida; el archivo no se guarda.
    """)
    return


@app.cell
def _(parsed):
    mo.stop(parsed is None, mo.md("_Sin capas válidas._"))

    dataset = source.build(parsed, datetime.now(timezone.utc))
    record = dataset["records"][0]
    _preview = {
        key: value
        for key, value in dataset.items()
        if key != "records"
    }
    _preview["records"] = [{
        "start": record["start"],
        "end": record["end"],
        "version": record["version"],
        "departamentos": len(record["departamentos"]["features"]),
        "provincias": len(record["provincias"]["features"]),
        "attribution": record["attribution"],
    }]
    mo.tree(_preview)


if __name__ == "__main__":
    app.run()
