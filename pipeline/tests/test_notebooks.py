"""Los notebooks de ../notebooks muestran el pipeline; no lo reimplementan."""

import ast
import json
import os
import subprocess
import sys
import threading
from contextlib import contextmanager
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

NOTEBOOKS_DIR = Path(__file__).parents[2] / "notebooks"
TESTS_DIR = Path(__file__).parent
SAMPLES_DIR = TESTS_DIR / "samples"
NOTEBOOKS = sorted(NOTEBOOKS_DIR.glob("*.py"))


def sample_uri(name: str) -> str:
    return (SAMPLES_DIR / name).resolve().as_uri()


# Each notebook runs with its source pointed at a sample instead of the network.
# A notebook not listed here must have its own test.
ENVIRONMENTS = {
    "noaa_cpc_oni": {"NOAA_CPC_ONI_URL": sample_uri("oni.ascii.txt")},
    "noaa_cpc_nino_weekly": {"NOAA_CPC_NINO_WEEKLY_URL": sample_uri("nino_weekly.for")},
    "noaa_cpc_outlook": {"NOAA_CPC_OUTLOOK_URL": sample_uri("outlook.html")},
    "noaa_ersst": {"NOAA_ERSST_URL": sample_uri("ersst.v5.el_nino.dat")},
    "open_meteo_glofas": {"OPEN_METEO_GLOFAS_URL": sample_uri("glofas.json")},
    "enfen_communique": {
        "ENFEN_COMMUNIQUE_PATH": str(SAMPLES_DIR / "enfen_17_2026.yaml")
    },
    "chirps": {},
}
# ERA5 requires a date window, so its test uses a local server.
ERA5 = "open_meteo_era5"
# These sources need a fixture of their own, so their test files run the notebook.
RUN_BY_SOURCE_TEST = ("noaa_oisst", "limites_inei_ign")
SOURCE_TEST_NAME = "test_notebook_runs_to_the_end_without_publishing"


@contextmanager
def era5_server():
    """Serve the ERA5 sample with the date window requested by the notebook."""
    sample = json.loads((SAMPLES_DIR / "era5.json").read_text(encoding="utf-8"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlsplit(self.path).query)
            start = date.fromisoformat(query["start_date"][0])
            days = [(start + timedelta(days=n)).isoformat() for n in range(90)]
            points = [{**p, "daily": {**p["daily"], "time": days}} for p in sample]
            body = json.dumps(points).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/era5"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def run_notebook(stem: str, env: dict[str, str], data_dir: Path):
    return subprocess.run(
        [sys.executable, str(NOTEBOOKS_DIR / f"{stem}.py")],
        env=os.environ | env | {"WAWAPACHA_DATA_DIR": str(data_dir)},
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_there_are_notebooks_to_check():
    assert NOTEBOOKS


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_defines_no_functions_or_classes(path):
    """Una celda de marimo se llama `_`; cualquier otra función o clase es lógica que debe vivir en pipeline/."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defined = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name != "_"
    ]

    assert defined == []


def test_every_notebook_is_run_by_a_test():
    unrun = [
        path.name
        for path in NOTEBOOKS
        if path.stem not in {*ENVIRONMENTS, ERA5, *RUN_BY_SOURCE_TEST}
    ]

    assert unrun == []


@pytest.mark.parametrize("stem", RUN_BY_SOURCE_TEST)
def test_the_source_test_that_runs_a_notebook_exists(stem):
    tree = ast.parse((TESTS_DIR / f"test_{stem}.py").read_text(encoding="utf-8"))

    defined = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }

    assert SOURCE_TEST_NAME in defined


@pytest.mark.parametrize("stem", ENVIRONMENTS)
def test_notebook_runs_to_the_end_without_publishing(stem, tmp_path):
    result = run_notebook(stem, ENVIRONMENTS[stem], tmp_path)

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []


def test_era5_notebook_runs_to_the_end_without_publishing(tmp_path):
    with era5_server() as url:
        result = run_notebook(ERA5, {"OPEN_METEO_ERA5_URL": url}, tmp_path)

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []
