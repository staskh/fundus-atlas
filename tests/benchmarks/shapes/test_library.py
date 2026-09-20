# ABOUTME: Tests for the shapes and, more importantly, for the theory they carry — a derivation that
# ABOUTME: is wrong makes every result wrong, and nothing downstream would catch it.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical

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


def test_every_theoretical_value_is_named_from_the_fixed_vocabulary() -> None:
    """A value under a name nothing can be compared against is not a test.

    Every key goes through `canonical.check`, so a typo fails here rather than becoming a row that
    silently matches no implementation's column for ever.
    """
    for name in library.SHAPES:
        for key in library.build(name, side=SIDE).theory:
            canonical.check(key)
            assert key.count("/") == 2, f"{name}: {key} is not 'biomarker/variant/structure'"


def test_a_straight_vessel_is_exactly_as_tortuous_as_a_straight_line() -> None:
    shape = library.build("straight", side=SIDE)

    assert shape.theory["tortuosity/hart-tau1/artery"] == 1.0
    assert shape.theory["tortuosity/hart-tau2/artery"] == 0.0
    assert shape.theory["tortuosity/hart-tau4/artery"] == 0.0


def test_an_arcs_tortuosity_matches_the_closed_form_and_the_arithmetic() -> None:
    """τ1 of a circular arc is θ / (2 sin(θ/2)); checked here against the curve it describes."""
    shape = library.build("arc", side=SIDE, angle=90.0)

    theta = np.deg2rad(90.0)
    assert shape.theory["tortuosity/hart-tau1/artery"] == pytest.approx(theta / (2 * np.sin(theta / 2)))
    # And the same number, arrived at by walking the curve rather than by the formula.
    points = np.asarray(shape.centreline)
    arc = float(np.hypot(*np.diff(points, axis=0).T).sum())
    chord = float(np.hypot(*(points[-1] - points[0])))
    assert arc / chord == pytest.approx(shape.theory["tortuosity/hart-tau1/artery"], rel=1e-3)


def test_an_arc_curves_by_one_over_its_radius() -> None:
    shape = library.build("arc", side=SIDE, angle=90.0)

    radius = shape.parameters["radius"]
    assert shape.theory["tortuosity/hart-tau2/artery"] == pytest.approx(np.deg2rad(90.0))
    # The mean curvature of a circular arc is the curvature, which is one over the radius.
    assert shape.theory["tortuosity/hart-tau4/artery"] == pytest.approx(1.0 / radius)


def test_a_sinusoids_length_matches_numerical_integration() -> None:
    """The closed form is an elliptic integral, so the theory is the integral, done finely."""
    shape = library.build("sinusoid", side=SIDE)

    amplitude = shape.parameters["amplitude"]
    wavelength = shape.parameters["wavelength"]
    cycles = shape.parameters["cycles"]
    x = np.linspace(0.0, wavelength * cycles, 2_000_001)
    slope = amplitude * (2 * np.pi / wavelength) * np.cos(2 * np.pi * x / wavelength)
    length = float(np.trapezoid(np.sqrt(1.0 + slope**2), x))
    assert shape.theory["vessel-area-and-length/skeleton-length/artery"] == pytest.approx(length, rel=1e-4)


def test_a_bifurcation_branches_at_the_angle_it_was_asked_for() -> None:
    shape = library.build("bifurcation", side=SIDE, angle=60.0)

    assert shape.theory["bifurcation-angle/between-daughters/artery"] == pytest.approx(60.0)
    assert shape.theory["junction-counts/junctions/vessels"] == 1.0
    assert shape.theory["junction-counts/endpoints/vessels"] == 3.0


def test_disjoint_segments_have_no_junctions_and_count_themselves() -> None:
    shape = library.build("disjoint", side=SIDE, segments=4)

    assert shape.theory["junction-counts/junctions/vessels"] == 0.0
    assert shape.theory["junction-counts/components/vessels"] == 4.0


