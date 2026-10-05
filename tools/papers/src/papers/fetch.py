"""Download the open PDF for a DOI into the cache, with a provenance sidecar."""

import json
from datetime import date
from pathlib import Path

import httpx

from papers import store
from papers.resolve import OpenCopy, open_copies


class NoOpenCopy(Exception):
    """No legal open-access PDF could be downloaded."""


def _download(client: httpx.Client, url: str) -> bytes:
    response = client.get(url)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise ValueError("response is not a PDF")
    return response.content


def fetch(client: httpx.Client, doi: str, retrieved: date | None = None) -> Path:
    """Save `cache/pdf/<slug>.pdf` and `<slug>.json`; return the PDF path."""
    doi = store.normalise_doi(doi)
    errors: list[str] = []
    for copy in open_copies(client, doi, errors):
        try:
            content = _download(client, copy.url)
        except (httpx.HTTPError, ValueError) as error:
            errors.append(f"{copy.url}: {error}")
            continue
        return _save(doi, copy, content, retrieved or date.today())
    detail = "".join(f"\n  {line}" for line in errors)
    raise NoOpenCopy(
        f"No open-access PDF found for {doi}.{detail}\n"
        f"If you have a copy, put it in {store.dropin_dir()}/ and run `papers read` on it."
    )


def _save(doi: str, copy: OpenCopy, content: bytes, retrieved: date) -> Path:
    slug = store.slugify(doi)
    store.pdf_dir().mkdir(parents=True, exist_ok=True)
    pdf = store.pdf_dir() / f"{slug}.pdf"
    pdf.write_bytes(content)
    sidecar = {
        "doi": doi,
        "title": copy.title,
        "url": copy.url,
        "licence": copy.licence,
        "version": copy.version,
        "source": copy.source,
        "retrieved": retrieved.isoformat(),
    }
    pdf.with_suffix(".json").write_text(
        json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return pdf
