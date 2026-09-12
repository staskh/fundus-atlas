# ABOUTME: Tests for the FQS fetcher against a synthetic copy of its published archive.
# ABOUTME: The point is the six doctors, the three graders, and which of them the manifest holds.

import zipfile

import openpyxl
import pytest

from datasets import fqs
from datasets.utils import manifest

META_HEADER = [
    "Column1",
    "file_name",
    "doc1",
    "doc2",
    "doc3",
    "doc4",
    "level1",
    "doc5",
    "level2",
    "doc6",
    "level3",
    "qualityLevel",
    "meanOpinionScore",
]


def an_archive(tmp_path, rows, folds=(("00", "train", ["00000.jpeg"]),)):
    """The shape figshare serves: photographs twice over, labels and folds in spreadsheets."""
    meta = openpyxl.Workbook()
    meta.active.append(META_HEADER)
    for row in rows:
        meta.active.append(row)
    meta_path = tmp_path / "meta_data.xlsx"
    meta.save(meta_path)

    path = tmp_path / "FIQSDataset.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.write(meta_path, "meta_data.xlsx")
        for row in rows:
            zf.writestr(f"full_size_images/{row[1]}", b"original")
            zf.writestr(f"images/{row[1]}", b"resized copy")
        for fold, role, names in folds:
            sheet = openpyxl.Workbook()
            sheet.active.append([None, "file_name", "qualityLevel", "meanOpinionScore"])
            for name in names:
                sheet.active.append([0, name, 2, 50])
            listing = tmp_path / f"{fold}-{role}.xlsx"
            sheet.save(listing)
            zf.write(listing, f"divisions/cross_validation-{fold}-{role}.xlsx")
    return path


def a_row(name="00000.PNG", scores=(60, 70, 55, 60, 62, 62), levels=(1, 2, 2), published=2):
    d1, d2, d3, d4, d5, d6 = scores
    l1, l2, l3 = levels
    return [0, name, d1, d2, d3, d4, l1, d5, l2, d6, l3, published, sum(scores) / 6]


def test_the_original_is_built_and_not_the_resized_copy(tmp_path):
    records = fqs.discover({"fqs": an_archive(tmp_path, [a_row()])})
    assert records[0].image.name == "full_size_images/00000.PNG"


def test_the_resized_copy_is_declared_as_not_built():
    assert any("images/" in what for what in fqs.SKIPPED)


def test_every_doctor_and_grader_is_kept_apart(tmp_path):
    readings = fqs.discover({"fqs": an_archive(tmp_path, [a_row()])})[0].readings
    graders = {r.reader for r in readings if r.field == "quality"}
    doctors = {r.reader for r in readings if r.field == "mos"}
    assert graders == {"level1", "level2", "level3", manifest.CONSENSUS}
    assert len(doctors) == 7


def test_the_published_class_is_translated_but_not_recomputed(tmp_path):
    readings = fqs.discover({"fqs": an_archive(tmp_path, [a_row(levels=(1, 2, 2), published=2)])})[
        0
    ].readings
    agreed = [r for r in readings if r.field == "quality" and r.reader == manifest.CONSENSUS]
    assert agreed[0].value == "bad"


def test_zero_is_the_best_class_not_the_worst(tmp_path):
    records = fqs.discover({"fqs": an_archive(tmp_path, [a_row(levels=(0, 0, 0), published=0)])})
    agreed = [
        r for r in records[0].readings if r.field == "quality" and r.reader == manifest.CONSENSUS
    ]
    assert agreed[0].value == "good"


def test_the_graders_disagreement_survives_into_the_manifest(tmp_path):
    # Six photographs have three graders who each said something different. The published median
    # is what the cell holds, and multi_reader is what says the graders did not agree.
    archive = an_archive(tmp_path, [a_row(levels=(0, 2, 1), published=1)])
    record = fqs.discover({"fqs": archive})[0]
    manifest.write(
        tmp_path / "store",
        [{"key": record.key, **record.extras}],
        fqs.EXTRA_COLUMNS,
        record.readings,
    )
    row = next(iter(manifest.read(tmp_path / "store")))
    assert row["quality"] == "usable"
    assert row["multi_reader"] == "mos;quality"
    assert row["readers"] == "doc1;doc2;doc3;doc4;doc5;doc6;level1;level2;level3"


def test_the_mean_opinion_score_is_the_published_one(tmp_path):
    readings = fqs.discover(
        {"fqs": an_archive(tmp_path, [a_row(scores=(60, 70, 55, 60, 62, 62))])}
    )[0].readings
    agreed = [r for r in readings if r.field == "mos" and r.reader == manifest.CONSENSUS]
    assert agreed[0].value == "61.5"


def test_a_fold_is_matched_by_name_because_the_extensions_disagree(tmp_path):
    # The fold spreadsheets name 00000.jpeg; the archive holds 00000.PNG.
    archive = an_archive(tmp_path, [a_row()], folds=(("00", "test", ["00000.jpeg"]),))
    assert fqs.discover({"fqs": archive})[0].extras["cv_00"] == "test"


def test_a_photograph_missing_from_a_fold_file_is_empty_rather_than_guessed(tmp_path):
    archive = an_archive(tmp_path, [a_row()], folds=(("03", "val", ["09999.jpeg"]),))
    assert fqs.discover({"fqs": archive})[0].extras["cv_03"] == ""


def test_there_is_no_canonical_split_to_record(tmp_path):
    # The folds come from an unseeded shuffle in the archive's own script, so they are one draw
    # rather than a split the authors published as the split.
    assert fqs.discover({"fqs": an_archive(tmp_path, [a_row()])})[0].split == "unspecified"


def test_no_resolution_is_claimed():
    assert fqs.RESOLUTION.um_per_px is None


def test_a_class_outside_the_published_three_is_an_error():
    with pytest.raises(ValueError):
        fqs.QUALITY.word("7")