def test_the_artery_vein_pair_has_the_ratio_of_its_widths() -> None:
    shape = library.build("artery-vein-pair", side=SIDE)

    wa = shape.parameters["artery_width"]
    wv = shape.parameters["vein_width"]
    assert shape.theory["avr/ratio-of-calibres/both"] == pytest.approx(wa / wv)
    assert shape.theory["vessel-calibre/mean-width/artery"] == pytest.approx(wa)
    assert shape.theory["vessel-calibre/mean-width/vein"] == pytest.approx(wv)
    assert shape.artery is not None and shape.vein is not None, "a ratio needs both classes"


def test_a_shape_with_one_class_leaves_the_other_absent() -> None:
    """Which is a test in itself: everything needing veins must come back as nothing."""
    shape = library.build("straight", side=SIDE)

    assert shape.vein is None
    assert not any(key.startswith("avr/") for key in shape.theory)
    assert not any(key.endswith("/vein") for key in shape.theory), (
        "a shape with no veins promises nothing about veins"
    )


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
        theory = shape.theory["vascular-density/over-field-of-view/vessels"]
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


def test_hart_s_compositional_pair_depends_on_the_radius_alone() -> None:
    """τ4 and τ5 are 1/r and 1/r², so seeing more of the same arc does not change them.

    That is Hart's argument for preferring them, and it is testable: τ2 and τ3 grow with the angle
    traced, these two do not. An implementation whose τ4 moves with the angle is computing τ2.
    """
    narrow = library.build("arc", side=SIDE, angle=45.0)
    wide = library.build("arc", side=SIDE, angle=120.0)

    assert narrow.parameters["radius"] == wide.parameters["radius"]
    for key in ("tortuosity/hart-tau4/artery", "tortuosity/hart-tau5/artery"):
        assert narrow.theory[key] == pytest.approx(wide.theory[key]), f"{key} moved with the angle"
    for key in ("tortuosity/hart-tau2/artery", "tortuosity/hart-tau3/artery"):
        assert wide.theory[key] > narrow.theory[key], f"{key} should grow with the angle"


def test_the_disc_sits_to_the_right_and_its_ring_stays_in_the_field_of_view() -> None:
    """The equivalents are measured out to three disc radii, which has to fit inside the retina."""
    shape = library.build("disc-spokes", side=SIDE)

    x, y, radius = shape.disc
    assert x > SIDE * 0.6, "the disc is to the right of centre"
    assert abs(y - SIDE / 2) < 1.0, "and level with it"
    reach = np.hypot(x - SIDE / 2, y - SIDE / 2) + library.ZONE_B_RADII[1] * radius
    assert reach < SIDE / 2, "the ring the equivalents need is inside the field of view"


def test_the_spokes_cross_the_ring_the_equivalents_are_measured_over() -> None:
    """A shape whose vessels miss the annulus cannot test a central retinal equivalent at all."""
    shape = library.build("disc-spokes", side=SIDE)

    x, y, radius = shape.disc
    grid = np.arange(SIDE) + 0.5
    px, py = np.meshgrid(grid, grid)
    distance = np.hypot(px - x, py - y) / radius
    ring = (distance >= library.ZONE_B_RADII[0]) & (distance <= library.ZONE_B_RADII[1])

    assert (shape.artery & ring).sum() > 0, "no artery crosses the ring"
    assert (shape.vein & ring).sum() > 0, "no vein crosses the ring"


def test_the_knudtson_equivalent_of_equal_vessels_is_what_the_recursion_gives() -> None:
    """Six vessels of one width, so every pairing order agrees and the shape tests the formula."""
    shape = library.build("disc-spokes", side=SIDE)

    width = shape.parameters["artery_width"]
    assert shape.theory["central-retinal-equivalents/knudtson/artery"] == pytest.approx(
        library.knudtson([width] * 6, "artery")
    )
    assert library.knudtson([10.0, 10.0], "artery") == pytest.approx(0.88 * np.hypot(10.0, 10.0))
    assert library.knudtson([7.0], "vein") == 7.0, "one vessel combines with nothing"


