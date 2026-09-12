# ABOUTME: Tests for the MSHF fetcher against a synthetic copy of its archive.
# ABOUTME: Three readers, six groups, an ultra-wide-field split to leave alone, and an empty tab.

import zipfile

import openpyxl

from datasets import mshf
from datasets.utils import manifest

HEAD = ["image name", "illumination", "clarity", "contrast", "Overall"]


def an_archive(tmp_path, agreed=True):
    """The shape figshare serves, including the tab that holds an all-zero table."""
    root = mshf.ROOT
    photographs = {
        "DR-XJU": ["DR-XJU-1.jpg", "DR-XJU-30.jpg"],
        "DR-ZJU": ["DR-ZJU-1.jpg"],
        "Local1": ["Local1-1.jpg"],
        "UWF-mosaic": ["UWF-mosaic-1.jpg"],
    }

    scores = openpyxl.Workbook()
    scores.active.title = "DR-XJU"
    scores["DR-XJU"].append(HEAD)
    if agreed:
        scores["DR-XJU"].append(["DR-XJU-1.jpg", 1, 1, 1, 1])
        scores["DR-XJU"].append(["DR-XJU-30.jpg", 0, 1, 1, 1])
    empty = scores.create_sheet(mshf.EMPTY_TAB)
    empty.append(["image name", "gold standard", None, None, None])
    empty.append([None, "illumination", "clarity", "contrast", "Overall"])
    for names in photographs.values():
        for name in names:
            empty.append([name, 0, 0, 0, 0])
    agreed_path = tmp_path / "agreed.xlsx"
    scores.save(agreed_path)

    individual = openpyxl.Workbook()
    sheet = individual.active
    sheet.title = "Sheet1"
    sheet.append(["image name", "annotator 1", None, None, None, None, "annotator 2"])
    sheet.append([None, *HEAD[1:], None, *HEAD[1:], None, *HEAD[1:]])
    readings = {
        "DR-XJU-1.jpg": [(1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1)],
        "DR-XJU-30.jpg": [(0, 1, 1, 1), (0, 1, 1, 1), (0, 1, 1, 1)],
        "DR-ZJU-1.jpg": [(1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1)],
        "Local1-1.jpg": [(1, 1, 1, 0), (0, 0, 0, 1), (1, 1, 1, 1)],
        "UWF-mosaic-1.jpg": [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)],
    }
    for name, (one, two, three) in readings.items():
        sheet.append([name, *one, None, *two, None, *three])
    individual_path = tmp_path / "individual.xlsx"
    individual.save(individual_path)

    path = tmp_path / "MSHF.zip"
    with zipfile.ZipFile(path, "w") as zf:
        for group, names in photographs.items():
            for name in names:
                zf.writestr(f"{root}/Original/{_where(group)}/{name}", b"photograph")
                half = "test" if name.endswith("30.jpg") else "train"
                stem = name.rsplit(".", 1)[0]
                zf.writestr(f"{root}/AI-use/{half}/{stem}.png", b"a copy under another extension")
        zf.write(agreed_path, mshf.AGREED)
        zf.write(individual_path, mshf.INDIVIDUAL)
        zf.writestr(f"__MACOSX/{root}/._.DS_Store", b"junk")
    return path


def _where(group):
    if group == "UWF-mosaic":
        return group
    return f"{'Portable_camera' if group.startswith('Local') else 'CFP'}/{group}"


def records(tmp_path, **kwargs):
    found = mshf.discover({"mshf": an_archive(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_the_ultra_widefield_mosaics_are_not_built(tmp_path):
    assert not any("uwf" in key for key in records(tmp_path))


def test_the_device_class_is_the_subset(tmp_path):
    found = records(tmp_path)
    assert found["train_dr_xju_1"].subset == "cfp"
    assert found["train_local1_1"].subset == "portable"


def test_the_group_carries_the_disease_it_was_collected_for(tmp_path):
    found = records(tmp_path)
    assert found["train_dr_xju_1"].disease == "diabetic retinopathy"
    assert found["train_local1_1"].disease == ""
    assert found["train_dr_xju_1"].extras["group"] == "DR-XJU"


def test_the_split_is_matched_without_the_extension(tmp_path):
    # Two photographs are .jpg among the originals and .png in the split.
    assert "test_dr_xju_30" in records(tmp_path)


def test_all_three_readers_are_kept_apart_on_every_component(tmp_path):
    readings = records(tmp_path)["train_dr_xju_1"].readings
    assert {r.field for r in readings} == {"illumination", "clarity", "contrast", "quality"}
    assert {r.reader for r in readings} == {
        "annotator1",
        "annotator2",
        "annotator3",
        manifest.CONSENSUS,
    }


def test_the_all_zero_table_is_never_read_as_an_agreed_score(tmp_path):
    # Every row of that table says 0, 0, 0, 0. Reading it would mark the whole dataset unusable.
    readings = records(tmp_path, agreed=False)["train_dr_xju_1"].readings
    assert manifest.CONSENSUS not in {r.reader for r in readings}
    assert {r.value for r in readings} == {"good"}


def test_a_group_with_no_agreed_score_says_so(tmp_path):
    found = records(tmp_path)
    assert "no agreed score" in found["train_dr_zju_1"].notes
    assert found["train_dr_xju_1"].notes == ""


def test_a_binary_score_is_stored_in_the_same_words_as_every_other_dataset(tmp_path):
    readings = records(tmp_path)["train_local1_1"].readings
    values = {(r.field, r.reader): r.value for r in readings}
    assert values[("quality", "annotator1")] == "bad"
    assert values[("quality", "annotator2")] == "good"


def test_no_resolution_is_claimed():
    assert mshf.RESOLUTION.um_per_px is None
