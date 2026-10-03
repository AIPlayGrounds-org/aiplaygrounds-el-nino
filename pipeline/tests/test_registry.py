import pytest

from wawapacha_pipeline import registry

ENTRY = {
    "id": "test-source",
    "institution": "Institution",
    "product": "Product",
    "block": "ENSO",
    "verdict": "pending",
    "delivery": "v0.1",
    "reviewed": "2026-10-01",
    "page": "https://example.org/",
    "update": "manual",
}
AUTOMATED = ENTRY | {
    "verdict": "automatable",
    "variable": "Variable",
    "unit": "°C",
    "data_type": "observed",
    "spatial_resolution": "Global",
    "temporal_resolution": "Monthly",
    "access": {"url": "https://example.org/data.txt"},
}


def write_registry(tmp_path, *blocks: str):
    path = tmp_path / "sources.toml"
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def minimal_block(source_id: str, verdict: str) -> str:
    return (
        f'[[source]]\nid = "{source_id}"\ninstitution = "I"\nproduct = "P"\nblock = "SST"\n'
        f'verdict = "{verdict}"\ndelivery = "v0.2"\nreviewed = "2026-10-01"\npage = "https://example.org/"\nupdate = "manual"\n'
    )


def test_every_automatable_registry_entry_has_a_source_module():
    sources = registry.load()
    modules = registry.discover()

    assert set(modules) == {
        source_id
        for source_id, entry in sources.items()
        if entry["verdict"] == "automatable"
    }
    for source_id, module in modules.items():
        assert module.ID == source_id
        assert source_id in sources, f"{source_id} is not in sources.toml"
        assert sources[source_id]["verdict"] == "automatable"


def test_discovery_rejects_an_automatable_entry_without_a_module(tmp_path):
    entry = AUTOMATED | {"id": "missing-source"}
    block = (
        "[[source]]\n"
        + "\n".join(
            f'{key} = "{value}"'
            for key, value in entry.items()
            if key not in {"access", "id"}
        )
        + '\nid = "missing-source"\n'
        + '\n[ source.access ]\nurl = "https://example.org/data.txt"\n'
    )

    with pytest.raises(registry.RegistryError, match="missing-source.*missing"):
        registry.discover(write_registry(tmp_path, block))


def test_the_real_registry_loads_and_has_unique_ids():
    sources = registry.load()

    assert len(sources) == 27
    assert all(entry["id"] == source_id for source_id, entry in sources.items())


def test_load_keeps_the_order_of_the_file(tmp_path):
    path = write_registry(
        tmp_path, minimal_block("b", "pending"), minimal_block("a", "discard")
    )

    assert list(registry.load(path)) == ["b", "a"]


def test_load_rejects_a_duplicated_id(tmp_path):
    block = minimal_block("a", "pending")

    with pytest.raises(registry.RegistryError, match="duplicate id"):
        registry.load(write_registry(tmp_path, block, block))


def test_get_rejects_an_unknown_source():
    with pytest.raises(registry.RegistryError, match="not in sources.toml"):
        registry.get("does-not-exist")


def test_check_accepts_a_pending_and_an_automated_entry():
    registry.check(ENTRY)
    registry.check(AUTOMATED)


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        (ENTRY | {"institucion": "x"}, "unknown fields"),
        (ENTRY | {"access": {"ruta": "x"}}, "unknown fields"),
        ({k: v for k, v in ENTRY.items() if k != "page"}, "missing fields"),
        (ENTRY | {"verdict": "maybe"}, "verdict"),
        (ENTRY | {"block": "Other"}, "block"),
        (ENTRY | {"delivery": "v9"}, "delivery"),
        (ENTRY | {"update": "hourly"}, "update"),
        (ENTRY | {"reviewed": "yesterday"}, "YYYY-MM-DD"),
        (ENTRY | {"notes": "one text"}, "list of strings"),
        (AUTOMATED | {"data_type": "status"}, "data_type"),
        ({k: v for k, v in AUTOMATED.items() if k != "unit"}, "unit"),
        (AUTOMATED | {"access": {}}, "access.url"),
    ],
)
def test_check_rejects_a_bad_entry(entry, message):
    with pytest.raises(registry.RegistryError, match=message):
        registry.check(entry)
