# ABOUTME: Optic disc and cup as polygons: traced once into the native frame, scaled to each size.
# ABOUTME: Polygons rather than rasters, so five experts per image cost rows and not files.

import csv
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import measure

#: What a fetcher declares when the dataset publishes the boundaries as coordinates. They are
#: transformed through the crop and nothing is traced.
COORDINATES = "coordinates"

#: What a fetcher declares when the dataset publishes masks. They are traced once, in the native
#: frame, and every size is scaled from that trace.
RASTER = "raster"

#: Douglas-Peucker tolerance, as a fraction of the outline's own perimeter. About 45 nodes for an
#: optic disc — the range a hand-drawn outline occupies, rather than a chain of pixel corners.
SIMPLIFY = 0.001

#: The header of a contour file. One file per image holds every structure and every reader.
COLUMNS = ("structure", "reader", "node", "x", "y")


def trace(mask: np.ndarray) -> np.ndarray:
    """The outline of the shape in a mask, as polygon nodes.

    :param mask: any non-zero value is inside the shape.
    :return: ``(n, 2)`` of x, y in the mask's own pixels, or empty where nothing was drawn.
    """
    filled = ndimage.binary_fill_holes(mask > 0)
    if not filled.any():
        return np.empty((0, 2))
    labels, count = ndimage.label(filled)
    if count > 1:
        sizes = ndimage.sum_labels(filled, labels, index=range(1, count + 1))
        filled = labels == (int(np.argmax(sizes)) + 1)

    outlines = measure.find_contours(filled.astype(float), 0.5)
    longest = max(outlines, key=len)
    perimeter = float(np.abs(np.diff(longest, axis=0)).sum())
    simplified = measure.approximate_polygon(longest, tolerance=SIMPLIFY * perimeter)
    return simplified[:, ::-1].astype(float)


def fidelity(mask: np.ndarray, polygon: np.ndarray) -> float:
    """How faithfully a traced polygon reproduces the mask it came from, as an IoU.

    Recorded per image rather than assumed: a trace is a claim about what an expert drew, and a
    poor one should be visible in the manifest instead of discovered later.

    A faithful trace scores about 0.98, not 1.0. The outline follows the 0.5 level, half a pixel
    inside the mask's filled edge, and that half pixel is a fixed cost of the convention rather
    than a fault. A materially lower score means the shape was not a single clean blob.
    """
    if len(polygon) < 3:
        return 0.0
    drawn = Image.new("1", (mask.shape[1], mask.shape[0]))
    ImageDraw.Draw(drawn).polygon([(x, y) for x, y in polygon], fill=1)
    filled, original = np.asarray(drawn), mask > 0
    union = (filled | original).sum()
    return float((filled & original).sum() / union) if union else 0.0


def write(path: Path, drawn: dict[tuple[str, str], np.ndarray], scale: float = 1.0) -> None:
    """Write one image's contours.

    :param drawn: (structure, reader) to nodes in the native frame.
    :param scale: ``size / crop_side``. At 1.0 the native floats are written as they are, because
        native is the annotation of record and rounding it would round every size with it; at any
        other scale the nodes are rounded to the integer pixels of that grid.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for (structure, reader), nodes in sorted(drawn.items()):
            for index, (x, y) in enumerate(nodes):
                if scale == 1.0:
                    writer.writerow([structure, reader, index, x, y])
                else:
                    writer.writerow([structure, reader, index, round(x * scale), round(y * scale)])


def read(path: Path) -> dict[tuple[str, str], np.ndarray]:
    """Read one image's contours back, keyed by structure and reader."""
    drawn: dict[tuple[str, str], list[tuple[float, float]]] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["structure"], row["reader"])
            drawn.setdefault(key, []).append((float(row["x"]), float(row["y"])))
    return {key: np.array(nodes) for key, nodes in drawn.items()}
