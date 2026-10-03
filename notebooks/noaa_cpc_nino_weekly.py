import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime

    import marimo as mo
    import plotly.express as px
    import polars as pl

    from wawapacha_pipeline.contract import ValidationError
    from wawapacha_pipeline.sources import noaa_cpc_nino_weekly as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # NOAA CPC — weekly Niño indices

    This notebook shows the source pipeline step by step: **download → read and
    validate → inspect → build the contract JSON**. It never writes to `data/`.

    The fixed-width file contains weekly SST and anomaly pairs for Niño 1+2,
    3, 3.4 and 4. Negative anomalies are glued to the SST, so parsing by
    whitespace would lose their sign. Panel 2 uses Niño 1+2 as its main series.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Step 1 · Download

    The source module retains the byte hash, `Last-Modified` header and UTC
    retrieval time alongside the downloaded text.
    """)
    return


@app.cell
def _():
    fetched = source.fetch()
    _lines = fetched.text.splitlines()
    mo.vstack([
        mo.md(f"Downloaded **{len(fetched.text.encode()):,} bytes** and **{len(_lines)} lines** from `{source.URL}`."),
        mo.md(f"SHA-256: `{fetched.sha256}` · Last-Modified: `{fetched.last_modified or 'not supplied'}` · Retrieved: `{fetched.retrieved_at}`"),
        mo.plain_text("\n".join(_lines[:4] + ["   ..."] + _lines[-3:])),
    ])
    return (fetched,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Step 2 · Read and validate

    Validation checks the four-line preamble, 62-character rows, fixed offsets,
    one-decimal numeric pairs, physical ranges, Wednesday dates, and strict
    seven-day continuity. A failure prevents publication.
    """)
    return


@app.cell
def _(fetched):
    try:
        records = source.parse(fetched.text)
        validation_error = None
    except ValidationError as error:
        records = None
        validation_error = str(error)
        if mo.app_meta().mode == "script":
            raise

    if validation_error:
        _out = mo.callout(mo.md(f"**Validation failed.** {validation_error}\n\nNothing will be published."), kind="danger")
    else:
        _out = mo.callout(mo.md(f"**Validation passed:** {len(records)} weeks, from {records[0]['start']} to {records[-1]['start']}."), kind="success")
    _out
    return (records,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Step 3 · Inspect the four regions

    Niño 1+2 is the first and main series for the Peru-facing panel. The other
    three regional pairs remain in every record for comparison.
    """)
    return


@app.cell
def _(records):
    mo.stop(records is None, mo.md("_No valid data._"))
    weekly = pl.DataFrame(records)
    weekly
    return (weekly,)


@app.cell
def _(weekly):
    _main = weekly.select(["start", "nino_1_2_sst", "nino_1_2_anomaly"])
    _fig = px.line(
        _main,
        x="start",
        y="nino_1_2_anomaly",
        labels={"start": "Week centered on", "nino_1_2_anomaly": "Niño 1+2 anomaly (°C)"},
        title="Panel 2 main series: Niño 1+2 anomaly",
    )
    _fig.update_traces(hovertemplate="%{x}<br>%{y:+.1f} °C<extra></extra>")
    px_chart = mo.ui.plotly(_fig)
    px_chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Step 4 · Build the JSON preview

    `source.build()` adds provenance from `sources.toml` and the contract
    ingestion timestamp. The notebook only previews the result; publishing is
    done by `wawapacha-pipeline run noaa-cpc-nino-weekly`.
    """)
    return


@app.cell
def _(fetched, records):
    mo.stop(records is None, mo.md("_No valid data._"))
    metadata = fetched.ingestion_metadata
    dataset = source.build(
        records,
        datetime.fromisoformat(metadata["retrieved_at"]),
        {key: metadata[key] for key in ("sha256", "last_modified")},
    )
    _preview = {key: value for key, value in dataset.items() if key != "records"}
    _preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(_preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
