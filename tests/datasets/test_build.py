# ABOUTME: End-to-end test of a build, on a synthetic two-image dataset written to disk.
# ABOUTME: Real files, real PNGs, real manifest — the only thing not real is the retina.

import json
import shutil

import numpy as np
import pytest
from PIL import Image

from datasets.utils import archives, build, cli, contours, fov, manifest, quality, resolution


def a_dataset(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for key, cx in (("a", 150), ("b", 160)):
        yy, xx = np.mgrid[0:300, 0:300]
        image = np.zeros((300, 300, 3), dtype=np.uint8)
        image[(xx - cx) ** 2 + (yy - 150) ** 2 <= 100**2] = 180
        Image.fromarray(image).save(raw / f"{key}.png")
        vessels = np.zeros((300, 300), dtype=np.uint8)
        vessels[145:155, 100:200] = 255
        Image.fromarray(vessels).save(raw / f"{key}_vessels.png")
    return raw


def discover(layers):
    raw = layers["local"]
    return [
        build.SourceRecord(
            key=key,
            image=raw / f"{key}.png",
            maps={"vessels": raw / f"{key}_vessels.png"},
            patient=f"p{key}",
            eye="od",
            extras={"artifact": "0"},
        )
        for key in ("a", "b")
    ]


def build_it(tmp_path, *argv):
    args = cli.parse("synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", *argv])
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated in the paper"),
        args=args,
        fov_strategy=fov.DETECT,
        quality_rule=quality.FromComponents({"artifact": "0"}),
        extra_columns=[manifest.Column("artifact", "0 is best")],
        skipped=["an ultra-wide-field split"],
    )
    return tmp_path / "store" / "synthetic"


