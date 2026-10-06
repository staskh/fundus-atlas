# ABOUTME: The fixed vocabulary of biomarker names: every measurement this repository can compare,
# ABOUTME: named once, so two implementations' columns can be read against each other or not at all.

from dataclasses import dataclass

#: What a measurement was taken over. `both` is only for a quantity that is inherently a ratio of
#: the two classes, which is the arteriovenous ratio and nothing else.
STRUCTURES = ("artery", "vein", "vessels", "both")

#: The regions a name may be qualified by, from `docs/biomarkers/regions-of-interest.md`.
#:
#: `A` and `C` are **reserved, not defined**: their bounds have to be read out of the ARIC papers
#: and written on that page before a name may use them, and stating a radius from memory is the
#: error the page exists to prevent.
REGIONS = ("fov", "B")

#: How per-segment or per-vessel values were pooled.
STATISTICS = ("mean", "median", "max", "min", "std", "length-weighted")

#: The two optional name parts sit in the same position, so a four-part name is ambiguous in shape
#: and only the token tells them apart. Disjointness is what makes that safe, and it is checked here
#: rather than assumed: a region named `mean` would make every such name ambiguous, silently.
_COLLISION = set(REGIONS) & set(STATISTICS)
if _COLLISION:
    raise RuntimeError(f"a region and a statistic share the name {sorted(_COLLISION)}")


@dataclass(frozen=True)
class Family:
    """What a family's names look like, where it departs from the global rules.

    :param structures: what it may be measured over; empty where the family measures no vessel.
    :param region: the default region, or ``None`` where one is **required** rather than defaulted.
    :param regional: whether a region may be given at all.
    """

    means: str
    structures: tuple[str, ...] = ("artery", "vein", "vessels")
    region: str | None = "fov"
    regional: bool = True
    statistic: str = "median"


#: The five families. Adding a sixth is a decision, not a side effect of an implementation
#: returning something new — see the `document-biomarker` skill.
FAMILIES: dict[str, Family] = {
    "calibre": Family("how wide the vessels are, and everything built from widths"),
    "tortuosity": Family("the shape of a vessel's path"),
    "density": Family("how much vasculature there is, and how it is spread"),
    "topology": Family("where the network branches and how it connects"),
    # Measures no vessel, so it carries no structure and takes no region: these are defined
    # relative to landmarks rather than over an area.
    "landmarks": Family(
        "the optic nerve head and the fovea", structures=(), region=None, regional=False
    ),
}


@dataclass(frozen=True)
class Biomarker:
    """One definition, under one family.

    :param unit: **never pixels.** ``1`` is dimensionless, and is a unit rather than a blank.
    :param structures: overrides the family's, for a name that applies to fewer.
    :param region: ``None`` where this biomarker *requires* a region although its family defaults.
    :param statistics: which poolings apply; empty where the quantity is one number per image.
    :param whole_vessel: whether a ``vessel-`` form exists — the same quantity over whole
        root-to-tip vessels rather than over segments between intersection points.
    """

    means: str
    unit: str
    structures: tuple[str, ...] | None = None
    region: str | None = "inherit"
    statistics: tuple[str, ...] = ()
    whole_vessel: bool = False
    paper: str = ""


_POOLED = ("mean", "median", "std")

#: Pooling for a quantity measured **along** a vessel, where a longer segment is better evidence
#: than a shorter one and several implementations say so: VascX reports a length-weighted diameter
#: and a length-weighted tortuosity, PVBM and OCULAR a length-weighted tortuosity beside a median.
#: It is a different number from the plain mean, not a refinement of it, so it is a statistic of
#: its own rather than something an implementation may quietly substitute.
_ALONG = (*_POOLED, "length-weighted")

