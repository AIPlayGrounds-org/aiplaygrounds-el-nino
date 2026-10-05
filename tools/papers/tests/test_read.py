import pypdfium2
import pytest
from reportlab.pdfgen import canvas

from papers import store
from papers.cli import main
from papers.read import PdfNotFound, locate, read

SENTENCE = "Coastal warming reached the Peruvian shelf."


def text_pdf(path):
    page = canvas.Canvas(str(path))
    page.setFont("Helvetica", 22)
    page.drawString(72, 700, SENTENCE)
    page.save()


def scanned_pdf(source, target):
    """Rasterise the first page of `source` into an image-only PDF."""
    page = pypdfium2.PdfDocument(source)[0]
    page.render(scale=3).to_pil().convert("RGB").save(target, "PDF", resolution=216)


def words(pdf_path) -> int:
    page = pypdfium2.PdfDocument(pdf_path)[0]
    return len(page.get_textpage().get_text_range().split())


def test_text_pdf_converts_to_markdown(tmp_path):
    pdf = tmp_path / "A Paper.pdf"
    text_pdf(pdf)

    path, count = read(str(pdf))

    assert path == store.md_dir() / "a_paper.md"
    assert "Peruvian shelf" in path.read_text(encoding="utf-8")
    assert count >= len(SENTENCE.split())


def test_scanned_pdf_is_read_with_ocr(tmp_path):
    original = tmp_path / "original.pdf"
    scan = tmp_path / "scan.pdf"
    text_pdf(original)
    scanned_pdf(original, scan)
    assert words(original) > 0
    assert words(scan) == 0, "the scan must have no text layer"

    path, _ = read(str(scan))

    assert "peruvian" in path.read_text(encoding="utf-8").lower()


def test_read_finds_cached_and_dropin_pdfs_by_doi(tmp_path):
    store.dropin_dir().mkdir(parents=True)
    dropped = store.dropin_dir() / "10.1_demo-paper.pdf"
    dropped.write_bytes(b"%PDF-1.4")
    assert locate("10.1/demo-paper") == dropped

    store.pdf_dir().mkdir(parents=True)
    cached = store.pdf_dir() / "10.1_demo-paper.pdf"
    cached.write_bytes(b"%PDF-1.4")
    assert locate("https://doi.org/10.1/DEMO-paper") == cached


def test_read_unknown_paper_points_to_fetch_and_dropin():
    with pytest.raises(PdfNotFound, match="papers fetch") as raised:
        locate("10.1/missing")
    assert str(store.dropin_dir()) in str(raised.value)


def test_cli_read_prints_path_and_word_count(tmp_path, capsys):
    pdf = tmp_path / "cli.pdf"
    text_pdf(pdf)
    assert main(["read", str(pdf)]) == 0
    path, count = capsys.readouterr().out.splitlines()
    assert path == str(store.md_dir() / "cli.md")
    assert count.endswith(" words")
