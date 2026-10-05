import pytest

from papers import store
from papers.cli import main
from papers.search import MarkdownNotFound, search

TEXT = """# Title

The Kelvin wave arrived in March.
Nothing here.
Neutral conditions in the Pacific, but NEUTRAL SST off Peru.
Value 12.5 mm and 7 mm.
"""


@pytest.fixture
def slug():
    store.md_dir().mkdir(parents=True)
    (store.md_dir() / "10.1_demo.md").write_text(TEXT, encoding="utf-8")
    return "10.1_demo"


def test_substring_is_case_insensitive_and_numbers_lines_from_one(slug):
    assert list(search(slug, "neutral")) == [
        (5, "Neutral conditions in the Pacific, but NEUTRAL SST off Peru.")
    ]


def test_substring_is_literal(slug):
    assert list(search(slug, "12.5 mm")) == [(6, "Value 12.5 mm and 7 mm.")]
    assert list(search(slug, "12.5|7")) == []


def test_regex(slug):
    assert [n for n, _ in search(slug, r"\d+ mm", regex=True)] == [6]


def test_a_doi_finds_the_same_paper(slug):
    assert [n for n, _ in search("10.1/demo", "kelvin")] == [3]


def test_missing_markdown_says_to_read_first(slug):
    with pytest.raises(MarkdownNotFound, match="papers read"):
        list(search("10.9_other", "x"))


def test_cli_prints_numbered_lines_and_exits_one_without_matches(slug, capsys):
    assert main(["search", slug, "kelvin"]) == 0
    assert capsys.readouterr().out == "3: The Kelvin wave arrived in March.\n"
    assert main(["search", slug, "absent"]) == 1
