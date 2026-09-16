# ABOUTME: What is measured about an optic disc and cup: overlap, where the boundary sits, and the
# ABOUTME: ratio a referral rests on. Pure functions over masks — no model, no store, no file.

import numpy as np
from skimage.draw import polygon as _polygon

#: The two structures, in the order every table lists them.
STRUCTURES = ("disc", "cup")


def dice(said: np.ndarray, truth: np.ndarray) -> float | None:
    """How much two outlines overlap, on the usual scale of 0 to 1.

    `None` where neither outline exists: there is nothing to overlap, which is not the same as
    overlapping not at all.
    """
    total = int(said.sum()) + int(truth.sum())
    if total == 0:
        return None
    return 2 * float((said & truth).sum()) / total


def centre(mask: np.ndarray) -> tuple[float, float] | None:
    """Where a shape sits, as the centre of its own area."""
    ys, xs = np.nonzero(mask)
    if not xs.size:
        return None
    return float(xs.mean()), float(ys.mean())


def centre_offset(said: np.ndarray, truth: np.ndarray) -> float | None:
    """How far a prediction's centre is from the expert's, in pixels."""
    one, other = centre(said), centre(truth)
    if one is None or other is None:
        return None
    return float(np.hypot(one[0] - other[0], one[1] - other[1]))


def extent(mask: np.ndarray) -> tuple[float, float] | None:
    """How wide and how tall a shape is, in pixels."""
    ys, xs = np.nonzero(mask)
    if not xs.size:
        return None
    return float(xs.max() - xs.min() + 1), float(ys.max() - ys.min() + 1)


def equivalent_radius(mask: np.ndarray) -> float | None:
    """The radius of a circle of the same area, which is what most clinical software reports."""
    area = float(mask.sum())
    return float(np.sqrt(area / np.pi)) if area else None


def vertical_ratio(cup: np.ndarray, optic_disc: np.ndarray) -> float | None:
    """Cup height over disc height — the cup-to-disc ratio a referral decision rests on."""
    inner, outer = extent(cup), extent(optic_disc)
    if inner is None or outer is None or outer[1] == 0:
        return None
    return inner[1] / outer[1]


def area_ratio(cup: np.ndarray, optic_disc: np.ndarray) -> float | None:
    """Cup area over disc area, which some projects report instead."""
    outer = float(optic_disc.sum())
    return float(cup.sum()) / outer if outer else None


def outside_its_disc(cup: np.ndarray, optic_disc: np.ndarray) -> float | None:
    """The share of a predicted cup that falls outside its own disc.

    Measured rather than repaired: a cup that is not inside its disc is a fact about the model, and
    silently intersecting the two would hide it while improving every other number.
    """
    area = float(cup.sum())
    return float((cup & ~optic_disc).sum()) / area if area else None


def mask_of(nodes: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """The region a polygon encloses, in a frame of the given shape."""
    mask = np.zeros(shape, dtype=bool)
    if nodes is None or len(nodes) < 3:
        return mask
    rows, columns = _polygon(nodes[:, 1], nodes[:, 0], shape)
    mask[rows, columns] = True
    return mask


def measure(said: dict[str, np.ndarray], truth: dict[str, np.ndarray]) -> dict[str, float | None]:
    """Every measurement of one photograph, for one reader, in one dictionary.

    Signed where it can be: a model that calls every cup too large is a different problem from one
    that scatters, and an absolute error hides which of the two you have.
    """
    found: dict[str, float | None] = {}
    #: The expert's own disc is the ruler every offset is also given in, because a ten-pixel error
    #: is a different error on a 2,576-pixel photograph and on a 1,444-pixel one.
    diameter = equivalent_radius(truth["disc"]) * 2 if truth.get("disc") is not None else None
    for structure in STRUCTURES:
        mine, theirs = said.get(structure), truth.get(structure)
        if mine is None or theirs is None:
            continue
        found[f"{structure}_dice"] = dice(mine, theirs)
        offset = centre_offset(mine, theirs)
        found[f"{structure}_centre_offset"] = offset
        found[f"{structure}_centre_offset_diameters"] = (
            offset / diameter if offset is not None and diameter else None
        )
        for name, measured in (("width", 0), ("height", 1)):
            one, other = extent(mine), extent(theirs)
            found[f"{structure}_{name}_error"] = (
                one[measured] - other[measured] if one and other else None
            )
        mine_r, theirs_r = equivalent_radius(mine), equivalent_radius(theirs)
        found[f"{structure}_radius_error"] = (
            mine_r - theirs_r if mine_r is not None and theirs_r is not None else None
        )
        drawn = extent(theirs)
        found[f"truth_{structure}_width"] = drawn[0] if drawn else None
        found[f"truth_{structure}_height"] = drawn[1] if drawn else None
        found[f"truth_{structure}_radius"] = theirs_r

    if {"disc", "cup"} <= set(said) and {"disc", "cup"} <= set(truth):
        for name, ratio in (("vertical", vertical_ratio), ("area", area_ratio)):
            mine = ratio(said["cup"], said["disc"])
            theirs = ratio(truth["cup"], truth["disc"])
            found[f"said_{name}_ratio"] = mine
            found[f"truth_{name}_ratio"] = theirs
            found[f"cup_{name}_ratio_error"] = (
                mine - theirs if mine is not None and theirs is not None else None
            )
        found["cup_outside_its_disc"] = outside_its_disc(said["cup"], said["disc"])
    return found
