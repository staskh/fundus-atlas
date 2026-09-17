# ABOUTME: The camera scale a dataset never published, inferred from the median optic disc of a
# ABOUTME: sample — committed as evidence, and copied into the manifest of the store it describes.

import argparse
import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from .utils import manifest, paths, resolution

#: How many photographs a group is measured from. Enough for a median to settle, small enough to
#: re-run; a group with fewer uses all of them and says so.
SAMPLE = 32

#: The seed the draw is recorded with, so two runs measure the same photographs.
SEED = 0

#: The disc segmenter this uses, by the slug of its catalogue page.
MODEL = "lunetv2-odc"

#: How far the discs of one group may scatter and still be one camera: the median absolute
#: deviation, as a share of the median. Disc diameter already varies about a tenth between people
#: on one device; more than that is mixed devices, mixed aiming, or a model that missed the disc.
SPREAD_GATE = 0.10

#: Fewer measured discs than this and a median means nothing, whatever its spread.
FLOOR = 16

#: Why a group was refused, in the words the JSON records.
TOO_FEW = "too-few: fewer than {floor} discs were measured, which is too few for a median"
TOO_WIDE = "spread: the discs disagree by {spread:.0%} of the median, more than {gate:.0%}"
NO_DISCS = "model-failed: the model found no disc on any photograph drawn"


@dataclass
class Group:
    """One camera: photographs of one subset at one native size, within a tolerance."""

    subset: str
    width: int
    height: int
    rows: list[dict[str, str]] = field(default_factory=list)

    def holds(self, row: dict[str, str]) -> bool:
        """Whether this photograph is of the same camera as the ones already here."""
        return row["subset"] == self.subset and resolution.same_camera(
            int(row["native_width"]), int(row["native_height"]), self.as_group()
        )

    def as_group(self) -> dict[str, object]:
        """This camera as the committed file names it, which is how a stamp matches a row to it."""
        return {"subset": self.subset, "native_width": self.width, "native_height": self.height}


def groups(rows: list[dict[str, str]]) -> list[Group]:
    """The cameras a dataset holds: its own subsets, each at its own native size.

    One scale per group, never one per dataset and never one per photograph: a dataset's own
    subcollections are different devices, and a 30° subset and a 50° one are different
    magnifications even at the same pixel size.
    """
    found: list[Group] = []
    for row in rows:
        for group in found:
            if group.holds(row):
                group.rows.append(row)
                break
        else:
            found.append(
                Group(row["subset"], int(row["native_width"]), int(row["native_height"]), [row])
            )
    return found


def measure(
    store: Path,
    slug: str,
    adapter: object,
    sample: int = SAMPLE,
    seed: int = SEED,
    subset: str = "",
) -> dict[str, object]:
    """Measure every group of one store, and return what should be committed about it."""
    rows = [row for row in manifest.read(store) if not subset or row["subset"] == subset]
    built = (
        json.loads((store / "build.json").read_text()) if (store / "build.json").exists() else {}
    )
    measured = []
    for group in groups(rows):
        print(
            f"{slug}: {group.subset} at {group.width}×{group.height}, "
            f"{len(group.rows)} photographs",
            file=sys.stderr,
        )
        measured.append(_measured(store, group, adapter, sample, seed))
    return {
        "dataset": slug,
        "typical_disc_um": resolution.DISC_MICRONS,
        "model": getattr(adapter, "slug", "unknown"),
        "builder_version": built.get("builder_version"),
        "n_requested": sample,
        "seed": seed,
        "spread_gate": SPREAD_GATE,
        "fingerprint": _fingerprint(adapter, built, sample, seed),
        "groups": measured,
    }


def _measured(
    store: Path, group: Group, adapter: object, sample: int, seed: int
) -> dict[str, object]:
    """One camera's scale, or the record of why it could not be given one."""
    drawn = _drawn(group.rows, sample, seed)
    diameters, keys = [], []
    for row in drawn:
        found = _diameter(store, row, adapter)
        if found is not None:
            diameters.append(found)
            keys.append(row["key"])

    record: dict[str, object] = {
        "subset": group.subset,
        "native_width": group.width,
        "native_height": group.height,
        "n_drawn": len(drawn),
        "n_measured": len(diameters),
        "keys": keys,
    }
    if not diameters:
        return {**record, "accepted": False, "note": NO_DISCS}

    # Rounded before anything is derived from it, so that a reader recomputing 1800 / median from
    # this file gets the number the file reports rather than one a hidden decimal away.
    middle = round(float(np.median(diameters)), 2)
    scatter = float(np.median([abs(value - middle) for value in diameters]))
    spread = scatter / middle if middle else math.inf
    record |= {
        "median_disc_px": middle,
        "mad_disc_px": round(scatter, 2),
        "mad_over_median": round(spread, 4),
    }
    if len(diameters) < FLOOR:
        return {**record, "accepted": False, "note": TOO_FEW.format(floor=FLOOR)}
    if spread > SPREAD_GATE:
        return {
            **record,
            "accepted": False,
            "note": TOO_WIDE.format(spread=spread, gate=SPREAD_GATE),
        }
    return {**record, "accepted": True, "um_per_px": round(resolution.from_disc(middle), 4)}


