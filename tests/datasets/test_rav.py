# ABOUTME: Tests for the RAV fetcher: what it finds in the Dataverse archive, how it reads the
# ABOUTME: camera and the participants from the metadata, and how it reads the layered masks.

import io
import zipfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from datasets import rav

CAMERAS = {
    "193067": "TOPCON 3D OCT-1000",
    "545431": "TOPCON TRC-50EX + DXC-950P",
    "697308": "TOPCON TRC-50EX + DXC-950P",
}


def a_png(pixels: np.ndarray) -> bytes:
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_photograph() -> bytes:
    pixels = np.zeros((64, 64, 3), dtype=np.uint8)
    ys, xs = np.ogrid[:64, :64]
    pixels[(ys - 32) ** 2 + (xs - 32) ** 2 < 30**2] = (180, 90, 40)
    return a_png(pixels)


def a_map() -> bytes:
    pixels = np.zeros((64, 64, 3), dtype=np.uint8)
    pixels[10:14, 8:56, 0] = 255
    pixels[20:24, 8:56, 2] = 255
    pixels[30:32, 30:34, 1] = 255
    return a_png(pixels)


def an_archive(
    tmp_path: Path, undescribed: str = "", unmapped: str = "", cameras: dict | None = None
) -> Path:
    """The shape DataverseNL serves: `dataset/` with `rgb/`, `av_masks/` and `metadata.csv`."""
    cameras = cameras or CAMERAS
    metadata = "id,device,patient_age,patient_sex\n" + "".join(
        f"{key},{camera},{60 + index},{'MF'[index % 2]}\n"
        for index, (key, camera) in enumerate(cameras.items())
    )
    path = tmp_path / "doi-10.34894-9oimwy.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("MANIFEST.TXT", "dataset/README (text/plain)\n")
        archive.writestr("dataset/README", "# Rotterdam Artery-vein Segmentation Dataset\n")
        archive.writestr("dataset/metadata.csv", metadata)
        for key in [*cameras, *([undescribed] if undescribed else [])]:
            archive.writestr(f"dataset/rgb/RAV_{key}.png", a_photograph())
            if key != unmapped:
                archive.writestr(f"dataset/av_masks/RAV_{key}.png", a_map())
    return path


def records(tmp_path: Path, **kwargs):
    found = rav.discover({rav.SLUG: an_archive(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_every_photograph_becomes_a_record_with_its_map(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert sorted(found) == ["rav_193067", "rav_545431", "rav_697308"]
    assert set(found["rav_193067"].maps) == {"av"}


def test_no_split_is_invented(tmp_path: Path) -> None:
    """The authors publish none."""
    assert {record.split for record in records(tmp_path).values()} == {"unspecified"}


def test_the_camera_is_the_subset(tmp_path: Path) -> None:
    """Every photograph is 1024 square, so the camera is the only thing that tells two apart."""
    found = records(tmp_path)

    assert found["rav_193067"].subset == "topcon_3d_oct_1000"
    assert found["rav_545431"].subset == found["rav_697308"].subset == "topcon_trc_50ex_dxc_950p"


def test_a_camera_name_becomes_a_subset_name() -> None:
    assert rav.subset_of("TOPCON TRC-50VT - Analog Fundus Camera") == (
        "topcon_trc_50vt_analog_fundus_camera"
    )


def test_the_participant_is_recorded_as_the_metadata_writes_it(tmp_path: Path) -> None:
    extras = records(tmp_path)["rav_193067"].extras

    assert extras == {"patient_age": "60", "patient_sex": "M"}


def test_a_photograph_the_metadata_never_mentions_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(LookupError, match="999999"):
        records(tmp_path, undescribed="999999")


def test_a_photograph_without_a_map_keeps_its_row_and_says_so(tmp_path: Path) -> None:
    record = records(tmp_path, unmapped="545431")["rav_545431"]

    assert record.maps == {}
    assert "no artery/vein map" in record.notes


def test_the_masks_are_read_as_layers_red_artery_blue_vein_green_unknown() -> None:
    pixels = np.array([[[255, 0, 0], [0, 0, 255], [255, 0, 255], [0, 255, 0]]], dtype=np.uint8)
    masks = rav.LAYERS.masks(pixels)

    assert list(masks["artery"][0]) == [255, 0, 255, 0]
    assert list(masks["vein"][0]) == [0, 255, 255, 0]
    assert list(masks["vessels"][0]) == [255, 255, 255, 255]


def test_the_download_is_direct_and_carries_no_checksum() -> None:
    """DataverseNL zips the record on request, so the bytes are not stable to check against."""
    (source,) = rav.SOURCES

    assert source.url and not source.manual
    assert source.sha256 == ""
