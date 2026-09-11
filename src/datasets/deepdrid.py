# ABOUTME: Fetcher for DeepDRiD — the ISBI 2020 challenge's regular fundus photographs, two views
# ABOUTME: per eye, with DR grades and the artefact, clarity and field-definition quality scores.

"""DeepDRiD fetcher.

The dataset is not released as archives: the photographs are committed to a GitHub repository, so
this pins a commit and checks out only the regular-fundus subtree. Three splits arrive — training
and validation with a CSV of labels, and the challenge's online-evaluation set whose labels were
added later as two spreadsheets. Every image is a JPEG under ``Images/<patient>/<image_id>.jpg``.

The ultra-wide-field sub-challenge lives in the same repository and is **not** built, per the
skill's rule 13.7: a 200 degree frame beside a 45 degree one makes every measurement in a store
mean two things at once.

Layers
------
regular_fundus_images: photographs and labels for all three splits. Required.
"""

import csv
from pathlib import Path

import openpyxl

from datasets.utils import archives, build, cli, fov, manifest, quality, resolution

#: Slug, matching docs/datasets/deepdrid.md and this module's filename.
SLUG = "deepdrid"

#: The photographs are in the repository itself, so the commit is the provenance anchor.
SOURCES = [
    archives.GitSource(
        layer="deepdrid",
        repo="https://github.com/deepdrdoc/Deep-Diabetic-Retinopathy-Image-Dataset-DeepDRiD-.git",
        commit="56d8af71319803150d0e7b90533e0918c7bf85ee",
        paths=["regular_fundus_images"],
        licence="CC BY-SA 4.0 — share-alike, so anything derived from it carries the same terms",
    ),
]

#: What is deliberately left in the repository.
SKIPPED = ["the ultra-widefield sub-challenge (sub-challenge 3), a different instrument"]

#: The diabetic-retinopathy scale, in the authors' own words from the release's Readme. Level 5
#: occurs in no published split, but is kept so that its appearance would not be an error.
DR_LEVELS = {
    "0": "no apparent retinopathy",
    "1": "mild npdr",
    "2": "moderate npdr",
    "3": "severe npdr",
    "4": "pdr",
    "5": "ungradable",
}

#: The authors' overall verdict on a photograph, in their words.
OVERALL_QUALITY = {
    "0": "not good enough for diagnosis",
    "1": "good enough for diagnosis",
}

#: Columns only this dataset has. The quality subscores are the reason it is worth having.
EXTRA_COLUMNS = [
    manifest.Column("overall_quality", "The authors' own verdict, in their words"),
    manifest.Column("artifact", "0 none to 10 covering the posterior pole; lower is better"),
    manifest.Column(
        "clarity", "1 to 10, how deep a vascular arch and how many lesions are legible"
    ),
    manifest.Column("field_definition", "1 to 10, how well the disc and macula are framed"),
    manifest.Column("patient_dr_level", "The grade for the patient, from both eyes together"),
    manifest.Column("view", "Which photograph of this eye: the dataset takes at least two"),
    manifest.Column(
        "screening_project", "Nicheng, Shanghai or Nation; unstated for the test split"
    ),
]

#: The authors publish their own verdict, so it is mapped rather than derived from the subscores.
QUALITY = quality.Published(
    {OVERALL_QUALITY["1"]: "good", OVERALL_QUALITY["0"]: "bad"},
    column="overall_quality",
)

#: No field angle, no scale and no disc annotation to anchor on, so no resolution is claimed.
RESOLUTION = resolution.Declared(
    um_per_px=None,
    source="unknown",
    note="neither a field angle nor a scale is published, and there is no disc annotation to "
    "anchor on; consumers report pixels",
)

#: The three releases, as the authors split them.
SPLITS = {
    "regular-fundus-training": "train",
    "regular-fundus-validation": "val",
    "Online-Challenge1&2-Evaluation": "test",
}

EYES = {"l": "os", "r": "od"}


