# ABOUTME: The fixed vocabulary of biomarker names: every measurement this repository can compare,
# ABOUTME: named once, so two implementations' columns can be read against each other or not at all.

#: What a measurement was taken over. A biomarker computed on arteries is not the same measurement
#: as the one computed on veins, and a table that merges them is comparing two things.
STRUCTURES = ("artery", "vein", "vessels", "both")

#: Every canonical name, as `biomarker/variant/structure`.
#:
#: - **biomarker** is a page in `docs/biomarkers/`;
#: - **variant** is one of that page's numbered variants — the definition, not the name, because
#:   "tortuosity" names at least three incompatible formulas;
#: - **structure** is what it was measured over. `both` is only for a measurement that is
#:   inherently a ratio of the two classes, which is the arteriovenous ratio and nothing else.
#:
#: A name here is a claim that two numbers under it are comparable. Adding one is a decision, which
#: is why they are listed rather than assembled from whatever an implementation happened to return.
NAMES: dict[str, str] = {
    # Tortuosity — Hart's seven, then the ones that are not Hart's.
    "tortuosity/hart-tau1/{s}": "arc length over chord length; 1 for a straight vessel",
    "tortuosity/hart-tau2/{s}": "total curvature, ∫κ ds",
    "tortuosity/hart-tau3/{s}": "total squared curvature, ∫κ² ds",
    "tortuosity/hart-tau4/{s}": "mean curvature, ∫κ ds / s — compositional, and implemented here by nobody",
    "tortuosity/hart-tau5/{s}": "mean squared curvature, ∫κ² ds / s — likewise",
    "tortuosity/hart-tau6/{s}": "total curvature over chord, ∫κ ds / chord",
    "tortuosity/hart-tau7/{s}": "total squared curvature over chord, ∫κ² ds / chord",
    "tortuosity/grisan-density/{s}": "Grisan's tortuosity density over constant-sign subsegments",
    "tortuosity/arc-chord-times-inflections/{s}": "τ1 multiplied by the number of curvature sign changes",
    "tortuosity/spline-mean-curvature/{s}": "mean curvature sampled along a fitted spline",
    "tortuosity/inflection-count/{s}": "how many times the curvature changes sign",
    # Calibre, and what is built from it.
    "vessel-calibre/mean-width/{s}": "mean vessel width, in pixels unless a scale was supplied",
    "vessel-calibre/median-width/{s}": "median vessel width",
    "central-retinal-equivalents/knudtson/{s}": (
        "the Knudtson equivalent over the disc-centred ring — CRAE on arteries, CRVE on veins"
    ),
    "central-retinal-equivalents/hubbard/{s}": "the Hubbard equivalent over the same ring",
    "avr/knudtson/both": "arteriolar over venular equivalent, both Knudtson",
    "avr/hubbard/both": "arteriolar over venular equivalent, both Hubbard",
    "avr/ratio-of-calibres/both": "mean artery width over mean vein width, with no ring and no equivalent",
    # How much retina the vessels cover, and how complicated they are.
    "vascular-density/over-field-of-view/{s}": "vessel area as a fraction of the field of view",
    "vascular-density/over-image/{s}": "vessel area as a fraction of the whole frame, lit or not",
    "fractal-dimension/box-counting/{s}": "box-counting dimension",
    "fractal-dimension/multifractal-d0/{s}": "capacity dimension of the multifractal spectrum",
    "fractal-dimension/multifractal-d1/{s}": "information dimension",
    "fractal-dimension/multifractal-d2/{s}": "correlation dimension",
    "vessel-area-and-length/area/{s}": "total vessel area, in pixels squared",
    "vessel-area-and-length/skeleton-length/{s}": "total centreline length, in pixels",
    "sparsity/mean-distance/{s}": "mean distance from retina to the nearest vessel",
    "sparsity/max-distance/{s}": "the furthest any retina is from a vessel",
    # Where the vessels branch, and how the network is put together.
    "junction-counts/junctions/{s}": "how many places three or more branches meet",
    "junction-counts/endpoints/{s}": "how many free ends the network has",
    "junction-counts/components/{s}": "how many separate pieces the network is in",
    "bifurcation-angle/between-daughters/{s}": "the angle between the two daughter vessels, in degrees",
}


def names() -> dict[str, str]:
    """Every canonical name, expanded over the structures each one applies to."""
    expanded: dict[str, str] = {}
    for template, meaning in NAMES.items():
        if "{s}" not in template:
            expanded[template] = meaning
            continue
        for structure in ("artery", "vein", "vessels"):
            expanded[template.format(s=structure)] = meaning
    return expanded


def check(name: str) -> str:
    """The name, or an error saying why it is not one.

    Every theoretical value and every mapping from an implementation's own column goes through
    here, so a typo is a failure rather than a row nothing will ever match.
    """
    known = names()
    if name not in known:
        raise LookupError(
            f"{name!r} is not a canonical biomarker name. They are listed in "
            f"src/biomarkers/canonical.py and documented in docs/BIOMARKER-NAMES.md"
        )
    return name
