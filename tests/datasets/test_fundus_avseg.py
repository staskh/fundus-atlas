# ABOUTME: Tests for the Fundus-AVSeg fetcher: what it finds in the archive, how it reads the
# ABOUTME: authors' split, metadata and quality labels, and what it refuses to invent.

import io
import zipfile
from pathlib import Path

import numpy as np
import openpyxl
import pytest
from PIL import Image

from datasets import fundus_avseg
from datasets.utils import av

NAMES = ["001_G.png", "002_N.png", "003_D.png", "004_A.png"]


def a_photograph(size: tuple[int, int] = (64, 64)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    ys, xs = np.ogrid[: size[1], : size[0]]
    inside = (ys - size[1] / 2) ** 2 + (xs - size[0] / 2) ** 2 < (min(size) / 2) ** 2
    pixels[inside] = (180, 90, 40)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_map(size: tuple[int, int] = (64, 64)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[10:14, 8:56] = (255, 0, 0)
    pixels[20:24, 8:56] = (0, 0, 255)
    pixels[30:32, 30:34] = (0, 255, 0)
    pixels[40:42, 30:34] = (255, 255, 255)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def an_archive(tmp_path: Path, names: list[str] | None = None, undescribed: str = "") -> Path:
    """The shape figshare serves; `undescribed` adds a photograph the metadata never mentions."""
    names = names or NAMES
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(["image name", "eye id", "disease type", "image quality"])
    for index, name in enumerate(names):
        sheet.append(
            [
                name,
                "right" if index % 2 else "left",
                "Glaucoma",
                "Low-quality" if index else "High-quality",
            ]
        )
    metadata = io.BytesIO()
    book.save(metadata)

    path = tmp_path / "Fundus-AVSeg.zip"
    with zipfile.ZipFile(path, "w") as archive:
        if undescribed:
            archive.writestr(f"Fundus-AVSeg/images/{undescribed}", a_photograph())
            archive.writestr(f"Fundus-AVSeg/annotation/{undescribed}", a_map())
        for name in names:
            archive.writestr(f"Fundus-AVSeg/images/{name}", a_photograph())
            archive.writestr(f"Fundus-AVSeg/annotation/{name}", a_map())
        archive.writestr("Fundus-AVSeg/metadata.xlsx", metadata.getvalue())
        archive.writestr("Fundus-AVSeg/training.txt", "\n".join(names[:2]))
        archive.writestr("Fundus-AVSeg/testing.txt", "\n".join(names[2:]))
    return path


def records(tmp_path: Path, **kwargs):
    found = fundus_avseg.discover({fundus_avseg.SLUG: an_archive(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_every_photograph_becomes_a_record_with_its_map(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert len(found) == 4
    assert set(found["train_001_g"].maps) == {"av"}


def test_the_key_carries_the_split_the_authors_published(tmp_path: Path) -> None:
    """The split is theirs — `training.txt` and `testing.txt` — and is never invented."""
    found = records(tmp_path)

    assert sorted(found) == ["test_003_d", "test_004_a", "train_001_g", "train_002_n"]
    assert found["train_001_g"].split == "train"
    assert found["test_003_d"].split == "test"


def test_the_disease_is_the_word_the_metadata_uses(tmp_path: Path) -> None:
    assert records(tmp_path)["train_001_g"].disease == "glaucoma"


def test_the_eye_side_is_recorded_in_the_atlas_vocabulary(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert found["train_001_g"].eye == "os", "the metadata's 'left'"
    assert found["train_002_n"].eye == "od"


def test_the_published_quality_label_is_mapped_rather_than_recomputed(tmp_path: Path) -> None:
    """The authors' token travels in its own column and the declared rule maps it.

    The record must not preset `quality_source`: that tells the build a set of per-reader gradings
    will fill the cell, and this dataset publishes one grade and names no graders — which would
    leave every row's `quality` empty while claiming to be published.
    """
    found = records(tmp_path)

    assert found["train_001_g"].quality_source == ""
    assert found["train_001_g"].extras["published_quality"] == "High-quality"
    assert fundus_avseg.QUALITY.grade({"published_quality": "Low-quality"})[0] == "bad"
    assert fundus_avseg.QUALITY.grade({"published_quality": "High-quality"})[0] == "good"


def test_the_two_sensor_sizes_are_two_subsets(tmp_path: Path) -> None:
    """The archive says nothing about which camera took which photograph; size is all there is."""
    assert fundus_avseg.subset_of(2656, 1992) == "large"
    assert fundus_avseg.subset_of(1280, 1280) == "square"


def test_each_record_carries_the_sensor_it_came_off(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert {record.subset for record in found.values()} == {"other"}, "the fixture's 64px squares"
    assert all(record.subset for record in found.values()), "never left for the build to guess"


def test_the_palette_is_the_one_the_dataset_publishes() -> None:
    labels = fundus_avseg.PALETTE.labels(
        np.array([[[255, 0, 0], [0, 0, 255], [0, 255, 0], [255, 255, 255], [0, 0, 0]]], np.uint8)
    )

    assert list(labels[0]) == [
        av.index(name) for name in ("artery", "vein", "crossing", "uncertain", "background")
    ]


def test_no_vessel_layer_is_written(tmp_path: Path) -> None:
    """Its vessel mask is derived from the artery/vein labels rather than drawn, so storing one
    would let a model be scored twice against the same annotation and called independent."""
    assert all("vessels" not in record.maps for record in records(tmp_path).values())


def test_a_photograph_the_metadata_never_mentions_is_an_error(tmp_path: Path) -> None:
    """A dataset that has grown an image is a thing to look at, not to build with blank labels."""
    with pytest.raises(LookupError, match="005_N.png"):
        records(tmp_path, undescribed="005_N.png")
