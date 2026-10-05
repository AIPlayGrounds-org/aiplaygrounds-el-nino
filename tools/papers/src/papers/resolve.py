"""Find legal open-access PDFs for a DOI.

Order: OpenAlex (best location, then every other location), Semantic Scholar,
Europe PMC. Each source is asked only when the earlier copies did not download.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import quote

import httpx

OPENALEX = "https://api.openalex.org/works/doi:{doi}"
SEMANTIC_SCHOLAR = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


@dataclass(frozen=True)
class OpenCopy:
    url: str
    licence: str | None
    version: str | None
    source: str
    title: str | None = None


def _get_json(client: httpx.Client, url: str, **params: str) -> dict:
    response = client.get(url, params=params or None)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json()


def _openalex(client: httpx.Client, doi: str) -> Iterator[OpenCopy]:
    work = _get_json(client, OPENALEX.format(doi=quote(doi, safe="/")))
    locations = [work.get("best_oa_location"), *(work.get("locations") or [])]
    for location in locations:
        if not location or not location.get("is_oa") or not location.get("pdf_url"):
            continue
        yield OpenCopy(
            url=location["pdf_url"],
            licence=location.get("license"),
            version=location.get("version"),
            source="openalex",
            title=work.get("title"),
        )


def _semantic_scholar(client: httpx.Client, doi: str) -> Iterator[OpenCopy]:
    paper = _get_json(
        client,
        SEMANTIC_SCHOLAR.format(doi=quote(doi, safe="/")),
        fields="title,openAccessPdf",
    )
    pdf = paper.get("openAccessPdf")
    if pdf and pdf.get("url"):
        yield OpenCopy(
            url=pdf["url"],
            licence=pdf.get("license"),
            version=None,
            source="semantic-scholar",
            title=paper.get("title"),
        )


def _europe_pmc(client: httpx.Client, doi: str) -> Iterator[OpenCopy]:
    found = _get_json(
        client, EUROPE_PMC, query=f'DOI:"{doi}"', format="json", resultType="core"
    )
    for record in found.get("resultList", {}).get("result", []):
        if record.get("doi", "").lower() != doi:
            continue
        for link in (record.get("fullTextUrlList") or {}).get("fullTextUrl", []):
            if (
                link.get("documentStyle") == "pdf"
                and link.get("availabilityCode") == "OA"
            ):
                yield OpenCopy(
                    url=link["url"],
                    licence=record.get("license"),
                    version=None,
                    source="europe-pmc",
                    title=record.get("title"),
                )


PROVIDERS = (_openalex, _semantic_scholar, _europe_pmc)


def open_copies(
    client: httpx.Client, doi: str, errors: list[str] | None = None
) -> Iterator[OpenCopy]:
    """Yield open PDF locations in priority order, without repeating a URL.

    A provider that fails is skipped and described in `errors`.
    """
    seen: set[str] = set()
    for provider in PROVIDERS:
        try:
            for copy in provider(client, doi):
                if copy.url not in seen:
                    seen.add(copy.url)
                    yield copy
        except (httpx.HTTPError, ValueError) as error:
            if errors is not None:
                errors.append(f"{provider.__name__.strip('_')}: {error}")
