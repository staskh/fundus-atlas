# ABOUTME: Tests for the three AutoMorph implementations: what each is handed, what it answers
# ABOUTME: under, and the peculiarities each adapter is allowed to know about and must declare.

import numpy as np
import pytest

from benchmarks.shapes import library
from biomarkers import canonical
from biomarkers.utils import catalogue

#: Big enough for the ring the equivalents are measured over, as in the PVBM tests.
SIDE = 1024

FAMILY = ("automorph", "automorphalyzer", "automorphclass")


@pytest.fixture(scope="module")
def shape():
    return library.build("spokes-macula-centred", side=SIDE, um_per_px=10.0)


@pytest.mark.parametrize("slug", FAMILY)
def test_it_declares_what_it_needs_and_what_pins_it(slug) -> None:
    adapter = catalogue.load(slug)
    declared = adapter.declare()

    assert declared["slug"] == slug
    assert "artery" in adapter.needs
    assert "rotation" in adapter.invariant
    assert declared["upstream"]["commit"], "a run records the code that produced the number"
    assert adapter.identity() == declared["upstream"]["commit"]


@pytest.mark.parametrize("slug", FAMILY)
def test_it_answers_under_its_own_names_and_says_what_they_mean(slug) -> None:
    """The evidence carries the implementation's vocabulary; the translation is declared beside it.

    A reader checking a number against its authors' documentation looks for the name they use, so
    that is what a run records. What each of those columns is believed to measure is a claim, and
    it travels as a separate declaration that an analysis can apply or disbelieve.
    """
    adapter = catalogue.load(slug)
    names = adapter.declare()["names"]

    assert set(names) == set(adapter.keys()), "every column says what it is believed to mean"
    assert set(adapter.declare()["calls"]) == set(adapter.keys())
    for catalogued in names.values():
        if catalogued is not None:
            canonical.check(catalogued)


@pytest.mark.parametrize("slug", FAMILY)
def test_it_forms_the_union_of_the_classes_itself(slug, shape) -> None:
    """Handed both classes it measures three maps, and the third is the union it made.

    That is the same derivation the artery/vein benchmark applies to every model, so a number
    measured here and a mask scored there describe the same vessels.
    """
    adapter = catalogue.load(slug)

    measured = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)

    names = adapter.declare()["names"]
    for structure in ("artery", "vein", "vessels"):
        answered = [
            own
            for own, catalogued in names.items()
            if catalogued and catalogued.endswith(f"/{structure}") and measured[own] is not None
        ]
        assert answered, f"{slug} answered nothing for {structure}"


@pytest.mark.parametrize("slug", FAMILY)
def test_a_class_it_was_not_given_comes_back_as_nothing(slug, shape) -> None:
    """Never substituting one class for the other, which would be invisible in the evidence."""
    adapter = catalogue.load(slug)

    measured = adapter.measure(shape.artery, None, shape.fov, shape.disc, shape.um_per_px)

    names = adapter.declare()["names"]
    veins = [
        own
        for own, catalogued in names.items()
        if (catalogued or own).endswith(("/vein", "_vein", "_veins"))
    ]
    assert veins, "the keys exist so a table has the same columns whatever it was given"
    assert all(measured[key] is None for key in veins)


def test_automorphalyzer_catalogues_zone_b_and_not_zone_c(shape) -> None:
    """*Our finding:* its zone B is the annulus PVBM measures over; its zone C is not.

    B is two to three disc radii, which is exactly PVBM's region, so a value from B is comparable
    with PVBM's. C is two to five radii and comparable with nothing, so it keeps its own name and
    is stored beside it rather than being dropped or silently equated.
    """
    adapter = catalogue.load("automorphalyzer")
    names = adapter.declare()["names"]

    assert names["CRAE_Knudtson@B_artery"] == "calibre/CRE-knudtson/artery/B"
    assert names["CRVE_Knudtson@B_vein"] == "calibre/CRE-knudtson/vein/B"
    assert "CRAE_Knudtson@C_artery" in adapter.keys(), "zone C is kept under its own name"
    assert adapter.declare()["zones"]["B"] == "2 to 3 disc radii"


