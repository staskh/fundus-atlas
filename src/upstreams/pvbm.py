# ABOUTME: PVBM, the Python Vasculature Biomarker toolbox: installed at the commit its catalogue
# ABOUTME: page describes, and reached one analysis class at a time.

from .utils import source

#: The commit `docs/projects/pvbm.md` describes, which is what a result here is attributable to.
#: PyPI carries a later release; the pin follows the page rather than the newest upload, per
#: `add-upstream` §2.
COMMIT = "5edb79a6eff5eceb94f1acc623b8d13e126bcfa7"

CODE = source.Installed("pvbm", commit=COMMIT)


def geometry() -> object:
    """Areas, lengths, tortuosity, junction counts and branching angles."""
    from PVBM.GeometricalAnalysis import GeometricalVBMs

    return GeometricalVBMs()


def fractals() -> object:
    """The multifractal dimensions and the singularity length.

    Its defaults are its own — ten box sizes, twenty-five rotations — and are left alone, because a
    benchmark of somebody's implementation measures the implementation as it ships.
    """
    from PVBM.FractalAnalysis import MultifractalVBMs

    return MultifractalVBMs()


def equivalents() -> object:
    """The central retinal equivalents, both Hubbard's and Knudtson's."""
    from PVBM.CentralRetinalAnalysis import CREVBMs

    return CREVBMs()


def provenance() -> dict[str, object]:
    return CODE.provenance()
