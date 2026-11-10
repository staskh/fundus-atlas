# ABOUTME: Tests for the ORIGA fetcher, which cannot download and must be given a bundle by hand.
# ABOUTME: The bundle is read where it lies, and its uploader's derived copies are not mistaken for it.

import csv
import io
import zipfile

import numpy as np
import pytest
from PIL import Image

from datasets import origa
from datasets.utils import archives, contours

ROWS = [
    {"Eye": "OD", "Filename": "001.jpg", "ExpCDR": "0.5", "Set": "A", "Glaucoma": "0"},
    {"Eye": "OS", "Filename": "002.jpg", "ExpCDR": "0.7", "Set": "B", "Glaucoma": "1"},
]


def png(pixels: np.ndarray, fmt: str = "PNG") -> bytes:
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format=fmt)
    return out.getvalue()


def a_mask() -> np.ndarray:
    """What the bundle publishes: 0 outside, 1 the rim, 2 the cup."""
    yy, xx = np.mgrid[0:200, 0:200]
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 60**2] = 1
    mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 30**2] = 2
    return mask


def a_sheet(rows) -> bytes:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def a_bundle(tmp_path, rows=ROWS, with_masks=True, under="ORIGA"):
    """A zip laid out as the Kaggle bundle is: ORIGA beside G1020 and REFUGE, with the uploader's
    own cropped and squared copies in folders whose names also start with ``Images``."""
    path = tmp_path / "bundle.zip"
    photograph = np.zeros((200, 200, 3), dtype=np.uint8)
    with zipfile.ZipFile(path, "w") as z:
        for row in rows:
            stem = row["Filename"].rsplit(".", 1)[0]
            z.writestr(f"{under}/Images/{stem}.jpg", png(photograph, "JPEG"))
            z.writestr(f"{under}/Images_Cropped/{stem}.jpg", png(photograph[:50, :50], "JPEG"))
            z.writestr(f"{under}/Images_Square/{stem}.jpg", png(photograph[:80, :80], "JPEG"))
            if with_masks:
                z.writestr(f"{under}/Masks/{stem}.png", png(a_mask()))
                z.writestr(f"{under}/Masks_Cropped/{stem}.png", png(a_mask()[:50, :50]))
        z.writestr(f"{under}/Images_Square/._001.jpg", b"mac rubbish")
        z.writestr(f"{under}/OrigaList.csv", a_sheet(rows))
        z.writestr(f"{under}/origa_info.csv", b"Image,Source,CDR,Label\n/x/001.jpg,Origa,0.5,0\n")
        z.writestr("G1020/G1020.csv", b"imageID,binaryLabels\nimage_0.jpg,0\n")
        z.writestr("G1020/Images/image_0.jpg", png(photograph, "JPEG"))
    return path


def records(tmp_path, **kwargs):
    return {r.key: r for r in origa.discover({origa.SLUG: a_bundle(tmp_path, **kwargs)})}


def test_it_refuses_to_download_and_asks_for_the_archive():
    with pytest.raises(PermissionError, match="--archive"):
        origa.SOURCES[0].obtain(None)


def test_the_bundle_is_read_where_it_lies():
    assert origa.SOURCES[0].extract_it is False


def test_the_spreadsheet_is_found_by_the_column_that_matters(tmp_path):
    assert set(records(tmp_path)) == {"001", "002"}


def test_the_photograph_is_the_one_in_images_not_the_uploaders_cropped_copy(tmp_path):
    found = records(tmp_path)
    assert found["001"].image.name == "ORIGA/Images/001.jpg"


def test_the_mask_is_the_one_in_masks_not_the_uploaders_cropped_copy(tmp_path):
    disc = records(tmp_path)["001"].outlines[("disc", origa.READER)]
    assert disc.source.name == "ORIGA/Masks/001.png"


def test_the_graders_own_ratio_is_carried(tmp_path):
    assert records(tmp_path)["001"].extras["expert_cdr"] == "0.5"


