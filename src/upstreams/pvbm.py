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


def perimeter(segmentation):
    """The vessel border's length, which the new analysis class no longer exposes.

    `GeometricalAnalysis` had a `compute_perimeter`; `GeometryAnalysis` has none, so the helper
    both of them call is reached directly rather than reviving a deprecated class for one number.

    **The copy is not defensive tidiness — it is required.** `compute_perimeter_` walks the mask
    and sets each pixel it visits to zero, so it returns its input emptied. The deprecated wrapper
    hid that by calling it on `segmentation_skeleton.copy()`; calling the helper directly does not,
    and a caller who reuses the array afterwards gets zeros with no error. That cost an afternoon
    here: the geometry call that followed reported an area of 0 and the fractal analysis failed an
    assertion that its input contains a 1.

    :return: the perimeter, and the skeletonised **border** — a closed outline with no endpoints,
        which is not a centreline whatever its variable name suggests.
    """
    CODE.on_path()
    from PVBM.helpers.perimeter import compute_perimeter_

    return compute_perimeter_(segmentation.copy())


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
