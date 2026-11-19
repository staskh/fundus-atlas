# ABOUTME: Tests for the HRF fetcher: one set of photographs with three provenances, the disease in
# ABOUTME: every filename, and an artery/vein layer a second group added years later.

import io
import zipfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from datasets import hrf
from datasets.utils import build, cli, contours, fov, manifest

STEMS = ["01_dr", "01_g", "01_h", "02_dr"]


def an_image(size=(60, 40), colour=(120, 60, 30)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[6:34, 10:50] = colour
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_mask(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0]), dtype=np.uint8)
    pixels[6:34, 10:50] = 255
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def an_av_map(size=(60, 40)) -> bytes:
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[10:12, 12:48] = (255, 0, 0)
    pixels[20:22, 12:48] = (0, 0, 255)
    pixels[15:17, 20:24] = (0, 255, 0)
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_seg_plus_mask(colour: tuple[int, int, int] | None, size: int = 20) -> bytes:
    """A HRF-Seg+ mask: white paper with one structure painted on it, anti-aliased at the edge."""
    pixels = np.full((size, size, 4), 255, dtype=np.uint8)
    if colour is not None:
        pixels[5:15, 5:15, :3] = colour
        pixels[4, 5:15, :3] = [(c + 3 * 255) // 4 for c in colour]
    out = io.BytesIO()
    Image.fromarray(pixels).save(out, format="PNG")
    return out.getvalue()


def a_seg_plus_archive(tmp_path: Path, stems=STEMS, cupless=("02_dr",)) -> Path:
    archive = tmp_path / "HRF-Seg+.zip"
    with zipfile.ZipFile(archive, "w") as held:
        held.writestr("HRF-Seg+/class_dict.csv", "name, r, g, b\n")
        for stem in stems:
            suffix = "JPG" if stem.endswith("_dr") else "jpg"
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_IMAGES}/{stem}.{suffix}", an_image((20, 20)))
            disc = a_seg_plus_mask((128, 64, 128))
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_DISC}/{stem}.png", disc)
            cup = None if stem in cupless else (130, 76, 0)
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_CUP}/{stem}.png", a_seg_plus_mask(cup))
    return archive


def layers(tmp_path: Path, with_av: bool = True, with_seg_plus: bool = True) -> dict[str, Path]:
    archive = tmp_path / "all.zip"
    with zipfile.ZipFile(archive, "w") as held:
        for stem in STEMS:
            held.writestr(f"images/{stem}.jpg", an_image())
            held.writestr(f"manual1/{stem}.tif", a_mask())
            held.writestr(f"mask/{stem}_mask.tif", a_mask())
    found = {hrf.SLUG: archive}
    if with_av:
        tree = tmp_path / "hrf-av"
        (tree / hrf.AV_FOLDER).mkdir(parents=True)
        for stem in STEMS:
            (tree / hrf.AV_FOLDER / f"{stem}_AVmanual.png").write_bytes(an_av_map())
        found[hrf.AV_LAYER] = tree
    if with_seg_plus:
        found[hrf.SEG_PLUS_LAYER] = a_seg_plus_archive(tmp_path)
    return found


def records(tmp_path: Path, **kwargs):
    return {record.key: record for record in hrf.discover(layers(tmp_path, **kwargs))}


