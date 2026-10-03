"""Lo que comparten todas las fuentes: el error de validación y la publicación del JSON."""

import json
import os
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads(
    (REPO_ROOT / "schema" / "dataset.schema.json").read_text(encoding="utf-8")
)
DATA_TYPES = SCHEMA["properties"]["data_type"]["enum"]
_VALIDATOR = Draft202012Validator(SCHEMA)
# Carpeta donde se publican los JSON: data/ en la raíz del repositorio.
# WAWAPACHA_DATA_DIR permite usar otra carpeta (por ejemplo, en los tests).
DATA_DIR = Path(os.environ.get("WAWAPACHA_DATA_DIR", REPO_ROOT / "data"))


class ValidationError(Exception):
    """La descarga no cumple docs/data-contract.md y no debe publicarse."""


def validate(dataset: dict) -> None:
    """Check the dataset against schema/dataset.schema.json."""
    error = best_match(_VALIDATOR.iter_errors(dataset))
    if error is not None:
        where = "/".join(str(part) for part in error.absolute_path) or "(root)"
        raise ValidationError(
            f"The JSON does not match the schema at {where}: {error.message}"
        )


def publish(dataset: dict, data_dir: Path = DATA_DIR) -> Path:
    """Valida el dataset y lo guarda en data/<id>.json.

    Escribe primero en un archivo temporal y luego lo renombra. Así, si algo
    falla a mitad de camino, el JSON anterior queda intacto.
    """
    validate(dataset)
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / f"{dataset['id']}.json"
    fd, tmp = tempfile.mkstemp(dir=data_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, target)
    except BaseException:
        os.unlink(tmp)
        raise
    return target


def relative_path(path: Path) -> str:
    """Ruta relativa a la raíz del repositorio, con «/»: se lee igual en Windows, Linux y Mac."""
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()
