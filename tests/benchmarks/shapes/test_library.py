# ABOUTME: Tests for the shapes and, more importantly, for the theory they carry — a derivation that
# ABOUTME: is wrong makes every result wrong, and nothing downstream would catch it.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical

SIDE = 1024


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
    assert shape.theory["tortuosity/hart-tau1/artery"] == pytest.approx(
        theta / (2 * np.sin(theta / 2))
    )
    # And the same number, arrived at by walking the curve rather than by the formula.
    points = np.asarray(shape.centreline)
    arc = float(np.hypot(*np.diff(points, axis=0).T).sum())
    chord = float(np.hypot(*(points[-1] - points[0])))
    assert arc / chord == pytest.approx(shape.theory["tortuosity/hart-tau1/artery"], rel=1e-3)


def test_an_arc_curves_by_one_over_its_radius() -> None:
    shape = library.build("arc", side=SIDE, angle=90.0)

    radius = shape.parameters["artery_radius"]
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
    assert shape.theory["vessel-area-and-length/skeleton-length/artery"] == pytest.approx(
        length, rel=1e-4
    )


def test_a_bifurcation_branches_at_the_angle_it_was_asked_for() -> None:
    shape = library.build("bifurcation", side=SIDE, angle=60.0)

    assert shape.theory["bifurcation-angle/between-daughters/artery"] == pytest.approx(60.0)
    assert shape.theory["junction-counts/junctions/artery"] == 1.0
    assert shape.theory["junction-counts/junctions/vessels"] == 2.0, "one Y per class"
    assert shape.theory["junction-counts/endpoints/artery"] == 3.0
    assert shape.theory["junction-counts/endpoints/vessels"] == 6.0


def test_disjoint_segments_have_no_junctions_and_count_themselves() -> None:
    shape = library.build("disjoint", side=SIDE, segments=4)

    assert shape.theory["junction-counts/junctions/vessels"] == 0.0
    assert shape.theory["junction-counts/components/artery"] == 4.0
    assert shape.theory["junction-counts/components/vessels"] == 8.0, "four lines per class"


