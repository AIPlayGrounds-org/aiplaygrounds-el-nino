import json

import pytest

from wawapacha_pipeline.contract import (
    DATA_DIR,
    REPO_ROOT,
    ValidationError,
    publish,
    validate,
)

PUBLISHED = sorted((REPO_ROOT / "data").glob("*.json"))


def valid_dataset() -> dict:
    return {
        "id": "test-source",
        "source": {
            "institution": "Institution",
            "product": "Product",
            "url": "https://example.org/data.txt",
        },
        "variable": "Variable",
        "unit": "°C",
        "data_type": "observed",
        "spatial_resolution": "Global",
        "temporal_resolution": "Monthly",
        "ingestion_time": "2026-10-01T12:00:00+00:00",
        "processing_version": "0.1.0",
        "records": [{"start": "2026-01", "end": "2026-01", "value": 1.0}],
    }


def test_there_is_published_data_to_check():
    assert PUBLISHED


@pytest.mark.parametrize("path", PUBLISHED, ids=lambda p: p.name)
def test_published_json_matches_the_schema(path):
    validate(json.loads(path.read_text(encoding="utf-8")))


def test_data_dir_defaults_to_the_repo_data_folder():
    assert DATA_DIR == REPO_ROOT / "data"


def test_accepts_a_source_with_its_own_fields():
    validate(valid_dataset())


@pytest.mark.parametrize(
    ("change", "where"),
    [
        (lambda d: d.pop("unit"), "unit"),
        (lambda d: d.update(data_type="status"), "data_type"),
        (lambda d: d.update(ingestion_time="yesterday"), "ingestion_time"),
        (lambda d: d.update(records=[]), "records"),
        (lambda d: d.update(extra=1), "extra"),
        (lambda d: d["source"].update(url="ftp://example.org"), "source/url"),
        (lambda d: d["records"][0].pop("end"), "records/0"),
        (lambda d: d["records"][0].update(start="January"), "records/0/start"),
    ],
)
def test_rejects_a_dataset_that_breaks_the_contract(change, where):
    dataset = valid_dataset()
    change(dataset)

    with pytest.raises(ValidationError, match=where):
        validate(dataset)


def test_oni_records_must_have_exactly_the_oni_fields():
    dataset = valid_dataset() | {"id": "noaa-cpc-oni"}

    with pytest.raises(ValidationError, match="records/0"):
        validate(dataset)


def test_publish_refuses_an_invalid_dataset_and_leaves_no_file(tmp_path):
    dataset = valid_dataset()
    dataset.pop("variable")

    with pytest.raises(ValidationError, match="variable"):
        publish(dataset, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_publish_keeps_the_previous_json_when_the_new_one_is_invalid(tmp_path):
    previous = tmp_path / "test-source.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")
    dataset = valid_dataset() | {"data_type": "status"}

    with pytest.raises(ValidationError):
        publish(dataset, tmp_path)

    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'
