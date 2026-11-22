# ABOUTME: Tests for the synthetic cup: where it is drawn, and the cup-to-disc ratios its geometry
# ABOUTME: requires at each angle the photograph is turned to.

import math

import numpy as np
import pytest

from benchmarks.shapes import library, scene, truth

SIDE = 1024


def _extent(mask: np.ndarray, axis: int) -> int:
    """How many pixels a mask spans along rows (`axis=0`) or columns (`axis=1`)."""
    lit = np.flatnonzero(mask.any(axis=1 - axis))
    return int(lit[-1] - lit[0] + 1)


def test_the_cup_is_fundus_biomarkers_cup() -> None:
    """The two repositories draw the same eye, so their cups must agree."""
    assert scene.CUP_HORIZONTAL == 0.40
    assert scene.CUP_VERTICAL == 0.55
    assert library.scene("straight").cup == (0.40, 0.55)


def test_the_cup_sits_inside_the_disc_on_its_centre() -> None:
    drawn = library.build("straight", side=SIDE)

    assert drawn.cup.any()
    assert not (drawn.cup & ~drawn.disc_mask).any(), "the cup must lie inside the disc"
    rows, cols = np.nonzero(drawn.cup)
    x, y, _ = drawn.disc
    assert cols.mean() == pytest.approx(x, abs=0.5)
    assert rows.mean() == pytest.approx(y, abs=0.5)


def test_the_disc_mask_is_the_circle_handed_over() -> None:
    """An adapter drawing the disc from `(x, y, r)` must get the stored disc mask back."""
    drawn = library.build("arc", side=SIDE, rotation=30.0)
    x, y, radius = drawn.disc
    rows, cols = np.mgrid[:SIDE, :SIDE]
    circle = (cols - x) ** 2 + (rows - y) ** 2 <= radius**2

    assert (circle != drawn.disc_mask).sum() <= 4, "at most a few boundary pixels may differ"


@pytest.mark.parametrize("rotation", [0.0, 30.0, 45.0, 90.0])
def test_the_drawn_ratios_follow_the_derived_ones(rotation) -> None:
    """Extent over extent, read off the drawing, is the derived ratio to within a pixel."""
    drawn = library.build("straight", side=SIDE, rotation=rotation)
    found = truth.cup_ratios(library.scene("straight"), rotation)
    disc = _extent(drawn.disc_mask, 0)
    one_pixel = 1.0 / disc

    vertical = _extent(drawn.cup, 0) / disc
    horizontal = _extent(drawn.cup, 1) / _extent(drawn.disc_mask, 1)
    assert vertical == pytest.approx(found["landmarks/CDR-vertical"].value, abs=2 * one_pixel)
    assert horizontal == pytest.approx(found["landmarks/CDR-horizontal"].value, abs=2 * one_pixel)
    area = drawn.cup.sum() / drawn.disc_mask.sum()
    assert area == pytest.approx(found["landmarks/CDR-area"].value, rel=0.02)


def test_turning_a_quarter_swaps_the_vertical_and_horizontal_ratios() -> None:
    upright = truth.cup_ratios(library.scene("straight"), 0.0)
    turned = truth.cup_ratios(library.scene("straight"), 90.0)

    assert upright["landmarks/CDR-vertical"].value == pytest.approx(0.55)
    assert upright["landmarks/CDR-horizontal"].value == pytest.approx(0.40)
    assert turned["landmarks/CDR-vertical"].value == pytest.approx(0.40)
    assert turned["landmarks/CDR-horizontal"].value == pytest.approx(0.55)
    assert turned["landmarks/CDR-area"].value == pytest.approx(0.22)


def test_every_shape_settles_the_three_ratios_under_catalogued_names() -> None:
    from biomarkers import canonical

    found = library.truths("tree", 15.0)
    for name in ("landmarks/CDR-vertical", "landmarks/CDR-horizontal", "landmarks/CDR-area"):
        canonical.check(name)
        assert found[name].kind == "exact"
    angle = math.radians(15.0)
    assert found["landmarks/CDR-vertical"].value == pytest.approx(
        math.hypot(0.40 * math.sin(angle), 0.55 * math.cos(angle))
    )
