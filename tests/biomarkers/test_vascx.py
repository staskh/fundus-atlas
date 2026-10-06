# ABOUTME: Tests for the VascX adapter: the fovea it has to supply, the one conversion it makes,
# ABOUTME: and the rule that anything depending on the invented axis stays uncatalogued.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

SIDE = 1024


def an_adapter():
    return catalogue.load("vascx")


@pytest.fixture(scope="module")
def shape():
    return library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)


def test_it_declares_the_configuration_it_ran() -> None:
    """A VascX feature is a configurable object, so which configuration ran is part of the result."""
    declared = an_adapter().declare()

    assert declared["slug"] == "vascx"
    assert declared["feature_set"] == "fs_od_centered", "a set VascX ships, not one assembled here"
    assert "disc diameters" in declared["circle"]
    assert declared["upstream"], "a run records the code that produced the number"


def test_every_name_it_answers_under_is_catalogued_or_plainly_its_own() -> None:
    adapter = an_adapter()

    for key in adapter.keys():
        if "/" in key:
            canonical.check(key)
    assert set(adapter.declare()["names"]) == set(adapter.keys())


def test_nothing_measured_against_the_invented_axis_is_catalogued() -> None:
    """The fovea is this fixture's convention, so anything oriented on it is ours, not VascX's.

    A synthetic shape has no macula. VascX's grids need one, so the adapter supplies it — which
    means superior, inferior, temporal and nasal are directions this repository chose. Comparing
    them against anything would be comparing the fixture with itself.
    """
    adapter = an_adapter()

    behind = adapter.declare()["names"]
    for own, catalogued in behind.items():
        if catalogued is None:
            continue
        assert not any(
            direction in own for direction in ("superior", "inferior", "temporal", "nasal")
        ), f"{own} claims {catalogued} but is measured against the axis we invented"
    assert any("temporal_angle" in key for key in adapter.keys()), "and it is still measured"


def test_the_fovea_follows_the_framing() -> None:
    """Frame centre where the disc is off-centre; one offset away where the disc is centred."""
    adapter = an_adapter()

    macula = adapter._fovea(SIDE, SIDE * 0.70, SIDE * 0.5)
    centred = adapter._fovea(SIDE, SIDE / 2, SIDE / 2)

    assert macula == pytest.approx((SIDE / 2, SIDE / 2)), (
        "a macula-centred frame centres the macula"
    )
    assert centred[0] < SIDE / 2, "a disc-centred frame puts the macula to one side of the disc"
    assert centred[1] == pytest.approx(SIDE / 2)


def test_it_converts_its_millimetres_back_to_the_pixels_every_adapter_reports(shape) -> None:
    """The only conversion it makes, and it is exact: the scale is the shape's own.

    VascX is the one implementation here that works in physical units, because it is the one that
    takes a scale. Its calibre comes back in millimetres and it reports pixels, like every other
    adapter — and `canonical.from_pixels` is the single place those pixels become the microns the
    catalogued name is in, which is what this test walks end to end.
    """
    adapter = an_adapter()

    measured = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)

    # Under VascX's own names, which is what a run records; the ground truth is the shape's.
    names = adapter.declare()["names"]
    calibre = next(
        own for own, name in names.items() if name == "calibre/width/artery/length-weighted"
    )
    equivalent = next(
        own for own, name in names.items() if name == "calibre/CRE-knudtson/artery/B"
    )

    for own, catalogued in (
        (calibre, "calibre/width/artery/length-weighted"),
        (equivalent, "calibre/CRE-knudtson/artery/B"),
    ):
        assert canonical.from_pixels(
            catalogued, measured[own], shape.um_per_px
        ) == pytest.approx(shape.theory[catalogued], rel=0.05), catalogued


def test_it_declines_when_handed_one_class(shape) -> None:
    """Its retina is assembled from both at once, and substituting one for the other would hide."""
    adapter = an_adapter()

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    assert all(value is None for value in measured.values())
    assert adapter.trouble, "and it says why rather than leaving empty cells"


