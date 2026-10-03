# ABOUTME: Tests for the OCULAR adapter: that it measures PVBM's code as OCULAR modified it, and
# ABOUTME: that the positional list it returns is read in the order OCULAR returns it.

from pathlib import Path

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

SIDE = 1024


def an_adapter():
    return catalogue.load("ocular")


@pytest.fixture(scope="module")
def shape():
    return library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)


def test_it_declares_what_pins_it_and_which_traversal_it_ran() -> None:
    adapter = an_adapter()
    declared = adapter.declare()

    assert declared["slug"] == "ocular"
    assert declared["upstream"]["commit"], "a run records the code that produced the number"
    assert declared["traversal"] == "recursive", "OCULAR's own default, left alone"


def test_every_name_it_answers_under_is_catalogued_or_plainly_its_own() -> None:
    adapter = an_adapter()

    for key in adapter.keys():
        if "/" in key:
            canonical.check(key)
    assert set(adapter.declare()["names"]) == set(adapter.keys())


def test_the_three_tortuosity_aggregations_are_told_apart() -> None:
    """It returns three, and the vocabulary can now name two of them apart.

    A pooled ratio of sums, a median of ratios and an arc-weighted mean are three aggregations of
    one idea. Two of them are statistics the catalogue names — `median` and `length-weighted` —
    and they map to names that differ in that part, so nothing makes them look like agreement.
    The third divides one sum by another rather than pooling per-vessel values at all, and no
    statistic describes it, so it stays under OCULAR's own name.
    """
    adapter = an_adapter()
    behind = adapter.declare()["names"]

    assert behind["median_tortuosity_artery"] == "tortuosity/hart-tau1/artery/median"
    assert (
        behind["length_weighted_tortuosity_artery"]
        == "tortuosity/hart-tau1/artery/length-weighted"
    )
    assert behind["median_tortuosity_artery"] != behind["length_weighted_tortuosity_artery"]
    assert "pooled_tortuosity_artery" in adapter.keys(), "the ratio of sums is kept"
    assert behind["pooled_tortuosity_artery"] is None, "and claims no catalogued biomarker"


def test_it_reaches_no_central_retinal_equivalents() -> None:
    """Its copy keeps PVBM's graph machinery and returns geometry only — a difference in scope."""
    adapter = an_adapter()

    assert "calibre/CRE-knudtson" in adapter.declare()["absent"]
    assert not [key for key in adapter.keys() if key.startswith("central-retinal")]


def test_it_measures_pvbms_code_and_agrees_with_pvbm_on_tortuosity(shape) -> None:
    """The point of cataloguing the two together: OCULAR imports PVBM's tortuosity helper.

    On one shape the two should therefore return very nearly the same number, and a divergence
    would be something OCULAR changed rather than a different definition.
    """
    ocular = an_adapter().measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)
    pvbm = catalogue.load("pvbm").measure(
        shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px
    )

    # Each under its own name for the same quantity: OCULAR's `median_tortuosity` is PVBM's
    # `median_tortuosity`, because it is literally PVBM's function.
    assert ocular["median_tortuosity_artery"] == pytest.approx(
        pvbm["median_tortuosity_artery"], rel=0.01
    )


def test_a_class_it_was_not_given_comes_back_as_nothing(shape) -> None:
    adapter = an_adapter()

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    veins = [key for key in measured if key.endswith(("/vein", "_vein"))]
    assert veins and all(measured[key] is None for key in veins)


def test_a_crash_is_recorded_rather_than_raised() -> None:
    adapter = an_adapter()
    empty = np.zeros((SIDE, SIDE), dtype=bool)

    measured = adapter.measure(
        empty, None, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 10.0
    )

    assert set(measured) <= set(adapter.keys())


def test_it_says_where_its_catalogue_page_is() -> None:
    """Its slug does not name its page — the project is OCULARNet — so it has to say.

    Anything generating a link to an implementation's page asks the adapter rather than assuming
    the slug is the filename, which produced a broken link on the configuration page until it did.
    """
    declared = an_adapter().declare()

    assert declared["page"] == "ocularnet"
    assert (
        Path(__file__).resolve().parents[2] / "docs" / "projects" / f"{declared['page']}.md"
    ).exists()
