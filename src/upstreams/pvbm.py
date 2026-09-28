# ABOUTME: PVBM, the Python Vasculature Biomarker toolbox: cloned at the commit its catalogue page
# ABOUTME: describes, and reached one analysis class at a time.

from .utils import source

#: The commit `docs/projects/pvbm.md` describes, which is what a result here is attributable to.
#: PyPI carries a later release; the pin follows the page rather than the newest upload, per
#: `add-upstream` §2.
COMMIT = "5edb79a6eff5eceb94f1acc623b8d13e126bcfa7"

#: **Cloned rather than installed**, although PVBM is pip-installable and was installed until now.
#:
#: Two reasons, and the second is the one that forced it. A clone is the only way to read the code a
#: result came from without going to look at somebody's site-packages, which matters most for the
#: upstream whose deprecations this atlas has to track. And OCULAR's measuring class imports PVBM's
#: helpers *at runtime* — it is a modified copy of PVBM's own module — so the two have to agree
#: about which PVBM that is. While PVBM was a pip dependency the answer was implicit and
#: unrecorded; now both reach the same pinned tree, and `src/upstreams/ocular.py` says so.
CODE = source.Checkout("pvbm", "https://github.com/aim-lab/PVBM", COMMIT)


def geometry() -> object:
    """Areas, lengths, tortuosity, junction counts and branching angles.

    **`GeometryAnalysis`, not `GeometricalAnalysis`.** The two ship side by side at this commit and
    both export a class called `GeometricalVBMs`, which is the trap: the one in
    `GeometricalAnalysis` warns on construction that it is deprecated and goes in version 3.0. The
    one here is the replacement, and it is not a rename — it takes the optic disc, walks the tree
    from the vessels that leave it, and returns one list of biomarkers rather than five methods'
    worth. `docs/projects/pvbm.md` §9 records what that changes.
    """
    CODE.on_path()
    from PVBM.GeometryAnalysis import GeometricalVBMs

    return GeometricalVBMs()


#: **No perimeter is published here.** `GeometricalAnalysis` had a `compute_perimeter`;
#: `GeometryAnalysis`, which this atlas measures with, has no equivalent. Offering one anyway meant
#: transcribing four lines out of the retired class and calling `PVBM.helpers.perimeter`, which
#: neither class exposes as an interface — so a benchmark reporting it would be reporting a number
#: this version of PVBM does not produce. The defect that transcription uncovered is still recorded
#: on `docs/projects/pvbm.md` §8, because it is PVBM's defect and outlives our use of it.

def fractals() -> object:
    """The multifractal dimensions and the singularity length.

    Its defaults are its own — ten box sizes, twenty-five rotations — and are left alone, because a
    benchmark of somebody's implementation measures the implementation as it ships.
    """
    CODE.on_path()
    from PVBM.FractalAnalysis import MultifractalVBMs

    return MultifractalVBMs()


def equivalents() -> object:
    """The central retinal equivalents, both Hubbard's and Knudtson's."""
    CODE.on_path()
    from PVBM.CentralRetinalAnalysis import CREVBMs

    return CREVBMs()


def provenance() -> dict[str, object]:
    return CODE.provenance()
