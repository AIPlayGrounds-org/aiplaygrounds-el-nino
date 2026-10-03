import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    from datetime import datetime, timezone
    from pathlib import Path

    import marimo as mo
    import numpy as np
    from rasterio.io import MemoryFile
    from rasterio.transform import from_origin

    from wawapacha_pipeline.sources import chirps as source


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # CHIRPS v3 — pentad rainfall by department

    This notebook shows **discover → read and mask → validate → build the JSON**.
    The source uses preliminary Latin America GeoTIFFs, keeps the rolling 36-month
    window, and compares each pentad with the static 1991–2020 baseline. It does not
    download or publish while running; publication uses `wawapacha-pipeline run chirps`.
    """)
    return


@app.cell
def _():
    index_path = Path(__file__).parents[1] / "pipeline" / "tests" / "samples" / "chirps_index.html"
    index = index_path.read_text(encoding="utf-8")
    discovered = source.discover(index, "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/prelim/pentads/latam/tifs/")
    mo.md(f"**Discovery:** {len(discovered)} fixture files; the module reads the live listing from `{source.INDEX_URL}` and chooses its newest file.")
    return (discovered,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Read, mask and validate

    Rasterio reads the single band. The code converts `-9999` to missing, rejects
    negative rainfall or values over 5,000 mm per pentad, and averages the cells
    touched by each department polygon. This tiny raster only illustrates the step;
    the real run downloads CHC GeoTIFFs.
    """)
    return


@app.cell
def _():
    values = np.full((5, 5), 12.0, dtype="float32")
    with MemoryFile() as memory:
        with memory.open(driver="GTiff", width=5, height=5, count=1, dtype="float32", crs="EPSG:4326", transform=from_origin(0, 1, 0.05, 0.05)) as raster:
            raster.write(values, 1)
        tiny_geotiff = memory.read()
    boundary = {
        "name": "Muestra",
        "code": "PE01",
        "geometry": {"type": "Polygon", "coordinates": [[[0, 1], [0.25, 1], [0.25, 0.75], [0, 0.75], [0, 1]]]},
    }
    masked = source.aggregate(tiny_geotiff, [boundary])
    mo.tree({"Rasterio": "GeoTIFF EPSG:4326, 0.05°", "department_mean_mm": masked})
    return


@app.cell
def _(discovered):
    baseline = source.load_baseline()
    preview = source.Pentad(2026, 9, 6, discovered[-1].url)
    dataset = source.build(
        [{
            "region": "Muestra",
            "code": "PE01",
            "start": preview.start.isoformat(),
            "end": preview.end.isoformat(),
            "precipitation_mm": 12.0,
            "anomaly_mm": round(12.0 - baseline["09.6"]["PE01"], 1),
        }],
        datetime.now(timezone.utc),
    )
    mo.tree({**{key: value for key, value in dataset.items() if key != "records"}, "records": dataset["records"]})
    return


if __name__ == "__main__":
    app.run()