def test_automorph_declares_the_size_it_really_measures_at() -> None:
    """*Our finding:* retipy resizes every input to 912², whatever it was handed.

    `Retina._open_image` calls `cv2.resize(..., (912, 912), INTER_CUBIC)` on every file it opens,
    so a pixel-valued width is in 912-pixels rather than the frame's, and a one-pixel skeleton does
    not survive the interpolation. An adapter may know that; it may not hide it.
    """
    declared = catalogue.load("automorph").declare()

    assert declared["working_size"] == 912
    assert declared["scale_written"] == 1.0, "so its width comes back in pixels, not microns"


def test_automorph_and_automorphclass_reach_no_equivalents() -> None:
    """A difference in scope, not a defect, and it is declared rather than left to be noticed.

    AutoMorph assembles its equivalents in a driver script rather than a callable, and
    AutoMorphClass's vessel features take no disc at all. Reproducing either would be measuring
    this repository's CRAE rather than theirs.
    """
    for slug in ("automorph", "automorphclass"):
        adapter = catalogue.load(slug)
        assert "calibre/CRE-knudtson" in adapter.declare()["absent"]
        assert "calibre/AVR-knudtson" in adapter.declare()["absent"]
        assert not [
            name for name in adapter.declare()["names"].values() if name and "/CRE-" in name
        ]


def test_the_family_answers_the_same_six_quantities(shape) -> None:
    """What makes a side-by-side possible: two of them are rewrites of the first.

    All three compute the same six measurements, so a difference between their numbers is a
    change somebody made rather than a different quantity. They do **not** all pool them the same
    way — see the test below — so what is shared is the measurement, which is the name without its
    statistic.
    """
    shared = None
    for slug in FAMILY:
        catalogued = {
            _measurement(name)
            for name in catalogue.load(slug).declare()["names"].values()
            if name
        }
        shared = catalogued if shared is None else shared & catalogued

    assert len(shared) >= 15, f"only {len(shared)} measurements in common across the family"
    for name in ("tortuosity/hart-tau1/artery", "density/box-counting/vessels"):
        assert name in shared


def _measurement(name: str) -> str:
    """A catalogued name with its statistic taken off — what was measured, not how it was pooled."""
    head, _, last = name.rpartition("/")
    return head if last in canonical.STATISTICS else name


def test_automorphclass_weights_by_length_where_its_two_siblings_take_a_mean() -> None:
    """*Our finding, from `_tortuosity_per_window`:* `len_weighted=True` is its default.

    AutoMorph and AutoMorphalyzer sum over vessels and divide by the vessel count; AutoMorphClass
    multiplies each vessel's value by its own curve length and divides by the total. Those are
    different statistics of one measurement, and part of why the three disagree on one picture —
    so the catalogued names they answer to differ in the statistic and nowhere else.
    """
    behind = {slug: catalogue.load(slug).declare()["names"] for slug in FAMILY}

    assert behind["automorph"]["distance_tortuosity_artery"] == (
        "tortuosity/hart-tau1/artery/mean"
    )
    assert behind["automorphalyzer"]["tortuosity_distance@whole_artery"] == (
        "tortuosity/hart-tau1/artery/mean"
    )
    assert behind["automorphclass"]["distance_tortuosity_artery"] == (
        "tortuosity/hart-tau1/artery/length-weighted"
    )


def test_a_crash_is_recorded_rather_than_raised() -> None:
    """One unmeasurable shape must not lose a run of hundreds."""
    for slug in FAMILY:
        adapter = catalogue.load(slug)
        empty = np.zeros((SIDE, SIDE), dtype=bool)

        measured = adapter.measure(
            empty, None, np.ones((SIDE, SIDE), dtype=bool), (10.0, 10.0, 5.0), 10.0
        )

        assert set(measured) <= set(adapter.keys())
