# ABOUTME: Tests for the manifest schema: fixed columns, tail columns, labels.csv and multi_reader.
# ABOUTME: No downloads — rows are built by hand.

import csv

import pytest

from datasets.utils import manifest


def a_row(**overrides):
    row = {"key": "training_21", "subset": "main", "split": "train"}
    row.update(overrides)
    return row


def test_the_fixed_columns_come_first_in_the_documented_order(tmp_path):
    manifest.write(tmp_path, [a_row()], extra_columns=[])
    with open(tmp_path / "manifest.csv") as f:
        header = next(csv.reader(f))
    assert header == list(manifest.CORE_COLUMNS)
    assert header[0] == "key"
    assert header[-1] == "notes"


def test_a_value_never_written_is_empty_not_a_zero(tmp_path):
    manifest.write(tmp_path, [a_row()], extra_columns=[])
    row = next(iter(manifest.read(tmp_path)))
    assert row["um_per_px"] == ""
    assert row["disease"] == ""


def test_dataset_specific_columns_are_appended_after_notes(tmp_path):
    extra = [manifest.Column("age", "years"), manifest.Column("artifact", "0 is best")]
    manifest.write(tmp_path, [a_row(age="61", artifact="4")], extra_columns=extra)
    with open(tmp_path / "manifest.csv") as f:
        header = next(csv.reader(f))
    assert header[-3:] == ["notes", "age", "artifact"]


def test_a_tail_column_may_not_shadow_a_fixed_one():
    with pytest.raises(ValueError, match="quality"):
        manifest.Column("quality", "a second opinion about the same thing")


def test_a_row_carrying_a_column_nobody_declared_is_an_error(tmp_path):
    with pytest.raises(ValueError, match="age"):
        manifest.write(tmp_path, [a_row(age="61")], extra_columns=[])


def test_one_reader_per_field_writes_no_labels_file(tmp_path):
    manifest.write(tmp_path, [a_row(quality="good")], extra_columns=[])
    assert not (tmp_path / "labels.csv").exists()


def test_several_readers_are_kept_whole_in_labels(tmp_path):
    readings = [
        manifest.Reading("training_21", "quality", "grader1", "good"),
        manifest.Reading("training_21", "quality", "grader2", "usable"),
    ]
    manifest.write(tmp_path, [a_row()], extra_columns=[], readings=readings)
    with open(tmp_path / "labels.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0] == {
        "key": "training_21",
        "field": "quality",
        "reader": "grader1",
        "value": "good",
    }


def test_a_published_consensus_is_what_the_manifest_holds(tmp_path):
    readings = [
        manifest.Reading("training_21", "quality", "grader1", "good"),
        manifest.Reading("training_21", "quality", "grader2", "usable"),
        manifest.Reading("training_21", "quality", "consensus", "good"),
    ]
    manifest.write(tmp_path, [a_row()], extra_columns=[], readings=readings)
    row = next(iter(manifest.read(tmp_path)))
    assert row["quality"] == "good"
    assert row["multi_reader"] == "quality"


def test_readers_who_disagree_with_no_consensus_leave_the_cell_empty(tmp_path):
    readings = [
        manifest.Reading("training_21", "quality", "grader1", "good"),
        manifest.Reading("training_21", "quality", "grader2", "bad"),
    ]
    manifest.write(tmp_path, [a_row()], extra_columns=[], readings=readings)
    row = next(iter(manifest.read(tmp_path)))
    assert row["quality"] == ""
    assert row["multi_reader"] == "quality"
    assert row["readers"] == "grader1;grader2"


def test_readers_who_agree_speak_with_one_voice(tmp_path):
    readings = [
        manifest.Reading("training_21", "quality", "grader1", "good"),
        manifest.Reading("training_21", "quality", "grader2", "good"),
    ]
    manifest.write(tmp_path, [a_row()], extra_columns=[], readings=readings)
    row = next(iter(manifest.read(tmp_path)))
    assert row["quality"] == "good"
    assert row["multi_reader"] == "quality"


def test_the_fetcher_may_not_set_a_cell_that_readings_also_decide(tmp_path):
    readings = [manifest.Reading("training_21", "quality", "grader1", "good")]
    with pytest.raises(ValueError, match="quality"):
        manifest.write(tmp_path, [a_row(quality="bad")], extra_columns=[], readings=readings)


def test_a_code_is_stored_as_the_dataset_s_own_words_for_it():
    legend = {"0": "no apparent retinopathy", "3": "severe npdr"}
    assert manifest.spell_out("3", legend, "disease") == "severe npdr"


def test_an_ungraded_image_stays_empty_rather_than_becoming_a_word():
    assert manifest.spell_out("", {"0": "none"}, "disease") == ""


def test_a_code_the_legend_does_not_explain_is_an_error():
    with pytest.raises(ValueError, match="disease is '7'"):
        manifest.spell_out("7", {"0": "none"}, "disease")
