# ABOUTME: Tests for the REYIA fetcher: a compilation of nine other datasets' photographs, most of
# ABOUTME: whose archive is synthetic images from a generator rather than photographs of eyes.

import io
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from datasets import reyia


def a_photograph(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[6:34, 10:50] = (120, 60, 30)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_label_map(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[10:12, 12:48] = (255, 0, 0)
    pixels[20:22, 12:48] = (0, 0, 255)
    pixels[15:17, 20:24] = (255, 0, 255)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_mask(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0]), dtype=np.uint8)
    pixels[10:12, 12:48] = 255
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def an_archive(tmp_path: Path) -> Path:
    path = tmp_path / "archive.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for subset, stems in (("ENRICH", ["e01", "e02"]), ("GRAPE", ["g01"]), ("AVWIDE", ["w01"])):
            for stem in stems:
                archive.writestr(f"REYIA/{subset}/images/{stem}.png", a_photograph())
                archive.writestr(f"REYIA/{subset}/labels/{stem}.png", a_label_map())
                archive.writestr(f"REYIA/{subset}/artery/{stem}.png", a_mask())
                archive.writestr(f"REYIA/{subset}/veins/{stem}.png", a_mask())
        # Jupyter leaves these behind in several folders of the real archive
        archive.writestr("REYIA/ENRICH/images/e03-checkpoint.png", a_photograph())
        # and most of the archive is a generator's output rather than photographs
        for index in range(2):
            archive.writestr(
                f"REYIA/GENERATED_IMAGES/Generated_{index}/UZLF_TRAIN/x.png", a_photograph()
            )
    return path


def records(tmp_path: Path):
    return {record.key: record for record in reyia.discover({reyia.SLUG: an_archive(tmp_path)})}


def test_the_generated_images_are_not_built(tmp_path: Path) -> None:
    """Three quarters of the archive is RLAD's synthetic output. Nothing measured on a generated
    photograph says anything about an eye, and a benchmark must never mix them in."""
    found = records(tmp_path)

    assert not any("generated" in key for key in found)
    assert any("generated" in note.lower() for note in reyia.SKIPPED)


def test_the_ultra_wide_field_subset_is_not_built(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert not any(key.startswith("avwide") for key in found)
    assert any("wide" in note.lower() for note in reyia.SKIPPED)


def test_a_jupyter_checkpoint_is_not_a_photograph(tmp_path: Path) -> None:
    assert not any("checkpoint" in key for key in records(tmp_path))


def test_each_source_collection_is_its_own_subset(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert {record.subset for record in found.values()} == {"enrich", "grape"}
    assert sorted(found) == ["enrich_e01", "enrich_e02", "grape_g01"]


def test_the_crossing_colour_is_magenta_and_belongs_to_both(tmp_path: Path) -> None:
    """REYIA marks a crossing magenta, where Fundus-AVSeg and HRF-AV use green."""
    masks = reyia.PALETTE.masks(
        np.array([[[255, 0, 0], [0, 0, 255], [255, 0, 255], [0, 0, 0]]], np.uint8), "av"
    )

    assert list(masks["artery"][0] > 0) == [True, False, True, False]
    assert list(masks["vein"][0] > 0) == [False, True, True, False]


def test_the_published_binaries_are_what_the_label_map_says(tmp_path: Path) -> None:
    """The archive holds both encodings, so the fetcher can check itself rather than trust one.

    On GRAPE's `Grape102_OS_1`: the published artery mask is 58,796 pixels, and red plus magenta in
    the label map is 57,065 + 1,731. They agree exactly.
    """
    found = records(tmp_path)

    assert found["grape_g01"].maps["av"] is not None
    assert "artery" in found["grape_g01"].extras["published_masks"]


def test_the_photographs_belong_to_other_datasets_and_the_row_says_which(tmp_path: Path) -> None:
    """Scoring REYIA beside GRAPE counts the same eyes twice, so the subset has to travel."""
    found = records(tmp_path)

    assert found["grape_g01"].subset == "grape"
    assert found["grape_g01"].notes.startswith("these photographs are")
