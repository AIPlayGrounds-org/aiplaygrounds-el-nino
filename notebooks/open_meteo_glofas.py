import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone
    import json

    import marimo as mo
    import polars as pl

    from wawapacha_pipeline.sources import open_meteo_glofas as source


@app.cell
def _():
    mo.md(r"""
    # Open-Meteo GloFAS — caudal simulado en cuencas peruanas

    Este notebook muestra el mismo recorrido que el pipeline: **descargar → validar →
    expandir las series diarias → armar el JSON**. La fuente es un modelo hidrológico,
    por lo que los datos no son mediciones ni niveles oficiales de alerta.

    - [Fuente y atribución](../docs/sources.md#open-meteo-glofas)
    - [Contrato de datos](../docs/data-contract.md)
    - [Implementación](../pipeline/src/wawapacha_pipeline/sources/open_meteo_glofas.py)

    El notebook no escribe en `data/`; para publicar se usa
    `wawapacha-pipeline run open-meteo-glofas`.
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## Paso 1 · Descargar

    La petición consulta los 11 puntos peruanos registrados y solicita el caudal, la
    media, mediana, máximo, mínimo y percentiles 25/75 del conjunto GloFAS.
    """)
    return


@app.cell
def _():
    ingestion_time = datetime.now(timezone.utc)
    raw = source.fetch()
    payload = json.loads(raw)
    mo.vstack(
        [
            mo.md(f"Descargados **{len(raw.encode()):,} bytes** desde `{source.URL}`."),
            mo.md(f"La respuesta contiene **{len(payload)} puntos** y sus coordenadas de cuadrícula."),
            mo.plain_text(raw[:600] + "…"),
        ]
    )
    return ingestion_time, payload, raw


@app.cell
def _():
    mo.md(r"""
    ## Paso 2 · Validar y expandir

    `source.parse()` comprueba HTTP/JSON en la descarga, las 11 coordenadas conocidas,
    las unidades exactas `m³/s`, arrays alineados, fechas ISO consecutivas, valores
    finitos no negativos y `null` como único valor faltante. Después convierte cada
    posición de las arrays en un registro diario. Las fechas hasta la ingestión UTC son
    `estimated`; el horizonte es `forecast`.
    """)
    return


@app.cell
def _(ingestion_time, raw):
    records = source.parse(raw, ingestion_time.date())
    records_frame = pl.DataFrame(records)
    mo.vstack(
        [
            mo.callout(
                mo.md(f"**Validación correcta:** {len(records):,} registros diarios."),
                kind="success",
            ),
            mo.ui.table(records_frame.head(20)),
        ]
    )
    return (records,)


@app.cell
def _(records):
    mo.md(r"""
    ## Paso 3 · Ver pasado y pronóstico

    El eje muestra los registros por tipo de dato. La cola de fechas que el API entrega
    sin valores se conserva como `null`, para no inventar una fecha final ni convertir un
    faltante en cero.
    """)
    return


@app.cell
def _(records):
    summary_frame = pl.DataFrame(records)
    summary = summary_frame.group_by(["point", "data_type"]).agg(
        pl.len().alias("days"),
        pl.col("river_discharge").is_null().sum().alias("missing_discharge"),
    ).sort(["point", "data_type"])
    summary
    return (summary,)


@app.cell
def _(ingestion_time, records):
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` añade la procedencia del registro en `sources.toml`, la hora de
    ingestión y la versión del procesamiento. Solo se inspecciona el resultado en
    memoria: este notebook no publica ni guarda ningún archivo.
    """)
    dataset = source.build(records, ingestion_time)
    preview = {key: value for key, value in dataset.items() if key != "records"}
    preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