def test_every_photograph_carries_its_vessels_its_field_and_its_arteries(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert sorted(found) == ["01_dr", "01_g", "01_h", "02_dr"]
    assert sorted(found["01_dr"].maps) == ["av", "fov", "vessels"]


def test_the_disease_comes_from_the_name_the_authors_gave_the_file(tmp_path: Path) -> None:
    """`_dr`, `_g` and `_h` are the dataset's own three groups of fifteen."""
    found = records(tmp_path)

    assert found["01_dr"].disease == "diabetic retinopathy"
    assert found["01_g"].disease == "glaucoma"
    assert found["01_h"].disease == "healthy"


def test_the_artery_vein_layer_is_optional_and_its_absence_is_recorded(tmp_path: Path) -> None:
    """It is a second group's work from a repository with no licence, so a build must survive
    without it rather than refusing to produce the vessel dataset HRF itself published."""
    found = records(tmp_path, with_av=False)

    assert sorted(found["01_dr"].maps) == ["fov", "vessels"]
    assert "artery/vein" in found["01_dr"].notes


def test_the_palette_is_the_one_that_repository_publishes() -> None:
    masks = hrf.PALETTE.masks(
        np.array([[[255, 0, 0], [0, 0, 255], [0, 255, 0], [0, 0, 0]]], np.uint8), "av"
    )

    assert list(masks["artery"][0] > 0) == [True, False, True, False], "artery and the crossing"
    assert list(masks["vein"][0] > 0) == [False, True, True, False]
    assert list(masks["vessels"][0] > 0) == [True, True, True, False]


def test_the_vessel_gold_standard_is_the_authors_own_and_not_the_union(tmp_path: Path) -> None:
    """The store keeps HRF's hand-drawn `manual1` tracing, never the artery/vein union.

    The two turn out to be the same tracing — they differ by 0.004% of pixels across the dataset,
    because HRF-AV coloured HRF's own gold standard — but which file the store holds still has to be
    the published one, so that the page's claim can be checked rather than assumed.
    """
    found = records(tmp_path)

    assert "manual1" in str(found["01_dr"].maps["vessels"].name)


def test_the_field_of_view_mask_is_the_published_one(tmp_path: Path) -> None:
    found = records(tmp_path)

    assert "mask" in str(found["01_dr"].maps["fov"].name)
    assert hrf.FOV_STRATEGY == fov.FROM_MASK


def test_disc_and_cup_come_from_hrf_seg_plus_and_are_placed_by_its_crop(tmp_path: Path) -> None:
    """HRF-Seg+ draws on a 500-pixel crop around the nerve head, so every outline carries the crop
    it was drawn on, for the build to find in the photograph."""
    found = records(tmp_path)

    outlines = found["01_dr"].outlines
    assert sorted(outlines) == [("cup", hrf.SEG_PLUS_READER), ("disc", hrf.SEG_PLUS_READER)]
    assert found["01_dr"].roi.name == f"HRF-Seg+/{hrf.SEG_PLUS_IMAGES}/01_dr.JPG"


def test_the_disc_and_cup_layer_is_optional(tmp_path: Path) -> None:
    found = records(tmp_path, with_seg_plus=False)

    assert found["01_dr"].outlines == {}
    assert found["01_dr"].roi is None
    assert "disc and cup" in found["01_dr"].notes


def test_a_photograph_hrf_seg_plus_skipped_has_no_outline_and_says_so(tmp_path: Path) -> None:
    held = layers(tmp_path)
    held[hrf.SEG_PLUS_LAYER] = a_seg_plus_archive(tmp_path, stems=["01_dr", "01_g", "01_h"])

    found = {record.key: record for record in hrf.discover(held)}

    assert found["02_dr"].outlines == {}
    assert "disc and cup" in found["02_dr"].notes


def test_a_structure_is_the_paint_and_not_the_paper_round_it() -> None:
    """The masks are a colour on white, and several disc masks blend the two along the edge: a
    pixel nearer the paint is the structure, a pixel nearer the paper is not."""
    grey = np.array(Image.open(io.BytesIO(a_seg_plus_mask((128, 64, 128)))).convert("L"))

    inside = hrf.STRUCTURE.mask_from(grey) > 0

    assert inside[5:15, 5:15].all()
    assert inside.sum() == 100, "the blended edge row is nearer the paper and stays outside"


def test_an_empty_cup_mask_is_white_paper_and_holds_no_structure() -> None:
    grey = np.array(Image.open(io.BytesIO(a_seg_plus_mask(None))).convert("L"))

    assert not (hrf.STRUCTURE.mask_from(grey) > 0).any()


def test_the_whole_build_puts_hrf_seg_plus_outlines_into_the_crop(tmp_path: Path) -> None:
    """End to end on synthetic files: the crop is found in the photograph, the disc is traced in
    it, and a photograph with an empty cup mask gets a disc and a note rather than a cup."""

    rng = np.random.default_rng(1)
    archive = tmp_path / "all.zip"
    photos, crops = {}, {}
    with zipfile.ZipFile(archive, "w") as held:
        for stem in ["01_dr", "02_dr"]:
            photo = rng.integers(40, 200, size=(80, 120, 3), dtype=np.uint8)
            photos[stem] = photo
            out = io.BytesIO()
            Image.fromarray(photo).save(out, format="PNG")
            held.writestr(f"images/{stem}.png", out.getvalue())
            held.writestr(f"manual1/{stem}.tif", a_mask((120, 80)))
            field = np.full((80, 120), 255, dtype=np.uint8)
            out = io.BytesIO()
            Image.fromarray(field).save(out, format="PNG")
            held.writestr(f"mask/{stem}_mask.tif", out.getvalue())
    seg = tmp_path / "HRF-Seg+.zip"
    with zipfile.ZipFile(seg, "w") as held:
        for stem in ["01_dr", "02_dr"]:
            out = io.BytesIO()
            Image.fromarray(photos[stem][30:50, 70:90]).save(out, format="PNG")
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_IMAGES}/{stem}.JPG", out.getvalue())
            disc = a_seg_plus_mask((128, 64, 128))
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_DISC}/{stem}.png", disc)
            cup = None if stem == "02_dr" else (130, 76, 0)
            held.writestr(f"HRF-Seg+/{hrf.SEG_PLUS_CUP}/{stem}.png", a_seg_plus_mask(cup))

    store_root = tmp_path / "store"
    args = cli.parse(hrf.SLUG, ["--data-root", str(store_root), "--archive", str(archive)])
    layers_given = {hrf.SLUG: archive, hrf.SEG_PLUS_LAYER: seg}
    build.run(
        slug=hrf.SLUG,
        sources=[],
        discover=lambda _: hrf.discover(layers_given),
        resolution_of=hrf.RESOLUTION,
        args=args,
        fov_strategy=hrf.FOV_STRATEGY,
        extra_columns=hrf.EXTRA_COLUMNS,
        readers={"av": hrf.PALETTE},
    )
    store = store_root / hrf.SLUG
    rows = {row["key"]: row for row in manifest.read(store)}

    assert (int(rows["01_dr"]["roi_x0"]), int(rows["01_dr"]["roi_y0"])) == (70, 30)
    drawn = contours.read(store / "crop" / "contours" / "01_dr.csv")
    disc = drawn[("disc", hrf.SEG_PLUS_READER)]
    # The paint fills 5..14 of the crop, so 75..84 and 35..44 of the photograph.
    assert disc[:, 0].mean() + int(rows["01_dr"]["crop_x0"]) == pytest.approx(79.5, abs=1)
    assert disc[:, 1].mean() + int(rows["01_dr"]["crop_y0"]) == pytest.approx(39.5, abs=1)
    assert ("cup", hrf.SEG_PLUS_READER) in drawn
    assert set(rows["01_dr"]["maps"].split(";")) >= {"disc", "cup"}

    assert "cup" not in rows["02_dr"]["maps"].split(";")
    assert "disc" in rows["02_dr"]["maps"].split(";")
    assert "no cup" in rows["02_dr"]["notes"]
