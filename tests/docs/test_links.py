# ABOUTME: Every relative Markdown link in the catalogue, the plans and the skills resolves to a
# ABOUTME: file that exists — including the ones written to be read from a page they are copied into.

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: A relative link to another Markdown file. Anchors are dropped; a target carrying a `<placeholder>`
#: is skipped, because `docs/models/<slug>.md` names a page the author is about to write.
LINK = re.compile(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)")

#: What is checked. The skills are in because a pointer a reader cannot follow is a pointer that
#: stops being maintained — all 24 of the ones this test first found were off by one directory,
#: a skill sitting at `.claude/skills/<name>/` and counting two levels to the root instead of three.
TREES = ("docs", ".claude/skills")
PAGES = ("README.md", "CLAUDE.md", "PLAN-BENCHMARK.md", "PLAN-BIOMARKER.md")

#: **Where a file's links are resolved from, when that is not the file's own directory.** A
#: template is not a page: it is the text of a page somebody is about to write, so its links have to
#: work from *that* page's directory. The same is true of a fenced example showing what a generated
#: block contains. Resolving those where they sit would demand the opposite of what they need.
RESOLVED_FROM = {
    ".claude/skills/document-biomarker/template.md": "docs/biomarkers",
    ".claude/skills/document-dataset/template.md": "docs/datasets",
    ".claude/skills/document-model/template.md": "docs/models",
    ".claude/skills/document-paper/template.md": "docs/papers",
    ".claude/skills/document-project/template.md": "docs/projects",
    ".claude/skills/document-benchmark/SKILL.md": "docs/benchmarks",
}


def _pages() -> list[Path]:
    found = [ROOT / name for name in PAGES]
    for tree in TREES:
        found.extend(sorted((ROOT / tree).rglob("*.md")))
    return [page for page in found if page.exists()]


def _resolves_from(page: Path) -> list[Path]:
    """The directories a page's links may be read from — its own, and any it is written for.

    A skill that carries an example *and* its own prose needs both: the example resolves from the
    page it illustrates and the prose from where it sits, and neither is wrong.
    """
    declared = RESOLVED_FROM.get(str(page.relative_to(ROOT)))
    return [page.parent] + ([ROOT / declared] if declared else [])


@pytest.mark.parametrize("page", _pages(), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_relative_link_resolves(page: Path) -> None:
    here = str(page.relative_to(ROOT))
    broken = []
    for link in LINK.findall(page.read_text()):
        if link.startswith(("http://", "https://")) or "<" in link:
            continue
        if not any((base / link).resolve().exists() for base in _resolves_from(page)):
            broken.append(link)

    assert not broken, f"{here} links to files that do not exist: {broken}"
