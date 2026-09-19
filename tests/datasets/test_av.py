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


def test_a_colour_a_shade_off_is_treated_as_the_one_it_came_from() -> None:
    """Published maps are saved through editors and lossy formats, so colours arrive a shade off."""
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"})
    pixels = np.zeros((1, 3, 3), dtype=np.uint8)
    pixels[0, 0] = (250, 4, 6)
    pixels[0, 1] = (3, 2, 251)

    labels = palette.labels(pixels)

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
        {
            (255, 0, 0): "artery",
            (0, 0, 255): "vein",
            (0, 255, 0): "crossing",
            (255, 255, 255): "uncertain",
        }
    )
    labels = palette.labels(coloured())

    binaries = av.binaries(labels)

    assert binaries["artery"][0].all() and binaries["artery"][2].all(), "artery plus crossing"
    assert binaries["vein"][1].all() and binaries["vein"][2].all(), "vein plus crossing"
    assert not binaries["artery"][1].any()
    assert not binaries["vein"][0].any()


def test_the_vessel_mask_holds_every_vessel_including_the_unclassified_ones() -> None:
    palette = av.Palette(
        {
            (255, 0, 0): "artery",
            (0, 0, 255): "vein",
            (0, 255, 0): "crossing",
            (255, 255, 255): "uncertain",
        }
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


def a_drawing() -> np.ndarray:
    """An annotation drawn dark on a white page, as several datasets publish one."""
    pixels = np.full((4, 6, 3), 255, dtype=np.uint8)
    pixels[1, :4] = (237, 27, 36)
    pixels[2, :4] = (250, 248, 249)
    return pixels


def test_ink_on_a_white_page_is_the_annotation() -> None:
    drawn = av.Ink()

    masks = drawn.masks(a_drawing(), "artery")

    assert list(masks) == ["artery"]
    assert masks["artery"][1, :4].all(), "the drawn stroke"
    assert not masks["artery"][0].any(), "the page"
    assert not masks["artery"][2].any(), "a compression halo is not a stroke"


def test_a_palette_and_an_ink_reader_answer_the_same_way() -> None:
    """Both say: here are the store's binary masks for this published file."""
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein", (0, 255, 0): "crossing"})

    masks = palette.masks(coloured()[:3], "av")

    assert sorted(masks) == ["artery", "vein", "vessels"]
    assert masks["artery"].dtype == np.uint8


def test_how_dark_counts_as_ink_can_be_said_where_a_dataset_needs_it() -> None:
    faint = np.full((1, 2, 3), 255, dtype=np.uint8)
    faint[0, 0] = (200, 200, 200)

    assert av.Ink(threshold=100).masks(faint, "vessels")["vessels"].any() is np.False_
    assert av.Ink(threshold=40).masks(faint, "vessels")["vessels"][0, 0]


def test_an_anti_aliased_stroke_is_read_as_the_colour_it_fades_from() -> None:
    """Three of HRF-AV's 45 maps were saved with anti-aliased strokes, so their edges run the whole
    ramp from a class colour down to the background: (60, 60, 217), (60, 60, 158), (22, 22, 253).

    A pixel is therefore read as the class whose ramp it lies on, not as the colour it is nearest:
    a flat distance either refuses half the ramp or swallows colours nobody declared.
    """
    ramp = np.array([[[60, 60, 217], [60, 60, 158], [0, 0, 40], [253, 22, 22]]], dtype=np.uint8)
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"}, tolerance=64)

    masks = palette.masks(ramp)

    assert list(masks["vein"][0] > 0) == [True, True, True, False], "blue, all the way down"
    assert masks["artery"][0, 3]


def test_a_pixel_nearer_the_background_than_any_stroke_is_background() -> None:
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"}, tolerance=64)

    masks = palette.masks(np.array([[[43, 43, 43], [2, 2, 2]]], dtype=np.uint8))

    assert not masks["vessels"].any(), "grey is equally far from every ramp, so it is the page"


def test_a_colour_on_no_ones_ramp_is_still_refused() -> None:
    """The guard is what catches a map that has grown a class — white, say, for uncertain.

    It survives a widened tolerance: white sits 255 off every ramp a red-and-blue palette declares.
    """
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"}, tolerance=64)

    with pytest.raises(ValueError, match="255, 255, 255"):
        palette.masks(np.array([[[255, 255, 255]]], dtype=np.uint8))


def test_with_the_guard_open_a_grey_falls_to_the_background() -> None:
    """HRF-AV's three anti-aliased maps need every pixel assigned rather than any refused.

    A grey is equally far from every ramp, so it lands on the background — which is what a stray
    pixel between two strokes should be — while a blend still lands on the colour it came from.
    """
    palette = av.Palette({(255, 0, 0): "artery", (0, 0, 255): "vein"}, tolerance=256)

    masks = palette.masks(
        np.array([[[231, 231, 231], [74, 74, 74], [60, 60, 217], [253, 22, 22]]], dtype=np.uint8)
    )

    assert list(masks["vessels"][0] > 0) == [False, False, True, True]
    assert masks["vein"][0, 2] and masks["artery"][0, 3]
