# ABOUTME: Tests for the AVRDB fetcher: one folder per photograph, arteries and veins drawn on white
# ABOUTME: in separate files, and the crossings the dataset itself puts in both of them.

import io
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from datasets import avrdb

STEMS = ["IM006106", "IM005488"]


def a_photograph() -> bytes:
    pixels = np.zeros((40, 60, 3), dtype=np.uint8)
    pixels[8:32, 14:46] = (120, 60, 30)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="JPEG", quality=95)
    return out.getvalue()


def a_drawing(colour: tuple[int, int, int], rows: slice) -> bytes:
    pixels = np.full((40, 60, 3), 255, dtype=np.uint8)
    pixels[rows, 14:46] = colour
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="JPEG", quality=95)
    return out.getvalue()


def an_archive(
    tmp_path: Path,
    stems: list[str] | None = None,
    drop: str = "",
    spelling: dict[str, str] | None = None,
) -> Path:
    """The shape Mendeley serves, with the misspellings the deposit actually contains."""
    stems = stems or STEMS
    spelling = spelling or {}
    path = tmp_path / "AVRDB.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for stem in stems:
            here = f"AV/{stem}/{stem}"
            archive.writestr(f"{here}.JPG", a_photograph())
            named = {name: spelling.get(name, name) for name in ("arteries", "veins", "vessels")}
            if drop != "arteries":
                archive.writestr(
                    f"{here}--{named['arteries']}.jpg", a_drawing((237, 27, 36), slice(10, 14))
                )
            if drop != "veins":
                archive.writestr(
                    f"{here}--{named['veins']}.jpg", a_drawing((45, 49, 146), slice(12, 16))
                )
            if drop != "vessels":
                archive.writestr(
                    f"{here}--{named['vessels']}.jpg", a_drawing((35, 31, 32), slice(10, 16))
                )
            archive.writestr(f"{here}--both.jpg", a_photograph())
            archive.writestr(f"{here}.ai", b"%PDF-1.5 not an annotation")
    return path


def records(tmp_path: Path, **kwargs):
    found = avrdb.discover({avrdb.SLUG: an_archive(tmp_path, **kwargs)})
    return {record.key: record for record in found}


def test_each_folder_is_one_photograph_with_its_three_drawings(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert sorted(found) == ["im005488", "im006106"]
    assert sorted(found["im006106"].maps) == ["artery", "vein", "vessels"]


def test_the_illustrator_source_and_the_overlay_are_not_annotations(tmp_path: Path) -> None:
    """`--both` is the photograph with the vessels painted over it, and `.ai` is the drawing file."""
    found = records(tmp_path)

    assert "both" not in found["im006106"].maps
    assert not any(str(source).endswith(".ai") for source in found["im006106"].maps.values())


def test_a_photograph_missing_a_drawing_keeps_the_ones_it_has(tmp_path: Path) -> None:
    found = records(tmp_path, drop="vessels")

    assert sorted(found["im006106"].maps) == ["artery", "vein"]
    assert "no vessels drawing" in found["im006106"].notes


def test_the_ink_reader_finds_what_was_drawn_and_not_the_page() -> None:
    drawn = np.asarray(
        Image.open(io.BytesIO(a_drawing((237, 27, 36), slice(10, 14)))).convert("RGB")
    )

    masks = avrdb.DRAWN.masks(drawn, "artery")

    assert masks["artery"][11, 20]
    assert not masks["artery"][0, 0], "the white page"
    assert 0.9 < masks["artery"].astype(bool).sum() / (4 * 32) < 1.2


def test_the_key_is_the_dataset_s_own_name_for_the_photograph(tmp_path: Path) -> None:
    """No split is published, so the key is the folder's name and nothing invented."""
    assert records(tmp_path)["im006106"].split == "unspecified"


def test_a_misspelled_drawing_is_still_that_drawing(tmp_path: Path) -> None:
    """The deposit spells the suffix seven different wrong ways across its hundred folders.

    `--veisn`, `--veinds`, `--vein`, `--artery`, `--artry`, `--atertries` — composing the name the
    fetcher expects finds nothing for those photographs and reports a dataset with holes in it.
    """
    found = records(tmp_path, spelling={"veins": "veisn", "arteries": "artry"})

    assert sorted(found["im006106"].maps) == ["artery", "vein", "vessels"]
    assert not found["im006106"].notes


def test_a_drawing_filed_under_another_photographs_name_is_still_found(tmp_path: Path) -> None:
    """One folder holds a file whose name begins with a different photograph's id."""
    path = an_archive(tmp_path)
    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr("AV/IM000168/IM000168.JPG", a_photograph())
        archive.writestr("AV/IM000168/IM000999--veins.jpg", a_drawing((45, 49, 146), slice(12, 16)))
        archive.writestr(
            "AV/IM000168/IM000168--arteries.jpg", a_drawing((237, 27, 36), slice(10, 14))
        )
        archive.writestr(
            "AV/IM000168/IM000168--vessels.jpg", a_drawing((35, 31, 32), slice(10, 16))
        )

    found = {record.key: record for record in avrdb.discover({avrdb.SLUG: path})}

    assert sorted(found["im000168"].maps) == ["artery", "vein", "vessels"]
