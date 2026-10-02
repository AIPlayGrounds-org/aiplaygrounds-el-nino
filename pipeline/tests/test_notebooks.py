"""Los notebooks de ../notebooks muestran el pipeline; no lo reimplementan."""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

NOTEBOOKS_DIR = Path(__file__).parents[2] / "notebooks"
SAMPLE_PATH = Path(__file__).parent / "samples" / "oni.ascii.txt"
NOTEBOOKS = sorted(NOTEBOOKS_DIR.glob("*.py"))


def test_there_are_notebooks_to_check():
    assert NOTEBOOKS


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_defines_no_functions_or_classes(path):
    """Una celda de marimo se llama `_`; cualquier otra función o clase es lógica que debe vivir en pipeline/."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defined = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name != "_"
    ]

    assert defined == []


def test_oni_notebook_runs_to_the_end_without_publishing(tmp_path):
    env = os.environ | {"NOAA_CPC_ONI_URL": SAMPLE_PATH.resolve().as_uri(), "WAWAPACHA_DATA_DIR": str(tmp_path)}

    result = subprocess.run(
        [sys.executable, str(NOTEBOOKS_DIR / "noaa_cpc_oni.py")],
        env=env, capture_output=True, text=True, encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []
