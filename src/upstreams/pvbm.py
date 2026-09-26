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

    `GeometricalAnalysis.compute_perimeter` did this in four lines and `GeometryAnalysis` has no
    equivalent, so those four are **transcribed here** rather than a deprecated class being revived
    for one number. What they do is worth stating, because the helper's name does not: an eight-
    neighbour Laplacian marks the mask's border, the border is skeletonised, and
    `compute_perimeter_` measures *that skeleton's* length. It is a length-of-skeleton routine, not
    a perimeter routine — handing it the mask itself returns a number an order of magnitude too
    large, which is what happened here before this was read properly.

    **The copy is required, not defensive.** `compute_perimeter_` walks what it is given and zeroes
    every pixel it visits, so it returns its input erased. The deprecated wrapper copied for the
    same reason.

    A test pins this against the values the deprecated class produced, because a transcription that
    drifts from its original is worse than no transcription at all.

    :return: the perimeter, and the skeletonised **border** — a closed outline with no endpoints,
        which is not a centreline whatever its variable name suggests.
    """
    import numpy as np
    from scipy.signal import convolve2d
    from skimage.morphology import skeletonize

    CODE.on_path()
    from PVBM.helpers.perimeter import compute_perimeter_

    edges = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    border = convolve2d(segmentation, edges, mode="same") > 0
    outline = skeletonize(np.ascontiguousarray(border))
    length, _ = compute_perimeter_(outline.copy())
    return length, outline


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
