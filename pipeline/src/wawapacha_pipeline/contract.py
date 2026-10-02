"""Lo que comparten todas las fuentes: el error de validación y la publicación del JSON."""

import json
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
# Carpeta donde se publican los JSON: data/ en la raíz del repositorio.
# WAWAPACHA_DATA_DIR permite usar otra carpeta (por ejemplo, en los tests).
DATA_DIR = Path(os.environ.get("WAWAPACHA_DATA_DIR", REPO_ROOT / "data"))


class ValidationError(Exception):
    """La descarga no cumple docs/datos.md y no debe publicarse."""


def publish(dataset: dict, data_dir: Path = DATA_DIR) -> Path:
    """Guarda el dataset en data/<id>.json.

    Escribe primero en un archivo temporal y luego lo renombra. Así, si algo
    falla a mitad de camino, el JSON anterior queda intacto.
    """
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
