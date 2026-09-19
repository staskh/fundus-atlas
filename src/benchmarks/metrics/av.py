# ABOUTME: What is measured about an artery/vein segmentation: how much of it overlaps the expert's
# ABOUTME: and how much of the network it reproduces. Pure functions over masks — no model, no store.

import numpy as np
from skimage.morphology import skeletonize

#: The three maps this benchmark scores, in the order every table lists them. `vessels` is the union
#: of the other two rather than a separate prediction: a model that finds arteries and veins has
#: found the vessels, and scoring that union says whether its mistakes are about *which* vessel a
#: pixel belongs to or about whether there is a vessel there at all.
STRUCTURES = ("artery", "vein", "vessels")


def dice(said: np.ndarray, truth: np.ndarray) -> float | None:
    """How much two segmentations overlap, on the usual scale of 0 to 1.

    `None` where neither holds anything: a photograph with no vein annotated, scored against a model
    that drew none, has nothing to be right or wrong about — which is not the same as being wrong.
    """
    total = int(said.sum()) + int(truth.sum())
    if total == 0:
        return None
    return 2 * float((said & truth).sum()) / total


def cldice(said: np.ndarray, truth: np.ndarray) -> float | None:
    """How much of each network the other one covers, along their centrelines.

    Overlap alone cannot tell a vessel traced too thick from one traced in two pieces: the first is
    wrong about width and right about the network, the second the reverse, and a biomarker computed
    from either is wrong in a different way. clDice asks a connectedness question instead — what
    share of the model's centreline falls inside the expert's vessels, and what share of the
    expert's centreline falls inside the model's — and combines the two as a harmonic mean.

    From Shit et al., *clDice — a Novel Topology-Preserving Loss Function for Tubular Structure
    Segmentation*, CVPR 2021.
    """
    if int(said.sum()) + int(truth.sum()) == 0:
        return None
    precision = _covered(_centreline(said), truth)
    sensitivity = _covered(_centreline(truth), said)
    if precision is None or sensitivity is None:
        return 0.0
    if precision + sensitivity == 0:
        return 0.0
    return 2 * precision * sensitivity / (precision + sensitivity)


def _centreline(mask: np.ndarray) -> np.ndarray:
    """One-pixel-wide skeleton of a segmentation, which is what connectedness is measured on."""
    return skeletonize(np.asarray(mask, dtype=bool))


def _covered(skeleton: np.ndarray, mask: np.ndarray) -> float | None:
    """What share of a centreline lies inside a segmentation. `None` where there is no centreline."""
    total = int(skeleton.sum())
    if total == 0:
        return None
    return float((skeleton & mask).sum()) / total


def vessels_of(masks: dict[str, np.ndarray]) -> np.ndarray:
    """Arteries and veins together, which is what a vessel score is measured on.

    Derived rather than predicted: a model in this benchmark is asked for the two classes, and the
    union is what they say about where the vessels are. Where a crossing is in both, it is in the
    union once.
    """
    found = [mask for name, mask in masks.items() if name in ("artery", "vein")]
    if not found:
        return np.zeros((1, 1), dtype=bool)
    union = np.zeros_like(found[0], dtype=bool)
    for mask in found:
        union |= np.asarray(mask, dtype=bool)
    return union


def measure(said: dict[str, np.ndarray], truth: dict[str, np.ndarray]) -> dict[str, float | None]:
    """Every measurement of one photograph, against one reader's annotation.

    Overlap and connectedness, for the arteries, the veins, and the vessels they make together.
    Anything else a study wants — a calibre, a ratio, a tortuosity — is a biomarker rather than a
    segmentation and is measured in its own benchmark, from the masks this one keeps.
    """
    said = {**said, "vessels": vessels_of(said)}
    truth = {**truth, "vessels": vessels_of(truth)}
    found: dict[str, float | None] = {}
    for structure in STRUCTURES:
        mine, theirs = said.get(structure), truth.get(structure)
        if mine is None or theirs is None:
            continue
        mine = np.asarray(mine, dtype=bool)
        theirs = np.asarray(theirs, dtype=bool)
        found[f"{structure}_dice"] = dice(mine, theirs)
        found[f"{structure}_cldice"] = cldice(mine, theirs)
    return found
