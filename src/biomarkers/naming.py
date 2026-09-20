# ABOUTME: The table joining each implementation's own column names to canonical biomarker names.
# ABOUTME: A mapping here is a claim about what somebody's code computes, and it is often wrong.

from . import canonical

#: What each implementation calls each measurement, and which canonical name we believe it answers
#: to. `None` means the column maps to nothing catalogued — a finding rather than an omission.
#:
#: **A row is a claim.** It usually comes from reading the implementation's source, and the
#: synthetic benchmark is what tests it: a shape where two variants give different known values
#: separates them by measurement. `docs/BIOMARKER-NAMES.md` carries the same table for a reader,
#: with a mark saying whether each mapping has been measured or merely asserted.
NAMES: dict[str, dict[str, str | None]] = {
    "pvbm": {
        # Geometry, computed once per class.
        "area_artery": "vessel-area-and-length/area/artery",
        "area_vein": "vessel-area-and-length/area/vein",
        "length_artery": "vessel-area-and-length/skeleton-length/artery",
        "length_vein": "vessel-area-and-length/skeleton-length/vein",
        "median_tortuosity_artery": "tortuosity/hart-tau1/artery",
        "median_tortuosity_vein": "tortuosity/hart-tau1/vein",
        "median_branching_angle_artery": "bifurcation-angle/between-daughters/artery",
        "median_branching_angle_vein": "bifurcation-angle/between-daughters/vein",
        "endpoints_artery": "junction-counts/endpoints/artery",
        "endpoints_vein": "junction-counts/endpoints/vein",
        "intersections_artery": "junction-counts/junctions/artery",
        "intersections_vein": "junction-counts/junctions/vein",
        # PVBM's perimeter has no canonical name: nothing else in the catalogue computes the
        # boundary length of a vessel mask, and a name exists to make two numbers comparable.
        "perimeter_artery": None,
        "perimeter_vein": None,
        # The multifractal spectrum. PVBM's three dimensions are of the multifractal analysis, not
        # the plain box count, which is why they map to the multifractal names and not to
        # `fractal-dimension/box-counting`.
        "capacity_dimension_artery": "fractal-dimension/multifractal-d0/artery",
        "capacity_dimension_vein": "fractal-dimension/multifractal-d0/vein",
        "entropy_dimension_artery": "fractal-dimension/multifractal-d1/artery",
        "entropy_dimension_vein": "fractal-dimension/multifractal-d1/vein",
        "correlation_dimension_artery": "fractal-dimension/multifractal-d2/artery",
        "correlation_dimension_vein": "fractal-dimension/multifractal-d2/vein",
        "singularity_length_artery": None,
        "singularity_length_vein": None,
        # The equivalents, and the ratios this adapter forms from them because PVBM leaves that
        # division to its user.
        "crae_knudtson": "central-retinal-equivalents/knudtson/artery",
        "crve_knudtson": "central-retinal-equivalents/knudtson/vein",
        # *Our finding, 2026-09-20:* PVBM computes these from **pixel** widths, and Hubbard's
        # constants were fitted in microns. The canonical name says microns, so a value here is
        # not comparable with one from an implementation that converts first — which is a defect
        # of the implementation rather than of the mapping, and is why the benchmark reports the
        # number rather than correcting it.
        "crae_hubbard": "central-retinal-equivalents/hubbard/artery",
        "crve_hubbard": "central-retinal-equivalents/hubbard/vein",
        "avr_knudtson": "avr/knudtson/both",
        "avr_hubbard": "avr/hubbard/both",
    },
}


def canonical_for(implementation: str, key: str) -> str | None:
    """The canonical name an implementation's column is believed to answer to, or `None`."""
    mapped = NAMES.get(implementation, {}).get(key)
    return canonical.check(mapped) if mapped else None


def mapped(implementation: str) -> dict[str, str]:
    """Only the columns that map to something, which is what a comparison can use."""
    return {
        key: name
        for key, name in NAMES.get(implementation, {}).items()
        if name is not None
    }
