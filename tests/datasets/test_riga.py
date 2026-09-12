# ABOUTME: Tests for the RIGA fetcher against a synthetic copy of the RIGA+ archive.
# ABOUTME: Six readers, two structures packed into each mask, and MESSIDOR images to leave out.

import io
import zipfile

import numpy as np
from PIL import Image

from datasets import riga
from datasets.utils import contours


def a_mask():
    yy, xx = np.mgrid[0:200, 0:200]
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 60**2] = 255
    mask[(xx - 100) ** 2 + (yy - 100) ** 2 <= 25**2] = 128
    buffer = io.BytesIO()
    Image.fromarray(mask).save(buffer, format="TIFF")
    return buffer.getvalue()


def an_archive(tmp_path, readers=6):
    path = tmp_path / "RIGAPlus.zip"
    photographs = [
        ("BinRushed", "BinRushed1", "image1"),
        ("Magrabia", "MagrabiaMale", "image7"),
        ("MESSIDOR_Base1", "Labeled", "image20"),
    ]
    with zipfile.ZipFile(path, "w") as zf:
        for folder, collection, stem in photographs:
            zf.writestr(f"RIGA/{folder}/{collection}/{stem}.tif", b"photograph")
            for n in range(1, readers + 1):
                zf.writestr(f"RIGA-mask/{folder}/{collection}/{stem}-{n}.tif", a_mask())
        # The photographs RIGA+ adds for domain adaptation, which carry no RIGA annotation.
        zf.writestr("RIGA/MESSIDOR_Base1/Unlabeled/image99.tif", b"photograph")
        zf.writestr("BinRushed_train.csv", b"the repackagers' own split")
    return path


def records(tmp_path, **kwargs):
    return {r.key: r for r in riga.discover({"riga": an_archive(tmp_path, **kwargs)})}


def test_the_three_sources_are_the_subsets(tmp_path):
    found = records(tmp_path)
    assert {r.subset for r in found.values()} == {"binrushed", "magrabia", "messidor"}


def test_the_key_names_the_source_the_collection_and_the_photograph(tmp_path):
    assert "binrushed_binrushed1_image1" in records(tmp_path)


def test_the_folder_inside_a_source_is_kept_because_messidor_has_three(tmp_path):
    found = records(tmp_path)
    assert found["messidor_labeled_image20"].extras["collection"] == "Labeled"


def test_a_photograph_with_no_annotation_is_not_part_of_riga(tmp_path):
    # RIGA+ adds unlabelled MESSIDOR photographs for domain adaptation; they are MESSIDOR's.
    assert all("image99" not in key for key in records(tmp_path))


def test_all_six_readers_give_both_structures(tmp_path):
    outlines = records(tmp_path)["binrushed_binrushed1_image1"].outlines
    assert set(outlines) == {
        (structure, f"expert{n}") for structure in ("disc", "cup") for n in range(1, 7)
    }


def test_each_structure_names_the_values_it_is_made_of(tmp_path):
    outlines = records(tmp_path)["binrushed_binrushed1_image1"].outlines
    assert outlines[("cup", "expert1")].values == riga.CUP
    assert outlines[("disc", "expert1")].values == riga.DISC


def test_the_cup_traces_smaller_than_the_disc_it_sits_in(tmp_path):
    outlines = records(tmp_path)["binrushed_binrushed1_image1"].outlines
    image = np.asarray(Image.open(io.BytesIO(a_mask())).convert("L"))
    disc = contours.trace(outlines[("disc", "expert1")].mask_from(image))
    cup = contours.trace(outlines[("cup", "expert1")].mask_from(image))
    assert (cup[:, 1].max() - cup[:, 1].min()) < (disc[:, 1].max() - disc[:, 1].min())


def test_fewer_readers_than_six_is_taken_as_it_comes(tmp_path):
    outlines = records(tmp_path, readers=4)["binrushed_binrushed1_image1"].outlines
    assert {reader for _, reader in outlines} == {f"expert{n}" for n in range(1, 5)}


def test_the_repackagers_split_is_declared_as_not_built():
    assert any("split" in what for what in riga.SKIPPED)


def test_no_resolution_is_claimed_because_the_photographs_were_resized():
    assert riga.RESOLUTION.um_per_px is None
    assert "800x800" in riga.RESOLUTION.note


def test_no_field_of_view_is_looked_for_in_a_crop():
    # RIGA+ ships crops around the nerve head. There is no field edge to fit a circle to, and
    # fitting one to the sliver that is sometimes in frame gave circles 36 and 13,646 pixels
    # across on 800-pixel images.
    import inspect

    from datasets.utils import fov

    assert f"fov.{fov.WHOLE.upper()}" in inspect.getsource(riga.main)
