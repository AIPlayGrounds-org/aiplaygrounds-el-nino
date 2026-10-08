import re
from pathlib import Path

import pytest

from wawapacha_pipeline.contract import REPO_ROOT

TESTS_DIR = REPO_ROOT / "pipeline" / "tests"
SKIPPED_DIRECTORIES = {".git", ".venv", "node_modules", ".nuxt", ".output"}
TEST_NAME = re.compile(r"`(test_[a-z0-9_]+)`")
TEST_LINK = re.compile(r"\[`(test_[a-z0-9_]+)`\]\(([^)#]+)\)")
TEST_FILE_LINK = re.compile(r"\]\(([^)#]*(?:tests?/|test_)[^)#]*\.(?:py|ts))")
DEFINITION = re.compile(r"^\s*(?:async )?def (test_[a-z0-9_]+)", re.MULTILINE)


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*.md")
        if not SKIPPED_DIRECTORIES & set(path.relative_to(REPO_ROOT).parts)
    )


def defined_tests(tests_dir: Path = TESTS_DIR) -> dict[Path, set[str]]:
    return {
        path.resolve(): set(DEFINITION.findall(path.read_text(encoding="utf-8")))
        for path in tests_dir.glob("test_*.py")
    }


def problems(text: str, directory: Path, tests: dict[Path, set[str]]) -> list[str]:
    """What a document says about tests that the test files do not back."""
    found = []
    for name in TEST_NAME.findall(text):
        if not any(name in names for names in tests.values()):
            found.append(f"{name} is not defined in the tests")
    for name, target in TEST_LINK.findall(text):
        if name not in tests.get((directory / target).resolve(), set()):
            found.append(f"{name} is not defined in {target}")
    for target in TEST_FILE_LINK.findall(text):
        if not (directory / target).exists():
            found.append(f"{target} does not exist")
    return found


@pytest.mark.parametrize(
    "document", markdown_files(), ids=lambda path: str(path.relative_to(REPO_ROOT))
)
def test_docs_name_only_tests_that_exist(document):
    found = problems(
        document.read_text(encoding="utf-8"), document.parent, defined_tests()
    )

    assert not found, "; ".join(found)


def test_the_check_reports_a_missing_test_a_wrong_file_and_a_missing_file(tmp_path):
    (tmp_path / "test_a.py").write_text("def test_exists():\n    pass\n")
    (tmp_path / "test_b.py").write_text("async def test_other():\n    pass\n")
    text = (
        "[`test_exists`](test_a.py) is fine and so is `test_other`. "
        "[`test_exists`](test_b.py) is in the wrong file, `test_gone` is missing, "
        "and [the test](test_c.py) does not exist."
    )

    assert problems(text, tmp_path, defined_tests(tmp_path)) == [
        "test_gone is not defined in the tests",
        "test_exists is not defined in test_b.py",
        "test_c.py does not exist",
    ]
