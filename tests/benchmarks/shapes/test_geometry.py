# ABOUTME: Tests for rasterising a continuous centreline into a mask, and for rotating one — the two
# ABOUTME: operations every synthetic shape rests on, checked against what geometry requires.

import numpy as np

from benchmarks.shapes import geometry

SIDE = 512


def a_vessel(side: int, degrees: float = 0.0) -> np.ndarray:
    """The same continuous vessel — 60% of the frame long, 2% wide — drawn at any grid and angle."""
    centre = (side / 2.0, side / 2.0)
    points = [(side * 0.2, side / 2.0), (side * 0.8, side / 2.0)]
    return geometry.draw(geometry.turn(points, degrees, centre), side * 0.02, side)


def test_the_area_of_a_drawn_vessel_converges_on_the_area_geometry_requires() -> None:
    """A rasterised shape is not the shape, and the benchmark's whole method is that the difference
    shrinks as the grid refines. It has to be true of the generator before it can be asked of an
    implementation.

    The excess at a coarse grid is the boundary: a vessel whose centreline lies on the lattice
    takes the pixels on both sides of it, so its width comes out a pixel over. That is one pixel in
    ten at side 256 and one in eighty at side 2048.
    """
    errors = []
    for side in (256, 512, 1024, 2048):
        length, width = side * 0.6, side * 0.02
        # A stadium, not a rectangle: the distance to a segment is clamped at its ends, so the
        # vessel finishes in a half-disc of the same width rather than a square edge.
        expected = length * width + np.pi * (width / 2.0) ** 2
        errors.append(abs(a_vessel(side).sum() - expected) / expected)

    assert errors == sorted(errors, reverse=True), f"error did not shrink with the grid: {errors}"
    # What is left at the finest grid is one lattice row — the vessel's centreline lies on the
    # lattice here, so it takes the pixels either side of it and comes out a pixel wide over. That
    # is 20% of a 5-pixel vessel at side 256 and 2.4% of a 41-pixel one at 2048.
    assert errors[-1] < 0.03, f"and is small by the finest grid: {errors[-1]:.4f}"


def test_rotating_a_vessel_changes_its_area_less_as_the_grid_refines() -> None:
    """The generator's own invariance, stated the way it is true.

    Drawing at 0° and 90° puts the centreline on the lattice and takes a row either side of it;
    at 30° it does not. So the spread across angles is a rasterising artefact, and what must hold
    is that it shrinks — otherwise an implementation's rotation spread could never be read as its
    own.
    """
    spreads = []
    for side in (256, 512, 1024, 2048):
        areas = [a_vessel(side, degrees).sum() for degrees in (0, 30, 45, 90)]
        spreads.append(max(areas) / min(areas) - 1.0)

    assert spreads == sorted(spreads, reverse=True), f"spread did not shrink: {spreads}"
    # It settles at one lattice row out of the vessel's width — 19% of a 5-pixel vessel at side
    # 256, 2.4% of a 41-pixel one at 2048 — rather than at nothing.
    assert spreads[-1] < 0.03, f"and is small by the finest grid: {spreads[-1]:.4f}"


def test_turning_by_a_full_circle_returns_the_same_points() -> None:
    points = [(10.0, 20.0), (30.0, 40.0)]

    turned = geometry.turn(points, 360.0, (256.0, 256.0))

    assert np.allclose(turned, points)


def test_turning_moves_a_point_the_way_a_protractor_would() -> None:
    """A quarter turn about the origin sends (1, 0) to (0, 1), in image coordinates."""
    turned = geometry.turn([(1.0, 0.0)], 90.0, (0.0, 0.0))

    assert np.allclose(turned, [(0.0, 1.0)], atol=1e-9)


def test_a_vessel_is_as_wide_as_it_was_asked_to_be() -> None:
    """Measured across the line, which is what a calibre implementation will try to recover."""
    width = 11.0
    drawn = geometry.draw([(100.0, 256.0), (400.0, 256.0)], width, SIDE)

    column = drawn[:, 250]
    assert abs(int(column.sum()) - width) <= 1, "a horizontal vessel is its width in pixels tall"


def test_nothing_is_drawn_outside_the_frame() -> None:
    drawn = geometry.draw([(-50.0, 256.0), (600.0, 256.0)], 9.0, SIDE)

    assert drawn.shape == (SIDE, SIDE)
    assert drawn[:, 0].any(), "a vessel leaving the frame still fills the edge it crosses"


def test_the_field_of_view_is_a_disc_of_the_frame() -> None:
    fov = geometry.field_of_view(SIDE)

    assert fov[SIDE // 2, SIDE // 2]
    assert not fov[0, 0], "the corners of a fundus photograph are dark"
    assert abs(fov.mean() - np.pi / 4) < 0.01, "a circle inscribed in a square covers π/4 of it"