def test_every_shape_draws_an_artery_and_a_vein() -> None:
    """A segmentation of a real eye has both, so a shape that tests against one is unrepresentative.

    It also means every family pins the ratio of the two calibres, which is the one arteriovenous
    quantity that needs no disc and no ring.
    """
    for name in library.SHAPES:
        shape = library.build(name, side=SIDE)
        assert shape.artery is not None and shape.artery.any(), f"{name} draws no artery"
        assert shape.vein is not None and shape.vein.any(), f"{name} draws no vein"
        assert not (shape.artery & shape.vein).any(), f"{name} has a pixel in both classes"
        assert shape.theory["avr/ratio-of-calibres/both"] == pytest.approx(
            library.ARTERY_WIDTH_UM / library.VEIN_WIDTH_UM
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
    # From 512 up: a clinically sized optic disc fills too much of a smaller frame for a vessel
    # of this length to stay inside the field, and the library refuses rather than clipping it.
    for side in (1024, 1536, 2048):
        shape = library.build("straight", side=side)
        drawn = float((shape.artery | shape.vein).sum()) / float(shape.fov.sum())
        theory = shape.theory["vascular-density/over-field-of-view/vessels"]
        width = shape.parameters["artery_width"]
        assert abs(drawn - theory) / theory < 1.2 / width, (
            f"at side {side} the drawn density is further from the geometry than one row of pixels"
        )


def test_a_shape_can_be_built_at_any_grid_that_holds_it_and_says_which() -> None:
    """Any grid large enough, which is not any grid: a clinically sized optic disc and a vessel of
    ordinary length need room, and the library refuses a frame that would clip them."""
    for side in (1024, 2048):
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

    assert narrow.parameters["artery_radius"] == wide.parameters["artery_radius"]
    for key in ("tortuosity/hart-tau4/artery", "tortuosity/hart-tau5/artery"):
        assert narrow.theory[key] == pytest.approx(wide.theory[key]), f"{key} moved with the angle"
    for key in ("tortuosity/hart-tau2/artery", "tortuosity/hart-tau3/artery"):
        assert wide.theory[key] > narrow.theory[key], f"{key} should grow with the angle"


def test_the_disc_sits_to_the_right_and_its_ring_stays_in_the_field_of_view() -> None:
    """The equivalents are measured out to three disc radii, which has to fit inside the retina."""
    shape = library.build("spokes-macula-centred", side=SIDE)

    x, y, radius = shape.disc
    assert x > SIDE * 0.6, "the disc is to the right of centre"
    assert abs(y - SIDE / 2) < 1.0, "and level with it"
    reach = np.hypot(x - SIDE / 2, y - SIDE / 2) + library.ZONE_B_RADII[1] * radius
    assert reach < SIDE / 2, "the ring the equivalents need is inside the field of view"


def test_the_spokes_cross_the_ring_the_equivalents_are_measured_over() -> None:
    """A shape whose vessels miss the annulus cannot test a central retinal equivalent at all."""
    shape = library.build("spokes-macula-centred", side=SIDE)

    x, y, radius = shape.disc
    grid = np.arange(SIDE) + 0.5
    px, py = np.meshgrid(grid, grid)
    distance = np.hypot(px - x, py - y) / radius
    ring = (distance >= library.ZONE_B_RADII[0]) & (distance <= library.ZONE_B_RADII[1])

    assert (shape.artery & ring).sum() > 0, "no artery crosses the ring"
    assert (shape.vein & ring).sum() > 0, "no vein crosses the ring"


def test_the_knudtson_equivalent_of_equal_vessels_is_what_the_recursion_gives() -> None:
    """Six vessels of one width, so every pairing order agrees and the shape tests the formula."""
    shape = library.build("spokes-macula-centred", side=SIDE)

    width = shape.parameters["artery_width"]
    assert shape.theory["central-retinal-equivalents/knudtson/artery"] == pytest.approx(
        library.knudtson([width] * 6, "artery")
    )
    assert library.knudtson([10.0, 10.0], "artery") == pytest.approx(0.88 * np.hypot(10.0, 10.0))
    assert library.knudtson([7.0], "vein") == 7.0, "one vessel combines with nothing"


def test_resolution_moves_knudtson_s_pixels_and_leaves_hubbard_s_microns_alone() -> None:
    """One retina photographed at two resolutions is one retina, and the theory has to say so.

    A vessel's width is stated in microns here, so a finer scale draws the same vessel across more
    pixels. Knudtson's equivalent is computed on those pixels and moves with the resolution;
    Hubbard's is computed on microns and must not, because the eye did not change.
    """
    coarse = library.build("spokes-macula-centred", side=SIDE, um_per_px=20.0)
    fine = library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)

    knudtson = "central-retinal-equivalents/knudtson/artery"
    hubbard = "central-retinal-equivalents/hubbard/artery"
    assert fine.theory[knudtson] == pytest.approx(2.0 * coarse.theory[knudtson]), (
        "twice the pixels across the same vessel"
    )
    assert fine.theory[hubbard] == pytest.approx(coarse.theory[hubbard]), (
        "the artery is 80 µm wide however it was photographed"
    )


def test_hubbards_additive_constants_do_not_scale_with_the_vessel() -> None:
    """The trap `docs/biomarkers/central-retinal-equivalents.md` §3.1 records, in one line.

    Knudtson's recursion is purely multiplicative, so doubling every width doubles the answer
    exactly. Hubbard's carries constants fitted in microns — −10.76 for arterioles — and an
    additive term cannot scale, so doubling the widths does *not* double his equivalent. It is a
    small discrepancy at a realistic calibre and it is the whole reason the unit has to be stated.
    """
    ordinary, doubled = [80.0] * 6, [160.0] * 6

    assert library.knudtson(doubled, "artery") == pytest.approx(
        2.0 * library.knudtson(ordinary, "artery")
    )
    assert library.hubbard(doubled, "artery") != pytest.approx(
        2.0 * library.hubbard(ordinary, "artery"), rel=1e-6
    )


