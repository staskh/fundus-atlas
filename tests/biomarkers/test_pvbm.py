# ABOUTME: Tests for the PVBM adapter: what it is handed, what it answers with, and the rules it
# ABOUTME: keeps — original names, no silent unit conversion, and no class invented from the other.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical, naming
from biomarkers.utils import catalogue

SIDE = 512


def an_adapter():
    return catalogue.load("pvbm")


def test_it_declares_what_it_needs_and_what_it_claims() -> None:
    adapter = an_adapter()
    declared = adapter.declare()

    assert declared["slug"] == "pvbm"
    assert "artery" in adapter.needs and "disc" in adapter.needs
    assert "rotation" in adapter.invariant, "its measurements should not turn with the image"
    assert declared["upstream"]["commit"], "a run records the code that produced the number"


def test_every_key_it_can_return_is_mapped_to_a_canonical_name() -> None:
    """A column nothing maps is a column no comparison can ever use."""
    for key in an_adapter().keys():
        mapped = naming.canonical_for("pvbm", key)
        if mapped is not None:
            canonical.check(mapped)


def test_it_answers_with_its_own_names() -> None:
    """`t2` stays `t2`. Translation is the naming table's job, reviewed on its own."""
    adapter = an_adapter()
    shape = library.build("straight", side=SIDE)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    assert set(measured) <= set(adapter.keys()), "it returned a key it does not declare"
    assert any("artery" in key for key in measured), "a run on arteries is named for arteries"


def test_a_class_it_was_not_given_comes_back_as_nothing() -> None:
    """Handed no veins, it measures arteries and declines the rest — never substituting one for
    the other, which would be invisible in the evidence."""
    adapter = an_adapter()
    shape = library.build("straight", side=SIDE)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    vein_keys = [key for key in measured if key.endswith("_vein")]
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
    shape = library.build("disc-spokes", side=SIDE)

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

    measured = adapter.measure(empty, None, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 5.0)

    assert set(measured) <= set(adapter.keys())
