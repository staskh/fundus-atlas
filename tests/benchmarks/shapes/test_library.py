# ABOUTME: The synthetic shapes and their ground truth, tested against themselves: closed forms checked
# ABOUTME: by hand, renderings against the geometry, and every name against the vocabulary.

import math

import numpy as np
import pytest

from benchmarks.shapes import library, render, scene, truth
from biomarkers import canonical


def values(name: str) -> dict[str, object]:
    return {key: t.value for key, t in library.truths(name).items()}


def test_a_45_degree_camera_spans_12960_um_across_the_frame() -> None:
    assert scene.FOV_DIAMETER_UM == pytest.approx(45 * 288)
    assert render.um_per_px(2048) == pytest.approx(12960 / 2048)
    assert render.um_per_px(1024) == pytest.approx(2 * render.um_per_px(2048))


@pytest.mark.parametrize("name", list(library.SHAPES))
def test_every_shape_names_only_catalogued_biomarkers(name: str) -> None:
    found = library.truths(name)
    assert found
    for key in found:
        canonical.check(key)


@pytest.mark.parametrize("name", list(library.SHAPES))
def test_every_truth_says_how_it_is_known(name: str) -> None:
    assert {t.kind for t in library.truths(name).values()} <= set(truth.KINDS)


def test_a_straight_vessel_is_exactly_as_long_and_wide_as_drawn() -> None:
    got = values("straight")
    length, width = library.STRAIGHT_UM, scene.ARTERY_UM
    assert got["density/skeleton-length/artery"] == pytest.approx(length, rel=1e-6)
    # A tube: length × width and a round cap's disc at the two ends.
    assert got["density/area/artery"] == pytest.approx(
        length * width + math.pi * width**2 / 4, rel=1e-3
    )
    assert got["density/skeleton-length-rooted/artery"] == pytest.approx(length, rel=1e-6)
    assert got["calibre/width/artery/mean"] == pytest.approx(width)
    assert got["calibre/width/artery/std"] == pytest.approx(0.0)
    assert got["calibre/AVR-ratio/both"] == pytest.approx(scene.ARTERY_UM / scene.VEIN_UM)
    assert got["tortuosity/hart-tau1/artery/median"] == pytest.approx(1.0)
    assert got["tortuosity/hart-tau2/artery/mean"] == pytest.approx(0.0)
    assert got["tortuosity/inflection-count/artery"] == 0.0
    assert got["tortuosity/vessel-hart-tau1/vein/mean"] == pytest.approx(1.0)
    assert got["topology/endpoints/artery"] == 2.0
    assert got["topology/junctions/artery"] == 0.0
    assert got["topology/components/artery"] == 1.0


def test_an_arc_has_harts_closed_forms() -> None:
    got = values("arc")
    r, theta = library.ARC_ARTERY_RADIUS_UM, math.radians(library.ARC_DEGREES)
    assert got["tortuosity/hart-tau1/artery/mean"] == pytest.approx(
        theta / (2 * math.sin(theta / 2)), rel=1e-6
    )
    assert got["tortuosity/hart-tau2/artery/mean"] == pytest.approx(theta, rel=1e-6)
    assert got["tortuosity/hart-tau3/artery/mean"] == pytest.approx(theta / r, rel=1e-6)
    assert got["tortuosity/hart-tau4/artery/mean"] == pytest.approx(1 / r, rel=1e-6)
    assert got["tortuosity/hart-tau5/artery/mean"] == pytest.approx(1 / r**2, rel=1e-6)
    assert got["tortuosity/spline-curvature/artery/mean"] == pytest.approx(1 / r, rel=1e-6)
    assert got["tortuosity/grisan-density/artery/mean"] == 0.0


def test_an_arcs_arc_over_chord_does_not_depend_on_its_radius() -> None:
    got = values("arc")
    assert got["tortuosity/hart-tau1/artery/mean"] == pytest.approx(
        got["tortuosity/hart-tau1/vein/mean"], rel=1e-6
    )
    assert got["tortuosity/hart-tau3/artery/mean"] != pytest.approx(
        got["tortuosity/hart-tau3/vein/mean"], rel=1e-3
    )


