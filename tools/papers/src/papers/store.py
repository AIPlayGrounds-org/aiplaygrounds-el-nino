"""Where papers live on disk, and the names they get."""

import os
import re
from pathlib import Path

DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", re.IGNORECASE)


def home() -> Path:
    """Return the directory holding `cache/` and `dropin/`.

    `PAPERS_HOME` overrides the tool folder.
    """
    override = os.environ.get("PAPERS_HOME")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def pdf_dir() -> Path:
    return home() / "cache" / "pdf"


def md_dir() -> Path:
    return home() / "cache" / "md"


def dropin_dir() -> Path:
    return home() / "dropin"


def normalise_doi(value: str) -> str:
    return DOI_PREFIX.sub("", value.strip()).lower()


def slugify(value: str) -> str:
    """Lowercase file-safe name. A DOI and its slug give the same slug."""
    return re.sub(r"[^a-z0-9.-]+", "_", normalise_doi(value)).strip("_")
