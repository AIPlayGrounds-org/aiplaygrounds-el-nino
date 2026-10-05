"""Find the lines of a converted paper that match a text or pattern."""

import re
from collections.abc import Iterator
from pathlib import Path

from papers import store


class MarkdownNotFound(Exception):
    """The paper has not been converted yet."""


def markdown_path(slug: str) -> Path:
    path = store.md_dir() / f"{store.slugify(slug)}.md"
    if not path.is_file():
        raise MarkdownNotFound(f"No Markdown for {slug!r}. Run `papers read` first.")
    return path


def search(slug: str, text: str, regex: bool = False) -> Iterator[tuple[int, str]]:
    """Yield `(line number, line)` for each case-insensitive match.

    Line numbers start at 1.
    """
    pattern = re.compile(text if regex else re.escape(text), re.IGNORECASE)
    lines = markdown_path(slug).read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        if pattern.search(line):
            yield number, line