#: Every canonical biomarker, as `family/biomarker`. The structure, region and statistic are
#: appended at use, and the short form omits whatever is at its default.
NAMES: dict[str, Biomarker] = {
    # -- calibre ------------------------------------------------------------------------------
    "calibre/width": Biomarker(
        "the width of a vessel, measured along it", "µm", statistics=_ALONG, paper="bankhead-2012"
    ),
    # The equivalents are *defined* over a ring: there is no field-of-view-wide CRAE, so a name
    # without a region is an error rather than a default.
    "calibre/CRE-knudtson": Biomarker(
        "Knudtson's equivalent — CRAE on arteries, CRVE on veins",
        "µm",
        structures=("artery", "vein"),
        region=None,
        paper="knudtson-2003",
    ),
    "calibre/CRE-hubbard": Biomarker(
        "Hubbard's equivalent over the same ring",
        "µm",
        structures=("artery", "vein"),
        region=None,
        paper="hubbard-1999",
    ),
    "calibre/AVR-knudtson": Biomarker(
        "arteriolar over venular equivalent, both Knudtson",
        "1",
        structures=("both",),
        region=None,
        paper="knudtson-2003",
    ),
    "calibre/AVR-hubbard": Biomarker(
        "the same, both Hubbard", "1", structures=("both",), region=None, paper="hubbard-1999"
    ),
    "calibre/AVR-ratio": Biomarker(
        "mean artery width over mean vein width, no ring and no equivalent",
        "1",
        structures=("both",),
    ),
    # -- tortuosity ---------------------------------------------------------------------------
    "tortuosity/hart-tau1": Biomarker(
        "arc length over chord length; 1 for a straight vessel",
        "1",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau2": Biomarker(
        "total curvature, ∫κ ds — the total turning angle",
        "1",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau3": Biomarker(
        "total squared curvature, ∫κ² ds",
        "1/µm",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau4": Biomarker(
        "mean curvature, ∫κ ds / s — compositional",
        "1/µm",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau5": Biomarker(
        "mean squared curvature, ∫κ² ds / s — compositional",
        "1/µm²",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau6": Biomarker(
        "total curvature over chord",
        "1/µm",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/hart-tau7": Biomarker(
        "total squared curvature over chord",
        "1/µm²",
        statistics=_ALONG,
        whole_vessel=True,
        paper="hart-1999",
    ),
    "tortuosity/grisan-density": Biomarker(
        # **Inverse length, not dimensionless.** The sum of arc-over-chord excesses is a pure
        # number and it is then divided by the curve's own arc length, so the measure carries
        # `1/length` — which is why it must be reported per micron rather than per pixel.
        "Grisan's density over constant-sign subsegments",
        "1/µm",
        statistics=_ALONG,
        paper="grisan-2008",
    ),
    "tortuosity/inflection-count": Biomarker("how many times the curvature changes sign", "1"),
    "tortuosity/arc-chord-times-inflections": Biomarker(
        "τ1 multiplied by the inflection count", "1", statistics=_ALONG
    ),
    # The mean is a *statistic*, not part of the name — which is why this is not
    # `spline-mean-curvature`, as it was until 2026-09-30.
    "tortuosity/spline-curvature": Biomarker(
        "curvature sampled along a fitted spline", "1/µm", statistics=_ALONG
    ),
    # -- density ------------------------------------------------------------------------------
    "density/area": Biomarker("total vessel area", "µm²", paper="martinez-perez-2000"),
    "density/skeleton-length": Biomarker(
        "total centreline length", "µm", paper="martinez-perez-2000"
    ),
    "density/over-fov": Biomarker("vessel area as a fraction of the field of view", "1"),
    "density/over-image": Biomarker(
        "the same over the whole frame, lit or not — it names its own denominator", "1"
    ),
    "density/sparsity": Biomarker(
        "distance from retina to the nearest vessel",
        "µm",
        statistics=("mean", "max"),
        paper="vargas-2026",
    ),
    "density/box-counting": Biomarker("box-counting dimension", "1"),
    "density/multifractal-d0": Biomarker("capacity dimension", "1", paper="stosic-2006"),
    "density/multifractal-d1": Biomarker("information dimension", "1", paper="stosic-2006"),
    "density/multifractal-d2": Biomarker("correlation dimension", "1", paper="stosic-2006"),
    # -- topology -----------------------------------------------------------------------------
    "topology/junctions": Biomarker(
        "how many places three or more branches meet", "1", paper="martinez-perez-2000"
    ),
    "topology/endpoints": Biomarker(
        "how many free ends the network has", "1", paper="martinez-perez-2000"
    ),
    "topology/components": Biomarker("how many separate pieces the network is in", "1"),
    "topology/branching-angle": Biomarker(
        "the angle between the two daughter vessels at a bifurcation",
        "degrees",
        structures=("artery", "vein"),
        statistics=_POOLED,
        paper="martinez-perez-2000",
    ),
    "topology/temporal-angle": Biomarker(
        "the angle between the superior and inferior temporal arcades",
        "degrees",
        structures=("artery", "vein"),
        statistics=_POOLED,
        paper="vargas-2026",
    ),
    # -- landmarks ----------------------------------------------------------------------------
    "landmarks/CDR-vertical": Biomarker("the cup's vertical diameter over the disc's", "1"),
    "landmarks/CDR-area": Biomarker("the cup's area over the disc's", "1"),
    "landmarks/disc-fovea-distance": Biomarker(
        "the straight-line distance from the disc centre to the fovea", "µm", paper="vargas-2026"
    ),
}


def structures(stem: str) -> tuple[str, ...]:
    """The structures a biomarker is measured over, its family's default unless it overrides one.

    Empty where the biomarker has none — the optic disc is neither an artery nor a vein.
    """
    return _structures(stem)


def _structures(stem: str) -> tuple[str, ...]:
    entry, family = NAMES[stem], FAMILIES[stem.split("/")[0]]
    return entry.structures if entry.structures is not None else family.structures


def _region(stem: str) -> str | None:
    entry, family = NAMES[stem], FAMILIES[stem.split("/")[0]]
    return family.region if entry.region == "inherit" else entry.region


