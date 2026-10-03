import base64
import copy
import io
import json
import os
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from wawapacha_pipeline import registry
from wawapacha_pipeline.contract import ValidationError, publish, validate
from wawapacha_pipeline.sources import limites_inei_ign as source

PIPELINE_DIR = Path(__file__).parents[1]
SAMPLES_DIR = Path(__file__).parent / "samples"
ADMIN1_TEMPLATE = json.loads(
    (SAMPLES_DIR / "limites_admin1.geojson").read_text(encoding="utf-8")
)
ADMIN2_TEMPLATE = json.loads(
    (SAMPLES_DIR / "limites_admin2.geojson").read_text(encoding="utf-8")
)


def _feature(template: dict, name: str, code: str, index: int, province: bool) -> dict:
    feature = copy.deepcopy(template["features"][0])
    prefix = -170 + index % 10
    bottom = -80 + (index // 10) * 0.7
    width = 0.4 if province else 0.7
    height = 0.4 if province else 0.7
    feature["properties"] = {
        ("adm2_name" if province else "adm1_name"): name,
        ("adm2_pcode" if province else "adm1_pcode"): code,
        "valid_on": "2020-07-14",
        "version": "v01",
        "lang": "es",
    }
    feature["geometry"] = {
        "type": "Polygon",
        "coordinates": [
            [
                [prefix, bottom],
                [prefix + width, bottom],
                [prefix + width, bottom + height],
                [prefix, bottom + height],
                [prefix, bottom],
            ]
        ],
    }
    return feature


def valid_layers() -> tuple[dict, dict]:
    departments = {
        "type": "FeatureCollection",
        "features": [
            _feature(
                ADMIN1_TEMPLATE,
                f"Department {index:02d}",
                f"PE{index:02d}",
                index,
                False,
            )
            for index in range(1, 26)
        ],
    }
    provinces = {
        "type": "FeatureCollection",
        "features": [
            _feature(
                ADMIN2_TEMPLATE,
                f"Province {index:03d}",
                f"PE{index % 25 + 1:02d}{index // 25 + 1:02d}",
                index,
                True,
            )
            for index in range(196)
        ],
    }
    return departments, provinces


def archive_bytes(
    departments: dict | None = None,
    provinces: dict | None = None,
    members: dict[str, bytes | str] | None = None,
) -> bytes:
    if departments is None or provinces is None:
        departments, provinces = valid_layers()
    members = members or {}
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "per_admin1.geojson",
                members.get("per_admin1.geojson", json.dumps(departments)),
            )
            archive.writestr(
                "per_admin2.geojson",
                members.get("per_admin2.geojson", json.dumps(provinces)),
            )
            for name, value in members.items():
                if name not in {"per_admin1.geojson", "per_admin2.geojson"}:
                    archive.writestr(name, value)
        return buffer.getvalue()


def test_reads_and_simplifies_both_layers():
    parsed = source.parse(archive_bytes())

    assert parsed["valid_on"] == "2020-07-14"
    assert parsed["version"] == "v01"
    assert len(parsed["departamentos"]["features"]) == 25
    assert len(parsed["provincias"]["features"]) == 196
    assert parsed["departamentos"]["features"][0]["properties"] == {
        "name": "Department 01",
        "code": "PE01",
    }
    assert parsed["provincias"]["features"][0]["properties"] == {
        "name": "Province 000",
        "code": "PE0101",
        "parent": "PE01",
    }


def test_ignores_safe_unexpected_members_without_reading_them():
    parsed = source.parse(archive_bytes(members={"per_admin0.geojson": b"not JSON"}))

    assert len(parsed["departamentos"]["features"]) == 25