def test_the_eye_and_the_diagnosis_are_translated(tmp_path):
    found = records(tmp_path)
    assert (found["001"].eye, found["001"].disease) == ("od", "normal")
    assert (found["002"].eye, found["002"].disease) == ("os", "glaucoma")


def test_the_cup_is_two_and_the_disc_is_one_and_two(tmp_path):
    outlines = records(tmp_path)["001"].outlines
    mask = a_mask()
    cup = outlines[("cup", origa.READER)].mask_from(mask) > 0
    disc = outlines[("disc", origa.READER)].mask_from(mask) > 0
    assert cup.sum() == (mask == 2).sum()
    assert disc.sum() == (mask > 0).sum()


def test_a_bundle_that_moved_its_folders_still_builds(tmp_path):
    assert set(records(tmp_path, under="origa-650")) == {"001", "002"}


def test_the_other_datasets_in_the_bundle_are_left_to_their_own_fetchers(tmp_path):
    assert all(not key.startswith("image") for key in records(tmp_path))


def test_a_photograph_with_no_mask_is_built_and_said_so(tmp_path):
    record = records(tmp_path, with_masks=False)["001"]
    assert record.outlines == {}
    assert "no disc and cup mask" in record.notes


def test_a_bundle_without_origa_says_so_rather_than_building_nothing(tmp_path):
    path = tmp_path / "bare.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("G1020/G1020.csv", b"imageID,binaryLabels\nx.jpg,1\n")
    with pytest.raises(ValueError, match="expcdr"):
        origa.discover({origa.SLUG: path})


def test_a_handle_is_what_the_outlines_carry(tmp_path):
    outlines = records(tmp_path)["001"].outlines
    assert isinstance(outlines[("disc", origa.READER)].source, archives.Member)


def test_the_studys_own_a_and_b_sets_are_the_subsets(tmp_path):
    found = records(tmp_path)
    assert (found["001"].subset, found["002"].subset) == ("a", "b")


def test_a_sheet_with_no_sets_gives_one_subset(tmp_path):
    rows = [{"Filename": "001.jpg", "ExpCDR": "0.5", "Eye": "OD", "Glaucoma": "0"}]
    assert records(tmp_path, rows=rows)["001"].subset == "main"


def test_the_vertical_ratio_is_the_cups_height_over_the_discs():
    drawn = {
        ("disc", origa.READER): np.array([[0, 0], [10, 0], [10, 100], [0, 100]], dtype=float),
        ("cup", origa.READER): np.array([[2, 20], [8, 20], [8, 70], [2, 70]], dtype=float),
    }
    assert origa.vertical_cdr(drawn) == pytest.approx(0.5)


def test_the_ratio_is_unknown_without_both_structures():
    drawn = {("disc", origa.READER): np.array([[0, 0], [10, 0], [10, 100]], dtype=float)}
    assert origa.vertical_cdr(drawn) is None


def test_the_build_is_checked_against_the_graders_ratio(tmp_path):
    store = tmp_path / "store"
    where = store / "crop" / "contours"
    square = np.array([[0, 0], [10, 0], [10, 100], [0, 100]], dtype=float)
    contours.write(
        where / "001.csv",
        {("disc", origa.READER): square, ("cup", origa.READER): square * [1, 0.5]},
    )
    contours.write(
        where / "002.csv",
        {("disc", origa.READER): square, ("cup", origa.READER): square * [1, 0.2]},
    )
    rows = [{"key": "001", "expert_cdr": "0.5"}, {"key": "002", "expert_cdr": "0.7"}]
    found = origa.verify(store, {}, rows)
    assert found["checked"] == 2
    assert found["disagree_by_more_than_0.05"] == ["002"]


def test_the_route_recorded_is_the_kaggle_bundle_not_the_official_host():
    assert origa.SOURCES[0].url == "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"
    assert origa.SOURCES[0].manual, "declared, never downloaded: Kaggle needs an account"
