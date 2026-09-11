# ABOUTME: Tests for the DeepDRiD fetcher against a synthetic copy of its published layout.
# ABOUTME: Never touches the real archive: the point is the label wiring, not the photographs.

import csv

import openpyxl
import pytest

from datasets import deepdrid
from datasets.utils import quality

TRAIN_HEADER = [
    "patient_id",
    "image_id",
    "image_path",
    "Overall quality",
    "left_eye_DR_Level",
    "right_eye_DR_Level",
    "patient_DR_Level",
    "Clarity",
    "Field definition",
    "Artifact",
]


def a_release(root):
    """The two-CSV training layout and the two-spreadsheet evaluation layout."""
    train = root / "regular_fundus_images" / "regular-fundus-training"
    (train / "Images" / "1").mkdir(parents=True)
    with open(train / "regular-fundus-training.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(TRAIN_HEADER)
        w.writerow(["1", "1_l1", r"\x\1_l1.jpg", "1", "3", "", "3", "10", "8", "0"])
        w.writerow(["1", "1_r1", r"\x\1_r1.jpg", "0", "", "2", "3", "6", "8", "4"])
    with open(train / "regular-fundus-source-training.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["patient_id", "image_id", "image_path", "Source"])
        w.writerow(["1", "1_l1", "", "Nicheng"])
        w.writerow(["1", "1_r1", "", "Nicheng"])

    test = root / "regular_fundus_images" / "Online-Challenge1&2-Evaluation"
    test.mkdir(parents=True)
    grades = openpyxl.Workbook()
    grades.active.append(["image_id", "DR_Levels"])
    grades.active.append(["347_l2", 4])
    grades.save(test / "Challenge1_labels.xlsx")
    scores = openpyxl.Workbook()
    scores.active.append(["image_id", "Overall quality", "Artifact", "Clarity", "Field definition"])
    scores.active.append(["347_l2", 0, 8, 6, 8])
    scores.save(test / "Challenge2_labels.xlsx")

    validation = root / "regular_fundus_images" / "regular-fundus-validation"
    (validation / "Images").mkdir(parents=True)
    for name in ("regular-fundus-validation.csv", "regular-fundus-source-validation.csv"):
        with open(validation / name, "w", newline="") as f:
            csv.writer(f).writerow(TRAIN_HEADER if "source" not in name else ["image_id", "Source"])
    return root


def records(tmp_path):
    return {r.key: r for r in deepdrid.discover(a_release(tmp_path))}


def test_the_key_carries_the_split_the_authors_published(tmp_path):
    assert set(records(tmp_path)) == {"train_1_l1", "train_1_r1", "test_347_l2"}


def test_the_grade_taken_is_the_one_for_this_eye(tmp_path):
    found = records(tmp_path)
    assert (found["train_1_l1"].eye, found["train_1_l1"].disease) == ("os", "severe npdr")
    assert (found["train_1_r1"].eye, found["train_1_r1"].disease) == ("od", "moderate npdr")


def test_the_view_number_is_kept_because_two_views_are_one_eye(tmp_path):
    found = records(tmp_path)
    assert found["train_1_l1"].patient == "1"
    assert found["train_1_l1"].extras["view"] == "1"
    assert found["test_347_l2"].extras["view"] == "2"


def test_the_quality_subscores_are_carried_verbatim(tmp_path):
    extras = records(tmp_path)["train_1_r1"].extras
    assert extras["artifact"] == "4"
    assert extras["clarity"] == "6"
    assert extras["field_definition"] == "8"
    assert extras["overall_quality"] == "not good enough for diagnosis"


def test_the_evaluation_split_has_no_screening_project_or_patient_grade(tmp_path):
    extras = records(tmp_path)["test_347_l2"].extras
    assert extras["screening_project"] == ""
    assert extras["patient_dr_level"] == ""


def test_the_published_grade_decides_quality_not_the_subscores(tmp_path):
    found = records(tmp_path)
    # 1_l1 is perfect on clarity but not on field definition; the authors still called it usable
    # for diagnosis, and their verdict is the one that counts.
    assert deepdrid.QUALITY.grade(found["train_1_l1"].extras) == ("good", "published")
    assert deepdrid.QUALITY.grade(found["train_1_r1"].extras) == ("bad", "published")


def test_a_grade_is_stored_as_the_word_the_authors_gave_it(tmp_path):
    # A bare 3 in a manifest tells a reader nothing, and 0 is one misreading away from "no value".
    # The release's Readme says what each level means, so that wording is what the cell holds.
    found = records(tmp_path)
    assert found["train_1_l1"].extras["patient_dr_level"] == "severe npdr"
    assert found["test_347_l2"].disease == "pdr"


def test_every_declared_column_is_filled_by_every_record(tmp_path):
    declared = {column.name for column in deepdrid.EXTRA_COLUMNS}
    for record in records(tmp_path).values():
        assert set(record.extras) == declared


def test_the_ultra_widefield_split_is_declared_as_not_built():
    assert any("ultra-widefield" in what for what in deepdrid.SKIPPED)


def test_no_resolution_is_claimed_because_none_is_published():
    assert deepdrid.RESOLUTION.um_per_px is None
    assert deepdrid.RESOLUTION.source == "unknown"


def test_the_quality_mapping_covers_every_grade_the_dataset_uses():
    assert isinstance(deepdrid.QUALITY, quality.Published)
    with pytest.raises(ValueError):
        deepdrid.QUALITY.grade({"overall_quality": "something else entirely"})
