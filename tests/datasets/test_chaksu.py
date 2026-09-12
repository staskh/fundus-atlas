# ABOUTME: Tests for the Chaksu fetcher against a synthetic copy of its two-archive layout.
# ABOUTME: Five experts, three cameras, and an archive whose own capitalisation is inconsistent.

import zipfile

import numpy as np
import pytest
from PIL import Image

from datasets import chaksu
from datasets.utils import manifest

DECISION_HEADER = "Images,Expert.1,Expert.2,Expert.3,Expert.4,Expert.5,Majority Decision\n"


def a_mask(radius):
    yy, xx = np.mgrid[0:200, 0:200]
    return np.where((xx - 100) ** 2 + (yy - 100) ** 2 <= radius**2, 255, 0).astype(np.uint8)


def as_bytes(array):
    import io

    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="TIFF")
    return buffer.getvalue()


def an_archive(tmp_path, half="Train", name="Image101", camera="Bosch", decisions=None, case=None):
    """The shape figshare serves, including the inconsistent folder capitalisation."""
    case = case or {}
    path = tmp_path / f"{half}.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(f"{half}/1.0_Original_Fundus_Images/{camera}/{name}.JPG", b"photograph")
        for n, expert in enumerate(chaksu.EXPERTS, 1):
            for structure, radius in (("Disc", 60), ("Cup", 30)):
                folder = case.get((n, structure), structure)
                zf.writestr(
                    f"{half}/3.0_Doctors_Annotations_Binary_OD_OC/{expert}/{camera}/{folder}/{name}.tif",
                    as_bytes(a_mask(radius)),
                )
        verdicts = decisions or ["NORMAL"] * 5 + ["NORMAL"]
        body = DECISION_HEADER + f"{name}.jpg-{name}-1.jpg," + ",".join(verdicts) + "\n"
        zf.writestr(
            f"{half}/6.0_Glaucoma_Decision/Glaucoma_Decision_Comparison_{camera}_majority.csv",
            ("﻿" + body).encode("utf8"),
        )
        for other in chaksu.CAMERAS:
            if other != camera:
                zf.writestr(
                    f"{half}/6.0_Glaucoma_Decision/Glaucoma_Decision_Comparison_{other}_majority.csv",
                    DECISION_HEADER.encode("utf8"),
                )
        zf.writestr(f"__MACOSX/{half}/._.DS_Store", b"junk")
    return path


def records(tmp_path, **kwargs):
    return chaksu.discover({"train": an_archive(tmp_path, **kwargs)})


def test_the_key_names_the_split_the_camera_and_the_photograph(tmp_path):
    assert [r.key for r in records(tmp_path)] == ["train_bosch_image101"]


def test_each_camera_is_its_own_subset_because_they_are_not_the_same_shape(tmp_path):
    assert records(tmp_path, camera="Remidio")[0].subset == "remidio"


def test_all_five_experts_outlines_are_kept_apart(tmp_path):
    outlines = records(tmp_path)[0].outlines
    assert set(outlines) == {
        (structure, f"expert{n}") for structure in ("disc", "cup") for n in range(1, 6)
    }


def test_an_expert_whose_folder_is_lowercase_is_still_found(tmp_path):
    # The archive's capitalisation is not consistent: one expert's folder is Bosch/cup, another's
    # is Bosch/Cup. Composing the path instead of indexing what is there loses those experts.
    found = records(tmp_path, case={(2, "Cup"): "cup", (4, "Disc"): "disc"})[0].outlines
    assert ("cup", "expert2") in found
    assert ("disc", "expert4") in found
    assert len(found) == 10


def test_every_expert_decision_is_a_reading_of_its_own(tmp_path):
    readings = records(tmp_path)[0].readings
    assert {r.reader for r in readings} == {f"expert{n}" for n in range(1, 6)} | {
        manifest.CONSENSUS
    }
    assert {r.field for r in readings} == {"disease"}


def test_the_published_majority_is_what_the_manifest_will_hold(tmp_path):
    verdicts = ["GLAUCOMA SUSPECT", "NORMAL", "GLAUCOMA SUSPECT", "NORMAL", "NORMAL", "NORMAL"]
    readings = records(tmp_path, decisions=verdicts)[0].readings
    agreed = [r for r in readings if r.reader == manifest.CONSENSUS]
    assert agreed[0].value == "normal"


def test_the_misspelling_two_experts_use_is_read_as_the_verdict_it_is(tmp_path):
    # Two of the five write "GLAUCOMA  SUSUPECT" throughout: a double space and a transposition,
    # not a third category. Left verbatim it would split one verdict into two.
    verdicts = ["GLAUCOMA SUSPECT"] * 3 + ["GLAUCOMA  SUSUPECT"] * 2 + ["GLAUCOMA SUSPECT"]
    readings = records(tmp_path, decisions=verdicts)[0].readings
    assert {r.value for r in readings} == {"glaucoma suspect"}


def test_a_verdict_nobody_recognises_is_an_error_rather_than_a_new_category(tmp_path):
    with pytest.raises(ValueError, match="disease"):
        records(tmp_path, decisions=["MAYBE"] * 6)


def test_the_masks_are_read_from_inside_the_archive(tmp_path):
    outline = records(tmp_path)[0].outlines[("disc", "expert1")]
    assert outline.archive.name == "Train.zip"
    assert not (tmp_path / "Train").exists()


def test_the_photograph_is_read_from_inside_the_archive_too(tmp_path):
    assert records(tmp_path)[0].image.name.endswith("Image101.JPG")


def test_both_halves_are_built_as_one_store(tmp_path):
    train = an_archive(tmp_path / "a", half="Train", name="Image101")
    test = an_archive(tmp_path / "b", half="Test", name="Image900")
    found = chaksu.discover({"train": train, "test": test})
    assert [r.key for r in found] == ["train_bosch_image101", "test_bosch_image900"]
    assert {r.split for r in found} == {"train", "test"}


def test_the_fused_masks_are_declared_as_not_built():
    assert any("STAPLE" in what for what in chaksu.SKIPPED)


def test_no_resolution_is_claimed():
    assert chaksu.RESOLUTION.um_per_px is None


@pytest.fixture(autouse=True)
def _tmp_subdirs(tmp_path):
    (tmp_path / "a").mkdir(exist_ok=True)
    (tmp_path / "b").mkdir(exist_ok=True)