def test_every_layer_is_written_at_native_and_at_each_size(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    for size in ("native", "64"):
        for layer in ("images", "vessels", "fov"):
            assert (store / size / layer / "a.png").exists()


def test_a_size_is_square_and_native_is_the_crop(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    assert Image.open(store / "64" / "images" / "a.png").size == (64, 64)
    # Native is the field's bounding box, to within the pixel the circle fit can resolve.
    assert Image.open(store / "native" / "images" / "a.png").size[0] == pytest.approx(200, abs=1)


def test_the_manifest_describes_the_crop_it_made(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    row = next(iter(manifest.read(store)))
    assert row["key"] == "a"
    assert int(row["crop_side"]) == pytest.approx(200, abs=1)
    assert row["maps"] == "vessels;fov"
    assert row["patient"] == "pa"
    assert row["um_per_px"] == "5"


def test_the_quality_rule_runs_over_the_dataset_s_own_columns(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    row = next(iter(manifest.read(store)))
    assert (row["quality"], row["quality_source"]) == ("good", "derived")
    assert row["artifact"] == "0"


def test_a_skipped_subcollection_is_recorded_rather_than_forgotten(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    record = json.loads((store / "build.json").read_text())
    assert record["warnings"] == ["not built: an ultra-wide-field split"]
    assert record["partial"] is False
    assert record["images"] == 2


def test_a_limited_build_says_it_is_partial(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)), "--limit", "1")
    record = json.loads((store / "build.json").read_text())
    assert record["partial"] is True
    assert record["images"] == 1


def test_a_raw_tree_the_caller_supplied_is_never_deleted(tmp_path):
    raw = a_dataset(tmp_path)
    build_it(tmp_path, "--raw", str(raw))
    assert (raw / "a.png").exists()


def test_a_second_run_rebuilds_nothing(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    build_it(tmp_path, "--raw", str(raw))
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before


def test_force_rebuilds_anyway(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    build_it(tmp_path, "--raw", str(raw), "--force")
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns != before


def test_a_new_size_is_built_from_native_with_no_archive_in_reach(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    shutil.rmtree(raw)  # the archive is gone; native must be enough
    args = cli.parse("synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "32,64"])
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated in the paper"),
        args=args,
    )
    assert Image.open(store / "32" / "images" / "a.png").size == (32, 32)
    assert Image.open(store / "32" / "vessels" / "a.png").size == (32, 32)
    assert json.loads((store / "build.json").read_text())["sizes"] == [32, 64]


def test_an_interrupted_build_continues_rather_than_starting_over(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw), "--limit", "1")
    assert json.loads((store / "build.json").read_text())["partial"] is True
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns

    build_it(tmp_path, "--raw", str(raw))
    record = json.loads((store / "build.json").read_text())
    assert record["images"] == 2
    assert record["partial"] is False
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before


def test_the_source_path_is_recorded_inside_the_archive_not_on_this_machine(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    row = next(iter(manifest.read(store)))
    assert row["source_image"] == "a.png"


def test_a_rerun_after_the_manifest_is_lost_does_not_rewrite_the_images(tmp_path):
    raw = a_dataset(tmp_path)
    store = build_it(tmp_path, "--raw", str(raw))
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    (store / "manifest.csv").unlink()
    (store / "build.json").unlink()
    build_it(tmp_path, "--raw", str(raw))
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before
    assert len(list(manifest.read(store))) == 2


def outlined(layers):
    """One image whose disc and cup were drawn by two experts, as masks to trace."""
    raw = layers["local"]
    yy, xx = np.mgrid[0:300, 0:300]
    for name, r in (("disc_e1", 40), ("disc_e2", 44), ("cup_e1", 20), ("cup_e2", 18)):
        mask = np.where((xx - 150) ** 2 + (yy - 150) ** 2 <= r**2, 255, 0).astype(np.uint8)
        Image.fromarray(mask).save(raw / f"a_{name}.png")
    return [
        build.SourceRecord(
            key="a",
            image=raw / "a.png",
            outlines={
                ("disc", "expert1"): raw / "a_disc_e1.png",
                ("disc", "expert2"): raw / "a_disc_e2.png",
                ("cup", "expert1"): raw / "a_cup_e1.png",
                ("cup", "expert2"): raw / "a_cup_e2.png",
            },
        )
    ]


def build_outlined(tmp_path):
    raw = a_dataset(tmp_path)
    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=outlined,
        resolution_of=resolution.Declared(5.0, "published", "stated in the paper"),
        args=args,
    )
    return tmp_path / "store" / "synthetic", raw


def test_disc_and_cup_are_contours_rather_than_rasters(tmp_path):
    store, _ = build_outlined(tmp_path)
    assert (store / "native" / "contours" / "a.csv").exists()
    assert not (store / "native" / "disc").exists()
    row = next(iter(manifest.read(store)))
    assert row["maps"] == "fov;disc;cup"
    assert row["readers"] == "expert1;expert2"


def test_every_reader_of_every_structure_is_in_one_file(tmp_path):
    store, _ = build_outlined(tmp_path)
    drawn = contours.read(store / "native" / "contours" / "a.csv")
    assert set(drawn) == {
        ("disc", "expert1"),
        ("disc", "expert2"),
        ("cup", "expert1"),
        ("cup", "expert2"),
    }


def test_a_sized_contour_is_the_native_one_scaled(tmp_path):
    store, _ = build_outlined(tmp_path)
    native = contours.read(store / "native" / "contours" / "a.csv")[("disc", "expert1")]
    sized = contours.read(store / "64" / "contours" / "a.csv")[("disc", "expert1")]
    row = next(iter(manifest.read(store)))
    scale = 64 / int(row["crop_side"])
    assert len(sized) == len(native)
    assert sized[0][0] == pytest.approx(native[0][0] * scale, abs=1)


def test_an_outline_is_placed_by_the_crop_and_not_by_the_frame(tmp_path):
    store, _ = build_outlined(tmp_path)
    row = next(iter(manifest.read(store)))
    drawn = contours.read(store / "native" / "contours" / "a.csv")[("disc", "expert1")]
    # The disc sits at (150, 150) in the source; in the native frame it is that, less the crop.
    assert drawn[:, 0].mean() == pytest.approx(150 - int(row["crop_x0"]), abs=3)


def test_published_coordinates_are_translated_not_traced(tmp_path):
    raw = a_dataset(tmp_path)

    def discover_coords(layers):
        root = layers["local"]
        return [
            build.SourceRecord(
                key="a",
                image=root / "a.png",
                outlines={("disc", "consensus"): np.array([[150.0, 150.0], [160.0, 150.0]])},
            )
        ]

    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover_coords,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
    )
    store = tmp_path / "store" / "synthetic"
    row = next(iter(manifest.read(store)))
    drawn = contours.read(store / "native" / "contours" / "a.csv")[("disc", "consensus")]
    assert drawn[0][0] == pytest.approx(150 - int(row["crop_x0"]))
    assert len(drawn) == 2


def a_dataset_with_a_broken_file(tmp_path):
    raw = a_dataset(tmp_path)
    (raw / "b.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"truncated here")
    return raw


def test_an_unreadable_photograph_does_not_stop_the_build(tmp_path):
    # FQS ships three PNGs that are cut short. A dataset's own corruption is a fact about the
    # dataset, not a reason to abandon the other 2,243 photographs.
    store = build_it(tmp_path, "--raw", str(a_dataset_with_a_broken_file(tmp_path)))
    assert [row["key"] for row in manifest.read(store)] == ["a"]


def test_an_unreadable_photograph_is_named_in_the_build_record(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset_with_a_broken_file(tmp_path)))
    record = json.loads((store / "build.json").read_text())
    assert any("b.png" in warning for warning in record["warnings"])
    assert record["images"] == 1


def test_an_unreadable_outline_leaves_the_photograph_built(tmp_path):
    raw = a_dataset(tmp_path)

    def discover_broken(layers):
        records = outlined(layers)
        broken = raw / "a_disc_e2.png"
        broken.write_bytes(b"\x89PNG\r\n\x1a\n" + b"cut short")
        records[0].outlines[("disc", "expert2")] = broken
        return records

    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover_broken,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
    )
    store = tmp_path / "store" / "synthetic"
    row = next(iter(manifest.read(store)))
    drawn = contours.read(store / "native" / "contours" / "a.csv")
    assert ("disc", "expert1") in drawn
    assert ("disc", "expert2") not in drawn
    assert "could not be read" in row["notes"]


def test_an_image_whose_outlines_are_built_counts_as_built(tmp_path):
    # Disc and cup are contour files, not rasters. Looking for disc.png finds nothing, so every
    # image with an outline would be traced again on every run — ten masks apiece, for nothing.
    store, _ = build_outlined(tmp_path)
    row = next(iter(manifest.read(store)))
    assert row["maps"] == "fov;disc;cup"
    assert build._is_built("a", store, [64], {"a": row})


def test_an_image_whose_contours_are_missing_does_not_count_as_built(tmp_path):
    store, _ = build_outlined(tmp_path)
    row = next(iter(manifest.read(store)))
    (store / "64" / "contours" / "a.csv").unlink()
    assert not build._is_built("a", store, [64], {"a": row})


def test_a_reused_row_takes_this_run_s_readings(tmp_path):
    # A label corrected in the fetcher must reach a store that already has its images, without
    # rebuilding them and without colliding with the value the previous run recorded.
    raw = a_dataset(tmp_path)

    def with_verdict(verdict):
        def discover_graded(layers):
            records = discover(layers)
            for record in records:
                record.readings = [manifest.Reading(record.key, "disease", "consensus", verdict)]
            return records

        return discover_graded

    def run(verdict):
        args = cli.parse(
            "synthetic",
            ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)],
        )
        build.run(
            slug="synthetic",
            sources=[],
            discover=with_verdict(verdict),
            resolution_of=resolution.Declared(5.0, "published", "stated"),
            args=args,
            extra_columns=[manifest.Column("artifact", "0 is best")],
        )
        return tmp_path / "store" / "synthetic"

    store = run("normal")
    assert next(iter(manifest.read(store)))["disease"] == "normal"
    before = (store / "native" / "images" / "a.png").stat().st_mtime_ns
    (store / "build.json").unlink()
    store = run("glaucoma suspect")
    assert next(iter(manifest.read(store)))["disease"] == "glaucoma suspect"
    assert (store / "native" / "images" / "a.png").stat().st_mtime_ns == before


def test_two_structures_can_come_out_of_one_mask_file(tmp_path):
    raw = a_dataset(tmp_path)
    shared = raw / "a_both.png"
    yy, xx = np.mgrid[0:300, 0:300]
    packed = np.zeros((300, 300), dtype=np.uint8)
    packed[(xx - 150) ** 2 + (yy - 150) ** 2 <= 60**2] = 255
    packed[(xx - 150) ** 2 + (yy - 150) ** 2 <= 25**2] = 128
    Image.fromarray(packed).save(shared)

    def discover_packed(layers):
        return [
            build.SourceRecord(
                key="a",
                image=layers["local"] / "a.png",
                outlines={
                    ("disc", "expert1"): contours.Layer(archives.File(shared), (128, 255)),
                    ("cup", "expert1"): contours.Layer(archives.File(shared), (128,)),
                },
            )
        ]

    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover_packed,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
    )
    store = tmp_path / "store" / "synthetic"
    drawn = contours.read(store / "native" / "contours" / "a.csv")
    disc = drawn[("disc", "expert1")]
    cup = drawn[("cup", "expert1")]
    assert (disc[:, 1].max() - disc[:, 1].min()) == pytest.approx(120, abs=4)
    assert (cup[:, 1].max() - cup[:, 1].min()) == pytest.approx(50, abs=4)