def test_a_crash_is_recorded_rather_than_raised() -> None:
    adapter = an_adapter()
    empty = np.zeros((SIDE, SIDE), dtype=bool)

    measured = adapter.measure(
        empty, empty, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 10.0
    )

    assert set(measured) <= set(adapter.keys())


#: A frame big enough to hold a disc and a vessel running well past it, and small enough that
#: building VascX's graph over it takes a moment rather than a minute.
GAP_SIDE = 900

#: How wide the test vessel is drawn, in pixels.
GAP_WIDTH = 9


def _one_vein_with_a_gap(gap: int):
    """One straight vein past the disc, with `gap` pixels cut out of its middle, as VascX sees it.

    Built through VascX's own classes rather than through the adapter, because what is under test
    is the tracer rather than any biomarker.
    """
    from upstreams import vascx

    vascx.on_path()
    from rtnls_enface.disc import OpticDisc

    Retina, VesselTreeLayer, FundusVesselsLayer, _ = an_adapter()._loaded()
    vein = np.zeros((GAP_SIDE, GAP_SIDE), bool)
    vein[150:750, GAP_SIDE // 2 - GAP_WIDTH // 2 : GAP_SIDE // 2 + GAP_WIDTH // 2] = True
    if gap:
        vein[450 - gap // 2 : 450 + gap // 2 + gap % 2, :] = False
    artery = np.zeros((GAP_SIDE, GAP_SIDE), bool)
    artery[150:750, 200 : 200 + GAP_WIDTH] = True
    disc = np.zeros((GAP_SIDE, GAP_SIDE), np.uint8)
    rows, columns = np.mgrid[:GAP_SIDE, :GAP_SIDE]
    disc[(columns - GAP_SIDE // 2) ** 2 + (rows - 120) ** 2 <= 60**2] = 1
    retina = Retina(
        disc_path_or_mask=disc,
        layers={
            "arteries": VesselTreeLayer("arteries", artery, color=(1, 0, 0)),
            "veins": VesselTreeLayer("veins", vein, color=(0, 0, 1)),
            "vessels": FundusVesselsLayer(name="vessels", mask=artery | vein),
        },
        resolution=(GAP_SIDE, GAP_SIDE),
        mm_per_pixel=0.005,
        fovea_location=(GAP_SIDE * 0.8, GAP_SIDE * 0.5),
        roi_mask=np.ones((GAP_SIDE, GAP_SIDE), np.uint8),
    )
    # The 1024-pixel disc defect of `docs/projects/vascx.md` §8.1, worked around as the adapter does.
    retina.disc = OpticDisc(disc, fundus=retina, size=GAP_SIDE)
    return retina.layers["veins"]


@pytest.mark.parametrize("gap", [1, 9, 40])
def test_vascx_never_rejoins_a_vessel_across_a_gap(gap: int) -> None:
    """*Our finding, 2026-10-01.* One pixel of gap is one vessel more, at every width.

    `docs/projects/vascx.md` §8.3 and `docs/biomarkers/vessel-tracing.md` §3.2.1 are where this is
    written up, and this is what holds those pages to the code. It matters because VascX's own
    artery/vein model is a four-way softmax that cannot represent a crossing, so the losing vessel
    is cut at every one — and nothing downstream puts it back together.

    Four stages could bridge and none does; the last of them, `merge_edges` inside
    `_build_vessels`, refuses outright with `ValueError("The edges are not consecutive!")`.
    """
    whole = _one_vein_with_a_gap(0)
    broken = _one_vein_with_a_gap(gap)

    assert len(whole.resolved_segments) == 1, "an unbroken vein is one resolved vessel"
    assert len(broken.resolved_segments) == 2, f"a {gap}px gap must leave two, not one rejoined"
    assert len(broken.trees) == 2, "one tree per connected component, so the orphan is kept"
    longest = max(len(segment.skeleton) for segment in broken.resolved_segments)
    assert longest < 0.6 * max(len(s.skeleton) for s in whole.resolved_segments), (
        "the longest surviving vessel is a fraction of the whole one, not nearly all of it"
    )
