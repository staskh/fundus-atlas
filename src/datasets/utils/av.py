# ABOUTME: The artery/vein map every store holds: one set of class indices, and each dataset's own
# ABOUTME: colours declared so that a published palette is translated rather than guessed at.

import numpy as np

#: What an artery/vein map can say about a pixel, in the order the indices run. `crossing` is where
#: an artery and a vein overlap in projection, which most published maps mark as its own colour;
#: `uncertain` is where the annotator could not tell which vessel it was. Both are kept as their own
#: classes rather than folded into artery or vein, because folding them is a research decision and
#: the store does not make those.
CLASSES = ("background", "artery", "vein", "crossing", "uncertain")

#: How far off a declared colour's ramp a pixel may sit and still be taken for it. A map saved
#: without loss needs none of this; one that has been through an editor or a lossy format arrives a
#: shade off, and this is how much of that is tolerated before a colour counts as one nobody
#: declared.
TOLERANCE = 12

#: How far from white a pixel must be before it counts as something somebody drew. Several datasets
#: publish their annotation as a drawing on a white page rather than as a mask, saved as JPEG, so
#: every stroke carries a halo of compression around it. The threshold sits well above the halo and
#: well below the ink: on AVRDB, moving it from 40 to 90 changes the area by about 3%.
INK = 60

#: The classes that are vessel, whatever kind. A vessel map derived here is exactly their union.
VESSEL = ("artery", "vein", "crossing", "uncertain")


def index(name: str) -> int:
    """The stored index of one class."""
    return CLASSES.index(name)


def of(labels: np.ndarray, name: str) -> np.ndarray:
    """One class as a binary mask."""
    return labels == index(name)


def vessels(labels: np.ndarray) -> np.ndarray:
    """Every vessel pixel, whatever kind — the union an artery/vein map implies.

    A dataset that publishes a separate vessel mask publishes an independent annotation and that one
    is stored as `vessels`. This is the derived alternative, and the two are not interchangeable:
    a model scored against a derived mask is being scored against the artery/vein map again.
    """
    return np.isin(labels, [index(name) for name in VESSEL])


#: What a store holds for an artery/vein dataset: one binary mask per vessel kind, plus the union.
#: They are separate files rather than one label map because that is what every consumer wants —
#: a model predicts an artery mask, and scoring it is a comparison of two binary images.
BINARIES = ("artery", "vein", "vessels")


def binaries(labels: np.ndarray) -> dict[str, np.ndarray]:
    """One published artery/vein map as the masks the store keeps.

    **A crossing belongs to both.** Where an artery passes over a vein the projection is both
    vessels at once, not a third kind: withholding those pixels from the artery mask would score a
    model's correct artery as a false positive, and a model cannot be asked to reproduce an
    ambiguity of projection.

    `vessels` is every vessel pixel, including the ones the annotator could not classify. It is a
    **derived** mask wherever the dataset did not draw one independently, and the two are not
    interchangeable — see the `fetch-dataset` skill, section 12.
    """
    return {
        "artery": _written(of(labels, "artery") | of(labels, "crossing")),
        "vein": _written(of(labels, "vein") | of(labels, "crossing")),
        "vessels": _written(vessels(labels)),
    }


def _written(mask: np.ndarray) -> np.ndarray:
    """A binary mask as the store writes one: 0 or 255, one channel."""
    return np.where(mask, 255, 0).astype(np.uint8)