def names() -> dict[str, str]:
    """Every canonical name in its **short form**, expanded over the structures each applies to.

    The short form omits a region and a statistic that are at their default, so
    `tortuosity/hart-tau1/artery` is the median τ1 over the whole field of view. A biomarker whose
    family *requires* a region appears once per region instead, because it has no short form.

    The `vessel-` whole-vessel forms are included: they are separate biomarkers measured over
    root-to-tip paths rather than over segments, and pool a different population.
    """
    out: dict[str, str] = {}
    for stem, entry in NAMES.items():
        family, biomarker = stem.split("/")
        stems = [stem] + ([f"{family}/vessel-{biomarker}"] if entry.whole_vessel else [])
        for one in stems:
            structures = _structures(stem) or ("",)
            # A biomarker whose family *requires* a region has no short form, so it is listed
            # once per region instead. One that merely admits a region is listed in its short
            # form — which means the whole field of view — and again for each named region, which
            # are different measurements rather than spellings of one. A family that takes no
            # region at all is listed once, plainly.
            if not FAMILIES[family].regional:
                regions: list[str | None] = [None]
            elif _region(stem) is None:
                regions = list(REGIONS[1:])
            else:
                regions = [None, *REGIONS[1:]]
            # A biomarker that can be pooled is enumerated **once per statistic**, because those
            # are different measurements rather than aliases of one. A biomarker that cannot is
            # enumerated once, in its short form.
            poolings = list(entry.statistics) or [None]
            for structure in structures:
                for region in regions:
                    for statistic in poolings:
                        parts = (
                            [one]
                            + ([structure] if structure else [])
                            + ([region] if region else [])
                            + ([statistic] if statistic else [])
                        )
                        out["/".join(parts)] = entry.means
    return out


def unit(name: str) -> str:
    """The unit a canonical name is reported in. Never pixels."""
    return entry(check(name)).unit


#: How many powers of length each unit carries. A value measured on a pixel grid becomes the value
#: its canonical name declares by multiplying by `um_per_px` this many times — negative powers
#: dividing, and a dimensionless biomarker untouched.
_LENGTH_POWER = {"1": 0, "degrees": 0, "µm": 1, "µm²": 2, "1/µm": -1, "1/µm²": -2}


def length_power(name: str) -> int:
    """The powers of length a canonical name carries, so a pixel measurement can be converted.

    This is the whole of the rule that keeps a number comparable between a photograph at 1024 and
    the same eye at 2048: `value_in_pixels × um_per_px ** length_power(name)`. It lives beside the
    units rather than beside either caller, because a biomarker converted one way by the ground
    truth and another way by an implementation's adapter would compare two different quantities.
    """
    return _LENGTH_POWER[unit(name)]


def from_pixels(name: str, value: float, um_per_px: float) -> float:
    """A number an implementation measured on a pixel grid, in the unit its name declares.

    Every adapter in this repository reports what its implementation returned, in pixels, because
    that is what the implementation's own documentation describes and what a reader checking
    against it will look for. This is where such a number becomes comparable with one measured on
    a different grid, and with the shapes' ground truth — which arrives here already converted,
    by the same rule.
    """
    power = length_power(name)
    return value * um_per_px**power if power else value


def entry(name: str) -> Biomarker:
    """The vocabulary's record behind a name, whether or not it is a whole-vessel form.

    `NAMES` is keyed by the segment-wise stem, and the whole-vessel form is generated from it, so
    a caller holding `tortuosity/vessel-hart-tau1` cannot look itself up: the two share a record
    by construction, and this is where that is said once.
    """
    return NAMES[_stem_of(name)]


def known(name: str) -> bool:
    """Whether the vocabulary has a record behind this name."""
    try:
        return bool(entry(name))
    except (LookupError, ValueError):
        return False


def _stem_of(name: str) -> str:
    family, biomarker, *_ = name.split("/")
    return f"{family}/{biomarker.removeprefix('vessel-')}"


def check(name: str) -> str:
    """The name, or an error saying why it is not one.

    Every theoretical value and every mapping from an implementation's own column goes through
    here, so a typo is a failure rather than a row nothing will ever match.
    """
    parts = name.split("/")
    if len(parts) < 2:
        raise LookupError(f"{name!r} has no family and biomarker")
    stem = _stem_of(name)
    if stem not in NAMES:
        raise LookupError(
            f"{name!r} is not a canonical biomarker name: no {stem!r} in "
            f"src/biomarkers/canonical.py, documented in docs/BIOMARKER-NAMES.md"
        )
    entry, rest = NAMES[stem], parts[2:]
    allowed = _structures(stem)
    if allowed:
        if not rest or rest[0] not in allowed:
            raise LookupError(f"{name!r} needs a structure, one of {allowed}")
        rest = rest[1:]
    region = _region(stem)
    for token in rest:
        if token in REGIONS:
            if not FAMILIES[parts[0]].regional:
                raise LookupError(f"{name!r} names a region, and {parts[0]} takes none")
            region = token
        elif token in STATISTICS:
            if token not in entry.statistics:
                raise LookupError(f"{name!r} pools by {token!r}, which it does not support")
        else:
            raise LookupError(f"{name!r} carries {token!r}, which is no region and no statistic")
    # `None` means two different things and only one is an error: a family that takes no region at
    # all is fine without one, and a biomarker that *requires* one is not.
    if region is None and FAMILIES[parts[0]].regional:
        raise LookupError(f"{name!r} requires a region — it has no whole-field form")
    return name