def test_outlines_drawn_on_a_crop_are_placed_back_on_the_photograph(tmp_path):
    # GRAPE draws its disc and cup on a crop around the nerve head and publishes the coordinates in
    # that crop's frame. Imported as though they were full-frame they would land somewhere else
    # entirely, and every physical figure derived from them would be wrong but plausible.
    raw = tmp_path / "raw"
    raw.mkdir()
    rng = np.random.default_rng(0)
    photograph = rng.integers(40, 200, size=(300, 300, 3), dtype=np.uint8)
    Image.fromarray(photograph).save(raw / "a.png")
    Image.fromarray(photograph[60:160, 90:190]).save(raw / "a_roi.png")

    def discover_roi(layers):
        return [
            build.SourceRecord(
                key="a",
                image=layers["local"] / "a.png",
                roi=layers["local"] / "a_roi.png",
                outlines={("disc", "expert1"): np.array([[10.0, 20.0], [30.0, 40.0]])},
            )
        ]

    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover_roi,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
        extra_columns=[
            manifest.Column("roi_x0", "where the crop sits"),
            manifest.Column("roi_y0", "where the crop sits"),
            manifest.Column("roi_match", "how well it was found"),
        ],
    )
    store = tmp_path / "store" / "synthetic"
    row = next(iter(manifest.read(store)))
    assert (int(row["roi_x0"]), int(row["roi_y0"])) == (90, 60)
    assert float(row["roi_match"]) > 0.99
    drawn = contours.read(store / "native" / "contours" / "a.csv")[("disc", "expert1")]
    # The node is 10, 20 in the crop, so 100, 80 in the photograph, less the crop this build made.
    assert drawn[0][0] == pytest.approx(100 - int(row["crop_x0"]))
    assert drawn[0][1] == pytest.approx(80 - int(row["crop_y0"]))


