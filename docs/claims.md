# Claim registry

[`evidence/claims.toml`](../evidence/claims.toml) holds every sentence the site
states as fact. Each claim carries the quotes that support it, so a reader can
open the document and compare. The claim text is Spanish. Every field name and
locator is English.

## Format

The file starts with `checked_at`, the date of the latest pass over the
registry. Then come the claims:

```toml
[[claim]]
id = "icen-peak-1982-83"
claim_es = "..."
status = "verified"
date_checked = "2026-10-10"
reproduce = "uv run --project pipeline pipeline/scripts/check_icen.py"

[[claim.source]]
ref = "http://met.igp.gob.pe/datos/ICEN.txt"
locator = "ICEN.txt, data row for year 1983, month 6; the file has no pages"
quote = "1983   6    4.32"
sha256 = "af2514affa3a462fd5d509f054cd535ab105cf8397e9341e19761712121f5684"
```

| Field          | Rule                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------- |
| `id`           | Unique, lowercase, hyphenated. The site and [`story.md`](story.md) refer to a claim by it.                          |
| `claim_es`     | The sentence the site may state, with decimal commas. It says no more than its quotes say, and carries their limit. |
| `status`       | `verified` or `held`.                                                                                               |
| `date_checked` | The day the quotes were last compared with the documents.                                                           |
| `reproduce`    | Optional. A command, run from the repository root, that compares the claim's quotes with the live file.             |
| `ref`          | The URL of the document. A claim about code uses a link to the file at a commit.                                    |
| `locator`      | The document title and the page, section or paragraph. Never a line of a local copy.                                |
| `quote`        | Verbatim text in the source language. A claim has one or more `[[claim.source]]` entries.                           |
| `sha256`       | Optional. The hash of a data file that its publisher rewrites in place.                                             |

`status = "verified"` lets the site use the claim. `status = "held"` keeps a
claim whose quotes are checked out of the site: the claim is not bundled, and
`check:claims` rejects a `claim('id')` use or a story link that names it.
Changing a claim to `verified` is the step that publishes it. Any other status,
and a repeated `id`, is an error when the registry is read.

## Quotes and locators

- Copy the quote from the document. Keep its spelling, accents and typographic
  quotes.
- Join the lines of a paragraph with single spaces. Rejoin a word that the
  document hyphenates at a line end. Leave out a footnote marker that text
  extraction glues to a word.
- Write a table row on one line, cells separated by single spaces.
- In a PDF locator, `PDF p. N` is the page's position in the file. Add the
  printed page in parentheses when it differs.
- A scan without a text layer is transcribed from the page image, and its
  locator says so.
- A data file has no pages. Its locator names the row or rows.

No command compares quotes with documents. A person opens each `ref`, finds the
`locator` and reads the `quote` there.

## Reproduce commands

A claim about a data file (a row, a rank, a maximum, a rebuilt chronology) names
the script that checks it against the published file. The scripts read the file
with the ingestion module of the same source and take every expected value from
the quotes in the registry, so a corrected claim is checked against its new
quote:

- [`check_icen.py`](../pipeline/scripts/check_icen.py) compares every `ICEN.txt`
  row a claim quotes, the maximum of each event whose peak a claim names, the
  latest month and its rank, the 2026 values the ENFEN report prints, and the
  chronology of Nota Técnica ENFEN 01-2024 rebuilt from the file.
- [`check_weekly_nino.py`](../pipeline/scripts/check_weekly_nino.py) compares
  every row a claim quotes from the two CPC weekly files, and that the highest
  weekly Niño 1+2 anomaly of each file is a quoted row.

Each script prints the SHA-256 of what it fetched (and the `Last-Modified`
header when the ingestion reader returns it), then exits 1 when the file differs
from a quote. The `sha256` of a source is the hash of the file at
`date_checked`; a different hash with passing checks means the publisher rewrote
rows no claim quotes.

## Checks

```sh
cd web
bun run claims        # regenerate app/data/claims.ts from the registry
bun run check:claims
```

`claims` writes every `verified` claim to
[`claims.ts`](../web/app/data/claims.ts), so each one ships in the site bundle.
`check:claims` fails when:

- a `claim('id')` call in `web/app` or a `[id](../evidence/claims.toml)` link in
  [`story.md`](story.md) names an id that is missing or not `verified`;
- `claims.ts` differs from what the registry generates.

`generate` and `build` run both commands.

## Freshness

Sources change. CPC rewrites the last weeks of its weekly file, ENFEN replaces
an ICENtmp value with the ICEN, and IGP revises the latest ICEN. To re-check:

1. Run the `reproduce` command of each claim that has one.
2. Open the `ref` of every other claim and compare the quote.
3. Set `date_checked` on each claim you compared, and `checked_at` at the top.
4. Change or remove a claim whose quote no longer matches. Do not edit a quote
   to fit a changed document without changing the claim.