def test_a_clothoid_integrates_its_linear_curvature() -> None:
    got = values("clothoid")
    length, kappa = library.CLOTHOID_UM, library.CLOTHOID_END_CURVATURE
    assert got["tortuosity/hart-tau2/artery/mean"] == pytest.approx(kappa * length / 2, rel=1e-6)
    assert got["tortuosity/hart-tau3/artery/mean"] == pytest.approx(kappa**2 * length / 3, rel=1e-5)


def test_a_sinusoid_inflects_between_its_half_waves() -> None:
    got = values("sinusoid")
    # Two cycles: the curvature changes sign at the three interior zeros of the sine.
    assert got["tortuosity/inflection-count/artery"] == 3.0
    assert got["tortuosity/grisan-density/artery/mean"] > 0.0


def test_a_fork_counts_one_junction_three_ends_and_its_angle() -> None:
    got = values("bifurcation")
    assert got["topology/junctions/artery"] == 1.0
    assert got["topology/endpoints/artery"] == 3.0
    assert got["topology/branching-angle/artery/mean"] == pytest.approx(library.FORK_DEGREES)
    assert got["topology/branching-angle/artery/std"] == pytest.approx(0.0)
    parent = scene.ARTERY_UM
    daughter = parent / 2 ** (1 / 3)
    assert got["calibre/width/artery/mean"] == pytest.approx((parent + 2 * daughter) / 3)
    assert got["calibre/width/artery/median"] == pytest.approx(daughter)
    # A whole vessel turns once, by half the fork angle, at the junction.
    assert got["tortuosity/vessel-hart-tau2/artery/mean"] == pytest.approx(
        math.radians(library.FORK_DEGREES / 2)
    )
    assert "tortuosity/vessel-hart-tau3/artery/mean" not in got


def test_a_tree_counts_every_fork_and_tip() -> None:
    got = values("tree")
    assert got["topology/junctions/artery"] == 3.0
    assert got["topology/endpoints/artery"] == 5.0
    assert got["topology/components/artery"] == 1.0


def test_the_deep_tree_counts_its_forks_and_its_stubs() -> None:
    got = values("deep-bifurcation")
    forks = sum(2**g for g in range(library.DEEP_GENERATIONS))
    assert got["topology/junctions/artery"] == float(forks)
    # The root, a stub per fork, and the last generation's tips.
    assert got["topology/endpoints/artery"] == float(1 + forks + 2**library.DEEP_GENERATIONS)
    assert (
        library.truths("deep-bifurcation")["topology/branching-angle/artery/mean"].kind
        == "convention"
    )


def test_a_spur_is_counted_by_the_definition() -> None:
    got = values("spur")
    assert got["topology/junctions/artery"] == 1.0
    assert got["topology/endpoints/artery"] == 3.0
    assert got["topology/branching-angle/artery/mean"] == pytest.approx(90.0)


def test_a_crossing_is_two_vessels_and_its_counts_are_a_reading() -> None:
    found = library.truths("crossing")
    assert found["topology/junctions/artery"].value == 0.0
    assert found["topology/junctions/artery"].kind == "convention"
    assert found["calibre/width/artery/mean"].kind == "exact"


def test_orphans_have_no_rooted_length_and_no_whole_vessels() -> None:
    got = values("disjoint")
    assert got["density/skeleton-length-rooted/artery"] == 0.0
    assert got["topology/components/artery"] == float(library.DISJOINT_COUNT)
    vessel_forms = [key for key in got if key.startswith("tortuosity/vessel-")]
    assert vessel_forms and all(got[key] is None for key in vessel_forms)


def test_a_koch_curve_has_its_similarity_dimension_and_arc_over_chord() -> None:
    found = library.truths("koch")
    assert found["density/box-counting/artery"].value == pytest.approx(math.log(4) / math.log(3))
    assert found["density/box-counting/artery"].kind == "asymptotic"
    assert found["tortuosity/hart-tau1/artery/mean"].value == pytest.approx(
        (4 / 3) ** library.KOCH_DEPTH
    )