def _drawn(rows: list[dict[str, str]], sample: int, seed: int) -> list[dict[str, str]]:
    """The photographs to measure, chosen the same way twice."""
    if len(rows) <= sample:
        return list(rows)
    chosen = random.Random(seed).sample(range(len(rows)), sample)
    return [rows[index] for index in sorted(chosen)]


def _diameter(store: Path, row: dict[str, str], adapter: object) -> float | None:
    """One photograph's disc, as the diameter of a circle of the same area, in native pixels.

    The disc is a vertical oval, so its horizontal width is the wrong ruler; an equivalent diameter
    uses the whole outline. `None` where the model found nothing.
    """
    grid = getattr(adapter, "grid", 512)
    path = store / str(grid) / "images" / f"{row['key']}.png"
    if not path.exists():
        return None
    with Image.open(path) as image:
        pixels = np.asarray(image.convert("RGB"))
    side = int(row["crop_side"])
    prepared = adapter.prepare(pixels)[None]
    try:
        drawn = adapter.outline(prepared, [side], keys=[row["key"]])
    except TypeError:
        drawn = adapter.outline(prepared, [side])
    except Exception as failure:  # a crash is one photograph, not the group
        print(f"  {row['key']}: {failure!r}", file=sys.stderr)
        return None
    outlined = drawn[0]
    if outlined is None or outlined.outcome != "graded" or "disc" not in outlined.masks:
        return None
    area = float(outlined.masks["disc"].sum())
    return 2 * math.sqrt(area / math.pi) if area else None


def _fingerprint(adapter: object, built: dict[str, object], sample: int, seed: int) -> str:
    """Everything that would change the number, so a stale file can be told from a current one."""
    facts = {
        "model": getattr(adapter, "slug", "unknown"),
        "weights": adapter.identity() if hasattr(adapter, "identity") else "",
        "builder_version": built.get("builder_version"),
        "sample": sample,
        "seed": seed,
        "typical_disc_um": resolution.DISC_MICRONS,
        "spread_gate": SPREAD_GATE,
        "size_tolerance": resolution.SIZE_TOLERANCE,
        "floor": FLOOR,
    }
    return hashlib.sha256(json.dumps(facts, sort_keys=True, default=str).encode()).hexdigest()


def needs_inferring(store: Path) -> bool:
    """Whether this store is worth measuring at all.

    A dataset whose authors published a scale is exempt: replacing an author's measurement with an
    assumption about how big a disc usually is, is the error this command exists to avoid. Anything
    else is measured — including a store whose scale this repository derived from a stated field
    angle, because two independent derivations disagreeing is worth knowing. What may then be
    **written into** the manifest is a narrower question, and :data:`resolution.REPLACEABLE`
    answers it: a field-angle figure is preferred to a disc-anchored one and stands.
    """
    sources = {row.get("resolution_source", "") for row in manifest.read(store)}
    return sources != {"published"}


def run(
    slugs: list[str],
    root: Path | None = None,
    directory: Path | None = None,
    adapter: object | None = None,
    sample: int = SAMPLE,
    seed: int = SEED,
    subset: str = "",
    force: bool = False,
) -> list[dict[str, object]]:
    """Measure what has no published scale, commit it, and stamp it into the manifest."""
    where = directory or resolution.INFERRED
    written = []
    for slug in slugs:
        store = (root or paths.root()) / slug
        if not (store / manifest.MANIFEST).exists():
            print(f"warning: {slug} has no store built", file=sys.stderr)
            continue
        if not needs_inferring(store):
            print(f"{slug}: every photograph has a published scale — left alone", file=sys.stderr)
            continue
        model = adapter if adapter is not None else _catalogued()
        record = measure(store, slug, model, sample, seed, subset)
        if not force and _unchanged(slug, where, record):
            print(f"{slug}: unchanged — kept", file=sys.stderr)
            continue
        where.mkdir(parents=True, exist_ok=True)
        (where / f"{slug}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        stamped = resolution.stamp(store, slug, where)
        print(f"{slug}: {stamped} rows given a scale", file=sys.stderr)
        written.append(record)
    return written


def _unchanged(slug: str, where: Path, record: dict[str, object]) -> bool:
    stored = resolution.inferred(slug, where)
    return bool(stored) and stored.get("fingerprint") == record.get("fingerprint")


def _catalogued() -> object:
    """The disc model of record, loaded only when something actually has to be measured."""
    from models.utils import catalogue

    return catalogue.load(MODEL)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Infer a camera's microns per pixel from the typical optic disc."
    )
    parser.add_argument("--dataset", help="one dataset, or omit for every store that needs one")
    parser.add_argument("--subset", default="", help="one subset of that dataset")
    parser.add_argument("--data-root", help="override the store root")
    parser.add_argument("--sample", type=int, default=SAMPLE, help="photographs per group")
    parser.add_argument("--seed", type=int, default=SEED, help="the seed the draw uses")
    parser.add_argument(
        "--force", action="store_true", help="measure again even where nothing has changed"
    )
    asked = parser.parse_args(argv)
    root = Path(asked.data_root) if asked.data_root else paths.root()
    slugs = (
        [asked.dataset]
        if asked.dataset
        else sorted(path.name for path in root.glob("*") if (path / manifest.MANIFEST).exists())
    )
    run(
        slugs,
        root=root,
        sample=asked.sample,
        seed=asked.seed,
        subset=asked.subset,
        force=asked.force,
    )


if __name__ == "__main__":
    main()
