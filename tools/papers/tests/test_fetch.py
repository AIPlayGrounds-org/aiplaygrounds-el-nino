import json
from datetime import date

import httpx
import pytest
from conftest import fixture_json

from papers import store
from papers.cli import main
from papers.fetch import NoOpenCopy, fetch

DOI = "10.3389/fmars.2018.00367"
PUBLISHER = "www.frontiersin.org"
REPOSITORY = "hal.sorbonne-universite.fr"
PDF_BYTES = b"%PDF-1.4\nfake body"


def client_with(files: dict[str, httpx.Response]) -> httpx.Client:
    """Serve recorded API metadata and host-specific download responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host == "api.openalex.org":
            return httpx.Response(200, json=fixture_json("openalex"))
        if host in files:
            return files[host]
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_saves_the_pdf_and_its_provenance():
    client = client_with({PUBLISHER: httpx.Response(200, content=PDF_BYTES)})
    pdf = fetch(client, f"https://doi.org/{DOI.upper()}", retrieved=date(2001, 2, 3))

    assert pdf == store.pdf_dir() / "10.3389_fmars.2018.00367.pdf"
    assert pdf.read_bytes() == PDF_BYTES
    assert json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8")) == {
        "doi": DOI,
        "title": "Forcings and Evolution of the 2017 Coastal El Niño Off Northern Peru and Ecuador",
        "url": f"https://{PUBLISHER}/articles/{DOI}/pdf",
        "licence": "cc-by",
        "version": "publishedVersion",
        "source": "openalex",
        "retrieved": "2001-02-03",
    }


def test_fetch_records_the_copy_it_actually_downloaded():
    blocked = httpx.Response(200, content=b"<html>Just a moment...</html>")
    client = client_with(
        {PUBLISHER: blocked, REPOSITORY: httpx.Response(200, content=PDF_BYTES)}
    )
    pdf = fetch(client, DOI)
    sidecar = json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8"))
    assert sidecar["url"].startswith(f"https://{REPOSITORY}/")
    assert sidecar["version"] == "submittedVersion"
    assert sidecar["licence"] is None
    date.fromisoformat(sidecar["retrieved"])


def test_fetch_without_an_open_copy_points_to_the_dropin_folder():
    client = client_with(
        {PUBLISHER: httpx.Response(403), REPOSITORY: httpx.Response(500)}
    )
    with pytest.raises(NoOpenCopy) as raised:
        fetch(client, DOI)
    message = str(raised.value)
    assert DOI in message
    assert str(store.dropin_dir()) in message
    assert not store.pdf_dir().exists()


def test_cli_exits_non_zero_and_explains(monkeypatch, capsys):
    def failing(client, doi):
        raise NoOpenCopy(
            "No open-access PDF found for 10.1/x.\nUse the drop-in folder."
        )

    monkeypatch.setattr("papers.fetch.fetch", failing)
    assert main(["fetch", "10.1/x"]) == 1
    assert "drop-in folder" in capsys.readouterr().err
