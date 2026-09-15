# ABOUTME: Tests for the declared native resolution: a published value, one derived from a stated
# ABOUTME: field angle per image, and the honest absence of one.

import pytest

from datasets.utils import resolution


def test_a_field_angle_is_a_resolution_per_image_rather_than_per_dataset():
    declared = resolution.Declared(
        um_per_px=None, source="field_angle", degrees=30, note="a 30 degree camera"
    )

    # 300 microns to the degree, over a field 900 pixels across.
    assert declared.for_field(450.0) == pytest.approx(300 * 30 / 900)


def test_a_declared_value_ignores_the_field_it_is_given():
    declared = resolution.Declared(um_per_px=4.0, source="published", note="stated by the authors")

    assert declared.for_field(450.0) == pytest.approx(4.0)


def test_an_unknown_resolution_stays_unknown_whatever_the_field():
    declared = resolution.Declared(um_per_px=None, source="unknown", note="nothing published")

    assert declared.for_field(450.0) is None


def test_a_field_angle_without_the_angle_is_refused():
    with pytest.raises(ValueError, match="degrees"):
        resolution.Declared(um_per_px=None, source="field_angle", note="a camera")
