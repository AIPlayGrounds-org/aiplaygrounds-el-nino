import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def papers_home(tmp_path, monkeypatch):
    """Keep every test's cache and drop-in folder out of the real tool folder."""
    monkeypatch.setenv("PAPERS_HOME", str(tmp_path))
    return tmp_path


def fixture_json(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