def test_hubbard_declines_a_single_vessel_and_knudtson_passes_it_through() -> None:
    """Which is why the pair shape carries one equivalent and not the other."""
    assert library.knudtson([9.0], "artery") == 9.0
    with pytest.raises(ValueError, match="pair"):
        library.hubbard([90.0], "artery")


def test_the_three_arteriovenous_ratios_are_three_different_numbers() -> None:
    """A shape where the variants disagree is what makes them testable rather than interchangeable.

    Same vessels, same widths: the ratio of calibres is the ratio of the widths, Knudtson's carries
    its 0.88 against 0.95 through the recursion, and Hubbard's carries additive constants. An
    implementation reporting "AVR" without naming which is reporting one of these three.
    """
    shape = library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)

    plain = shape.theory["avr/ratio-of-calibres/both"]
    knudtson = shape.theory["avr/knudtson/both"]
    hubbard = shape.theory["avr/hubbard/both"]
    assert plain != pytest.approx(knudtson, rel=0.01), "0.88 against 0.95, compounded"
    assert knudtson != pytest.approx(hubbard, rel=0.01)

    # Hubbard's and the plain ratio read within a couple of per cent of each other here, so the
    # proof that they are different quantities is that only one of them moves when the vessels do.
    # Doubling every width leaves a ratio of calibres exactly where it was, and Knudtson's ratio
    # too, because both are multiplicative; Hubbard's additive constants do not scale, so his
    # moves. Two numbers that respond differently to the same change are not the same measurement.
    wider = library.build(
        "spokes-macula-centred", side=SIDE, um_per_px=10.0, artery_um=160.0, vein_um=240.0
    )
    assert wider.theory["avr/ratio-of-calibres/both"] == pytest.approx(plain)
    assert wider.theory["avr/knudtson/both"] == pytest.approx(knudtson)
    assert wider.theory["avr/hubbard/both"] != pytest.approx(hubbard, rel=0.01)


def test_a_shape_records_the_scale_it_was_built_with() -> None:
    assert library.build("straight", side=SIDE).um_per_px == library.UM_PER_PX
    # A finer scale makes the optic disc larger in pixels, so the frame has to grow with it.
    assert library.build("straight", side=2048, um_per_px=5.0).um_per_px == 5.0


def test_a_width_stated_in_microns_becomes_the_pixels_the_scale_implies() -> None:
    """An 80 µm artery is 16 px across at 5 µm per pixel and 8 px at 10, and is one artery."""
    fine = library.build("straight", side=2048, um_per_px=5.0)
    coarse = library.build("straight", side=SIDE, um_per_px=10.0)

    assert fine.parameters["artery_width"] == pytest.approx(16.0)
    assert fine.parameters["vein_width"] == pytest.approx(24.0)
    assert coarse.parameters["artery_width"] == pytest.approx(8.0)
    assert fine.disc[2] == pytest.approx(library.DISC_DIAMETER_UM / 2.0 / 5.0)


def test_the_two_framings_photograph_the_same_eye() -> None:
    """Macula-centred and disc-centred differ in where the disc sits and in nothing else.

    So every disc-anchored value must agree between them. A measurement that comes out differently
    on the two is reading the framing rather than the retina, which is the whole point of having
    both.
    """
    macula = library.build("spokes-macula-centred", side=SIDE)
    disc = library.build("spokes-disc-centred", side=SIDE)

    assert disc.disc[0] == pytest.approx(SIDE / 2.0), "the disc-centred framing centres the disc"
    assert macula.disc[0] > SIDE * 0.6, "the macula-centred one puts it to the side"

    # Everything anchored on the disc must agree. Sparsity must *not*: it asks how far the retina
    # is from a vessel, and moving the disc moves the vessels within the frame, so the two framings
    # genuinely differ there. Asserting they agree would be asserting the fixture is wrong.
    anchored = {
        name: value for name, value in macula.theory.items() if not name.startswith("sparsity/")
    }
    assert anchored == {
        name: value for name, value in disc.theory.items() if not name.startswith("sparsity/")
    }, "a disc-anchored measurement cannot depend on where the disc sits in the frame"
    assert macula.theory["sparsity/max-distance/vessels"] != pytest.approx(
        disc.theory["sparsity/max-distance/vessels"]
    ), "and sparsity is not disc-anchored, so it does"


