# papers

Reads scientific papers as Markdown, so a claim in the site's references can
quote the passage that supports it. A separate uv package: it imports nothing
from `pipeline/`, and `web/` and CI do not use it.

## Install

```sh
cd tools/papers
uv sync
```

The first conversion downloads Docling's models (about 500 MB, cached by Hugging
Face). Everything runs on CPU, and a two-column paper takes about two minutes.

## Smallest example

```sh
uv run papers fetch 10.3389/fmars.2018.00367   # cache/pdf/<slug>.pdf and <slug>.json
uv run papers read 10.3389/fmars.2018.00367    # cache/md/<slug>.md, prints path and word count
uv run papers search 10.3389/fmars.2018.00367 neutral
```

`search` prints `line: text` for each case-insensitive match and exits 1 when
nothing matches. `-e` reads the text as a regular expression. Its first argument
is a slug or a DOI.

## Where PDFs come from

`fetch` takes only legal open-access copies. It asks OpenAlex (the best
location, then every other location with a PDF), then Semantic Scholar, then
Europe PMC, and keeps the first that downloads. The sidecar JSON records the
DOI, title, URL, licence, version and retrieval date. With no open copy it exits
non-zero.

A PDF you obtained another way goes in `tools/papers/dropin/`, named
`<slug>.pdf`, where the slug is the DOI with each run of characters outside
`a-z 0-9 . -` replaced by `_` (`10.3389/fmars.2018.00367` becomes
`10.3389_fmars.2018.00367`). `papers read <doi-or-slug>` finds it there, and
`papers read path/to/file.pdf` reads any file.

Scanned pages are OCRed by Docling during `read`.

## Tests

```sh
uv run ruff format --check . && uv run ruff check .
uv run pytest
```

Resolution tests replay recorded API responses, with no network. The conversion
tests run Docling on generated PDFs, including one with no text layer, so the
first run needs the model download.

## Non-goals

- No unlicensed sources: no Sci-Hub, Library Genesis or other mirrors.
- No committed paper text. `cache/` and `dropin/` are git-ignored; quote short
  passages in the references and link the DOI.
- No metadata search, citation management or batch crawling.
- No GPU build. Linux installs the CPU build of torch.
