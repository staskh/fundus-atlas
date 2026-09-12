# ABOUTME: The square crop around the field of view, pasted into a canvas rather than sliced out.
# ABOUTME: Every layer of an image goes through the same square, so they stay in register.

from dataclasses import dataclass

import numpy as np

from datasets.utils.fov import Circle

#: How far past its fitted circle a footprint must reach before the square follows it, as a
#: fraction of the field's own diameter. A round field overshoots its fit by a few pixels in two
#: thousand — rasterisation and noise; Chaksu's Bosch handheld overshoots by fifty in thirteen
#: hundred, because its field is an ellipse.
ROUNDING = 0.005

#: A floor for that, so a small photograph is not held to a sub-pixel standard.
LEAST_ROUNDING = 2.0


@dataclass(frozen=True)
class Square:
    """A square in the photograph's own pixels. ``x0`` and ``y0`` may be negative."""

    x0: int
    y0: int
    side: int


def square_around(circle: Circle, field: np.ndarray | None = None) -> Square:
    """The square holding the whole field of view, whether or not the photograph contains all of it.

    It covers two things at once, and needs both. The **fitted circle**, because a field running
    off the sensor is still a circle and the part that missed the sensor is still part of it. And
    the **visible footprint**, because not every camera draws a circle: Chaksu's Bosch handheld
    produces a field 1441 wide and 1221 tall, and a square sized from a circle fitted to it is
    1337 across and shaves the retina off both sides.

    :param field: the photograph's footprint, as a boolean mask. Omitted, only the circle is used.
    """
    around_circle = Square(
        round(circle.cx - circle.r), round(circle.cy - circle.r), round(2 * circle.r)
    )
    if field is None or not field.any():
        return around_circle

    ys, xs = np.nonzero(field)
    left, right = circle.cx - circle.r, circle.cx + circle.r
    top, bottom = circle.cy - circle.r, circle.cy + circle.r
    rounding = max(LEAST_ROUNDING, ROUNDING * 2 * circle.r)
    # Only where the footprint genuinely reaches past the circle. A rasterised round field
    # overshoots its own fitted circle by a fraction of a pixel, and following that would move
    # every square in every store for no reason; a field that is not round overshoots by fifty.
    reaches = [
        left - float(xs.min()) > rounding,
        float(xs.max()) - right > rounding,
        top - float(ys.min()) > rounding,
        float(ys.max()) - bottom > rounding,
    ]
    if not any(reaches):
        return around_circle

    left, right = min(left, float(xs.min())), max(right, float(xs.max()))
    top, bottom = min(top, float(ys.min())), max(bottom, float(ys.max()))
    side = round(max(right - left, bottom - top))
    middle_x, middle_y = (left + right) / 2, (top + bottom) / 2
    return Square(round(middle_x - side / 2), round(middle_y - side / 2), side)


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
