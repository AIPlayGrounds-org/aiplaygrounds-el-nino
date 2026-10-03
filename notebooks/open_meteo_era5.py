import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone
    import json

    import marimo as mo
    import polars as pl

    from wawapacha_pipeline.sources import open_meteo_era5 as source


@app.cell
def _():
    mo.md(r"""
    # Open-Meteo ERA5 — daily precipitation by department

    This notebook shows the pipeline's **download → validation → expansion → JSON**
    path. ERA5 is a reanalysis cross-check for CHIRPS, not the primary precipitation
    record. Each department has one rounded Shapely representative point inside its
    boundary. The result is a point sample of a 0.25° cell, not a department mean.

    - [Source and attribution](../docs/sources.md#open-meteo-era5)
    - [Data contract](../docs/data-contract.md)
    - [Implementation](../pipeline/src/wawapacha_pipeline/sources/open_meteo_era5.py)

    The notebook does not write to `data/`; publishing uses
    `wawapacha-pipeline run open-meteo-era5`.
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## Step 1 · Download

    The request sends the 25 department points in one call, asks for the last 90 UTC
    days, and explicitly selects `models=era5`, `timezone=UTC`, and millimetres.
    """)
    return


@app.cell
def _():
    ingestion_time = datetime.now(timezone.utc)
    start, end = source.request_window(ingestion_time.date())
    urls = source.build_urls(start, end)
    raw = source.fetch(urls[0])
    payload = json.loads(raw)
    mo.vstack(
        [
            mo.md(f"Downloaded **{len(raw.encode()):,} bytes** in **{len(urls)} API call**."),
            mo.md(f"The response contains **{len(payload)} points**."),
            mo.plain_text(raw[:600] + "…"),
        ]
    )
    return end, ingestion_time, raw, start


@app.cell
def _():
    mo.md(r"""
    ## Step 2 · Validate and trim the unavailable tail

    Validation checks the returned snapped coordinates, exact units, aligned arrays,
    consecutive dates, and the physical range. `null` remains missing and is never
    changed to zero. The latest non-null day is discovered from this response rather
    than hard-coded.
    """)
    return


@app.cell
def _(raw, start, end):
    records = source.parse(raw, start, end)
    latest = source.last_non_null_day(records)
    records_frame = pl.DataFrame(records)
    mo.vstack(
        [
            mo.callout(mo.md(f"**Validation passed:** latest non-null day is **{latest}**."), kind="success"),
            mo.ui.table(records_frame.head(20)),
        ]
    )
    return latest, records


@app.cell
def _(records):
    summary = (
        pl.DataFrame(records)
        .group_by(["region", "code"])
        .agg(
            pl.len().alias("days"),
            pl.col("precipitation_mm").is_null().sum().alias("missing_days"),
        )
        .sort("code")
    )
    summary
    return (summary,)


@app.cell
def _(ingestion_time, records):
    mo.md(r"""
    ## Step 3 · Build the published JSON

    `source.build()` adds registry provenance, the ingestion time and processing
    version. The notebook only inspects the result in memory.
    """)
    dataset = source.build(records, ingestion_time)
    preview = {key: value for key, value in dataset.items() if key != "records"}
    preview["records"] = [dataset["records"][0], "…", dataset["records"][-1]]
    mo.tree(preview)
    return (dataset,)


if __name__ == "__main__":
    app.run()
