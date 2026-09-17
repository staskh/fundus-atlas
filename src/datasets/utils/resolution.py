# ABOUTME: Native resolution in microns per pixel, its provenance, and the value at any built size.
# ABOUTME: Never guessed: a dataset that publishes none keeps none, and consumers report pixels.

import csv
import json
from dataclasses import dataclass
from pathlib import Path

#: Where an inferred camera scale is committed, one JSON per dataset. It lives in the repository
#: rather than in the store, because the store is a rebuildable cache and this is a measurement: it
#: costs a pass of a disc model over a sample, and it carries the provenance no CSV cell has room
#: for — which model, which photographs, which gate.
INFERRED = Path(__file__).resolve().parents[3] / "results" / "um_resolution"

#: How far two photographs' native sizes may differ and still be the same camera. Field-of-view
#: detection moves the native dimensions by a few pixels on one device; more than this is another
#: magnification. The grouping that measures a scale and the stamp that writes it down must use one
#: tolerance, or the photographs a measurement was made from are the ones left without it.
SIZE_TOLERANCE = 0.10

#: The sources a stamped value may replace. A published figure is never among them: overwriting an
#: author's measurement with our assumption about how big a disc usually is, is the error this whole
#: split exists to prevent. A `field_angle` derivation is replaced, because it is also ours and is
#: the weaker of the two — the angle is what the camera is sold as, the disc is what is in the
#: photograph. Both are kept: the one that gave way is still on the dataset's page and in
#: `results/um_resolution/`, which is where the two can be compared.
#: `disc_anchored` is among them because it is **our own previous copy**: the JSON is the source of
#: truth, so a re-measurement has to be able to reach the manifest. Without it a `--force` run would
#: rewrite the evidence and leave every store quoting the numbers it had superseded.
REPLACEABLE = ("", "unknown", "field_angle", "disc_anchored")

#: How a resolution was arrived at, in order of preference. An author's own figure first; then a
#: disc measured on the photographs themselves; then a field angle, which is a nominal
#: specification multiplied by a constant and never measured on anything.
SOURCES = ("published", "disc_anchored", "field_angle", "inherited", "unknown")

#: Microns of retina spanned by one degree of field at the posterior pole. An approximation that
#: ignores eye length and projection, which is why `field_angle` ranks below a published value.
MICRONS_PER_DEGREE = 300.0

#: The width of a real optic disc, in microns. Anchored on the eye rather than on the camera.
DISC_MICRONS = 1800.0


@dataclass(frozen=True)
class Declared:
    """A dataset's native resolution, as established by the person writing its fetcher.

    :param um_per_px: microns per pixel, or `None` where it is per image or could not be
        established at all.
    :param source: one of :data:`SOURCES`.
    :param degrees: the stated field of view, for a dataset whose scale follows from it. The
        resolution is then **per image** rather than per dataset, because the field's diameter in
        pixels differs from photograph to photograph, so the value is computed by
        :meth:`for_field` as each row is written.
    :param note: the derivation, or why no value could be established.
    """

    um_per_px: float | None
    source: str
    note: str
    degrees: float | None = None

    def __post_init__(self) -> None:
        if self.source not in SOURCES:
            raise ValueError(f"{self.source!r} is not one of {SOURCES}")
        if self.source == "field_angle":
            if self.degrees is None:
                raise ValueError("source 'field_angle' needs the degrees the authors state")
            return
        if (self.um_per_px is None) != (self.source == "unknown"):
            raise ValueError("a value needs a source, and source 'unknown' needs no value")

    def for_field(self, fov_r: float) -> float | None:
        """This photograph's resolution, given the radius of the field that was fitted to it."""
        if self.source == "field_angle" and fov_r > 0:
            return from_field_angle(self.degrees, 2 * fov_r)
        return self.um_per_px


def um_per_px_at(um_per_px: float | None, crop_side: int, size: int) -> float | None:
    """The resolution of a built size, from the native one.

    One pixel at ``size`` spans ``crop_side / size`` native pixels. ``crop_side`` varies per image,
    so this is per row rather than per dataset — which is why the manifest records the crop.
    """
    if um_per_px is None:
        return None
    return um_per_px * crop_side / size


