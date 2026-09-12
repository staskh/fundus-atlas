# ABOUTME: Fetcher for Chaksu — 1,345 glaucoma-population photographs whose optic disc and cup were
# ABOUTME: outlined by five ophthalmologists each, with five independent glaucoma decisions as well.

"""Chaksu fetcher.

Two zips from figshare, train and test, each holding the same tree: the photographs under
``1.0_Original_Fundus_Images/<camera>/``, every expert's binary disc and cup masks under
``3.0_Doctors_Annotations_Binary_OD_OC/Expert N/<camera>/<structure>/``, and the five glaucoma
decisions in ``6.0_Glaucoma_Decision/``.

**The masks are never unpacked.** They are uncompressed TIFFs — 70 GB extracted against 11 GB in
the archives — and each is read once and turned into a polygon, so they are read where they lie.

Three cameras, and they are not the same shape: Remidio is portrait, 2448x3264, which most code
written for landscape photographs gets wrong. They are kept as three subsets.

Layers
------
train: Train.zip — photographs, per-expert masks and decisions. Required.
test: Test.zip — the same, for the test half. Required.
"""

import csv
import io
import random
import re
from pathlib import Path

import numpy as np
from PIL import Image

from datasets.utils import archives, build, cli, contours, fov, manifest, resolution

#: Slug, matching docs/datasets/chaksu.md and this module's filename.
SLUG = "chaksu"

SOURCES = [
    archives.Source(
        layer="train",
        url="https://ndownloader.figshare.com/files/37875672",
        filename="Train.zip",
        sha256="3c0fb482d6b711a8db418f98797007163db3e5bcb5abca3d8ffd0c462f9edf37",
        licence="CC BY 4.0",
        extract_it=False,
    ),
    archives.Source(
        layer="test",
        url="https://ndownloader.figshare.com/files/37875687",
        filename="Test.zip",
        sha256="90e89ad01bfb0c4c238ba22a4a46ab46b5849e2fc9253c7bda09509f6ca259fa",
        licence="CC BY 4.0",
        extract_it=False,
    ),
]

#: What is deliberately left in the archives.
SKIPPED = [
    (
        "the fused disc and cup masks (mean, median, majority, STAPLE): every one is a function "
        "of the five experts' outlines, which the store keeps"
    ),
    "the per-expert cup-to-disc measurements: each is computed from that expert's own outline",
    "the annotation overlays, which are the photographs with a boundary drawn on them",
]

#: The glaucoma decision, in the words the decision files use. The third spelling is a typo for the
#: second that appears throughout, from two of the five experts.
DECISIONS = {
    "NORMAL": "normal",
    "GLAUCOMA SUSPECT": "glaucoma suspect",
    "GLAUCOMA  SUSUPECT": "glaucoma suspect",
}

#: The five ophthalmologists, as the archive names them.
EXPERTS = ("Expert 1", "Expert 2", "Expert 3", "Expert 4", "Expert 5")

#: The three cameras, which are the dataset's own subcollections.
CAMERAS = ("Bosch", "Forus", "Remidio")

#: Some Bosch photographs name the person they came from: `P11_image_1` and `P11_image_2` are two
#: photographs of patient 11. Nothing else in the dataset identifies anyone.
PATIENT = re.compile(r"(p\d+)[_-]", re.IGNORECASE)

#: How many photographs the finished store is checked on, and how faithfully a redrawn contour
#: must match the mask it came from. The check is a round trip — trace, store, redraw in the
#: dataset's own coordinates — so it measures the crop and the scaling, not the tracing.
SAMPLES = 10
FAITHFUL = 0.95

#: No scale is published for any of the three cameras, and the disc annotations are in pixels.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="no camera scale or field angle is published; the discs are outlined in pixels",
)

PHOTOGRAPHS = "1.0_Original_Fundus_Images"
MASKS = "3.0_Doctors_Annotations_Binary_OD_OC"
DECISION_FILES = "6.0_Glaucoma_Decision"


def discover(layers: dict[str, Path]) -> list[build.SourceRecord]:
    """Enumerate the photographs, the five outlines of each, and the five decisions about it.

    :param layers: the train and test archives, unopened.
    :return: one record per photograph, by split, camera and name.
    """
    records = []
    # In the order the fetcher declares its layers, so the store's rows run train then test
    # rather than in whatever order the two names happen to sort.
    for split, archive in layers.items():
        half = _half(archive)
        decisions = _decisions(archive, half)
        outlines = _outlines(archive, half)
        for camera in CAMERAS:
            for member in _photographs(archive, half, camera):
                stem = Path(member.name).stem
                records.append(_record(split, camera, stem, member, decisions, outlines))
    return records


def _record(split, camera, stem, member, decisions, outlines) -> build.SourceRecord:
    key = f"{split}_{camera.lower()}_{stem.lower()}"
    said = decisions.get((camera.lower(), stem.lower()), {})
    readings = [
        manifest.Reading(
            key, "disease", _reader(expert), manifest.spell_out(verdict, DECISIONS, "disease")
        )
        for expert, verdict in said.items()
        if verdict
    ]
    named = PATIENT.match(stem)
    return build.SourceRecord(
        key=key,
        image=member,
        subset=camera.lower(),
        split=split,
        patient=named.group(1).lower() if named else "",
        readings=readings,
        outlines={
            (structure, _reader(expert)): mask
            for (structure, expert), mask in outlines.get(
                (camera.lower(), stem.lower()), {}
            ).items()
        },
    )