def test_a_frame_too_small_for_the_ring_is_refused_rather_than_drawn() -> None:
    """Three disc radii is 2700 µm, so a frame under about 5.5 mm cannot hold the ring at all.

    Drawing it anyway would truncate every vessel crossing the annulus and quietly produce
    equivalents describing a clipped ring, which is worse than no shape at all.
    """
    with pytest.raises(ValueError, match="outside its field of view"):
        library.build("spokes-macula-centred", side=512, um_per_px=5.0)


def test_the_demo_picture_shows_each_class_in_its_own_colour() -> None:
    """Nothing measures this, so all it has to be is unambiguous to a reader."""
    shape = library.build("spokes-macula-centred", side=SIDE)

    picture = library.demo_image(shape)

    assert picture.shape == (SIDE, SIDE, 3)
    assert picture.dtype == np.uint8
    assert (picture[shape.artery] == library.ARTERY_COLOUR).all()
    assert (picture[shape.vein] == library.VEIN_COLOUR).all()
    assert not (picture[~shape.fov] != 0).any(), "nothing is painted outside the field of view"


def test_the_koch_curve_has_a_dimension_a_box_count_can_reach() -> None:
    """Every other shape here is smooth, and a smooth curve's dimension is exactly 1.

    No estimator returns 1 from a bounded pixel image, so pinning it would charge every
    implementation with an error none of them can avoid. `log 4 / log 3` is exact, is not an
    integer, and is within reach of a box count over the scales a large frame offers — which is
    what makes it worth measuring against.
    """
    shape = library.build("koch", side=SIDE)

    assert library.KOCH_DIMENSION == pytest.approx(1.261859, abs=1e-6)
    for variant in ("box-counting", "multifractal-d0", "multifractal-d1", "multifractal-d2"):
        for structure in ("artery", "vein", "vessels"):
            assert shape.theory[f"fractal-dimension/{variant}/{structure}"] == pytest.approx(
                library.KOCH_DIMENSION
            ), "a monofractal's spectrum is a point, so all three dimensions are the same"


def test_the_deep_tree_counts_its_forks_and_its_spurs() -> None:
    """Three generations of forking, each junction also carrying a stub.

    A single fork cannot show what goes wrong on a tree: a junction counted as a cluster, a walk
    that loses a branch, a spur too short to survive a length filter. The counts are what this
    shape settles, and every piece is straight so no tortuosity aggregation confounds them.
    """
    shape = library.build("deep-bifurcation", side=SIDE)

    # 1 + 2 + 4 forks over three generations, and a free end for the trunk's start, each spur and
    # each final daughter.
    assert shape.theory["junction-counts/junctions/artery"] == 7.0
    assert shape.theory["junction-counts/endpoints/artery"] == 1.0 + 7.0 + 8.0
    assert shape.theory["junction-counts/components/artery"] == 1.0, "one tree, not many"
    assert shape.theory["tortuosity/hart-tau1/artery"] == pytest.approx(1.0), "every piece straight"


def test_every_shape_but_the_disjoint_one_leaves_the_optic_disc() -> None:
    """Vessels leave the eye at the disc, and they leave it at its margin rather than its centre.

    `disjoint` is the deliberate exception: it is what shows whether a measurement quietly requires
    a vessel to reach the disc before it will count it.
    """
    for name in library.SHAPES:
        shape = library.build(name, side=SIDE)
        x, y, radius = shape.disc
        starts = np.hypot(shape.centreline[0][0] - x, shape.centreline[0][1] - y)
        if name == "disjoint":
            assert starts > radius * 1.5, "the disjoint lines are nowhere near the disc"
        else:
            assert starts == pytest.approx(radius, abs=1.0), f"{name} does not start on the margin"