class Palette:
    """One dataset's colours, and what each of them means.

    Published artery/vein maps are RGB images and no two datasets agree on the colours — red and
    blue are usual for artery and vein, but the third and fourth classes vary, and some datasets
    swap them. The fetcher declares what it found; this translates it into the indices of
    :data:`CLASSES` so that every store reads alike.

    :param colours: RGB tuple to class name. Black is background and need not be declared.
    :param tolerance: how far a pixel may sit from a declared colour and still be taken for it, on
        the channel furthest away. The default suits a map saved without loss; a dataset whose
        strokes are anti-aliased declares its own. It cannot move a pixel to the wrong class, since
        the colours a palette declares are separated by 255 on some channel — it can only decide
        whether an edge pixel is refused or assigned.
    """

    def __init__(
        self, colours: dict[tuple[int, int, int], str], tolerance: int = TOLERANCE
    ) -> None:
        self.tolerance = tolerance
        unknown = sorted({name for name in colours.values() if name not in CLASSES})
        if unknown:
            raise ValueError(f"{', '.join(unknown)} is not one of {CLASSES}")
        self.colours = {(0, 0, 0): "background", **colours}

    def masks(self, pixels: np.ndarray, name: str = "av") -> dict[str, np.ndarray]:
        """The store's binary masks for one published map, translated from this dataset's colours."""
        return binaries(self.labels(pixels, tolerance=self.tolerance))

    def labels(self, pixels: np.ndarray, tolerance: int | None = None) -> np.ndarray:
        """Translate one published map into stored class indices.

        A pixel is read as **the class whose ramp it lies on**: the segment from the background
        colour to that class's own. Maps saved with anti-aliased strokes have edges running the
        whole length of such a ramp — HRF-AV's blue strokes fade through (60, 60, 217) and
        (60, 60, 158) — and a flat distance from the declared colour either refuses half of every
        edge or is loosened until it swallows colours nobody declared. Distance off the ramp is
        what :data:`TOLERANCE` measures.

        :raises ValueError: on a colour lying off every ramp, naming it. A map that has grown a
            class is a thing to look at rather than to quietly call background.
        """
        tolerance = self.tolerance if tolerance is None else tolerance
        flat = pixels.reshape(-1, 3).astype(np.float64)
        background = np.array(_named(self.colours, "background"), dtype=np.float64)
        drawn = [(colour, name) for colour, name in self.colours.items() if name != "background"]

        # Distance to the background itself, and to each class's ramp from it.
        offsets = [np.abs(flat - background).max(axis=1)]
        meanings = [index("background")]
        for colour, name in drawn:
            direction = np.array(colour, dtype=np.float64) - background
            along = ((flat - background) @ direction) / max(float(direction @ direction), 1e-9)
            on_ramp = background + np.clip(along, 0.0, 1.0)[:, None] * direction
            offsets.append(np.abs(flat - on_ramp).max(axis=1))
            meanings.append(index(name))

        off = np.vstack(offsets)
        nearest = off.argmin(axis=0)
        found = off[nearest, np.arange(off.shape[1])]
        if (found > tolerance).any():
            colour = flat[np.argmax(found > tolerance)]
            raise ValueError(
                f"the map holds ({', '.join(str(int(v)) for v in colour)}), which lies off every "
                f"ramp this palette declares: {self.colours}"
            )
        return np.take(meanings, nearest).astype(np.uint8).reshape(pixels.shape[:2])


class Ink:
    """An annotation published as a drawing on a page rather than as a mask.

    AVRDB draws its arteries in red and its veins in blue on white, one file each, as JPEG. There is
    no palette to read: the file already says which vessel it holds, and what is wanted is simply
    which pixels were drawn on. Anything far enough from the page colour is a stroke.

    :param page: the colour of an undrawn pixel.
    :param threshold: how far from it, on the channel furthest away, a pixel must sit to count.
    """

    def __init__(self, page: tuple[int, int, int] = (255, 255, 255), threshold: int = INK) -> None:
        self.page = page
        self.threshold = threshold

    def masks(self, pixels: np.ndarray, name: str) -> dict[str, np.ndarray]:
        """The one mask this file holds, under the name the fetcher asked for it by."""
        distance = np.abs(pixels.astype(np.int16) - np.array(self.page, dtype=np.int16)).max(axis=2)
        return {name: _written(distance > self.threshold)}


def _named(colours: dict[tuple[int, int, int], str], wanted: str) -> tuple[int, int, int]:
    """The colour a palette gives one class, for the background it always declares."""
    for colour, name in colours.items():
        if name == wanted:
            return colour
    return (0, 0, 0)
