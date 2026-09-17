# ABOUTME: The artery/vein map every store holds: one set of class indices, and each dataset's own
# ABOUTME: colours declared so that a published palette is translated rather than guessed at.

import numpy as np

#: What an artery/vein map can say about a pixel, in the order the indices run. `crossing` is where
#: an artery and a vein overlap in projection, which most published maps mark as its own colour;
#: `uncertain` is where the annotator could not tell which vessel it was. Both are kept as their own
#: classes rather than folded into artery or vein, because folding them is a research decision and
#: the store does not make those.
CLASSES = ("background", "artery", "vein", "crossing", "uncertain")

#: How far a published colour may sit from the one a dataset declared and still be taken for it, as
#: the largest difference on any one channel. Maps come back a shade off when they have been through
#: an editor or a lossy format; this is wide enough for that and far narrower than the gap between
#: any two classes in the palettes catalogued here.
TOLERANCE = 12

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
    """

    def __init__(self, colours: dict[tuple[int, int, int], str]) -> None:
        unknown = sorted({name for name in colours.values() if name not in CLASSES})
        if unknown:
            raise ValueError(f"{', '.join(unknown)} is not one of {CLASSES}")
        self.colours = {(0, 0, 0): "background", **colours}

    def labels(self, pixels: np.ndarray, tolerance: int = 0) -> np.ndarray:
        """Translate one published map into stored class indices.

        :param tolerance: how far a pixel may sit from a declared colour and still be taken for it,
            as the largest difference on any one channel — the same measure `utils.fov` uses for the
            surround. Published maps come back a shade off when they have been through an editor or
            a lossy format; anything further away is a colour nobody declared.
        :raises ValueError: on a colour this palette does not explain, naming it. A map that has
            grown a class is a thing to look at rather than to quietly call background.
        """
        flat = pixels.reshape(-1, 3).astype(np.int16)
        declared = np.array(list(self.colours), dtype=np.int16)
        meanings = [index(name) for name in self.colours.values()]

        distance = np.abs(flat[:, None, :] - declared[None, :, :]).max(axis=2)
        nearest = distance.argmin(axis=1)
        found = distance[np.arange(len(flat)), nearest]
        if (found > tolerance).any():
            colour = flat[np.argmax(found > tolerance)]
            raise ValueError(
                f"the map holds ({', '.join(str(int(v)) for v in colour)}), which this palette "
                f"does not explain: {self.colours}"
            )
        return np.take(meanings, nearest).astype(np.uint8).reshape(pixels.shape[:2])
