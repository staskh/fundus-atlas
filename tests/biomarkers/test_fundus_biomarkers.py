# ABOUTME: Tests for the fundus-biomarkers adapter: catalogued names answered as themselves, zone C
# ABOUTME: under its own spelling, values converted to pixels, and a missing class left empty.

import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

SIDE = 1024
UM_PER_PX = 10.0


@pytest.fixture(scope="module")
def adapter():
    return catalogue.load("fundus-biomarkers")


@pytest.fixture(scope="module")
def shape():
    return library.build("spokes-disc-centred", side=SIDE, um_per_px=UM_PER_PX)


def test_every_name_it_answers_under_is_catalogued_or_plainly_its_own(adapter) -> None:
    for key in adapter.keys():
        if "/" in key:
            canonical.check(key)
    assert any(".C" in key for key in adapter.keys()), "zone C is kept, under its own name"
    names = adapter.declare()["names"]
    assert set(names) == set(adapter.keys())
    assert all(names[key] is None for key in names if "/" not in key)


def test_it_reports_pixels_that_convert_back_to_the_shape_s_microns(adapter, shape) -> None:
    found = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, UM_PER_PX)
    expected = shape.theory["calibre/CRE-knudtson/artery/B"]
    measured = canonical.from_pixels(
        "calibre/CRE-knudtson/artery/B", found["calibre/CRE-knudtson/artery/B"], UM_PER_PX
    )
    assert measured == pytest.approx(expected, rel=0.03)


def test_a_missing_class_is_none_and_never_borrowed(adapter, shape) -> None:
    found = adapter.measure(shape.artery, None, shape.fov, shape.disc, UM_PER_PX)
    assert found["density/area/vein"] is None
    assert found["calibre/AVR-knudtson/both/B"] is None
    assert found["density/area/artery"] is not None


def test_without_a_scale_nothing_is_guessed(adapter, shape) -> None:
    found = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, None)
    assert all(value is None for value in found.values())
