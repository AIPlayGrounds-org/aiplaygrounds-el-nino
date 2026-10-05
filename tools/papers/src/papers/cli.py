import argparse
import re
import sys

import httpx

from papers import fetch as fetching
from papers import read as reading
from papers import search as searching

USER_AGENT = "wawapacha-papers/0.1 (open-access reader)"


def _fetch(args: argparse.Namespace) -> int:
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=60
    ) as client:
        pdf = fetching.fetch(client, args.doi)
    print(pdf)
    return 0


def _read(args: argparse.Namespace) -> int:
    path, words = reading.read(args.target)
    print(f"{path}\n{words} words")
    return 0


def _search(args: argparse.Namespace) -> int:
    found = 0
    for number, line in searching.search(args.slug, args.text, args.regex):
        print(f"{number}: {line}")
        found += 1
    return 0 if found else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="papers", description="Read open-access papers as Markdown."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="download the open-access PDF for a DOI")
    fetch.add_argument("doi")
    fetch.set_defaults(run=_fetch)

    read = commands.add_parser("read", help="convert a PDF, DOI or slug to Markdown")
    read.add_argument(
        "target", help="PDF path, DOI, or slug of a cached or drop-in PDF"
    )
    read.set_defaults(run=_read)

    search = commands.add_parser(
        "search", help="print matching lines with line numbers"
    )
    search.add_argument("slug", help="slug or DOI of a converted paper")
    search.add_argument("text", help="case-insensitive substring")
    search.add_argument(
        "-e", "--regex", action="store_true", help="treat text as a regular expression"
    )
    search.set_defaults(run=_search)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (
        fetching.NoOpenCopy,
        reading.PdfNotFound,
        searching.MarkdownNotFound,
        re.error,
    ) as error:
        print(f"papers: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
