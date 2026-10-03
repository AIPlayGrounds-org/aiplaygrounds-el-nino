import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone

    import marimo as mo

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import enfen_communique as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # ENFEN — Comunicado Oficial

    El estado oficial del sistema de alerta de El Niño Costero, tal como lo declara la Comisión Multisectorial ENFEN en cada comunicado.

    - La fuente: [`docs/sources.md`](../docs/sources.md#enfen-communique)
    - Reglas de los datos: [`docs/data-contract.md`](../docs/data-contract.md)

    Este notebook muestra paso a paso lo que hace [`pipeline/`](../pipeline/src/wawapacha_pipeline/sources/enfen_communique.py): **leer → validar → comprobar si está vencido → armar el JSON**. No define lógica de la fuente y no escribe en `data/`; para publicar, usa `wawapacha-pipeline run enfen-communique`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 1 · Leer

    No se descarga nada: una persona copia el comunicado más reciente en `pipeline/inputs/enfen.yaml`, cada dos semanas aproximadamente.
    """)
    return


@app.cell
def _():
    raw = source.fetch()

    mo.vstack([
        mo.md(f"Leído `{source.PATH}`:"),
        mo.plain_text(raw),
    ])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 2 · Validar

    `source.parse()` exige:

    - una sola clave `enfen`, con `number`, `year`, `date`, `status`, `url` y `next_due`, y sin campos desconocidos;
    - fechas ISO sin comillas; la fecha no está en el futuro y es del año indicado; `next_due` es posterior;
    - un estado que sea exactamente una de las cinco frases oficiales, sin normalizar;
    - una URL `https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-<número>-<año>/` que nombre el mismo comunicado;
    - si hay `checked_at`, que no sea anterior al comunicado ni futuro.
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
        _out = mo.callout(mo.md(f"**Validación correcta:** comunicado {records[0]['number']}-{records[0]['year']}."), kind="success")
    _out
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 3 · ¿Está vencido?

    El estado rige hasta el siguiente comunicado. Si hoy, en hora de Lima, es posterior a la fecha que el comunicado anuncia (`next_due`, guardada como `end`), el registro se marca `stale`: nadie actualizó el YAML a tiempo y la web debe avisarlo.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    _record = records[0]
    mo.hstack([
        mo.stat(_record["status"], label="Estado oficial", caption=f"Comunicado {_record['number']}-{_record['year']}, {_record['start']}"),
        mo.stat("Vencido" if _record["stale"] else "Vigente", label="Próximo comunicado", caption=f"previsto el {_record['end']}"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Paso 4 · Armar el JSON

    `source.build()` añade al registro la procedencia que declara [`sources.toml`](../sources.toml), según el [esquema](../schema/dataset.schema.json). Aquí solo se muestra: el JSON no se guarda.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_Sin datos válidos._"))

    dataset = source.build(records, datetime.now(timezone.utc))
    mo.tree(dataset)
    return (dataset,)


if __name__ == "__main__":
    app.run()
