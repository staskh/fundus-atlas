# ABOUTME: Tests for the two measurements an artery/vein benchmark makes — overlap and connectedness
# ABOUTME: — against shapes whose answer is arithmetic rather than another program's output.

import numpy as np
import pytest

from benchmarks.metrics import av


def a_line(length: int = 60, row: int = 30, width: int = 3, start: int = 10) -> np.ndarray:
    drawn = np.zeros((60, 80), dtype=bool)
    drawn[row : row + width, start : start + length] = True
    return drawn


def test_two_identical_vessels_overlap_completely() -> None:
    drawn = a_line()

    assert av.dice(drawn, drawn) == pytest.approx(1.0)
    assert av.cldice(drawn, drawn) == pytest.approx(1.0)


def test_nothing_in_common_scores_nothing() -> None:
    assert av.dice(a_line(row=10), a_line(row=50)) == pytest.approx(0.0)
    assert av.cldice(a_line(row=10), a_line(row=50)) == pytest.approx(0.0)


def test_overlap_is_twice_the_shared_area_over_the_two_areas() -> None:
    said, truth = a_line(width=4), a_line(width=2)

    assert av.dice(said, truth) == pytest.approx(2 * 2 / (4 + 2))


def test_a_vessel_traced_too_thick_keeps_its_connectedness() -> None:
    """This is why clDice is measured beside Dice.

    A model that draws every vessel three times as wide, around the same centre, is wrong about
    width and right about the network. Overlap halves; clDice does not move. The two together say
    which kind of wrong a model is, which one alone cannot.
    """
    truth = a_line(row=30, width=2)
    said = a_line(row=28, width=6)

    assert av.dice(said, truth) == pytest.approx(0.5)
    assert av.cldice(said, truth) > 0.95


def test_a_vessel_traced_thick_and_off_centre_loses_its_centreline() -> None:
    """Thickening a vessel to one side moves its centreline out of the expert's vessel entirely.

    clDice is a statement about where the centre of a vessel runs, not about how much ink is near
    it, and this is the case that shows the difference.
    """
    truth = a_line(row=30, width=2)
    said = a_line(row=30, width=6)

    assert av.dice(said, truth) == pytest.approx(0.5), "the same overlap as the centred case"
    assert av.cldice(said, truth) < 0.1, "and none of the connectedness"


def test_a_vessel_broken_in_two_costs_both_scores_alike() -> None:
    """A gap removes pixels and centreline in the same proportion, so neither score hides it.

    Worth pinning because it is the case clDice is often assumed to punish harder: it does not. What
    it catches is the thickness error above, not a missing sixth of a vessel.
    """
    truth = a_line(length=60)
    said = truth.copy()
    said[:, 35:45] = False

    assert av.dice(said, truth) == pytest.approx(0.91, abs=0.02)
    assert av.cldice(said, truth) == pytest.approx(0.91, abs=0.02)


def test_a_missing_branch_costs_both_scores() -> None:
    truth = a_line() | a_line(row=45, start=40, length=30)
    said = a_line()

    assert av.dice(said, truth) == pytest.approx(0.80, abs=0.02)
    assert av.cldice(said, truth) == pytest.approx(0.80, abs=0.02)


def test_an_empty_prediction_against_an_empty_truth_is_not_a_score() -> None:
    """A photograph with no vein annotated and a model that drew none has nothing to measure."""
    empty = np.zeros((60, 80), dtype=bool)

    assert av.dice(empty, empty) is None
    assert av.cldice(empty, empty) is None


def test_predicting_vessels_where_there_are_none_scores_zero_rather_than_nothing() -> None:
    empty = np.zeros((60, 80), dtype=bool)

    assert av.dice(a_line(), empty) == pytest.approx(0.0)
    assert av.cldice(a_line(), empty) == pytest.approx(0.0)


def test_what_is_measured_for_one_photograph() -> None:
    truth = {"artery": a_line(row=20), "vein": a_line(row=40)}
    said = {"artery": a_line(row=20), "vein": a_line(row=40, width=6)}

    measured = av.measure(said, truth)

    assert measured["artery_dice"] == pytest.approx(1.0)
    assert measured["vein_dice"] < 1.0
    assert measured["vessels_dice"] is not None, "arteries and veins together"
    assert measured["artery_cldice"] == pytest.approx(1.0)
    assert set(measured) >= {
        "artery_dice",
        "vein_dice",
        "vessels_dice",
        "artery_cldice",
        "vein_cldice",
        "vessels_cldice",
    }


def test_the_vessel_score_is_the_union_of_what_the_model_drew() -> None:
    """The benchmark asks for arteries, veins, and the vessels they make together."""
    truth = {"artery": a_line(row=20), "vein": a_line(row=40)}
    said = {"artery": a_line(row=20), "vein": np.zeros((60, 80), dtype=bool)}

    measured = av.measure(said, truth)

    assert measured["vessels_dice"] == pytest.approx(2 / 3, abs=0.02), "half the network found"


def test_a_model_that_only_finds_vessels_is_measured_on_what_it_drew() -> None:
    """A vessel-only model has no arteries to take a union of, and its own map is the answer.

    Deriving `vessels` from artery and vein is what makes that column mean one thing across every
    artery/vein model. A model that predicts vessels directly cannot take part in that derivation,
    so its own prediction stands — which is why the benchmark calls it a reference rather than a
    competitor.
    """
    artery = np.zeros((8, 8), dtype=bool)
    artery[2:4, :] = True
    vein = np.zeros((8, 8), dtype=bool)
    vein[4:5, :] = True
    drawn = artery | vein

    measured = av.measure({"vessels": drawn}, {"artery": artery, "vein": vein, "vessels": drawn})

    assert measured["vessels_dice"] == pytest.approx(1.0)
    assert "artery_dice" not in measured, "it said nothing about arteries and is asked nothing"
    assert "vein_dice" not in measured


def test_an_annotation_of_vessels_alone_scores_the_vessel_column_and_no_other() -> None:
    """FIVES annotates vessels and neither class, so an artery/vein model is scored on its union."""
    artery = np.zeros((8, 8), dtype=bool)
    artery[2:4, :] = True
    vein = np.zeros((8, 8), dtype=bool)
    vein[6:8, :] = True

    measured = av.measure({"artery": artery, "vein": vein}, {"vessels": artery | vein})

    assert measured["vessels_dice"] == pytest.approx(1.0), "the union is what it said about vessels"
    assert "artery_dice" not in measured, "nothing was drawn to compare its arteries against"


def test_a_published_vessel_map_is_not_overwritten_by_an_empty_union() -> None:
    """The union is derived where there is something to derive it from, and never otherwise."""
    drawn = np.zeros((8, 8), dtype=bool)
    drawn[1:3, :] = True

    assert av.vessels_of({"vessels": drawn}).shape == drawn.shape
    assert av.vessels_of({"vessels": drawn}).sum() == drawn.sum()
    assert av.vessels_of({"artery": drawn, "vessels": np.zeros((8, 8), dtype=bool)}).sum() == (
        drawn.sum()
    ), "where arteries exist the union is still what the vessel column holds"
