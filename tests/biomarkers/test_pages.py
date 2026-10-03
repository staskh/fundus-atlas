# ABOUTME: Tests for the catalogue pages: that the generated blocks are current, and that the
# ABOUTME: tables a person writes beside them still name biomarkers the vocabulary actually has.

import re
from pathlib import Path

import pytest

from biomarkers import canonical, pages

DOCS = Path(__file__).resolve().parents[2] / "docs"


def test_the_committed_catalogue_pages_are_current() -> None:
    """A generated block and the record cannot disagree, because one is rendered from the other.

    This is the test the Grisan defect argues for: its unit was stated as dimensionless in a
    vocabulary table while its own derivation, two sections below on the same page, called it an
    inverse length. Nothing caught that until the physical units arrived and a shape disagreed
    across two resolutions.
    """
    record = pages.catalogue()
    for name in pages.PAGES:
        path = DOCS / name
        from benchmarks import docs

        assert path.read_text() == docs.render(path.read_text(), record, pages.BLOCKS), (
            f"{path.relative_to(DOCS.parent)} is stale — refresh it with "
            f"`python -m biomarkers.pages`"
        )


#: A canonical name as the hand-written tables spell it: a stem, then either one structure or a
#: `{a,b,c}` set of them, and possibly a region or a statistic after that.
WRITTEN = re.compile(r"`((?:[a-z]+)/(?:vessel-)?[A-Za-z0-9-]+(?:/[{}A-Za-z,-]+)*)`")


def _judgement_tables() -> str:
    """Only the section a person writes: the per-project tables, not the generated one above them.

    Scoping matters. The generated units table names every biomarker by construction, so a test
    reading the whole page would pass however many rows the hand-written tables had lost — which
    is the opposite of what these two tests are for.
    """
    page = (DOCS / "BIOMARKER-NAMES.md").read_text()
    start = page.index("## 3. What each project computes")
    end = page.index("## 4. What each project computes that has no canonical name")
    return page[start:end]


def _stems_named_on(page: str) -> set[str]:
    found = set()
    for match in WRITTEN.findall(page):
        parts = match.split("/")
        if len(parts) < 2 or parts[0] not in canonical.FAMILIES:
            continue
        found.add(f"{parts[0]}/{parts[1].removeprefix('vessel-')}")
    return found


def test_every_biomarker_named_in_the_project_tables_is_one_the_vocabulary_has() -> None:
    """A row for a biomarker that no longer exists is a claim about nothing.

    The ✅ and ⚠️ marks are judgements a person makes and cannot be generated, so what is checked
    is the one part of those tables that *is* a fact: the name in the left-hand column.
    """
    unknown = sorted(
        stem for stem in _stems_named_on(_judgement_tables()) if stem not in canonical.NAMES
    )

    assert not unknown, f"named on the page and absent from the vocabulary: {unknown}"


def test_every_biomarker_the_vocabulary_has_is_named_somewhere_on_the_page() -> None:
    """The other direction: a biomarker nobody wrote a row for is one nobody decided about.

    Adding a name to `canonical.py` is meant to be a decision (see `PLAN-BIOMARKER.md` §1.3), and
    a decision that leaves no trace on the page a reader consults is not one.
    """
    missing = sorted(set(canonical.NAMES) - _stems_named_on(_judgement_tables()))

    assert not missing, f"in the vocabulary and on no row: {missing}"


@pytest.mark.parametrize("name", sorted(canonical.NAMES))
def test_every_biomarker_has_a_family_page_to_link_to(name: str) -> None:
    family = name.split("/")[0]
    assert (DOCS / "biomarkers" / f"{family}.md").exists()