def test_a_check_on_the_finished_store_is_recorded_in_the_build(tmp_path):
    seen = {}

    def verify(store, layers, rows):
        seen["store"] = store
        seen["keys"] = [row["key"] for row in rows]
        return {"checked": len(rows), "worst": 0.97}

    raw = a_dataset(tmp_path)
    args = cli.parse(
        "synthetic", ["--data-root", str(tmp_path / "store"), "--sizes", "64", "--raw", str(raw)]
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
        extra_columns=[manifest.Column("artifact", "0 is best")],
        verify=verify,
    )
    store = tmp_path / "store" / "synthetic"
    assert seen["keys"] == ["a", "b"]
    assert seen["store"] == store
    assert json.loads((store / "build.json").read_text())["verification"] == {
        "checked": 2,
        "worst": 0.97,
    }


def test_a_build_with_nothing_to_check_says_nothing(tmp_path):
    store = build_it(tmp_path, "--raw", str(a_dataset(tmp_path)))
    assert "verification" not in json.loads((store / "build.json").read_text())


def test_a_traced_outline_can_be_drawn_back_into_the_mask_it_came_from():
    yy, xx = np.mgrid[0:200, 0:200]
    mask = np.where((xx - 100) ** 2 + (yy - 100) ** 2 <= 55**2, 255, 0).astype(np.uint8)
    redrawn = contours.rasterise(contours.trace(mask), mask.shape)
    overlap = (redrawn & (mask > 0)).sum() / (redrawn | (mask > 0)).sum()
    assert overlap > 0.98