def test_spokes_give_knudtsons_and_hubbards_equivalents() -> None:
    got = values("spokes-disc-centred")
    w = scene.ARTERY_UM
    # Six equal widths: three pairs, then a pair and a pass-through, then a pair.
    pair = 0.88 * math.sqrt(2) * w
    second = 0.88 * math.hypot(pair, pair)
    expected = 0.88 * math.hypot(second, pair)
    assert got["calibre/CRE-knudtson/artery/B"] == pytest.approx(expected, rel=1e-9)
    assert got["calibre/CRE-knudtson/artery/C"] == pytest.approx(expected, rel=1e-9)
    assert got["calibre/AVR-knudtson/both/B"] == pytest.approx(
        expected / got["calibre/CRE-knudtson/vein/B"]
    )
    assert got["calibre/CRE-hubbard/artery/B"] == pytest.approx(truth.hubbard([w] * 6, "artery"))
    assert got["landmarks/centring"] == "disc"
    assert values("spokes-macula-centred")["landmarks/centring"] == "macula"


def test_a_single_vessel_passed_through_the_recursion_is_a_reading() -> None:
    single = library.truths("straight")["calibre/CRE-knudtson/artery/B"]
    assert single.value == scene.ARTERY_UM and single.kind == "convention"


def test_hubbards_constants_do_not_scale_with_the_vessel() -> None:
    # The venular constant, +450.05 µm², is the one large enough to see.
    w = scene.VEIN_UM
    assert truth.hubbard([2 * w] * 6, "vein") != pytest.approx(
        2 * truth.hubbard([w] * 6, "vein"), rel=1e-3
    )
    assert truth.knudtson([2 * w] * 6, "artery") == pytest.approx(
        2 * truth.knudtson([w] * 6, "artery")
    )


def test_the_two_framings_photograph_the_same_eye_in_zone_b() -> None:
    disc, macula = values("spokes-disc-centred"), values("spokes-macula-centred")
    for key in ("calibre/CRE-knudtson/artery/B", "calibre/AVR-hubbard/both/B"):
        assert disc[key] == pytest.approx(macula[key])


def test_a_value_the_geometry_leaves_undefined_is_none_not_absent() -> None:
    straight = library.truths("straight")
    assert straight["topology/branching-angle/artery/mean"].value is None
    # A count of nothing is 0, which is not None.
    assert straight["topology/junctions/artery"].value == 0.0
    disjoint = library.truths("disjoint")
    assert disjoint["tortuosity/vessel-hart-tau1/artery/median"].value is None
    assert disjoint["calibre/CRE-knudtson/artery/B"].value is None
    assert disjoint["calibre/width/artery/B/mean"].value is None
    # The squared curvature of a corner is infinite, not undefined: left out.
    assert "tortuosity/hart-tau3/artery/median" not in library.truths("koch")


def test_the_vessels_as_one_class_are_the_two_pooled() -> None:
    got = values("straight")
    assert got["density/area/vessels"] == pytest.approx(
        got["density/area/artery"] + got["density/area/vein"]
    )
    assert got["density/skeleton-length/vessels"] == pytest.approx(2 * library.STRAIGHT_UM)
    assert got["topology/components/vessels"] == 2.0
    assert got["topology/endpoints/vessels"] == 4.0
    assert got["calibre/width/vessels/mean"] == pytest.approx((scene.ARTERY_UM + scene.VEIN_UM) / 2)
    assert got["tortuosity/hart-tau1/vessels/median"] == pytest.approx(1.0)


def test_no_union_name_is_written_that_the_vocabulary_lacks() -> None:
    assert not any(
        key.startswith(("calibre/CRE-", "calibre/AVR-")) and "/vessels" in key
        for key in library.truths("spokes-disc-centred")
    )