def discover(raw_root: Path) -> list[build.SourceRecord]:
    """Enumerate the regular fundus photographs and the labels published for them.

    :param raw_root: the checked-out repository.
    :return: one record per photograph, in split then image order.
    """
    root = raw_root / "regular_fundus_images"
    records = []
    for directory, split in SPLITS.items():
        labels = _labels(root / directory, split)
        for image_id, label in sorted(labels.items()):
            patient, view = image_id.split("_")
            records.append(_record(root / directory, split, image_id, patient, view, label))
    return records


def _record(directory, split, image_id, patient, view, label) -> build.SourceRecord:
    eye = EYES[view[0]]
    return build.SourceRecord(
        key=f"{split}_{image_id}",
        image=directory / "Images" / patient / f"{image_id}.jpg",
        split=split,
        patient=patient,
        eye=eye,
        disease=manifest.spell_out(label["dr_level"], DR_LEVELS, "disease"),
        extras={
            "overall_quality": manifest.spell_out(
                label["overall_quality"], OVERALL_QUALITY, "overall_quality"
            ),
            "artifact": label["artifact"],
            "clarity": label["clarity"],
            "field_definition": label["field_definition"],
            "patient_dr_level": manifest.spell_out(
                label["patient_dr_level"], DR_LEVELS, "patient_dr_level"
            ),
            "view": view[1:],
            "screening_project": label["screening_project"],
        },
    )


def _labels(directory: Path, split: str) -> dict[str, dict[str, str]]:
    """Every published label for one split, keyed by image id.

    The training and validation splits publish one CSV per split and a second naming the screening
    project each photograph came from. The evaluation split's labels were released a year later, as
    two spreadsheets — grades in one, quality in the other — with no screening project at all.
    """
    if split == "test":
        return _evaluation_labels(directory)

    release = directory.name.removeprefix("regular-fundus-")
    rows = {r["image_id"]: r for r in _csv(directory / f"{directory.name}.csv")}
    sources = {
        r["image_id"]: r["Source"] for r in _csv(directory / f"regular-fundus-source-{release}.csv")
    }
    return {
        image_id: {
            "dr_level": row[
                f"{'left' if image_id.split('_')[1][0] == 'l' else 'right'}_eye_DR_Level"
            ],
            "patient_dr_level": row["patient_DR_Level"],
            "overall_quality": row["Overall quality"],
            "artifact": row["Artifact"],
            "clarity": row["Clarity"],
            "field_definition": row["Field definition"],
            "screening_project": sources.get(image_id, ""),
        }
        for image_id, row in rows.items()
    }


def _evaluation_labels(directory: Path) -> dict[str, dict[str, str]]:
    grades = _sheet(directory / "Challenge1_labels.xlsx")
    scores = _sheet(directory / "Challenge2_labels.xlsx")
    return {
        image_id: {
            "dr_level": str(row["DR_Levels"]),
            "patient_dr_level": "",
            "overall_quality": str(scores[image_id]["Overall quality"]),
            "artifact": str(scores[image_id]["Artifact"]),
            "clarity": str(scores[image_id]["Clarity"]),
            "field_definition": str(scores[image_id]["Field definition"]),
            "screening_project": "",
        }
        for image_id, row in grades.items()
    }


def _csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _sheet(path: Path) -> dict[str, dict[str, object]]:
    rows = list(openpyxl.load_workbook(path, read_only=True).active.values)
    header = [str(name) for name in rows[0]]
    return {str(row[0]): dict(zip(header, row)) for row in rows[1:]}


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``uv run python -m datasets.deepdrid``."""
    args = cli.parse(SLUG, argv)
    return build.run(
        slug=SLUG,
        sources=SOURCES,
        discover=discover,
        resolution_of=RESOLUTION,
        args=args,
        fov_strategy=fov.DETECT,
        quality_rule=QUALITY,
        extra_columns=EXTRA_COLUMNS,
        skipped=SKIPPED,
    )


if __name__ == "__main__":
    raise SystemExit(main())
