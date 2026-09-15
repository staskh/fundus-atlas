# ABOUTME: Tests for the PAPILA fetcher against a synthetic copy of its unpacked archive.
# ABOUTME: Two experts per structure, a clinical row per eye, and a grade nobody published.

import numpy as np
import openpyxl
import pytest
from PIL import Image

from datasets import papila


def a_tree(tmp_path, eyes=None, strays=()):
    """The shape the zip unpacks into: one hashed directory holding four subtrees.

    :param strays: contour files the archive carries twice, under a macOS duplicate name.
    """
    root = tmp_path / "PapilaDB-PAPILA-17f8fa7746adb20275b5b6a0d99dc9dfe3007e9f"
    photographs = root / papila.PHOTOGRAPHS
    contours = root / papila.CONTOURS
    clinical = root / papila.CLINICAL
    for where in (photographs, contours, clinical):
        where.mkdir(parents=True)

    eyes = eyes or [("#002", "OD", 47, 0, 0), ("#002", "OS", 47, 0, 2), ("#004", "OD", 58, 1, 1)]
    for patient, side, *_ in eyes:
        stem = f"RET{patient.lstrip('#')}{side}"
        Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8)).save(photographs / f"{stem}.jpg")
        for structure in ("disc", "cup"):
            for expert in (1, 2):
                (contours / f"{stem}_{structure}_exp{expert}.txt").write_text(
                    "   1.0000000e+01   2.0000000e+01\n   3.0000000e+01   4.0000000e+01\n"
                )
    for name in strays:
        (contours / name).write_text("   1.0000000e+01   2.0000000e+01\n")

    for side in ("od", "os"):
        book = openpyxl.Workbook()
        sheet = book.active
        sheet.title = "Sheet1"
        sheet.append([None, "Age", "Gender", "Diagnosis", "Refractive_Defect"])
        sheet.append(
            [
                None,
                "Age",
                "Gender",
                "Diagnosis",
                "dioptre_1",
                "dioptre_2",
                "astigmatism",
                "Phakic/Pseudophakic",
                "Pneumatic",
                "Perkins",
                "Pachymetry",
                "Axial_Length",
                "VF_MD",
            ]
        )
        sheet.append(["ID"])
        for patient, eye_side, age, gender, diagnosis in eyes:
            if eye_side.lower() != side:
                continue
            sheet.append(
                [patient, age, gender, diagnosis, 0.75, -1.75, 90, 0, 21, None, 586, 23.64, -0.07]
            )
        book.save(clinical / f"patient_data_{side}.xlsx")
    return tmp_path


def records(tmp_path, **kwargs):
    found = papila.discover({"papila": a_tree(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_the_key_names_the_patient_and_the_eye(tmp_path):
    assert set(records(tmp_path)) == {"ret002_od", "ret002_os", "ret004_od"}


def test_both_eyes_of_one_person_carry_the_same_patient(tmp_path):
    found = records(tmp_path)
    assert found["ret002_od"].patient == found["ret002_os"].patient == "RET002"
    assert found["ret002_od"].eye == "od"
    assert found["ret002_os"].eye == "os"


def test_the_diagnosis_is_stored_as_words_rather_than_a_code(tmp_path):
    found = records(tmp_path)
    assert found["ret002_od"].disease == "healthy"
    assert found["ret002_os"].disease == "glaucoma"
    assert found["ret004_od"].disease == "glaucoma suspect"


def test_both_experts_drew_both_structures(tmp_path):
    record = records(tmp_path)["ret002_od"]
    assert set(record.outlines) == {
        ("disc", "expert1"),
        ("disc", "expert2"),
        ("cup", "expert1"),
        ("cup", "expert2"),
    }
    assert record.readers == ["expert1", "expert2"]


def test_a_contour_is_read_as_coordinates_in_the_photographs_own_frame(tmp_path):
    record = records(tmp_path)["ret002_od"]
    assert np.allclose(record.outlines[("disc", "expert1")], [[10.0, 20.0], [30.0, 40.0]])
    assert record.roi is None, "PAPILA annotates the photograph, not a crop of it"


def test_the_archives_duplicate_contour_files_are_not_read_twice(tmp_path):
    record = records(tmp_path, strays=("RET002OD_cup_exp2 2.txt",))["ret002_od"]

    assert len(record.outlines[("cup", "expert2")]) == 2, "the canonical file, not the stray copy"
    assert set(record.outlines) == {
        ("disc", "expert1"),
        ("disc", "expert2"),
        ("cup", "expert1"),
        ("cup", "expert2"),
    }


def test_the_clinical_record_travels_as_this_datasets_own_columns(tmp_path):
    record = records(tmp_path)["ret002_od"]
    assert record.extras["age"] == "47"
    assert record.extras["gender"] == "0", "codes stay as the authors wrote them"
    assert record.extras["pachymetry"] == "586"
    assert record.extras["axial_length"] == "23.64"
    assert record.extras["vf_md"] == "-0.07"
    assert record.extras["perkins"] == "", "an unmeasured value is empty, not zero"


def test_every_photograph_is_assumed_sound_and_says_that_it_was_assumed(tmp_path):
    record = records(tmp_path)["ret002_od"]

    assert record.quality_source == ""
    assert papila.QUALITY.grade({}) == ("good", "assumed")
    assert "quality" not in papila.QUALITY.because.lower() or papila.QUALITY.because


def test_the_assumption_is_declared_with_its_reason(tmp_path):
    assert len(papila.QUALITY.because) > 20, "the reason is recorded, not implied"


def test_a_photograph_with_no_clinical_row_is_kept_and_said_to_have_none(tmp_path):
    tree = a_tree(tmp_path)
    root = tree / "PapilaDB-PAPILA-17f8fa7746adb20275b5b6a0d99dc9dfe3007e9f"
    Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8)).save(
        root / papila.PHOTOGRAPHS / "RET999OD.jpg"
    )

    found = {record.key: record for record in papila.discover({"papila": tree})}

    assert found["ret999_od"].disease == ""
    assert "clinical" in found["ret999_od"].notes


def test_a_diagnosis_code_the_legend_does_not_cover_is_refused(tmp_path):
    with pytest.raises(ValueError, match="7"):
        records(tmp_path, eyes=[("#002", "OD", 47, 0, 7)])
