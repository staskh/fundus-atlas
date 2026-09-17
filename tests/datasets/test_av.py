# ABOUTME: Tests for the artery/vein label map every store holds: one convention of class indices,
# ABOUTME: and each dataset's own colours declared rather than guessed.

import numpy as np
import pytest

from datasets.utils import av


def coloured() -> np.ndarray:
    """A tiny map in the colours Fundus-AVSeg publishes: red artery, blue vein, green crossing."""
    pixels = np.zeros((4, 4, 3), dtype=np.uint8)
    pixels[0] = (255, 0, 0)
    pixels[1] = (0, 0, 255)
    pixels[2] = (0, 255, 0)
    pixels[3] = (255, 255, 255)
    return pixels


def test_every_store_holds_the_same_class_indices() -> None:
    """A consumer reads one convention, whatever colours the dataset happened to publish."""
    assert av.CLASSES == ("background", "artery", "vein", "crossing", "uncertain")
    assert av.index("artery") == 1
    assert av.index("vein") == 2


def test_a_datasets_own_colours_are_declared_and_translated() -> None:
    palette = av.Palette(
        {
            (255, 0, 0): "artery",
            (0, 0, 255): "vein",
            (0, 255, 0): "crossing",
            (255, 255, 255): "uncertain",
        }
    )

    labels = palette.labels(coloured())

    assert labels.dtype == np.uint8
    assert list(labels[:, 0]) == [1, 2, 3, 4]
    assert labels.shape == (4, 4)


def test_black_is_background_without_being_declared() -> None:
    palette = av.Palette({(255, 0, 0): "artery"})

    labels = palette.labels(np.zeros((2, 2, 3), dtype=np.uint8))

    assert labels.max() == 0


def test_a_colour_nobody_declared_is_an_error_rather_than_background() -> None:
    """A map that has grown a class is a thing to look at, not to silently drop."""
    palette = av.Palette({(255, 0, 0): "artery"})
    pixels = np.zeros((2, 2, 3), dtype=np.uint8)
    pixels[0, 0] = (0, 0, 255)

    with pytest.raises(ValueError, match="0, 0, 255"):
        palette.labels(pixels)


def test_a_palette_naming_a_class_that_does_not_exist_is_refused() -> None:
    with pytest.raises(ValueError, match="capillary"):
        av.Palette({(255, 0, 0): "capillary"})


def test_nearly_black_is_treated_as_the_colour_it_is_closest_to() -> None:
    """Published maps are saved as JPEG or through editors, so colours arrive a shade off."""
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"})
    pixels = np.zeros((1, 3, 3), dtype=np.uint8)
    pixels[0, 0] = (250, 4, 6)
    pixels[0, 1] = (3, 2, 251)

    labels = palette.labels(pixels, tolerance=12)

    assert list(labels[0]) == [1, 2, 0]


def test_the_vessels_of_an_artery_vein_map_are_its_classes_together() -> None:
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein", (0, 255, 0): "crossing"})
    labels = palette.labels(coloured()[:3])

    assert av.vessels(labels).sum() == 12, "artery, vein and crossing are all vessel"
    assert av.of(labels, "artery").sum() == 4


def test_a_crossing_belongs_to_both_the_artery_and_the_vein() -> None:
    """Where the two vessels cross, the pixel is artery and vein at once.

    A projection of two vessels one over the other is not a third kind of vessel; scoring a model's
    artery mask against a ground truth that withheld those pixels would count a correct artery as a
    false positive.
    """
    palette = av.Palette(
        {(255, 0, 0): "artery", (0, 0, 255): "vein", (0, 255, 0): "crossing",
         (255, 255, 255): "uncertain"}
    )
    labels = palette.labels(coloured())

    binaries = av.binaries(labels)

    assert binaries["artery"][0].all() and binaries["artery"][2].all(), "artery plus crossing"
    assert binaries["vein"][1].all() and binaries["vein"][2].all(), "vein plus crossing"
    assert not binaries["artery"][1].any()
    assert not binaries["vein"][0].any()


def test_the_vessel_mask_holds_every_vessel_including_the_unclassified_ones() -> None:
    palette = av.Palette(
        {(255, 0, 0): "artery", (0, 0, 255): "vein", (0, 255, 0): "crossing",
         (255, 255, 255): "uncertain"}
    )
    binaries = av.binaries(palette.labels(coloured()))

    assert binaries["vessels"][:4].all(), "artery, vein, crossing and uncertain are all vessel"
    assert not binaries["artery"][3].any(), "an unclassified vessel is neither artery nor vein"


def test_the_binaries_are_written_as_the_store_writes_masks() -> None:
    palette = av.Palette({(255, 0, 0): "artery"})
    binaries = av.binaries(palette.labels(coloured()[:1]))

    for name, mask in binaries.items():
        assert mask.dtype == np.uint8, name
        assert set(np.unique(mask).tolist()) <= {0, 255}, name
