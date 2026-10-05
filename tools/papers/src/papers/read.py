"""Convert a PDF to Markdown with Docling."""

from functools import cache
from pathlib import Path

from papers import store


class PdfNotFound(Exception):
    """The argument names no PDF in the cache, the drop-in folder or on disk."""


def locate(target: str) -> Path:
    """Resolve a file path, a DOI, or a slug to a PDF."""
    path = Path(target)
    if path.suffix.lower() == ".pdf" and path.is_file():
        return path
    slug = store.slugify(target)
    for folder in (store.pdf_dir(), store.dropin_dir()):
        candidate = folder / f"{slug}.pdf"
        if candidate.is_file():
            return candidate
    raise PdfNotFound(
        f"No PDF for {target!r}. Run `papers fetch <doi>`, or put the PDF in "
        f"{store.dropin_dir()}/ as {slug}.pdf."
    )


@cache
def _converter():
    # Import Docling lazily. Its torch dependency is unnecessary for other commands.
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    # OCR runs only on regions without a text layer. This supports scans and text PDFs.
    options = PdfPipelineOptions(do_ocr=True)
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def convert(pdf: Path) -> str:
    return _converter().convert(pdf).document.export_to_markdown()


def read(target: str) -> tuple[Path, int]:
    """Write `cache/md/<slug>.md`; return its path and word count."""
    pdf = locate(target)
    markdown = convert(pdf)
    store.md_dir().mkdir(parents=True, exist_ok=True)
    out = store.md_dir() / f"{store.slugify(pdf.stem)}.md"
    out.write_text(markdown, encoding="utf-8")
    return out, len(markdown.split())