@pytest.mark.parametrize(
    ("label", "make_payload", "message"),
    [
        (
            "missing member",
            lambda: _remove_member("per_admin2.geojson"),
            "missing expected members",
        ),
        (
            "malformed JSON",
            lambda: archive_bytes(members={"per_admin1.geojson": b"{"}),
            "malformed JSON",
        ),
        (
            "wrong feature collection type",
            lambda: _change_layer(lambda layer: layer.update(type="Feature")),
            "FeatureCollection",
        ),
        (
            "wrong feature count",
            lambda: _change_layer(lambda layer: layer["features"].pop()),
            "expected 25 features",
        ),
        (
            "unsupported geometry",
            lambda: _change_feature(
                lambda feature: feature["geometry"].update(type="Point")
            ),
            "Polygon or MultiPolygon",
        ),
        (
            "empty geometry",
            lambda: _change_feature(
                lambda feature: feature["geometry"].update(coordinates=[])
            ),
            "coordinates cannot be empty",
        ),
        (
            "open ring",
            lambda: _change_feature(
                lambda feature: feature["geometry"]["coordinates"][0].pop()
            ),
            "not closed",
        ),
        (
            "self-intersecting ring",
            lambda: _change_feature(
                lambda feature: feature["geometry"].update(
                    coordinates=[[[0, 0], [2, 3], [0, 2], [3, 0], [0, 0]]]
                )
            ),
            "invalid polygon topology",
        ),
        (
            "hole outside shell",
            lambda: _change_feature(
                lambda feature: feature["geometry"].update(
                    coordinates=[
                        [
                            [-80, -5],
                            [-79, -5],
                            [-78, -4],
                            [-78, -3],
                            [-79, -2],
                            [-80, -3],
                            [-80, -5],
                        ],
                        [
                            [-81, -4],
                            [-80.5, -4],
                            [-80.5, -3.5],
                            [-81, -3.5],
                            [-81, -4],
                        ],
                    ]
                )
            ),
            "Hole lies outside shell",
        ),
        (
            "overlapping multipolygon parts",
            lambda: _change_feature(
                lambda feature: feature["geometry"].update(
                    type="MultiPolygon",
                    coordinates=[
                        [
                            [
                                [-80, -5],
                                [-79, -5],
                                [-78.5, -4],
                                [-79, -3],
                                [-80, -3],
                                [-80, -5],
                            ]
                        ],
                        [
                            [
                                [-79.5, -4.5],
                                [-78.5, -4.5],
                                [-78, -3.5],
                                [-79, -3],
                                [-79.5, -4.5],
                            ]
                        ],
                    ],
                )
            ),
            "Self-intersection",
        ),
        (
            "coordinate outside WGS84",
            lambda: _change_feature(
                lambda feature: feature["geometry"]["coordinates"][0].__setitem__(
                    0, [181, -5]
                )
            ),
            "outside WGS84",
        ),
        (
            "duplicate department code",
            lambda: _change_department(
                lambda feature: feature["properties"].update(adm1_pcode="PE01")
            ),
            "duplicate code",
        ),
        (
            "invalid province code",
            lambda: _change_province(
                lambda feature: feature["properties"].update(adm2_pcode="PE01")
            ),
            "invalid code",
        ),
        (
            "unknown province parent",
            lambda: _change_province(
                lambda feature: feature["properties"].update(adm2_pcode="PE9901")
            ),
            "not a department code",
        ),
        (
            "empty name",
            lambda: _change_feature(
                lambda feature: feature["properties"].update(adm1_name=" ")
            ),
            "non-empty name",
        ),
        (
            "inconsistent metadata",
            lambda: _change_feature(
                lambda feature: feature["properties"].update(version="v02")
            ),
            "consistent",
        ),
        (
            "unparseable valid date",
            lambda: _change_feature(
                lambda feature: feature["properties"].update(valid_on="2020/07/14")
            ),
            "ISO date",
        ),
        (
            "unparseable version",
            lambda: _change_feature(
                lambda feature: feature["properties"].update(version="version-one")
            ),
            "version is not parseable",
        ),
        (
            "unparseable language",
            lambda: _change_feature(
                lambda feature: feature["properties"].update(lang="spa")
            ),
            "two-letter code",
        ),
    ],
)
def test_rejects_each_declared_validation_failure(label, make_payload, message):
    with pytest.raises(ValidationError, match=message):
        source.parse(make_payload())


def _remove_member(name: str) -> bytes:
    departments, provinces = valid_layers()
    members = (
        {"per_admin1.geojson": json.dumps(departments)}
        if name == "per_admin2.geojson"
        else {}
    )
    if name == "per_admin1.geojson":
        members = {"per_admin2.geojson": json.dumps(provinces)}
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as archive:
            for member, value in members.items():
                archive.writestr(member, value)
        return buffer.getvalue()


def _change_layer(change) -> bytes:
    departments, provinces = valid_layers()
    change(departments)
    return archive_bytes(departments, provinces)


def _change_feature(change) -> bytes:
    departments, provinces = valid_layers()
    change(departments["features"][0])
    return archive_bytes(departments, provinces)


def _change_department(change) -> bytes:
    departments, provinces = valid_layers()
    change(departments["features"][1])
    return archive_bytes(departments, provinces)


def _change_province(change) -> bytes:
    departments, provinces = valid_layers()
    change(provinces["features"][0])
    return archive_bytes(departments, provinces)


def test_rejects_unsafe_zip_member_paths():
    with pytest.raises(ValidationError, match="Unsafe ZIP member path"):
        source.parse(archive_bytes(members={"../per_admin3.geojson": b"ignored"}))


def test_rejects_non_utf8_geojson():
    with pytest.raises(ValidationError, match="not UTF-8"):
        source.parse(archive_bytes(members={"per_admin1.geojson": b"\xff"}))


