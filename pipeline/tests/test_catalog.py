import json
from datetime import timedelta

from wawapacha_pipeline import catalog, cli, registry


def test_docs_sources_is_up_to_date_with_the_registry():
    """If this fails, run `uv run wawapacha-pipeline sources` and commit the change."""
    expected = catalog.render(registry.load(), cli.CATALOG_SOURCES)

    assert catalog.CATALOG_PATH.read_text(encoding="utf-8") == expected


def test_web_source_catalog_is_up_to_date_with_the_registry():
    expected = catalog.render_web(registry.load(), cli.CATALOG_SOURCES)

    assert catalog.WEB_CATALOG_PATH.read_text(encoding="utf-8") == expected


def test_web_catalog_carries_the_stale_threshold_the_freshness_command_uses():
    sources = registry.load()
    web = json.loads(catalog.render_web(sources, cli.CATALOG_SOURCES))["sources"]

    for entry in web:
        update = sources[entry["id"]]["update"]
        if update == "manual":
            assert "stale_after_hours" not in entry
        else:
            assert timedelta(hours=entry["stale_after_hours"]) == (
                registry.stale_after(update)
            )
    assert {entry["id"] for entry in web if "stale_after_hours" in entry}


def test_there_is_one_section_per_source_the_pipeline_reads_and_none_for_the_rest():
    text = catalog.render(registry.load(), cli.CATALOG_SOURCES)

    for source_id in registry.load():
        assert (f"### {source_id}\n" in text) == (source_id in cli.CATALOG_SOURCES)


def test_sources_command_writes_the_catalog(tmp_path, monkeypatch, capsys):
    target = tmp_path / "sources.md"
    web_target = tmp_path / "source-catalog.json"
    monkeypatch.setattr(catalog, "CATALOG_PATH", target)
    monkeypatch.setattr(catalog, "WEB_CATALOG_PATH", web_target)

    assert cli.main(["sources"]) == 0

    assert target.read_text(encoding="utf-8") == catalog.render(
        registry.load(), cli.CATALOG_SOURCES
    )
    assert web_target.read_text(encoding="utf-8") == catalog.render_web(
        registry.load(), cli.CATALOG_SOURCES
    )
    assert "Wrote" in capsys.readouterr().out


def test_table_cells_escape_the_pipe():
    lines = catalog.table(("A", "B"), [("x | y", "z")])

    assert lines[2] == "| x \\| y | z   |"


def test_wrap_keeps_code_and_links_whole():
    text = "one " * 19 + "`two three` [a b](http://x.y/z)"

    lines = catalog.wrap(text)

    assert all(len(line) <= catalog.WIDTH for line in lines)
    assert any("`two three`" in line for line in lines)
    assert any("[a b](http://x.y/z)" in line for line in lines)


def test_wrap_never_starts_a_line_with_a_list_marker():
    text = "word " * 13 + "in December 2020."

    lines = catalog.wrap(text)

    assert not any(line.startswith("2020.") for line in lines)
    assert lines[-1] == "December 2020."
