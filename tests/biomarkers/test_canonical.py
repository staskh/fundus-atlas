# ABOUTME: Tests for the vocabulary's records: the names fundus-biomarkers taught it, and the one
# ABOUTME: biomarker whose answer is a category rather than a number.

import pytest

from biomarkers import canonical


@pytest.mark.parametrize(
    "name",
    [
        "density/skeleton-length-rooted/artery",
        "density/skeleton-length-rooted/vein/B",
        "density/skeleton-length-rooted/vein/C",
    ],
)
def test_the_rooted_skeleton_length_is_a_length_per_class_and_region(name: str) -> None:
    assert canonical.check(name) == name
    assert canonical.unit(name) == "µm"


def test_the_rooted_skeleton_length_is_measured_per_class() -> None:
    with pytest.raises(LookupError):
        canonical.check("density/skeleton-length-rooted/vessels")


def test_the_horizontal_cup_to_disc_ratio_is_a_ratio() -> None:
    assert canonical.unit("landmarks/CDR-horizontal") == "1"


def test_centring_is_a_category_with_its_values_named() -> None:
    assert canonical.unit("landmarks/centring") == "category"
    assert canonical.values("landmarks/centring") == ("disc", "macula", "unknown")


def test_a_category_is_never_converted() -> None:
    assert canonical.length_power("landmarks/centring") == 0
    assert canonical.from_pixels("landmarks/centring", "macula", 5.0) == "macula"


def test_a_number_has_no_categories() -> None:
    assert canonical.values("landmarks/CDR-vertical") == ()


@pytest.mark.parametrize("stem", sorted(canonical.NAMES))
def test_a_biomarker_is_a_category_exactly_when_it_names_its_values(stem: str) -> None:
    record = canonical.NAMES[stem]
    assert (record.unit == "category") == bool(record.values)
