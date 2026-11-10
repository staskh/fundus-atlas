# ABOUTME: A synthetic scene photographed: artery, vein and field-of-view masks on a square frame of
# ABOUTME: any side, the scene turned about the frame centre, and the disc in that frame's pixels.

import math
from dataclasses import dataclass

import numpy as np
import shapely

from .scene import DISC_RADIUS_UM, FOV_DIAMETER_UM, FOV_RADIUS_UM, Scene
from .truth import _tubes


@dataclass(frozen=True)
class Drawing:
    """What an implementation is handed: two masks and a field on a `side` × `side` frame, and the
    disc as ``(x, y, radius)`` in that frame's pixels."""

    artery: np.ndarray
    vein: np.ndarray
    fov: np.ndarray
    disc: tuple[float, float, float]
    um_per_px: float


def um_per_px(side: int) -> float:
    """The scale of a frame whose side spans the field of view's diameter."""
    return FOV_DIAMETER_UM / side


def turn(x, y, rotation: float):
    """Scene µm to frame µm: turned `rotation` degrees counter-clockwise on screen (y down) about
    the frame centre.

    **The whole scene turns, disc included, about the frame centre.** Turning about the disc was
    this benchmark's first idea and it is wrong: a vessel a third of a frame from the disc sweeps a
    circle wide enough to leave the field, and a clipped vessel measures something other than the
    shape. Turning everything together keeps every distance — vessel to vessel, vessel to disc —
    exactly as it was, and a circular field of view is unchanged by the turn.
    """
    a = math.radians(rotation)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def render(scene: Scene, rotation: float = 0.0, side: int = 2048) -> Drawing:
    """Each pixel is lit when its centre, carried back into the scene, lies inside the drawing.

    **Pixel ``i``'s centre is at ``i``**, the convention an array index has, a centroid of mask
    pixels has, and every disc estimate in `results/disc_estimation/` therefore has. The disc handed
    over is in that convention, so it sits exactly on the disc the masks were drawn around rather
    than half a pixel off it.

    The geometry is rotated and drawn afresh rather than a picture being turned: resampling a
    structure a few pixels wide destroys it — rescaling one dataset's tracing here turned 19
    connected components into 309 — so the grid is the only difference between two angles.
    """
    um = um_per_px(side)
    frame = (np.arange(side) + 0.5 - side / 2.0) * um
    fx, fy = np.meshgrid(frame, frame)
    # The scene point each pixel centre shows: the frame turned back.
    x, y = turn(fx, fy, -rotation)
    masks = {}
    for vessel, net in scene.classes().items():
        drawn = _tubes(net)
        shapely.prepare(drawn)
        masks[vessel] = shapely.contains_xy(drawn, x, y)
    cx, cy = turn(*scene.disc, rotation)
    centre = side / 2.0 - 0.5
    return Drawing(
        artery=masks["artery"],
        vein=masks["vein"],
        fov=fx**2 + fy**2 <= FOV_RADIUS_UM**2,
        disc=(centre + cx / um, centre + cy / um, DISC_RADIUS_UM / um),
        um_per_px=um,
    )
