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
    return library.build("spokes-macula-centred", side=SIDE)


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


def test_automorphalyzer_catalogues_zones_b_and_c(shape) -> None:
    """*Our finding:* its two zones are the catalogue's two zones, so both are named.

    B is two to three disc radii, which is exactly PVBM's region. C is two to five radii, which is
    Cheung et al.'s Extended zone as `docs/biomarkers/regions-of-interest.md` §4 defines it — the
    annulus containing B, not a ring outside it. An equivalent stays tied to its own class: the
    CRAE column over the vein map is a different number and keeps its own name.
    """
    adapter = catalogue.load("automorphalyzer")
    names = adapter.declare()["names"]

    assert names["CRAE_Knudtson@B_artery"] == "calibre/CRE-knudtson/artery/B"
    assert names["CRVE_Knudtson@B_vein"] == "calibre/CRE-knudtson/vein/B"
    assert names["CRAE_Knudtson@C_artery"] == "calibre/CRE-knudtson/artery/C"
    assert names["CRVE_Knudtson@C_vein"] == "calibre/CRE-knudtson/vein/C"
    assert names["tortuosity_distance@C_artery"] == "tortuosity/hart-tau1/artery/C/mean"
    assert names["CRAE_Knudtson@C_vein"] is None, "a CRAE over the vein map is not a CRVE"
    assert adapter.declare()["zones"]["B"] == "2 to 3 disc radii"
    assert adapter.declare()["zones"]["C"] == "2 to 5 disc radii"


def test_automorph_measures_at_912_with_the_thresholds_its_drivers_read() -> None:
    """*Our finding, 2026-11-22:* AutoMorph's M2 stage hands M3 a binary 912 × 912 map, and every
    driver reads `resources/retipy.config` — 15 pixels per window and an R² of 0.96, not the
    defaults of `evaluate_window`. Both are what its own run does, so both are what this does."""
    declared = catalogue.load("automorph").declare()

    assert declared["working_size"] == 912
    assert declared["min_pixels_per_vessel"] == 15
    assert declared["r2_threshold"] == pytest.approx(0.96)


def test_automorphclass_reaches_no_equivalents() -> None:
    """A difference in scope, not a defect: its vessel features take no disc and compute none."""
    adapter = catalogue.load("automorphclass")
    assert "calibre/CRE-knudtson" in adapter.declare()["absent"]
    assert "calibre/AVR-knudtson" in adapter.declare()["absent"]
    assert not [name for name in adapter.declare()["names"].values() if name and "/CRE-" in name]


def test_automorph_answers_every_column_its_run_writes(shape) -> None:
    """*Our finding, 2026-11-22:* `run.sh` writes 72 numbers a picture — six for the disc and cup,
    18 over the whole picture, and 24 in each of zones B and C, the zone stage adding Hubbard's and
    Knudtson's equivalents and both ratios. Every one is a key, and on spokes from the disc the
    equivalents come back, each from its own class's map."""
    adapter = catalogue.load("automorph")
    names = adapter.declare()["names"]
    assert len(names) == 72
    assert names["CRAE_Hubbard_zone_b"] == "calibre/CRE-hubbard/artery/B"
    assert names["CRVE_Knudtson_zone_c"] == "calibre/CRE-knudtson/vein/C"
    assert names["AVR_Knudtson_zone_b"] == "calibre/AVR-knudtson/both/B"
    assert names["average_width_artery_zone_c"] == "calibre/width/artery/C/length-weighted"
    assert names["vessel_density_artery_zone_b"] is None, "its denominator is the whole frame"

    measured = adapter.measure(
        shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px, cup=shape.cup
    )

    for own in (
        "CRAE_Hubbard_zone_b",
        "CRVE_Hubbard_zone_b",
        "CRAE_Knudtson_zone_b",
        "CRVE_Knudtson_zone_b",
        "AVR_Knudtson_zone_b",
    ):
        assert measured[own] is not None, own
    assert measured["AVR_Knudtson_zone_b"] == pytest.approx(
        measured["CRAE_Knudtson_zone_b"] / measured["CRVE_Knudtson_zone_b"]
    )


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
            _measurement(name) for name in catalogue.load(slug).declare()["names"].values() if name
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

    assert behind["automorph"]["distance_tortuosity_artery"] == ("tortuosity/hart-tau1/artery/mean")
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


@pytest.mark.parametrize(
    ("slug", "vertical", "horizontal"),
    [
        ("automorphclass", "cdr_vertical", "cdr_horizontal"),
        ("automorphalyzer", "CDR_vertical", "CDR_horizontal"),
        ("automorph", "CDR_vertical", "CDR_horizontal"),
    ],
)
def test_handed_a_cup_it_answers_the_cup_to_disc_ratios(slug, vertical, horizontal, shape) -> None:
    """*Our finding, 2026-11-22:* both descendants read a ratio off the bounding boxes of a disc
    mask and a cup mask, so handed the synthetic cup they answer close to its drawn 0.55 and 0.40.
    Close rather than exact: an extent is the last lit index minus the first, a pixel short."""
    adapter = catalogue.load(slug)
    names = adapter.declare()["names"]
    assert names[vertical] == "landmarks/CDR-vertical"
    assert names[horizontal] == "landmarks/CDR-horizontal"

    measured = adapter.measure(
        shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px, cup=shape.cup
    )

    assert measured[vertical] == pytest.approx(0.55, abs=0.02)
    assert measured[horizontal] == pytest.approx(0.40, abs=0.02)


@pytest.mark.parametrize("slug", FAMILY)
def test_handed_no_cup_it_answers_no_ratio(slug, shape) -> None:
    adapter = catalogue.load(slug)
    measured = adapter.measure(shape.artery, shape.vein, shape.fov, shape.disc, shape.um_per_px)
    ratios = [own for own, name in adapter.declare()["names"].items() if name and "CDR" in name]

    assert all(measured[own] is None for own in ratios)


@pytest.mark.parametrize(
    ("returned", "word"), [(True, "macula"), (False, "disc"), (-1, "unknown"), (None, "unknown")]
)
def test_automorphalyzer_says_its_centring_in_the_catalogue_s_words(returned, word) -> None:
    """*Our finding, 2026-11-22:* `macular_centred` is three-valued upstream — True, False, or −1
    where `get_disc_metrics` fell over — which is the catalogue's macula, disc and unknown. The −1
    is checked before the yes or no, because True equals 1 and −1 is truthy."""
    from biomarkers import automorphalyzer

    assert automorphalyzer._centring(returned) == word


@pytest.mark.parametrize(
    ("name", "centring"),
    [("spokes-macula-centred", "macula"), ("spokes-disc-centred", "disc")],
)
def test_automorphalyzer_answers_the_photograph_s_centring(name, centring) -> None:
    adapter = catalogue.load("automorphalyzer")
    assert adapter.declare()["names"]["macular_centred"] == "landmarks/centring"
    drawn = library.build(name, side=SIDE)

    measured = adapter.measure(
        drawn.artery, drawn.vein, drawn.fov, drawn.disc, drawn.um_per_px, cup=drawn.cup
    )

    assert measured["macular_centred"] == centring
    assert library.truths(name)["landmarks/centring"].value == centring
