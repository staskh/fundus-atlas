# ABOUTME: Tests for the claimed ground truth: every unnamed column is read by its own description,
# ABOUTME: and what each claim requires of a shape is what the geometry gives.

import math
from pathlib import Path

import pytest

from benchmarks.shapes import claims, library, store
from biomarkers import canonical
from biomarkers.utils import catalogue

GROUPED = ("pvbm", "ocular", "automorph", "automorphalyzer", "automorphclass", "vascx")
ROOT = Path(library.__file__).resolve().parents[3]


@pytest.mark.parametrize("slug", GROUPED)
def test_every_claim_names_a_column_the_implementation_returns(slug) -> None:
    keys = set(catalogue.load(slug).keys())
    for column in claims.claimed(slug):
        assert column in keys, f"{slug} returns no column {column!r}"


@pytest.mark.parametrize("slug", GROUPED)
def test_every_unnamed_column_is_claimed_or_said_to_be_a_mirror(slug) -> None:
    """A column the catalogue cannot name is otherwise unchecked, so each one is read here — or is
    one of the few that only re-measure a catalogued quantity over the wrong class."""
    names = catalogue.load(slug).declare()["names"]
    unnamed = {own for own, name in names.items() if name is None}
    mirrored = {own for own in unnamed if own.startswith(("CRAE_Knudtson@", "CRVE_Knudtson@"))}
    assert unnamed - mirrored <= set(claims.claimed(slug)), sorted(
        unnamed - mirrored - set(claims.claimed(slug))
    )


def test_a_claim_naming_the_vocabulary_names_a_real_biomarker() -> None:
    for claim in claims.CLAIMS:
        if claim.canonical:
            canonical.check(claim.canonical)
        assert bool(claim.canonical) + bool(claim.derive) + bool(claim.unsettled) == 1, claim


def test_the_ratio_of_sums_on_an_arc_is_its_arc_over_its_chord() -> None:
    """One segment per class, so the ratio of sums is that segment's own τ1."""
    theta = math.radians(library.ARC_DEGREES)
    found = claims._ratio_of_sums("artery")(library.scene("arc"), {}).value
    assert found == pytest.approx(theta / (2 * math.sin(theta / 2)), rel=1e-4)


def test_a_start_point_is_a_vessel_leaving_the_disc() -> None:
    assert claims._start_points("artery")(library.scene("spokes-disc-centred"), {}).value == 6
    assert claims._start_points("vein")(library.scene("disjoint"), {}).value == 0


def test_the_committed_table_holds_every_settled_claim() -> None:
    values, kinds = claims.read(ROOT / store.STORE)
    manifest = store.read(ROOT / store.STORE)
    assert set(values) == {row["key"] for row in manifest}, (
        "redraw with `python -m benchmarks.shapes.claims`"
    )
    settled = {claim.label for claim in claims.CLAIMS if not claim.unsettled}
    assert set().union(*kinds.values()) <= settled