def from_field_angle(degrees: float, fov_diameter_px: float) -> float:
    """Microns per pixel from a stated field of view. Source ``field_angle``."""
    return MICRONS_PER_DEGREE * degrees / fov_diameter_px


def from_disc(disc_diameter_px: float) -> float:
    """Microns per pixel from a marked optic disc. Source ``disc_anchored``."""
    return DISC_MICRONS / disc_diameter_px


def stamp(store: Path, slug: str, directory: Path | None = None) -> int:
    """Copy a dataset's inferred camera scale into the manifest rows it was measured from.

    The number is **not computed here**: it is read from the committed
    ``results/um_resolution/<slug>.json`` and copied into the rows whose subset and native size the
    group describes. That keeps a store build free of any disc model, lets a rebuilt store recover
    the figure without measuring anything again, and leaves one place — the JSON — where the
    derivation can be argued with.

    A row whose group has since been refused has its copy **withdrawn**: the JSON is the source of
    truth in both directions, and a manifest that went on quoting a number the evidence had taken
    back would be worse than one that never had it.

    :returns: how many rows were given a value they did not have, or had one taken away.
    :raises ValueError: if the scale was measured on a differently built store, since a changed
        crop changes the discs it was measured from.
    """
    record = inferred(slug, directory)
    if not record:
        return 0
    groups = _accepted(slug, directory)
    built = (
        json.loads((store / "build.json").read_text()) if (store / "build.json").exists() else {}
    )
    for group in groups:
        if group.get("builder_version") != built.get("builder_version"):
            raise ValueError(
                f"{slug}'s inferred scale was measured on builder version "
                f"{group.get('builder_version')} and this store is version "
                f"{built.get('builder_version')}; measure it again rather than stamping it"
            )

    path = store / "manifest.csv"
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        columns, rows = list(reader.fieldnames or []), list(reader)

    stamped = 0
    for row in rows:
        if row.get("resolution_source", "") not in REPLACEABLE:
            continue
        found = _group_of(row, groups)
        if found is not None:
            row["um_per_px"] = f"{float(found['um_per_px']):.6f}"
            row["resolution_source"] = "disc_anchored"
            stamped += 1
        elif row.get("resolution_source") == "disc_anchored":
            row["um_per_px"] = ""
            row["resolution_source"] = "unknown"
            stamped += 1

    if stamped:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns, restval="")
            writer.writeheader()
            writer.writerows(rows)
    return stamped


def inferred(slug: str, directory: Path | None = None) -> dict[str, object]:
    """What was committed about one dataset's inferred scale, or nothing at all."""
    path = (directory or INFERRED) / f"{slug}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _accepted(slug: str, directory: Path | None) -> list[dict[str, object]]:
    """The groups that passed their gate, each carrying the store they were measured on."""
    record = inferred(slug, directory)
    return [
        {**group, "builder_version": record.get("builder_version")}
        for group in record.get("groups", [])
        if group.get("accepted") and group.get("um_per_px") is not None
    ]


def same_camera(width: int, height: int, group: dict[str, object]) -> bool:
    """Whether a photograph of this size belongs to a group measured at that one."""
    return _near(width, int(group["native_width"])) and _near(height, int(group["native_height"]))


def _near(value: int, of: int) -> bool:
    return abs(value - of) <= SIZE_TOLERANCE * of


def _group_of(row: dict[str, str], groups: list[dict[str, object]]) -> dict[str, object] | None:
    """The camera this photograph belongs to: its own subcollection, at its own native size.

    Where two groups both fit — a device measured at two close sizes — the nearer one takes it, so
    that the answer does not depend on the order the groups happen to be written in.
    """
    width, height = int(row["native_width"]), int(row["native_height"])
    fitting = [
        group
        for group in groups
        if str(group.get("subset", "")) == row.get("subset", "")
        and same_camera(width, height, group)
    ]
    if not fitting:
        return None
    return min(fitting, key=lambda group: _distance(width, height, group))


def _distance(width: int, height: int, group: dict[str, object]) -> float:
    """How far a photograph is from a group's own size, relative to it."""
    return abs(width - int(group["native_width"])) / int(group["native_width"]) + abs(
        height - int(group["native_height"])
    ) / int(group["native_height"])
