# ABOUTME: The square crop around the field of view, pasted into a canvas rather than sliced out.
# ABOUTME: Every layer of an image goes through the same square, so they stay in register.

from dataclasses import dataclass

import numpy as np

from datasets.utils.fov import Circle


@dataclass(frozen=True)
class Square:
    """A square in the photograph's own pixels. ``x0`` and ``y0`` may be negative."""

    x0: int
    y0: int
    side: int


def square_around(circle: Circle) -> Square:
    """The square bounding the field of view, whether or not the photograph contains all of it."""
    return Square(round(circle.cx - circle.r), round(circle.cy - circle.r), round(2 * circle.r))


def apply(image: np.ndarray, square: Square, fill: int = 0) -> np.ndarray:
    """Paste the photograph into the square.

    Where the field runs off the sensor the square extends past the image, and the part with
    nothing behind it is filled rather than the square being shrunk to fit. Shrinking would move
    the field's centre, and every coordinate in the store is relative to that centre.

    :param image: ``(h, w)`` or ``(h, w, c)``.
    :param square: from :func:`square_around`.
    :return: an array ``square.side`` on each side.
    """
    shape = (square.side, square.side) + image.shape[2:]
    canvas = np.full(shape, fill, dtype=image.dtype)
    height, width = image.shape[:2]

    src_x0, src_y0 = max(0, square.x0), max(0, square.y0)
    src_x1 = min(width, square.x0 + square.side)
    src_y1 = min(height, square.y0 + square.side)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return canvas

    dst_x0, dst_y0 = src_x0 - square.x0, src_y0 - square.y0
    canvas[dst_y0 : dst_y0 + (src_y1 - src_y0), dst_x0 : dst_x0 + (src_x1 - src_x0)] = image[
        src_y0:src_y1, src_x0:src_x1
    ]
    return canvas


def pad_fraction(square: Square, height: int, width: int) -> float:
    """How much of the square has no photograph behind it, as a fraction of its area.

    A large value is a warning: most of what a consumer sees at the edges was invented here.
    """
    overlap_w = max(0, min(width, square.x0 + square.side) - max(0, square.x0))
    overlap_h = max(0, min(height, square.y0 + square.side) - max(0, square.y0))
    area = square.side**2
    return (area - overlap_w * overlap_h) / area
