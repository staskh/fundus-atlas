# ABOUTME: Tests that building across several processes produces exactly what one process does.
# ABOUTME: Chaksu took an hour and three quarters on one core; the store must not depend on that.

import csv

import numpy as np
from PIL import Image

from datasets.utils import build, cli, manifest, resolution


def a_dataset(root, count=6):
    root.mkdir(parents=True, exist_ok=True)
    for n in range(count):
        yy, xx = np.mgrid[0:200, 0:200]
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        image[(xx - 100) ** 2 + (yy - 100) ** 2 <= 70**2] = 150 + n
        Image.fromarray(image).save(root / f"{n}.png")
        mask = np.zeros((200, 200), dtype=np.uint8)
        mask[90:110, 90:110] = 255
        Image.fromarray(mask).save(root / f"{n}_disc.png")
    return root


def discover(layers):
    raw = layers["local"]
    return [
        build.SourceRecord(
            key=f"k{n}",
            image=raw / f"{n}.png",
            outlines={("disc", "expert1"): raw / f"{n}_disc.png"},
            readings=[manifest.Reading(f"k{n}", "disease", "consensus", "normal")],
        )
        for n in range(6)
    ]


def build_with(tmp_path, name, jobs):
    raw = a_dataset(tmp_path / "raw")
    root = tmp_path / name
    args = cli.parse(
        "synthetic",
        ["--data-root", str(root), "--sizes", "64", "--raw", str(raw), "--jobs", str(jobs)],
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
    )
    return root / "synthetic"


def rows_of(store):
    with open(store / "manifest.csv", newline="") as f:
        return list(csv.DictReader(f))


def test_several_processes_build_exactly_what_one_does(tmp_path):
    alone = rows_of(build_with(tmp_path, "one", jobs=1))
    together = rows_of(build_with(tmp_path, "many", jobs=4))
    assert alone == together


def test_the_rows_keep_the_order_the_fetcher_discovered_them_in(tmp_path):
    store = build_with(tmp_path, "many", jobs=4)
    assert [row["key"] for row in rows_of(store)] == [f"k{n}" for n in range(6)]


def test_the_files_are_all_there(tmp_path):
    store = build_with(tmp_path, "many", jobs=4)
    for n in range(6):
        assert (store / "native" / "images" / f"k{n}.png").exists()
        assert (store / "64" / "contours" / f"k{n}.csv").exists()


def test_readings_survive_the_crossing_between_processes(tmp_path):
    store = build_with(tmp_path, "many", jobs=4)
    assert {row["disease"] for row in rows_of(store)} == {"normal"}


def test_a_broken_file_is_still_reported_when_workers_are_used(tmp_path):
    raw = a_dataset(tmp_path / "raw")
    (raw / "3.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"cut short")
    root = tmp_path / "store"
    args = cli.parse(
        "synthetic",
        ["--data-root", str(root), "--sizes", "64", "--raw", str(raw), "--jobs", "4"],
    )
    build.run(
        slug="synthetic",
        sources=[],
        discover=discover,
        resolution_of=resolution.Declared(5.0, "published", "stated"),
        args=args,
    )
    import json

    record = json.loads((root / "synthetic" / "build.json").read_text())
    assert record["images"] == 5
    assert any("k3" in warning for warning in record["warnings"])


def test_one_job_is_asked_for_explicitly_and_the_default_uses_the_machine():
    assert cli.parse("hrf", ["--jobs", "1"]).jobs == 1
    assert cli.parse("hrf", []).jobs >= 1
