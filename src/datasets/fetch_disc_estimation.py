# ABOUTME: Where each photograph's optic disc and cup sit, and how large they are, in the native
# ABOUTME: crop — one CSV row per image key, committed with a sidecar naming what measured it.

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from .fetch_um_resolution import outlined
from .utils import manifest, paths, resample

#: Where the estimates are committed, one CSV and one JSON per dataset.
ESTIMATED = Path(__file__).resolve().parents[2] / "results" / "disc_estimation"

#: The disc-and-cup segmenter this uses, by the slug of its catalogue page.
MODEL = "segformer-disc-cup"

#: The frame every coordinate is in: the store's `native/` square, `crop_side` pixels across.
FRAME = "native crop"

#: What the CSV holds, in order.
COLUMNS = ("key", "outcome", "disc_cx", "disc_cy", "disc_r", "cup_cx", "cup_cy", "cup_r", "note")

#: What became of a photograph, beyond the model's own `graded`, `declined` and `failed`.
NO_DISC = "no-disc"
NO_IMAGE = "no-image"


def estimate(store: Path, adapter: object) -> list[dict[str, str]]:
    """One row per photograph in the manifest, in manifest order, whether or not a disc was found."""
    return [_estimated(store, row, adapter) for row in manifest.read(store)]


def _estimated(store: Path, row: dict[str, str], adapter: object) -> dict[str, str]:
    """One photograph's disc and cup, read from its native image resized to the model's grid."""
    key = row["key"]
    record = dict.fromkeys(COLUMNS, "") | {"key": key}
    path = store / "native" / "images" / f"{key}.png"
    if not path.exists():
        return record | {"outcome": NO_IMAGE}
    with Image.open(path) as image:
        pixels = np.asarray(image.convert("RGB"))
    prepared = adapter.prepare(resample.photograph(pixels, adapter.grid))[None]
    found = outlined(adapter, prepared, int(row["crop_side"]), key)
    if found is None:
        return record | {"outcome": "failed"}
    if found.outcome != "graded":
        return record | {"outcome": found.outcome, "note": found.note}
    disc = _circle(found.masks.get("disc"))
    if disc is None:
        return record | {"outcome": NO_DISC}
    record |= {"outcome": "graded", **dict(zip(("disc_cx", "disc_cy", "disc_r"), disc))}
    cup = _circle(found.masks.get("cup"))
    if cup is not None:
        record |= dict(zip(("cup_cx", "cup_cy", "cup_r"), cup))
    return record


def _circle(mask: np.ndarray | None) -> tuple[str, str, str] | None:
    """The centroid and equivalent radius of the largest connected patch, or `None` if empty.

    Only the largest patch counts, so a stray speck elsewhere cannot pull the centre off the disc.
    The radius is that of a circle of the same area: the disc is a vertical oval, and one axis
    alone is the wrong ruler.
    """
    if mask is None or not mask.any():
        return None
    labels, count = ndimage.label(mask)
    sizes = ndimage.sum_labels(mask, labels, range(1, count + 1))
    largest = labels == (int(np.argmax(sizes)) + 1)
    ys, xs = np.nonzero(largest)
    radius = math.sqrt(len(xs) / math.pi)
    return f"{xs.mean():.2f}", f"{ys.mean():.2f}", f"{radius:.2f}"


def _fingerprint(adapter: object, built: dict[str, object], keys: list[str]) -> str:
    """Everything that would change a row, so a stale file can be told from a current one."""
    facts = {
        "model": getattr(adapter, "slug", "unknown"),
        "weights": adapter.identity() if hasattr(adapter, "identity") else "",
        "grid": getattr(adapter, "grid", None),
        "builder_version": built.get("builder_version"),
        "frame": FRAME,
        "keys": keys,
    }
    return hashlib.sha256(json.dumps(facts, sort_keys=True, default=str).encode()).hexdigest()


def run(
    slugs: list[str],
    root: Path | None = None,
    directory: Path | None = None,
    adapter: object | None = None,
    force: bool = False,
) -> None:
    """Estimate every photograph of each store, and commit the CSV and its sidecar."""
    where = directory or ESTIMATED
    model = adapter
    for slug in slugs:
        store = (root or paths.root()) / slug
        if not (store / manifest.MANIFEST).exists():
            print(f"warning: {slug} has no store built", file=sys.stderr)
            continue
        model = model if model is not None else _catalogued()
        built = (
            json.loads((store / "build.json").read_text())
            if (store / "build.json").exists()
            else {}
        )
        keys = [row["key"] for row in manifest.read(store)]
        fingerprint = _fingerprint(model, built, keys)
        if not force and _unchanged(slug, where, fingerprint):
            print(f"{slug}: unchanged — kept", file=sys.stderr)
            continue
        print(f"{slug}: {len(keys)} photographs", file=sys.stderr)
        rows = estimate(store, model)
        where.mkdir(parents=True, exist_ok=True)
        with open(where / f"{slug}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(COLUMNS))
            writer.writeheader()
            writer.writerows(rows)
        sidecar = {
            "dataset": slug,
            "model": getattr(model, "slug", "unknown"),
            "grid": getattr(model, "grid", None),
            "builder_version": built.get("builder_version"),
            "frame": FRAME,
            "n_images": len(rows),
            "n_disc": sum(1 for row in rows if row["disc_r"]),
            "n_cup": sum(1 for row in rows if row["cup_r"]),
            "fingerprint": fingerprint,
        }
        (where / f"{slug}.json").write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
        print(f"{slug}: {sidecar['n_disc']} of {len(rows)} discs found", file=sys.stderr)


def _unchanged(slug: str, where: Path, fingerprint: str) -> bool:
    sidecar = where / f"{slug}.json"
    if not sidecar.exists() or not (where / f"{slug}.csv").exists():
        return False
    return json.loads(sidecar.read_text()).get("fingerprint") == fingerprint


def _catalogued() -> object:
    """The disc-and-cup model of record, loaded only when something actually has to be measured."""
    from models.utils import catalogue

    return catalogue.load(MODEL)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Estimate each photograph's optic disc and cup in the native crop."
    )
    parser.add_argument("--dataset", help="one dataset, or omit for every built store")
    parser.add_argument("--data-root", help="override the store root")
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
    run(slugs, root=root, force=asked.force)


if __name__ == "__main__":
    main()
