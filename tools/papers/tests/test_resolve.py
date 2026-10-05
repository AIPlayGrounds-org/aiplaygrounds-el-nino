import httpx
from conftest import fixture_json

from papers.resolve import open_copies


def client_for(routes: dict[str, dict | int]) -> httpx.Client:
    """Serve recorded API responses by host.

    A bare status code represents an error.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        body = routes.get(request.url.host, 404)
        if isinstance(body, int):
            return httpx.Response(body)
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_openalex_gives_best_location_first_then_others_without_repeats():
    client = client_for({"api.openalex.org": fixture_json("openalex")})
    copies = list(open_copies(client, "10.3389/fmars.2018.00367"))
    assert [(c.url, c.licence, c.version) for c in copies] == [
        (
            "https://www.frontiersin.org/articles/10.3389/fmars.2018.00367/pdf",
            "cc-by",
            "publishedVersion",
        ),
        (
            "https://hal.sorbonne-universite.fr/hal-02021154v1/file/fmars-05-00367.pdf",
            None,
            "submittedVersion",
        ),
    ]
    assert {c.source for c in copies} == {"openalex"}
    assert copies[0].title.startswith("Forcings and Evolution")


def test_non_open_locations_are_ignored():
    work = {
        "title": "Closed",
        "best_oa_location": None,
        "locations": [{"is_oa": False, "pdf_url": "https://publisher.example/x.pdf"}],
    }
    client = client_for({"api.openalex.org": work})
    assert list(open_copies(client, "10.1/x")) == []


def test_semantic_scholar_is_asked_when_openalex_has_nothing():
    client = client_for({"api.semanticscholar.org": fixture_json("semantic_scholar")})
    (copy,) = open_copies(client, "10.3389/fmars.2018.00367")
    assert copy.source == "semantic-scholar"
    assert copy.licence == "CCBY"
    assert copy.url.endswith("/10.3389/fmars.2018.00367/pdf")


def test_europe_pmc_gives_the_open_pdf_link_only():
    client = client_for({"www.ebi.ac.uk": fixture_json("europe_pmc")})
    (copy,) = open_copies(client, "10.1371/journal.pone.0185013")
    assert copy.source == "europe-pmc"
    assert copy.url == "https://europepmc.org/articles/PMC5612697?pdf=render"
    assert copy.licence == "cc by"


def test_europe_pmc_ignores_a_record_for_another_doi():
    client = client_for({"www.ebi.ac.uk": fixture_json("europe_pmc")})
    assert list(open_copies(client, "10.1371/journal.other")) == []


def test_a_failing_provider_is_skipped_and_reported():
    client = client_for(
        {
            "api.openalex.org": 500,
            "api.semanticscholar.org": fixture_json("semantic_scholar"),
        }
    )
    errors: list[str] = []
    copies = list(open_copies(client, "10.3389/fmars.2018.00367", errors))
    assert [c.source for c in copies] == ["semantic-scholar"]
    assert len(errors) == 1 and errors[0].startswith("openalex")
