# ABOUTME: Tests for the shapes and, more importantly, for the theory they carry — a derivation that
# ABOUTME: is wrong makes every result wrong, and nothing downstream would catch it.

import numpy as np
import pytest

from benchmarks.shapes import library

SIDE = 512


def test_every_shape_answers_with_two_classes_a_field_and_a_disc() -> None:
    """The contract an adapter is handed: two classes, either absent, and where the disc is."""
    for name in library.SHAPES:
        shape = library.build(name, side=SIDE)
        assert shape.artery is None or shape.artery.shape == (SIDE, SIDE)
        assert shape.vein is None or shape.vein.shape == (SIDE, SIDE)
        assert shape.artery is not None or shape.vein is not None, f"{name} draws nothing"
        assert shape.fov.shape == (SIDE, SIDE)
        assert len(shape.disc) == 3, f"{name} must say where the disc is"
        assert shape.theory, f"{name} carries no theoretical value, so it tests nothing"


def test_every_theoretical_value_names_a_catalogued_biomarker_and_variant() -> None:
    """A value under a name nothing can be compared against is not a test."""
    for name in library.SHAPES:
        for key in library.build(name, side=SIDE).theory:
            assert key.count("/") == 1, f"{name}: {key} is not 'biomarker/variant'"


def test_a_straight_vessel_is_exactly_as_tortuous_as_a_straight_line() -> None:
    shape = library.build("straight", side=SIDE)

    assert shape.theory["tortuosity/hart-tau1"] == 1.0
    assert shape.theory["tortuosity/total-curvature"] == 0.0


def test_an_arcs_tortuosity_matches_the_closed_form_and_the_arithmetic() -> None:
    """τ1 of a circular arc is θ / (2 sin(θ/2)); checked here against the curve it describes."""
    shape = library.build("arc", side=SIDE, angle=90.0)

    theta = np.deg2rad(90.0)
    assert shape.theory["tortuosity/hart-tau1"] == pytest.approx(theta / (2 * np.sin(theta / 2)))
    # And the same number, arrived at by walking the curve rather than by the formula.
    points = np.asarray(shape.centreline)
    arc = float(np.hypot(*np.diff(points, axis=0).T).sum())
    chord = float(np.hypot(*(points[-1] - points[0])))
    assert arc / chord == pytest.approx(shape.theory["tortuosity/hart-tau1"], rel=1e-3)


def test_an_arc_curves_by_one_over_its_radius() -> None:
    shape = library.build("arc", side=SIDE, angle=90.0)

    radius = shape.parameters["radius"]
    assert shape.theory["tortuosity/total-curvature"] == pytest.approx(np.deg2rad(90.0))
    assert shape.theory["curvature/constant"] == pytest.approx(1.0 / radius)


def test_a_sinusoids_length_matches_numerical_integration() -> None:
    """The closed form is an elliptic integral, so the theory is the integral, done finely."""
    shape = library.build("sinusoid", side=SIDE)

    amplitude = shape.parameters["amplitude"]
    wavelength = shape.parameters["wavelength"]
    cycles = shape.parameters["cycles"]
    x = np.linspace(0.0, wavelength * cycles, 2_000_001)
    slope = amplitude * (2 * np.pi / wavelength) * np.cos(2 * np.pi * x / wavelength)
    length = float(np.trapezoid(np.sqrt(1.0 + slope**2), x))
    assert shape.theory["vessel-area-and-length/skeleton-length"] == pytest.approx(length, rel=1e-4)


def test_a_bifurcation_branches_at_the_angle_it_was_asked_for() -> None:
    shape = library.build("bifurcation", side=SIDE, angle=60.0)

    assert shape.theory["bifurcation-angle/between-daughters"] == pytest.approx(60.0)
    assert shape.theory["junction-counts/junctions"] == 1.0
    assert shape.theory["junction-counts/endpoints"] == 3.0


def test_disjoint_segments_have_no_junctions_and_count_themselves() -> None:
    shape = library.build("disjoint", side=SIDE, segments=4)

    assert shape.theory["junction-counts/junctions"] == 0.0
    assert shape.theory["junction-counts/components"] == 4.0


def test_the_artery_vein_pair_has_the_ratio_of_its_widths() -> None:
    shape = library.build("artery-vein-pair", side=SIDE)

    wa = shape.parameters["artery_width"]
    wv = shape.parameters["vein_width"]
    assert shape.theory["avr/ratio-of-calibres"] == pytest.approx(wa / wv)
    assert shape.theory["vessel-calibre/artery"] == pytest.approx(wa)
    assert shape.theory["vessel-calibre/vein"] == pytest.approx(wv)
    assert shape.artery is not None and shape.vein is not None, "a ratio needs both classes"


def test_a_shape_with_one_class_leaves_the_other_absent() -> None:
    """Which is a test in itself: everything needing veins must come back as nothing."""
    shape = library.build("straight", side=SIDE)

    assert shape.vein is None
    assert not any(key.startswith("avr/") for key in shape.theory)


def test_the_drawn_density_approaches_the_density_geometry_requires() -> None:
    """The theory is the continuous fraction; the picture is pixels.

    What separates them is at most about one row of pixels along the vessel's length, so the
    relative difference is bounded by roughly one over the width in pixels — and it does **not**
    fall monotonically with the grid, because it depends on where the centreline happens to sit
    between pixel centres. It is a sawtooth, not a curve, which is worth having written down: a
    reader who sees the error rise between two resolutions should not read that as a defect.

    Computing the theory *from* the drawing instead would make it agree by construction and test
    nothing — and would move under rotation, which is exactly what this benchmark asks an
    implementation not to do.
    """
    for side in (256, 512, 1024):
        shape = library.build("straight", side=side)
        drawn = float(shape.artery.sum()) / float(shape.fov.sum())
        theory = shape.theory["vascular-density/over-field-of-view"]
        width = shape.parameters["width"]
        assert abs(drawn - theory) / theory < 1.2 / width, (
            f"at side {side} the drawn density is further from the geometry than one row of pixels"
        )


def test_a_shape_can_be_built_at_any_grid_and_says_which() -> None:
    for side in (256, 1024):
        shape = library.build("straight", side=side)
        assert shape.side == side
        assert shape.artery.shape == (side, side)


def test_rotation_is_recorded_and_changes_the_drawing_but_not_the_theory() -> None:
    """The invariance the benchmark asks of an implementation has to hold of the shapes first."""
    upright = library.build("arc", side=SIDE, angle=90.0)
    turned = library.build("arc", side=SIDE, angle=90.0, rotation=37.0)

    assert turned.rotation == 37.0
    assert turned.theory == upright.theory, "turning a shape does not change what it is"
    assert not np.array_equal(turned.artery, upright.artery), "but it does change the picture"
