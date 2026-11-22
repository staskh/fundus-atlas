# ABOUTME: Tests for what the synthetic notebooks read: the noise floor, the two comparisons, and
# ABOUTME: the ordering of a program's biomarkers from closest to furthest.

from pathlib import Path

import pandas as pd
import pytest

from benchmarks import synthetic_evidence as se
from benchmarks.shapes import claims, library, store

ROOT = Path(library.__file__).resolve().parents[3]


def test_a_difference_under_the_floor_is_no_difference() -> None:
    assert se.error(1.005, 1.0, size=1.0) == 0.0
    assert se.error(1.5, 1.0, size=1.0) == pytest.approx(0.5)
    assert se.signed(0.5, 1.0, size=1.0) == pytest.approx(-0.5)


def test_a_truth_of_nought_is_judged_against_the_floor_not_divided_by() -> None:
    """A straight vessel has no inflections; answering 0.5 is fifty floors out, not infinitely."""
    assert se.error(0.5, 0.0, size=1.0) == pytest.approx(50.0)


def test_spread_is_width_over_mean_and_needs_two_values() -> None:
    assert se.spread(pd.Series([1.0, 1.2]), size=1.0) == pytest.approx(0.2 / 1.1)
    assert pd.isna(se.spread(pd.Series([1.0]), size=1.0))
    assert se.spread(pd.Series([1.0, 1.004]), size=1.0) == 0.0


def test_best_and_worst_never_list_a_biomarker_twice() -> None:
    against = pd.DataFrame(
        {
            "implementation": "x",
            "canonical": ["a", "a", "b", "c", "d"],
            "error": [0.0, 0.0, 0.1, 0.5, 2.0],
            "shape": "straight",
            "rotation": 0.0,
        }
    )
    best, worst = se.best_and_worst(against, "x", tolerance=0.25)
    assert list(best.index) == ["a", "b"], "the closest half, the one inside the floor first"
    assert list(worst.index) == ["d", "c"], "only what is out of tolerance, furthest first"
    assert not set(best.index) & set(worst.index)


def test_what_turning_is_meant_to_move_is_read_off_the_claimed_table() -> None:
    moving = claims.turning(ROOT / store.STORE)
    assert ("automorphalyzer", "cup_centre_x") in moving
    assert ("pvbm", "tortuosity_index_artery") not in moving


def test_the_cup_s_diameters_turn_with_the_image_and_the_disc_s_do_not() -> None:
    """*Since 2026-11-22* the disc and cup sizes are canonical, so what turning should move is said
    beside the ratios rather than read off the claims."""
    from benchmarks.shapes.truth import TURN_WITH_THE_IMAGE

    assert "landmarks/cup-diameter-vertical" in TURN_WITH_THE_IMAGE
    assert "landmarks/disc-diameter-vertical" not in TURN_WITH_THE_IMAGE, "a circle does not turn"


def test_a_lineage_reads_under_its_own_projects_names() -> None:
    """*Added 2026-11-22.* Each sibling's column stands on the row of the column its lineage's own
    project gives the same quantity, so a reader finds AutoMorph's and PVBM's names, not ours."""
    from benchmarks.synthetic_evidence import native

    assert (
        native("automorphalyzer", "average_global_calibre@whole_artery") == "average_width_artery"
    )
    assert (
        native("automorphalyzer", "tortuosity_distance@C_vein") == "distance_tortuosity_vein_zone_c"
    )
    assert native("automorphalyzer", "CRAE_Knudtson@B_artery") == "CRAE_Knudtson_zone_b"
    assert native("automorphalyzer", "AVR_C") == "AVR_Knudtson_zone_c"
    assert native("automorphclass", "average_width_vessels") == "average_width_binary"
    assert native("automorphclass", "cdr_vertical") == "CDR_vertical"
    assert native("ocular", "pooled_tortuosity_artery") == "tortuosity_index_artery"
    assert native("vascx", "full_cre_arteries") == "full_cre_arteries"


def test_a_column_measuring_something_else_never_shares_a_row() -> None:
    """AutoMorphClass's zone C is 3 to 5 disc radii and AutoMorph's 2 to 5: one spelling, two
    regions. An arterial equivalent over the vein map is not AutoMorph's CRAE either."""
    from benchmarks.synthetic_evidence import native

    assert native("automorphclass", "average_width_artery_zone_c") != "average_width_artery_zone_c"
    assert native("automorphalyzer", "CRAE_Knudtson@B_vein").endswith("(automorphalyzer)")
    assert native("ocular", "length_weighted_tortuosity_artery").endswith("(ocular)")
