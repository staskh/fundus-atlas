# ABOUTME: Tests for the REFUGE fetcher: the challenge's own masks from the bundle's `gts` folders,
# ABOUTME: one subset per camera, and the uploader's re-encoded and squared copies left alone.

import io
import json
import zipfile

import numpy as np
import pytest
from PIL import Image

from datasets import refuge

TRAIN = {
    "0": {
        "ImgName": "g0001.jpg",
        "Fovea_X": 10.5,
        "Fovea_Y": 12.0,
        "Size_X": 2124,
        "Size_Y": 2056,
        "Label": 1,
    },
    "1": {
        "ImgName": "n0001.jpg",
        "Fovea_X": 11.0,
        "Fovea_Y": 13.0,
        "Size_X": 2124,
        "Size_Y": 2056,
        "Label": 0,
    },
}
VAL = {
    "0": {
        "ImgName": "V0001.jpg",
        "Fovea_X": 9.0,
        "Fovea_Y": 8.0,
        "Size_X": 1634,
        "Size_Y": 1634,
        "Label": 0,
    }
}
TEST = {"0": {"ImgName": "T0001.jpg", "Size_X": 1634, "Size_Y": 1634}}


def encoded(pixels: np.ndarray, fmt: str) -> bytes:
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format=fmt)
    return out.getvalue()


def a_mask() -> np.ndarray:
    """The challenge's encoding: 255 outside, 128 the rim, 0 the cup."""
    yy, xx = np.mgrid[0:100, 0:100]
    mask = np.full((100, 100), 255, dtype=np.uint8)
    mask[(xx - 50) ** 2 + (yy - 50) ** 2 <= 30**2] = 128
    mask[(xx - 50) ** 2 + (yy - 50) ** 2 <= 12**2] = 0
    return mask


def a_bundle(tmp_path, test_index=TEST):
    path = tmp_path / "bundle.zip"
    photograph = np.zeros((100, 100, 3), dtype=np.uint8)
    with zipfile.ZipFile(path, "w") as z:
        for split, index in (("train", TRAIN), ("val", VAL), ("test", test_index)):
            z.writestr(f"REFUGE/{split}/index.json", json.dumps(index).encode())
            for entry in index.values():
                stem = entry["ImgName"].rsplit(".", 1)[0]
                z.writestr(f"REFUGE/{split}/Images/{stem}.jpg", encoded(photograph, "JPEG"))
                z.writestr(f"REFUGE/{split}/Images_Cropped/{stem}.jpg", encoded(photograph, "JPEG"))
                z.writestr(f"REFUGE/{split}/gts/{stem}.bmp", encoded(a_mask(), "BMP"))
                z.writestr(f"REFUGE/{split}/Masks/{stem}.png", encoded(a_mask() // 100, "PNG"))
        z.writestr("REFUGE/Images_Square/n0001.png", encoded(photograph, "PNG"))
        z.writestr("REFUGE/train/illustrations/g0001.png", encoded(photograph, "PNG"))
        z.writestr("models/refuge_segmentation.pth", b"weights")
    return path


def records(tmp_path, **kwargs):
    return {r.key: r for r in refuge.discover({refuge.SLUG: a_bundle(tmp_path, **kwargs)})}


def test_it_refuses_to_download_and_asks_for_the_archive():
    with pytest.raises(PermissionError, match="--archive"):
        refuge.SOURCES[0].obtain(None)


def test_the_bundle_is_read_where_it_lies():
    assert refuge.SOURCES[0].extract_it is False


def test_every_photograph_of_every_split_is_built_and_keyed_by_its_split(tmp_path):
    assert set(records(tmp_path)) == {"train_g0001", "train_n0001", "val_v0001", "test_t0001"}


def test_the_split_is_the_one_the_bundle_publishes(tmp_path):
    found = records(tmp_path)
    assert (found["train_g0001"].split, found["test_t0001"].split) == ("train", "test")


def test_the_camera_is_the_subset(tmp_path):
    found = records(tmp_path)
    assert found["train_g0001"].subset == "visucam500"
    assert found["val_v0001"].subset == "cr2"
    assert found["test_t0001"].subset == "cr2"


def test_the_photograph_is_the_challenges_not_a_derived_copy(tmp_path):
    assert records(tmp_path)["train_g0001"].image.name == "REFUGE/train/Images/g0001.jpg"


def test_the_label_is_spelled_out_and_left_empty_where_none_is_published(tmp_path):
    found = records(tmp_path)
    assert found["train_g0001"].disease == "glaucoma"
    assert found["train_n0001"].disease == "normal"
    assert found["test_t0001"].disease == ""


def test_the_fovea_travels_in_the_published_photographs_own_pixels(tmp_path):
    found = records(tmp_path)
    assert found["train_g0001"].extras == {"fovea_x": "10.5", "fovea_y": "12.0"}
    assert found["test_t0001"].extras == {"fovea_x": "", "fovea_y": ""}


def test_the_outlines_come_from_the_challenges_own_masks(tmp_path):
    outlines = records(tmp_path)["train_g0001"].outlines
    assert outlines[("disc", refuge.READER)].source.name == "REFUGE/train/gts/g0001.bmp"


def test_the_cup_is_zero_and_the_disc_is_zero_and_128(tmp_path):
    outlines = records(tmp_path)["train_g0001"].outlines
    mask = a_mask()
    assert (outlines[("cup", refuge.READER)].mask_from(mask) > 0).sum() == (mask == 0).sum()
    assert (outlines[("disc", refuge.READER)].mask_from(mask) > 0).sum() == (mask < 255).sum()


def test_a_label_the_legend_does_not_explain_is_refused(tmp_path):
    index = {"0": {"ImgName": "T0001.jpg", "Size_X": 1634, "Size_Y": 1634, "Label": 3}}
    with pytest.raises(ValueError, match="3"):
        records(tmp_path, test_index=index)


def test_a_bundle_missing_a_split_says_so(tmp_path):
    path = tmp_path / "partial.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("REFUGE/train/index.json", json.dumps(TRAIN).encode())
    with pytest.raises(ValueError, match="val/index.json"):
        refuge.discover({refuge.SLUG: path})


def test_the_route_recorded_is_the_kaggle_bundle_not_the_official_host():
    assert refuge.SOURCES[0].url == "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"
    assert refuge.SOURCES[0].manual, "declared, never downloaded: Kaggle needs an account"