def test_a_vessel_leaving_the_field_of_view_is_refused() -> None:
    with pytest.raises(ValueError, match="field of view"):
        scene.check_inside(
            scene.Scene(
                name="out",
                disc=(0.0, 0.0),
                artery=scene.network([scene.line((0.0, 0.0), 0.0, 9000.0)], scene.ARTERY_UM),
                vein=scene.network([scene.line((0.0, 0.0), 90.0, 100.0)], scene.VEIN_UM),
            )
        )


def test_a_rendering_paints_the_geometry_at_any_rotation_and_resolution() -> None:
    expected = values("bifurcation")["density/area/artery"]
    for side, rotation in ((1024, 0.0), (2048, 30.0)):
        shape = library.build("bifurcation", side=side, rotation=rotation)
        assert shape.artery.shape == (side, side)
        assert shape.artery.sum() * shape.um_per_px**2 == pytest.approx(expected, rel=0.01)
        assert shape.fov.sum() * shape.um_per_px**2 == pytest.approx(
            math.pi * scene.FOV_RADIUS_UM**2, rel=0.01
        )


def test_the_disc_turns_with_the_scene_about_the_frame_centre() -> None:
    side = 1024
    upright = library.build("straight", side=side, rotation=0.0)
    turned = library.build("straight", side=side, rotation=90.0)
    # Pixel i's centre sits at i: the frame centre is (side - 1) / 2.
    middle = (side - 1) / 2
    assert upright.disc[0] > middle and upright.disc[1] == pytest.approx(middle)
    # A quarter turn counter-clockwise on screen carries the right of the frame to its top.
    assert turned.disc[0] == pytest.approx(middle)
    assert turned.disc[1] == pytest.approx(side - 1 - upright.disc[0])
    assert upright.disc[2] == pytest.approx(scene.DISC_RADIUS_UM / render.um_per_px(side))


def test_the_disc_handed_over_sits_on_the_pixels_drawn_around_it() -> None:
    side = 512
    shape = library.build("spokes-disc-centred", side=side)
    x, y, _ = shape.disc
    # The spokes are symmetric about the disc, so the drawn vessels' centroid is the disc centre.
    drawn = np.argwhere(shape.artery | shape.vein).mean(axis=0)
    assert drawn[1] == pytest.approx(x, abs=0.05)
    assert drawn[0] == pytest.approx(y, abs=0.05)


def test_truth_does_not_depend_on_the_grid_or_the_angle() -> None:
    one = library.build("tree", side=512, rotation=0.0)
    other = library.build("tree", side=1024, rotation=37.0)
    assert one.truths == other.truths
    assert not np.array_equal(one.artery, np.rot90(one.artery))


def test_every_shape_draws_an_artery_and_a_vein_inside_the_field() -> None:
    for name in library.SHAPES:
        shape = library.build(name, side=512)
        assert shape.artery.any() and shape.vein.any(), name
        assert not ((shape.artery | shape.vein) & ~shape.fov).any(), name


def test_the_demo_picture_shows_each_class_in_its_own_colour() -> None:
    shape = library.build("straight", side=256)
    picture = library.demo_image(shape)
    assert picture.shape == (256, 256, 3)
    assert (picture[shape.artery & ~shape.vein] == library.ARTERY_COLOUR).all()
    assert (picture[shape.vein & ~shape.artery] == library.VEIN_COLOUR).all()


def test_an_unknown_shape_is_refused() -> None:
    with pytest.raises(LookupError, match="no shape"):
        library.build("hexagon")


def test_equal_values_spread_by_exactly_nothing() -> None:
    """Equal tortuosities must give a std of 0, not 1e-16 of rounding.

    The analysis takes its noise floor from each biomarker's largest truth, so a truth of 1e-16
    where the geometry says 0 sets that floor at 1e-18, and every honest answer becomes a fault.
    """
    for shape in ("tree", "deep-bifurcation", "spokes-macula-centred", "spokes-disc-centred"):
        assert library.truths(shape)["tortuosity/hart-tau1/artery/std"].value == 0.0, shape
