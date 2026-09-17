# ABOUTME: Tests for the HRF fetcher: one set of photographs with three provenances, the disease in
# ABOUTME: every filename, and an artery/vein layer a second group added years later.

import io
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from datasets import hrf
from datasets.utils import fov

STEMS = ["01_dr", "01_g", "01_h", "02_dr"]


def an_image(size=(60, 40), colour=(120, 60, 30)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[6:34, 10:50] = colour
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_mask(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0]), dtype=np.uint8)
    pixels[6:34, 10:50] = 255
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def an_av_map(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[10:12, 12:48] = (255, 0, 0)
    pixels[20:22, 12:48] = (0, 0, 255)
    pixels[15:17, 20:24] = (0, 255, 0)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def layers(tmp_path: Path, with_av: bool = True) -> dict[str, Path]:
    archive = tmp_path / "all.zip"
    with zipfile.ZipFile(archive, "w") as held:
        for stem in STEMS:
            held.writestr(f"images/{stem}.jpg", an_image())
            held.writestr(f"manual1/{stem}.tif", a_mask())
            held.writestr(f"mask/{stem}_mask.tif", a_mask())
    found = {hrf.SLUG: archive}
    if with_av:
        tree = tmp_path / "hrf-av"
        (tree / hrf.AV_FOLDER).mkdir(parents=True)
        for stem in STEMS:
            (tree / hrf.AV_FOLDER / f"{stem}_AVmanual.png").write_bytes(an_av_map())
        found[hrf.AV_LAYER] = tree
    return found


def records(tmp_path: Path, **kwargs):
    return {record.key: record for record in hrf.discover(layers(tmp_path, **kwargs))}


def test_every_photograph_carries_its_vessels_its_field_and_its_arteries(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert sorted(found) == ["01_dr", "01_g", "01_h", "02_dr"]
    assert sorted(found["01_dr"].maps) == ["av", "fov", "vessels"]


def test_the_disease_comes_from_the_name_the_authors_gave_the_file(tmp_path: Path) -> None:
    """`_dr`, `_g` and `_h` are the dataset's own three groups of fifteen."""
    found = records(tmp_path)

    assert found["01_dr"].disease == "diabetic retinopathy"
    assert found["01_g"].disease == "glaucoma"
    assert found["01_h"].disease == "healthy"


def test_the_artery_vein_layer_is_optional_and_its_absence_is_recorded(tmp_path: Path) -> None:
    """It is a second group's work from a repository with no licence, so a build must survive
    without it rather than refusing to produce the vessel dataset HRF itself published."""
    found = records(tmp_path, with_av=False)

    assert sorted(found["01_dr"].maps) == ["fov", "vessels"]
    assert "artery/vein" in found["01_dr"].notes


def test_the_palette_is_the_one_that_repository_publishes() -> None:
    masks = hrf.PALETTE.masks(
        np.array([[[255, 0, 0], [0, 0, 255], [0, 255, 0], [0, 0, 0]]], np.uint8), "av"
    )

    assert list(masks["artery"][0] > 0) == [True, False, True, False], "artery and the crossing"
    assert list(masks["vein"][0] > 0) == [False, True, True, False]
    assert list(masks["vessels"][0] > 0) == [True, True, True, False]


def test_the_vessel_gold_standard_is_the_authors_own_and_not_the_union(tmp_path: Path) -> None:
    """The store keeps HRF's hand-drawn `manual1` tracing, never the artery/vein union.

    The two turn out to be the same tracing — they differ by 0.004% of pixels across the dataset,
    because HRF-AV coloured HRF's own gold standard — but which file the store holds still has to be
    the published one, so that the page's claim can be checked rather than assumed.
    """
    found = records(tmp_path)

    assert "manual1" in str(found["01_dr"].maps["vessels"].name)


def test_the_field_of_view_mask_is_the_published_one(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert "mask" in str(found["01_dr"].maps["fov"].name)
    assert hrf.FOV_STRATEGY == fov.FROM_MASK
