# ABOUTME: Optic disc and cup as polygons: traced once into the native frame, scaled to each size.
# ABOUTME: Polygons rather than rasters, so five experts per image cost rows and not files.

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import measure
from skimage.feature import match_template

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


@dataclass(frozen=True)
class Layer:
    """One structure inside a mask that holds more than one.

    RIGA+ writes the optic cup as 128 and the rim around it as 255, so the disc is both values
    together and the cup is one of them. Tracing such a file whole would give one shape where the
    dataset drew two.

    :param source: the file, on disk or inside an archive.
    :param values: the pixel values this structure is made of.
    """

    source: object
    values: tuple[int, ...]

    def mask_from(self, image: np.ndarray) -> np.ndarray:
        """The structure's own mask, from the image the file holds."""
        return np.where(np.isin(image, self.values), 255, 0).astype(np.uint8)


def locate(crop: np.ndarray, inside: np.ndarray) -> tuple[int, int, float]:
    """Find where a crop was taken from, and how sure that is.

    Some datasets annotate a region of interest rather than the photograph, and publish the
    coordinates in the crop's frame without saying where the crop came from. The crop itself is
    published too, so the offset can be recovered rather than assumed — which is the difference
    between contours that land on the optic nerve and contours that land somewhere plausible.

    :param crop: the region of interest, at the photograph's own scale.
    :param inside: the photograph.
    :return: the crop's top-left corner in the photograph, and the correlation there. A value near
        one means the crop was found; a low one means it was not, and the caller should not place
        anything.
    """
    found = match_template(inside.astype(float), crop.astype(float))
    y, x = np.unravel_index(int(np.argmax(found)), found.shape)
    return int(x), int(y), float(found.max())


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


def rasterise(polygon: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Fill a polygon back into a mask of the given height and width.

    The inverse of :func:`trace`, near enough to check one against the other: a store can be read
    back, redrawn in the coordinates the dataset published, and compared with what it published.
    """
    drawn = Image.new("1", (shape[1], shape[0]))
    if len(polygon) >= 3:
        ImageDraw.Draw(drawn).polygon([(x, y) for x, y in polygon], fill=1)
    return np.asarray(drawn)


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
    filled, original = rasterise(polygon, mask.shape[:2]), mask > 0
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