def test_rejects_duplicate_zip_member_names():
    with pytest.raises(ValidationError, match="duplicate member names"):
        departments, provinces = valid_layers()
        with io.BytesIO() as buffer:
            with zipfile.ZipFile(buffer, "w") as archive:
                archive.writestr("per_admin1.geojson", json.dumps(departments))
                archive.writestr("per_admin2.geojson", json.dumps(provinces))
                with pytest.warns(UserWarning, match="Duplicate name"):
                    archive.writestr("per_admin1.geojson", json.dumps(departments))
            source.parse(buffer.getvalue())


def test_build_contains_the_boundary_record_and_attribution():
    parsed = source.parse(archive_bytes())
    dataset = source.build(parsed, datetime(2026, 10, 2, 12, tzinfo=UTC))

    validate(dataset)
    record = dataset["records"][0]
    assert record["start"] == record["end"] == "2020-07-14"
    assert record["version"] == "v01"
    assert "CC BY 3.0 IGO" in record["attribution"]
    assert record["license_url"] == source.LICENSE_URL
    assert dataset["source"] == {
        "institution": registry.get(source.ID)["institution"],
        "product": registry.get(source.ID)["product"],
        "url": registry.get(source.ID)["access"]["url"],
    }


def test_publish_writes_the_json(tmp_path):
    parsed = source.parse(archive_bytes())
    dataset = source.build(parsed, datetime(2026, 10, 2, 12, tzinfo=UTC))

    path = publish(dataset, tmp_path)

    assert path == tmp_path / "limites-inei-ign.json"
    assert json.loads(path.read_text(encoding="utf-8")) == dataset


def test_rejects_neighbouring_features_that_overlap():
    def overlap_first_department(feature):
        first = _feature(ADMIN1_TEMPLATE, "Department 01", "PE01", 1, False)[
            "geometry"
        ]["coordinates"][0]
        feature["geometry"]["coordinates"] = [[[x + 0.3, y] for x, y in first]]

    with pytest.raises(ValidationError, match="overlap or have mismatched"):
        source.parse(_change_department(overlap_first_department))


def run_cli(source_path: Path, data_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ | {
        "LIMITES_INEI_IGN_URL": source_path.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(data_dir),
    }
    return subprocess.run(
        [sys.executable, "-m", "wawapacha_pipeline", "run", source.ID],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_publishes_a_local_fixture_without_network(tmp_path):
    source_path = tmp_path / "boundaries.zip"
    source_path.write_bytes(archive_bytes())

    result = run_cli(source_path, tmp_path / "data")

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Published limites-inei-ign: 1 records in ")
    published = json.loads(
        (tmp_path / "data" / "limites-inei-ign.json").read_text(encoding="utf-8")
    )
    assert len(published["records"][0]["departamentos"]["features"]) == 25


def test_cli_keeps_the_previous_json_when_the_zip_is_invalid(tmp_path):
    source_path = tmp_path / "broken.zip"
    source_path.write_bytes(b"not a ZIP")
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    previous = data_dir / "limites-inei-ign.json"
    previous.write_text('{"version": "previous"}', encoding="utf-8")

    result = run_cli(source_path, data_dir)

    assert result.returncode == 1
    assert "not a valid ZIP archive" in result.stderr
    assert previous.read_text(encoding="utf-8") == '{"version": "previous"}'


def test_publish_rejects_a_payload_over_the_gzip_limit(tmp_path):
    parsed = source.parse(archive_bytes())
    dataset = source.build(parsed, datetime(2026, 10, 2, 12, tzinfo=UTC))
    dataset["records"][0]["attribution"] = base64.b64encode(os.urandom(300_000)).decode(
        "ascii"
    )

    with pytest.raises(ValidationError, match="gzip bytes"):
        source.publish(dataset, tmp_path)

    assert not (tmp_path / "limites-inei-ign.json").exists()


def test_run_reports_the_number_of_dataset_records(monkeypatch, tmp_path):
    monkeypatch.setattr(source, "fetch", lambda: archive_bytes())
    monkeypatch.setattr(
        source, "publish", lambda dataset: tmp_path / "limites-inei-ign.json"
    )

    count, path = source.run(datetime(2026, 10, 2, 12, tzinfo=UTC))

    assert count == 1
    assert path == tmp_path / "limites-inei-ign.json"


def test_notebook_runs_to_the_end_without_publishing(tmp_path):
    source_path = tmp_path / "boundaries.zip"
    source_path.write_bytes(archive_bytes())
    env = os.environ | {
        "LIMITES_INEI_IGN_URL": source_path.resolve().as_uri(),
        "WAWAPACHA_DATA_DIR": str(tmp_path / "data"),
    }

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parents[2] / "notebooks" / "limites_inei_ign.py"),
        ],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "data").exists()