def _reader(column: str) -> str:
    """The reader a decision column belongs to.

    Anything that is not one of the five numbered experts is the agreed verdict, whatever it is
    called: the train archives head that column `Majority Decision` and two of the test archives
    head it `Glaucoma Decision`. Matching on the words would drop the consensus for a third of the
    test half and leave those photographs looking ungraded.
    """
    digits = "".join(ch for ch in column if ch.isdigit())
    return f"expert{digits}" if digits else manifest.CONSENSUS


def _half(archive: Path) -> str:
    """`Train` or `Test`: the archives name their own top directory, and the two differ in case."""
    first = archives.members(archive)[0].name
    return first.split("/")[0]


def _photographs(archive: Path, half: str, camera: str) -> list[archives.Member]:
    under = f"{half}/{PHOTOGRAPHS}/{camera}/"
    return sorted(archives.members(archive, under=under), key=lambda m: m.name)


def _outlines(archive: Path, half: str) -> dict:
    """Every expert's disc and cup mask, indexed by camera and photograph.

    Indexed rather than addressed directly because the archive's own capitalisation varies: one
    expert's folder is `Bosch/cup`, another's is `Bosch/Cup`, and a fetcher that composed the path
    would silently find nothing for some of the five.
    """
    found: dict = {}
    for member in archives.members(archive, under=f"{half}/{MASKS}/"):
        parts = member.name.split("/")
        if len(parts) < 6:
            continue
        _, _, expert, camera, structure, name = parts[:6]
        key = (camera.lower(), Path(name).stem.lower())
        found.setdefault(key, {})[(structure.lower(), expert)] = member
    return found


def _decisions(archive: Path, half: str) -> dict:
    """The five glaucoma decisions and the published majority, by camera and photograph."""
    said: dict = {}
    for camera in CAMERAS:
        name = f"{half}/{DECISION_FILES}/Glaucoma_Decision_Comparison_{camera}_majority.csv"
        for row in _csv(archive, name):
            image = row.get("Images") or ""
            if not image:
                continue
            stem = Path(image.split("-")[0]).stem.lower()
            said[(camera.lower(), stem)] = {
                column: value for column, value in row.items() if column != "Images"
            }
    return said


def _csv(archive: Path, name: str) -> list[dict[str, str]]:
    """One decision file, which is UTF-8 with a byte-order mark the csv module must not see."""
    with archives.Member(archive, name).open() as f:
        text = f.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def check(store: Path, layers: dict[str, Path], rows: list[dict[str, str]]) -> dict:
    """Redraw stored contours in the dataset's own coordinates and compare with its own masks.

    A round trip: the contour in `native/` is moved back by the crop it was made with, filled in at
    the photograph's original size, and set against the binary mask the archive publishes for that
    expert and that structure. It measures the crop and the placement rather than the tracing,
    which is where a silent error would sit — a contour can be a perfect outline of the wrong part
    of a photograph, and nothing in the store would say so.

    Sampled across all three cameras and all five experts, since the cameras differ in shape and
    the experts are separate files.

    :return: what was checked and how well it matched, for `build.json`.
    """
    chosen = _sample(rows)
    scores, failures = [], []
    for split, archive in layers.items():
        half = _half(archive)
        masks = _outlines(archive, half)
        for row in [r for r in chosen if r["split"] == split]:
            stem = row["key"].split("_", 2)[2]
            published = masks.get((row["subset"], stem), {})
            stored = contours.read(store / "native" / "contours" / f"{row['key']}.csv")
            back = np.array([int(row["crop_x0"]), int(row["crop_y0"])])
            for (structure, expert), member in sorted(published.items()):
                reader = _reader(expert)
                nodes = stored.get((structure, reader))
                if nodes is None:
                    continue
                with member.open() as f:
                    mask = np.asarray(Image.open(io.BytesIO(f.read())).convert("L")) > 0
                redrawn = contours.rasterise(nodes + back, mask.shape)
                union = (redrawn | mask).sum()
                score = float((redrawn & mask).sum() / union) if union else 0.0
                scores.append((row["subset"], reader, score))
                if score < FAITHFUL:
                    failures.append(
                        {
                            "key": row["key"],
                            "structure": structure,
                            "reader": reader,
                            "overlap": round(score, 4),
                        }
                    )
    if not scores:
        return {"checked": 0, "note": "no published mask could be read back"}

    values = np.array([score for _, _, score in scores])
    return {
        "what": (
            "each stored contour redrawn at the photograph's own size and compared with the binary "
            "mask the archive publishes for that expert and that structure"
        ),
        "photographs": len(chosen),
        "contours": len(scores),
        "overlap_median": round(float(np.median(values)), 4),
        "overlap_worst": round(float(values.min()), 4),
        "overlap_by_camera": _medians(scores, 0),
        "overlap_by_reader": _medians(scores, 1),
        "below_threshold": failures,
        "threshold": FAITHFUL,
    }


def _sample(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """A few photographs from each camera, chosen the same way on every run."""
    drawn = [row for row in rows if "disc" in row["maps"]]
    picked = []
    for camera in CAMERAS:
        from_camera = [row for row in drawn if row["subset"] == camera.lower()]
        picked += random.Random(0).sample(from_camera, min(SAMPLES, len(from_camera)))
    return picked


def _medians(scores, by: int) -> dict[str, float]:
    """The median overlap for each camera, or for each expert."""
    grouped: dict[str, list[float]] = {}
    for row in scores:
        grouped.setdefault(row[by], []).append(row[2])
    return {name: round(float(np.median(values)), 4) for name, values in sorted(grouped.items())}


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.chaksu``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        skipped=SKIPPED,
        verify=check,
    )


if __name__ == "__main__":
    raise SystemExit(main())
