# ABOUTME: Tests for the G1020 fetcher: the authors' own polygons, read from the LabelMe files the
# ABOUTME: bundle carries beside each photograph, rather than the masks the uploader rasterised.

import io
import json
import zipfile

import numpy as np
import pytest
from PIL import Image

from datasets import g1020
from datasets.utils import archives

DISC = [[10, 10], [50, 10], [50, 60], [10, 60]]
SMALL_DISC = [[12, 12], [14, 12], [14, 14], [12, 14]]
CUP = [[20, 20], [40, 20], [40, 40], [20, 40]]


def jpeg() -> bytes:
    out = io.BytesIO()
    Image.fromarray(np.zeros((80, 100, 3), dtype=np.uint8)).save(out, format="JPEG")
    return out.getvalue()


def labelme(*shapes) -> bytes:
    return json.dumps(
        {
            "imagePath": "x.jpg",
            "imageData": None,
            "shapes": [{"label": label, "points": points} for label, points in shapes],
        }
    ).encode()


def a_bundle(tmp_path, labels="imageID,binaryLabels\nimage_0.jpg,0\nimage_1.jpg,1\n"):
    path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("G1020/G1020.csv", labels.encode())
        z.writestr("G1020/Images/image_0.jpg", jpeg())
        z.writestr(
            "G1020/Images/image_0.json",
            labelme(("disc", DISC), ("cup", CUP), ("discLoc", [[0, 0], [60, 70]])),
        )
        z.writestr("G1020/Images/image_1.jpg", jpeg())
        z.writestr("G1020/Images/image_1.json", labelme(("disc", SMALL_DISC), ("disc", DISC)))
        # the uploader's derived copies, which are not the dataset
        z.writestr("G1020/Images_Cropped/img/image_0.jpg", jpeg())
        z.writestr("G1020/Images_Square/image_0.jpg", jpeg())
        z.writestr("G1020/NerveRemoved_Images/image_0.jpg", jpeg())
        z.writestr("G1020/Masks/image_0.png", jpeg())
        z.writestr("ORIGA/Images/001.jpg", jpeg())
    return path


def records(tmp_path, **kwargs):
    return {r.key: r for r in g1020.discover({g1020.SLUG: a_bundle(tmp_path, **kwargs)})}


def test_it_refuses_to_download_and_asks_for_the_archive():
    with pytest.raises(PermissionError, match="--archive"):
        g1020.SOURCES[0].obtain(None)


def test_the_bundle_is_read_where_it_lies():
    assert g1020.SOURCES[0].extract_it is False


def test_every_photograph_the_sheet_names_is_built_and_nothing_else(tmp_path):
    assert set(records(tmp_path)) == {"image_0", "image_1"}


def test_the_photograph_is_the_authors_not_a_derived_copy(tmp_path):
    assert records(tmp_path)["image_0"].image.name == "G1020/Images/image_0.jpg"
    assert isinstance(records(tmp_path)["image_0"].image, archives.Member)


def test_the_label_is_spelled_out(tmp_path):
    found = records(tmp_path)
    assert (found["image_0"].disease, found["image_1"].disease) == ("normal", "glaucoma")


def test_a_label_the_legend_does_not_explain_is_refused(tmp_path):
    with pytest.raises(ValueError, match="7"):
        records(tmp_path, labels="imageID,binaryLabels\nimage_0.jpg,7\n")


def test_the_polygons_are_the_coordinates_the_authors_drew(tmp_path):
    outlines = records(tmp_path)["image_0"].outlines
    assert set(outlines) == {("disc", g1020.READER), ("cup", g1020.READER)}
    assert np.allclose(outlines[("disc", g1020.READER)], DISC)
    assert np.allclose(outlines[("cup", g1020.READER)], CUP)


def test_the_disc_box_is_not_mistaken_for_a_disc(tmp_path):
    outlines = records(tmp_path)["image_0"].outlines
    assert len(outlines[("disc", g1020.READER)]) == len(DISC)


def test_of_two_discs_drawn_on_one_photograph_the_larger_is_kept_and_said_so(tmp_path):
    record = records(tmp_path)["image_1"]
    assert np.allclose(record.outlines[("disc", g1020.READER)], DISC)
    assert "two disc polygons" in record.notes


def test_a_photograph_with_no_cup_has_none(tmp_path):
    assert ("cup", g1020.READER) not in records(tmp_path)["image_1"].outlines


def test_the_scale_is_the_stated_field_angle():
    assert g1020.RESOLUTION.source == "field_angle"
    assert g1020.RESOLUTION.degrees == 45


def test_the_route_recorded_is_the_kaggle_bundle_not_the_official_host():
    assert g1020.SOURCES[0].url == "https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets"
    assert g1020.SOURCES[0].manual, "declared, never downloaded: Kaggle needs an account"
