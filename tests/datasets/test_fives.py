# ABOUTME: Tests for the FIVES fetcher against a synthetic copy of its unpacked archive.
# ABOUTME: The diagnosis is in the filename and the grade is derived, since none is published.

import numpy as np
import openpyxl
import pytest
from PIL import Image

from datasets import fives
from datasets.utils import quality


def a_tree(tmp_path, rows=None, ungraded=()):
    """The shape the RAR unpacks into, one directory deep.

    :param ungraded: photographs to put in the tree but leave out of the quality sheet.
    """
    root = tmp_path / "FIVES A Fundus Image Dataset"
    rows = rows or [
        ("Train", "A", 1, 1, 1, 1),
        ("Train", "G", 137, 0, 1, 1),
        ("Test", "N", 5, 0, 0, 1),
        ("Test", "D", 9, 0, 0, 0),
    ]
    for split in ("train", "test"):
        (root / split / fives.PHOTOGRAPHS).mkdir(parents=True)
        (root / split / fives.VESSELS).mkdir(parents=True)
    for tab, letter, number, *_ in rows:
        name = f"{number}_{letter}.png"
        split = tab.lower()
        Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8)).save(
            root / split / fives.PHOTOGRAPHS / name
        )
        Image.fromarray(np.zeros((16, 16), dtype=np.uint8)).save(
            root / split / fives.VESSELS / name
        )
    for split, letter, number in ungraded:
        Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8)).save(
            root / split / fives.PHOTOGRAPHS / f"{number}_{letter}.png"
        )
        Image.fromarray(np.zeros((16, 16), dtype=np.uint8)).save(
            root / split / fives.VESSELS / f"{number}_{letter}.png"
        )
    # The stray file the dataset page records, which a loader listing by extension must not take.
    (root / "train" / fives.PHOTOGRAPHS / "Thumbs.db").write_bytes(b"not an image")

    book = openpyxl.Workbook()
    book.active.title = "Train"
    book.create_sheet("Test")
    for tab in ("Train", "Test"):
        book[tab].append(["Disease", "Number", "IC", "Blur", "LC"])
    for tab, letter, number, ic, blur, lc in rows:
        book[tab].append([letter, number, ic, blur, lc])
    book.save(root / fives.QUALITY_SHEET)
    return tmp_path


def records(tmp_path, **kwargs):
    found = fives.discover({"fives": a_tree(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_the_key_carries_the_split_the_number_and_the_diagnosis(tmp_path):
    assert set(records(tmp_path)) == {"train_1_a", "train_137_g", "test_5_n", "test_9_d"}


def test_the_diagnosis_comes_from_the_letter_in_the_filename(tmp_path):
    found = records(tmp_path)
    assert found["train_137_g"].disease == "glaucoma"
    assert found["test_5_n"].disease == "normal"
    assert found["train_1_a"].disease == "age-related macular degeneration"


def test_every_photograph_has_its_vessel_mask(tmp_path):
    record = records(tmp_path)["train_1_a"]
    assert record.maps["vessels"].name == "1_A.png"
    assert record.maps["vessels"].parent.name == fives.VESSELS


def test_the_stray_thumbs_file_is_not_taken_for_a_photograph(tmp_path):
    assert all("thumbs" not in key for key in records(tmp_path))


def test_the_three_components_are_stored_in_words(tmp_path):
    extras = records(tmp_path)["train_137_g"].extras
    assert extras == {"illumination_contrast": "bad", "blur": "good", "low_contrast": "good"}


def test_the_grade_is_derived_because_none_is_published(tmp_path):
    found = records(tmp_path)
    grade = fives.QUALITY.grade
    assert grade(found["train_1_a"].extras) == ("good", "derived")
    assert grade(found["train_137_g"].extras) == ("usable", "derived")
    assert grade(found["test_5_n"].extras) == ("bad", "derived")
    assert grade(found["test_9_d"].extras) == ("bad", "derived")


def test_the_components_are_what_the_rule_is_declared_over():
    assert isinstance(fives.QUALITY, quality.FromComponents)
    assert set(fives.QUALITY.best) == {column.name for column in fives.EXTRA_COLUMNS}


def test_a_photograph_with_no_quality_row_is_an_error_rather_than_a_silent_blank(tmp_path):
    # Every photograph is graded; one that is not means the sheet and the archive have come apart,
    # which is worth stopping for rather than recording as an ungraded image.
    with pytest.raises(KeyError):
        records(tmp_path, ungraded=[("train", "A", 999)])


def test_no_resolution_is_claimed():
    assert fives.RESOLUTION.um_per_px is None
