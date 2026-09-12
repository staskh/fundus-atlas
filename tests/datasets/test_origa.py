# ABOUTME: Tests for the ORIGA fetcher, which cannot download and must be given a bundle by hand.
# ABOUTME: The bundle's layout is found rather than addressed, since it is a third party's packaging.

import csv

import numpy as np
import pytest
from PIL import Image

from datasets import origa
from datasets.utils import archives


def a_bundle(tmp_path, rows=None, with_masks=True, under="ORIGA"):
    """A third-party bundle carrying ORIGA beside other datasets."""
    rows = rows or [
        {"Filename": "001.jpg", "ExpCDR": "0.512", "Eye": "1", "Glaucoma": "0", "Set": "A"},
        {"Filename": "002.jpg", "ExpCDR": "0.703", "Eye": "2", "Glaucoma": "1", "Set": "B"},
    ]
    root = tmp_path / "bundle"
    images = root / under / "Images"
    masks = root / under / "Masks"
    images.mkdir(parents=True)
    masks.mkdir(parents=True)

    yy, xx = np.mgrid[0:200, 0:200]
    for row in rows:
        stem = row["Filename"].rsplit(".", 1)[0]
        Image.fromarray(np.zeros((200, 200, 3), dtype=np.uint8)).save(images / f"{stem}.jpg")
        if with_masks:
            mask = np.zeros((200, 200), dtype=np.uint8)
            mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 60**2] = 128
            mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 30**2] = 255
            Image.fromarray(mask).save(masks / f"{stem}.png")

    with open(root / under / "OrigaList.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # The rest of the bundle, which belongs to other datasets and other fetchers.
    (root / "G1020" / "Images").mkdir(parents=True)
    Image.fromarray(np.zeros((10, 10, 3), dtype=np.uint8)).save(root / "G1020" / "Images" / "x.jpg")
    return root


def records(tmp_path, **kwargs):
    return {r.key: r for r in origa.discover({"origa": a_bundle(tmp_path, **kwargs)})}


def test_it_refuses_to_download_and_asks_for_the_archive():
    with pytest.raises(PermissionError, match="--archive"):
        origa.SOURCES[0].obtain(None)


def test_the_spreadsheet_is_found_by_the_column_that_matters(tmp_path):
    assert set(records(tmp_path)) == {"001", "002"}


def test_the_graders_own_ratio_is_carried(tmp_path):
    assert records(tmp_path)["001"].extras["expert_cdr"] == "0.512"


def test_the_eye_and_the_diagnosis_are_translated(tmp_path):
    found = records(tmp_path)
    assert (found["001"].eye, found["001"].disease) == ("od", "normal")
    assert (found["002"].eye, found["002"].disease) == ("os", "glaucoma")


def test_both_structures_come_out_of_the_one_published_mask(tmp_path):
    outlines = records(tmp_path)["001"].outlines
    assert set(outlines) == {("disc", origa.READER), ("cup", origa.READER)}
    assert outlines[("cup", origa.READER)].values == origa.CUP
    assert outlines[("disc", origa.READER)].values == origa.DISC


def test_the_cup_is_the_inner_value_and_the_disc_is_both(tmp_path):
    outlines = records(tmp_path)["001"].outlines
    mask = np.asarray(Image.open(outlines[("disc", origa.READER)].source.path).convert("L"))
    disc = outlines[("disc", origa.READER)].mask_from(mask)
    cup = outlines[("cup", origa.READER)].mask_from(mask)
    assert (cup > 0).sum() < (disc > 0).sum()


def test_a_bundle_that_moved_its_folders_still_builds(tmp_path):
    assert set(records(tmp_path, under="origa-650")) == {"001", "002"}


def test_the_other_datasets_in_the_bundle_are_left_to_their_own_fetchers(tmp_path):
    assert all("x" != key for key in records(tmp_path))


def test_a_photograph_with_no_mask_is_built_and_said_so(tmp_path):
    record = records(tmp_path, with_masks=False)["001"]
    assert record.outlines == {}
    assert "no disc and cup mask" in record.notes


def test_a_bundle_without_origa_says_so_rather_than_building_nothing(tmp_path):
    bare = tmp_path / "bare"
    (bare / "G1020").mkdir(parents=True)
    with open(bare / "G1020" / "list.csv", "w", newline="") as f:
        f.write("Filename,Glaucoma\nx.jpg,1\n")
    with pytest.raises(ValueError, match="expcdr"):
        origa.discover({"origa": bare})


def test_a_handle_is_what_the_outlines_carry(tmp_path):
    outlines = records(tmp_path)["001"].outlines
    assert isinstance(outlines[("disc", origa.READER)].source, archives.File)


def test_the_studys_own_a_and_b_sets_are_the_subsets(tmp_path):
    found = records(tmp_path)
    assert (found["001"].subset, found["002"].subset) == ("a", "b")


def test_a_sheet_with_no_sets_gives_one_subset(tmp_path):
    rows = [{"Filename": "001.jpg", "ExpCDR": "0.5", "Eye": "1", "Glaucoma": "0"}]
    assert records(tmp_path, rows=rows)["001"].subset == "main"
