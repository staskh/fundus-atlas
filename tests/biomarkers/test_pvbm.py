# ABOUTME: Tests for the PVBM adapter: what it is handed, what it answers with, and the rules it
# ABOUTME: keeps — catalogued names, no silent unit conversion, and no class invented from another.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

#: Big enough for the ring the equivalents are measured over. A clinical optic disc is 1800 µm
#: across, so three disc radii is 2700 µm, and a frame that cannot hold that cannot carry a shape
#: which tests them.
SIDE = 1024


def an_adapter():
    return catalogue.load("pvbm")


def test_it_declares_what_it_needs_and_what_it_claims() -> None:
    adapter = an_adapter()
    declared = adapter.declare()

    assert declared["slug"] == "pvbm"
    assert "artery" in adapter.needs and "disc" in adapter.needs
    assert "rotation" in adapter.invariant, "its measurements should not turn with the image"
    assert declared["upstream"]["commit"], "a run records the code that produced the number"


def test_it_answers_under_pvbms_names_and_declares_what_they_mean() -> None:
    """The evidence carries PVBM's vocabulary; what each column is believed to measure is declared.

    A reader checking a number against PVBM's own documentation looks for `craek`, not for a name
    this repository invented. Translating is a claim about somebody else's code, and it travels as
    a declaration an analysis can apply or disbelieve rather than baked into the measurement.
    """
    adapter = an_adapter()
    names = adapter.declare()["names"]

    assert set(names) == set(adapter.keys())
    for catalogued in names.values():
        if catalogued is not None:
            canonical.check(catalogued)


def test_it_translates_its_own_columns_onto_catalogued_names() -> None:
    """The renaming happens here, so a run's evidence needs no translation step after it."""
    adapter = an_adapter()

    assert adapter.declare()["names"]["area_artery"] == "vessel-area-and-length/area/artery"
    assert adapter.canonical_for("area_artery") == "vessel-area-and-length/area/artery"
    # Read out of `compute_angles_dictionary`: it medians every pairwise angle at every junction,
    # the trunk included, so it is not the angle between a bifurcation's daughters.
    assert adapter.canonical_for("median_branching_angle_artery") is None
    assert "median_branching_angle_artery" in adapter.keys(), "and is measured all the same"


def test_a_column_the_catalogue_cannot_name_is_still_measured() -> None:
    """A quantity without a catalogued name is a gap in the catalogue, not a thing to throw away.

    PVBM's perimeter, its singularity length and the mean and spread of its branching angles have
    no catalogued name yet. Dropping them would make the benchmark quietly measure less than the
    implementation computes, and would hide what the catalogue is missing.
    """
    adapter = an_adapter()
    shape = library.build("straight", side=SIDE)

    measured = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)

    for own in ("perimeter_artery", "singularity_length_artery", "std_branching_angle_artery"):
        assert own in measured, f"{own} was not kept"
    assert measured["perimeter_artery"] is not None, "and it was actually measured"


def test_a_class_it_was_not_given_comes_back_as_nothing() -> None:
    """Handed no veins, it measures arteries and declines the rest — never substituting one for
    the other, which would be invisible in the evidence."""
    adapter = an_adapter()
    shape = library.build("straight", side=SIDE)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    vein_keys = [key for key in measured if key.endswith(("/vein", "_vein"))]
    assert vein_keys, "the keys exist so that a table has the same columns whatever it was given"
    assert all(measured[key] is None for key in vein_keys), "and every one of them is empty"


def test_a_ratio_of_two_classes_needs_both_of_them() -> None:
    adapter = an_adapter()
    shape = library.build("straight", side=SIDE)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    assert measured["avr_knudtson"] is None, "an AVR from arteries alone is the worst answer here"


def test_pvbm_computes_both_equivalents_from_pixel_widths_whatever_scale_it_is_given() -> None:
    """A finding rather than a preference, and the reason the adapter passes no scale on.

    PVBM measures widths from the mask in pixels and puts those pixel widths into both formulas.
    Knudtson's is scale-free so that is harmless. Hubbard's constants were fitted in microns and
    its additive term does not scale, so what it returns is not a pixel-valued Hubbard equivalent
    awaiting conversion — it is a different quantity. The adapter reproduces that rather than
    quietly feeding it microns, and the evidence carries it for the analysis to judge.
    """
    adapter = an_adapter()
    shape = library.build("spokes-macula-centred", side=SIDE)

    without = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, None)
    with_scale = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, 5.0)

    assert without["crae_knudtson"] is not None
    assert without["crae_hubbard"] is not None, "it computes one whether or not a scale exists"
    assert without["crae_hubbard"] == pytest.approx(with_scale["crae_hubbard"]), (
        "and the scale changes nothing, because PVBM never sees it"
    )


def test_it_recovers_the_tortuosity_of_a_straight_vessel() -> None:
    """The one measurement no implementation may get wrong."""
    adapter = an_adapter()
    shape = library.build("straight", side=1024)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    assert measured["median_tortuosity_artery"] == pytest.approx(1.0, abs=0.02)


def test_a_crash_is_recorded_rather_than_raised() -> None:
    """One unmeasurable shape must not lose a run of hundreds."""
    adapter = an_adapter()
    empty = np.zeros((SIDE, SIDE), dtype=bool)

    measured = adapter.measure(
        empty, None, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 5.0
    )

    assert set(measured) <= set(adapter.keys())


def test_it_measures_equivalents_at_the_grid_the_benchmark_runs_on() -> None:
    """At 2048² — not at the 512² the rest of these tests use, which is the whole point.

    PVBM writes pixel coordinates into arrays derived from the masks it is handed, so handing it
    8-bit masks overflows on a large frame: `Python integer 416 out of bounds for uint8`. The
    adapter caught that and returned no answer, which read in the results as PVBM declining rather
    than as our own defect. The size is the test.
    """
    adapter = an_adapter()
    shape = library.build("spokes-macula-centred", side=2048, um_per_px=5.0)

    answers = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, 5.0)

    assert not adapter.trouble, f"nothing should have fallen over: {adapter.trouble}"
    assert answers["crae_knudtson"] is not None, "twelve vessels leave the disc; it can answer"
    assert np.isfinite(answers["crae_knudtson"])


def test_it_says_which_call_each_measurement_comes_out_of() -> None:
    """A failure is recorded per call, so attributing it needs to know what each call produced.

    Without this a reader cannot tell a column lost to an exception from one the shape never
    defined: both are empty. The equivalents are the case that matters, because they raise on a
    long vessel while the geometry beside them is measured perfectly well.
    """
    calls = an_adapter().declare()["calls"]

    assert calls["area_artery"] == ["geometry_artery"]
    assert calls["capacity_dimension_vein"] == ["fractals_vein"]
    assert calls["crae_knudtson"] == ["equivalents_artery"]
    assert calls["crve_hubbard"] == ["equivalents_vein"]
    # A ratio needs both classes, so either failing costs it.
    assert calls["avr_knudtson"] == ["equivalents_artery", "equivalents_vein"]
    assert set(calls) == set(an_adapter().keys()), "every column says where it came from"