def test_the_pairs_vessels_do_cross_the_ring_the_equivalents_need() -> None:
    """Measured rather than assumed — and the measurement corrected an earlier belief.

    The pair was thought to sit too far from the disc to support an equivalent at all. Its vessels
    run outward past the disc, so each crosses the annulus once, which makes the Knudtson
    equivalent of a single vessel a legitimate degenerate case rather than a category error.
    """
    from scipy.ndimage import label

    shape = library.build("artery-vein-pair", side=SIDE)
    x, y, radius = shape.disc
    grid = np.arange(SIDE) + 0.5
    px, py = np.meshgrid(grid, grid)
    distance = np.hypot(px - x, py - y) / radius
    ring = (distance >= library.ZONE_B_RADII[0]) & (distance <= library.ZONE_B_RADII[1])

    assert label(shape.artery & ring)[1] == 1, "exactly one artery crosses the ring"
    assert label(shape.vein & ring)[1] == 1, "and exactly one vein"


def test_the_scale_changes_hubbards_equivalent_and_leaves_knudtson_s_alone() -> None:
    """Knudtson's formula is purely multiplicative and so scale-free; Hubbard's is not.

    Hubbard's constants were fitted in microns and the additive term does not scale, so the same
    vessels photographed at a different resolution give a different Hubbard equivalent — which is
    the trap `docs/biomarkers/central-retinal-equivalents.md` §3.1 records.
    """
    coarse = library.build("disc-spokes", side=SIDE, um_per_px=5.0)
    fine = library.build("disc-spokes", side=SIDE, um_per_px=20.0)

    knudtson = "central-retinal-equivalents/knudtson/artery"
    hubbard = "central-retinal-equivalents/hubbard/artery"
    assert coarse.theory[knudtson] == pytest.approx(fine.theory[knudtson]), (
        "Knudtson is in pixels and does not know what a micron is"
    )
    assert coarse.theory[hubbard] != pytest.approx(fine.theory[hubbard])
    assert fine.theory[hubbard] > coarse.theory[hubbard], "more microns per pixel, wider vessels"


def test_hubbard_declines_a_single_vessel_and_knudtson_passes_it_through() -> None:
    """Which is why the pair shape carries one equivalent and not the other."""
    assert library.knudtson([9.0], "artery") == 9.0
    with pytest.raises(ValueError, match="pair"):
        library.hubbard([90.0], "artery")


def test_the_pair_promises_knudtson_only_and_the_spokes_promise_both() -> None:
    pair = library.build("artery-vein-pair", side=SIDE)
    spokes = library.build("disc-spokes", side=SIDE)

    assert "central-retinal-equivalents/knudtson/artery" in pair.theory
    assert "central-retinal-equivalents/hubbard/artery" not in pair.theory, (
        "one artery cannot make a Hubbard pair, so the shape promises none"
    )
    assert "central-retinal-equivalents/hubbard/artery" in spokes.theory


def test_the_three_arteriovenous_ratios_are_three_different_numbers() -> None:
    """A shape where the variants disagree is what makes them testable rather than interchangeable.

    Same vessels, same widths: the ratio of calibres is the ratio of the widths, Knudtson's carries
    its 0.88 against 0.95 through the recursion, and Hubbard's carries additive constants. An
    implementation reporting "AVR" without naming which is reporting one of these three.
    """
    shape = library.build("disc-spokes", side=SIDE, um_per_px=10.0)

    plain = shape.theory["avr/ratio-of-calibres/both"]
    knudtson = shape.theory["avr/knudtson/both"]
    hubbard = shape.theory["avr/hubbard/both"]
    assert plain != pytest.approx(knudtson, rel=0.01), "0.88 against 0.95, compounded"
    assert knudtson != pytest.approx(hubbard, rel=0.01)

    # Hubbard's and the plain ratio can *coincide* at a particular scale — at this frame they are
    # within one per cent — so the proof that they are different quantities is that only one of
    # them moves when the scale does. Two numbers that respond differently to the same change are
    # not the same measurement, whatever they happen to read at one setting.
    wider = library.build("disc-spokes", side=SIDE, um_per_px=40.0)
    assert wider.theory["avr/ratio-of-calibres/both"] == pytest.approx(plain)
    assert wider.theory["avr/hubbard/both"] != pytest.approx(hubbard, rel=0.01)


def test_a_shape_records_the_scale_it_was_built_with() -> None:
    assert library.build("straight", side=SIDE).um_per_px == library.UM_PER_PX
    assert library.build("straight", side=SIDE, um_per_px=3.5).um_per_px == 3.5
