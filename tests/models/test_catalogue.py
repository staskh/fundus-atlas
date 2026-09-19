# ABOUTME: Tests for finding a model adapter by the slug its catalogue page carries, which is what
# ABOUTME: ties a benchmark result to the page that records what the model was trained on.

from pathlib import Path

import pytest

from models.utils import catalogue

PAGES = Path(__file__).resolve().parents[2] / "docs" / "models"


def test_an_adapter_is_found_by_its_catalogue_slug() -> None:
    adapter = catalogue.load("quickqual")

    assert adapter.slug == "quickqual"


def test_a_slug_with_no_adapter_says_where_adapters_live() -> None:
    with pytest.raises(LookupError, match="src/models"):
        catalogue.load("no-such-model")


def test_every_adapter_has_the_catalogue_page_its_marks_come_from() -> None:
    missing = [slug for slug in catalogue.slugs() if not (PAGES / f"{slug}.md").exists()]

    assert missing == [], "a model with no page cannot be benchmarked: the page carries its marks"


@pytest.mark.parametrize("slug", catalogue.slugs())
def test_every_adapter_declares_what_the_run_has_to_record(slug: str) -> None:
    declared = catalogue.load(slug).declare()

    assert declared["slug"] == slug
    assert declared["purpose"] in ("quality", "disc/cup", "artery/vein")
    assert declared["grid"] in (512, 1024, 1472), (
        "the store grid the adapter reads — a size the artery/vein stores build because LUNet "
        "works at 1472, since the grid belongs to the model rather than to the dataset"
    )
    assert declared["network_grid"] > 0, "the grid the network itself sees"
    assert isinstance(declared["upstream"], dict)
