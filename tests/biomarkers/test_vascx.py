# ABOUTME: Tests for the VascX adapter: the fovea it has to supply, the one conversion it makes,
# ABOUTME: and the rule that anything depending on the invented axis stays uncatalogued.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

SIDE = 1024


def an_adapter():
    return catalogue.load("vascx")


@pytest.fixture(scope="module")
def shape():
    return library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)


def test_it_declares_the_configuration_it_ran() -> None:
    """A VascX feature is a configurable object, so which configuration ran is part of the result."""
    declared = an_adapter().declare()

    assert declared["slug"] == "vascx"
    assert declared["feature_set"] == "fs_od_centered", "a set VascX ships, not one assembled here"
    assert "disc diameters" in declared["circle"]
    assert declared["upstream"], "a run records the code that produced the number"


def test_every_name_it_answers_under_is_catalogued_or_plainly_its_own() -> None:
    adapter = an_adapter()

    for key in adapter.keys():
        if "/" in key:
            canonical.check(key)
    assert set(adapter.declare()["names"]) == set(adapter.keys())


def test_nothing_measured_against_the_invented_axis_is_catalogued() -> None:
    """The fovea is this fixture's convention, so anything oriented on it is ours, not VascX's.

    A synthetic shape has no macula. VascX's grids need one, so the adapter supplies it — which
    means superior, inferior, temporal and nasal are directions this repository chose. Comparing
    them against anything would be comparing the fixture with itself.
    """
    adapter = an_adapter()

    behind = adapter.declare()["names"]
    for own, catalogued in behind.items():
        if catalogued is None:
            continue
        assert not any(
            direction in own for direction in ("superior", "inferior", "temporal", "nasal")
        ), f"{own} claims {catalogued} but is measured against the axis we invented"
    assert any("temporal_angle" in key for key in adapter.keys()), "and it is still measured"


def test_the_fovea_follows_the_framing() -> None:
    """Frame centre where the disc is off-centre; one offset away where the disc is centred."""
    adapter = an_adapter()

    macula = adapter._fovea(SIDE, SIDE * 0.70, SIDE * 0.5)
    centred = adapter._fovea(SIDE, SIDE / 2, SIDE / 2)

    assert macula == pytest.approx((SIDE / 2, SIDE / 2)), (
        "a macula-centred frame centres the macula"
    )
    assert centred[0] < SIDE / 2, "a disc-centred frame puts the macula to one side of the disc"
    assert centred[1] == pytest.approx(SIDE / 2)


def test_it_converts_its_millimetres_back_to_the_pixels_the_theory_is_in(shape) -> None:
    """The only conversion it makes, and it is exact: the scale is the shape's own.

    VascX is the one implementation here that works in physical units, because it is the one that
    takes a scale. Its calibre comes back in millimetres; the shapes state theirs in pixels.
    """
    adapter = an_adapter()

    measured = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)

    # Under VascX's own names, which is what a run records; the ground truth is the shape's.
    names = adapter.declare()["names"]
    calibre = next(own for own, name in names.items() if name == "vessel-calibre/mean-width/artery")
    equivalent = next(
        own for own, name in names.items() if name == "central-retinal-equivalents/knudtson/artery"
    )

    assert measured[calibre] == pytest.approx(
        shape.theory["vessel-calibre/mean-width/artery"], rel=0.05
    ), "an 80 µm artery at 10 µm per pixel is 8 px across"
    assert measured[equivalent] == pytest.approx(
        shape.theory["central-retinal-equivalents/knudtson/artery"], rel=0.05
    )


def test_it_declines_when_handed_one_class(shape) -> None:
    """Its retina is assembled from both at once, and substituting one for the other would hide."""
    adapter = an_adapter()

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    assert all(value is None for value in measured.values())
    assert adapter.trouble, "and it says why rather than leaving empty cells"


def test_a_crash_is_recorded_rather_than_raised() -> None:
    adapter = an_adapter()
    empty = np.zeros((SIDE, SIDE), dtype=bool)

    measured = adapter.measure(
        empty, empty, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 10.0
    )

    assert set(measured) <= set(adapter.keys())
