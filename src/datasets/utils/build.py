# ABOUTME: Turns a fetcher's list of source images into the standard store: native, each size,
# ABOUTME: the manifest, and build.json recording what this build actually is.

import json
import shutil
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from datasets.utils import archives, crop, fov, manifest, paths, quality, resample, resolution

#: Bumped when the crop, resample or grading rules change. A store built under an older number was
#: built to different rules, and a consumer can refuse to mix the two.
BUILDER_VERSION = 4

#: The maps a store can hold, in the order they appear in the `maps` column.
LAYERS = ("vessels", "av", "fov", "disc", "cup")


@dataclass
class SourceRecord:
    """One image as the dataset published it, before anything has been done to it.

    :param maps: layer name to the file holding it, for the layers this dataset publishes.
    :param extras: this dataset's own manifest columns.
    :param readings: every reader's opinion, where the dataset names its readers.
    """

    key: str
    image: Path
    subset: str = "main"
    split: str = "unspecified"
    patient: str = ""
    visit: str = ""
    eye: str = ""
    disease: str = ""
    notes: str = ""
    maps: dict[str, Path] = field(default_factory=dict)
    extras: dict[str, str] = field(default_factory=dict)
    readings: list[manifest.Reading] = field(default_factory=list)


def run(
    slug: str,
    sources: list,
    discover: Callable[[Path], list[SourceRecord]],
    resolution_of: resolution.Declared,
    args,
    fov_strategy: str = fov.DETECT,
    quality_rule: quality.Rule | None = None,
    extra_columns: list[manifest.Column] | None = None,
    skipped: Iterable[str] = (),
) -> int:
    """Build the store for one dataset.

    :param discover: given the extracted tree, what the dataset holds.
    :param skipped: subcollections deliberately not built — an ultra-wide-field split, per the
        skill's rule 13.7. Each is warned about here and recorded in `build.json`, because a store
        that is quietly smaller than its dataset is how someone comes to under-count it.
    """
    extra_columns = extra_columns or []
    store = paths.store(args)
    warnings = [f"not built: {what}" for what in skipped]
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    done = _previous_build(store)
    if done and not args.force and not done["partial"]:
        return _add_sizes(slug, store, args, done)

    raw, provenance = _obtain(sources, store, args)
    records = discover(raw)
    if args.limit:
        records = records[: args.limit]

    built = {} if args.force else {row["key"]: row for row in _previous_rows(store)}
    rows, readings = [], []
    for n, record in enumerate(records, 1):
        rows.append(
            built[record.key]
            if _is_built(record.key, store, args.sizes, built)
            else _build_one(
                record,
                store,
                raw,
                args.sizes,
                resolution_of,
                fov_strategy,
                quality_rule,
                args.force,
            )
        )
        readings.extend(record.readings)
        if n % 50 == 0 or n == len(records):
            print(f"\r{slug}: {n}/{len(records)} images", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)

    manifest.write(store, rows, extra_columns, readings)
    _write_build_json(store, args, provenance, len(rows), warnings)

    # Only what this build downloaded is ever deleted. A tree passed with --raw belongs to the
    # person who passed it, and may well be somewhere else entirely.
    if not args.keep_raw and not args.raw:
        shutil.rmtree(store / "raw", ignore_errors=True)
    return 0


def _previous_build(store: Path) -> dict | None:
    """What an earlier run left here, or `None` for a store that does not exist yet."""
    record = store / "build.json"
    return json.loads(record.read_text()) if record.exists() else None


def _previous_rows(store: Path) -> list[dict[str, str]]:
    """The rows an earlier run wrote, so an interrupted build keeps its finished work."""
    return list(manifest.read(store)) if (store / manifest.MANIFEST).exists() else []


def _is_built(key: str, store: Path, sizes: list[int], built: dict[str, dict[str, str]]) -> bool:
    """Whether this image is finished: described in the manifest and present at every size."""
    row = built.get(key)
    if row is None:
        return False
    layers = ["images", *(name for name in row.get("maps", "").split(";") if name)]
    return all(
        paths.layer(store, size, layer).joinpath(f"{key}.png").exists()
        for size in [paths.NATIVE, *sizes]
        for layer in layers
    )


def _add_sizes(slug: str, store: Path, args, done: dict) -> int:
    """Build the sizes that do not exist yet, from `native/` alone.

    No download, no archive, no re-tracing: a size added a year after the first build is identical
    to the same size built on day one, which is the whole reason `native/` is never optional.
    """
    missing = [size for size in args.sizes if not paths.frame(store, size).exists()]
    if not missing:
        print(f"{slug}: up to date at {done['sizes']}", file=sys.stderr)
        return 0

    keys = [row["key"] for row in manifest.read(store)]
    print(f"{slug}: adding {missing} from native/", file=sys.stderr)
    for n, key in enumerate(keys, 1):
        for layer in sorted(paths.frame(store, paths.NATIVE).iterdir()):
            frame = np.asarray(Image.open(layer / f"{key}.png"))
            for size in missing:
                out = paths.layer(store, size, layer.name)
                out.mkdir(parents=True, exist_ok=True)
                Image.fromarray(_resize(layer.name, frame, size)).save(out / f"{key}.png")
        if n % 50 == 0 or n == len(keys):
            print(f"\r{slug}: {n}/{len(keys)} images", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)

    done["sizes"] = sorted(set(done["sizes"]) | set(missing))
    (store / "build.json").write_text(json.dumps(done, indent=2) + "\n")
    return 0


def _obtain(sources: list, store: Path, args) -> tuple[Path, list[dict[str, str]]]:
    """Get the dataset onto disk, however this run was asked to."""
    if args.raw:
        return Path(args.raw), [{"layer": "local", "path": args.raw}]
    raw_dir = store / "raw"
    if args.archive:
        return archives.extract(Path(args.archive), raw_dir / "archive"), [
            {"layer": "local", "path": args.archive}
        ]
    trees, provenance = [], []
    for source in sources:
        try:
            tree, record = source.obtain(raw_dir, verify=args.verify)
        except PermissionError:
            if source.optional:
                continue
            raise
        trees.append(tree)
        provenance.append(record)
    return trees[0], provenance


def _build_one(
    record: SourceRecord,
    store: Path,
    raw: Path,
    sizes: list[int],
    resolution_of: resolution.Declared,
    fov_strategy: str,
    quality_rule: quality.Rule | None,
    force: bool = False,
) -> dict[str, str]:
    """Crop one image to its field of view, write every size of it, and describe it."""
    image = np.asarray(Image.open(record.image).convert("RGB"))
    height, width = image.shape[:2]

    if fov_strategy == fov.FROM_MASK and "fov" in record.maps:
        published = np.asarray(Image.open(record.maps["fov"]).convert("L"))
        circle = fov.detect(np.dstack([published] * 3))
        footprint = np.where(published > 0, 255, 0).astype(np.uint8)
    else:
        circle = fov.detect(image)
        footprint = fov.mask_of(image)

    square = crop.square_around(circle)
    frames = {"images": crop.apply(image, square), "fov": crop.apply(footprint, square)}
    for name, path in record.maps.items():
        if name == "fov":
            continue
        frames[name] = crop.apply(np.asarray(Image.open(path).convert("L")), square)

    for size in [paths.NATIVE, *sizes]:
        for name, frame in frames.items():
            out = paths.layer(store, size, name)
            out.mkdir(parents=True, exist_ok=True)
            written = out / f"{record.key}.png"
            if written.exists() and not force:
                continue
            frame_at = frame if size == paths.NATIVE else _resize(name, frame, size)
            Image.fromarray(frame_at).save(written)

    row = {
        "key": record.key,
        "subset": record.subset,
        "split": record.split,
        "native_width": str(width),
        "native_height": str(height),
        "fov_cx": f"{circle.cx:.1f}",
        "fov_cy": f"{circle.cy:.1f}",
        "fov_r": f"{circle.r:.1f}",
        "fov_source": circle.source,
        "crop_x0": str(square.x0),
        "crop_y0": str(square.y0),
        "crop_side": str(square.side),
        "pad_fraction": f"{crop.pad_fraction(square, height, width):.4f}",
        "um_per_px": "" if resolution_of.um_per_px is None else f"{resolution_of.um_per_px:g}",
        "resolution_source": resolution_of.source,
        "maps": ";".join(name for name in LAYERS if name in frames),
        "patient": record.patient,
        "visit": record.visit,
        "eye": record.eye,
        "disease": record.disease,
        "source_image": _inside(record.image, raw),
        "sha256": archives.sha256_of(record.image),
        "notes": record.notes,
        **record.extras,
    }
    graded, source = quality.grade_of(quality_rule, row)
    if graded or source:
        row["quality"], row["quality_source"] = graded, source
    return row


def _inside(image: Path, raw: Path) -> str:
    """Where the source file sits inside the archive.

    Relative, not absolute: the store is portable, and a path naming somebody's home directory
    stops tracing a row back the moment the store is moved or copied.
    """
    try:
        return str(image.resolve().relative_to(raw.resolve()))
    except ValueError:
        return str(image)


def _resize(layer: str, frame: np.ndarray, size: int) -> np.ndarray:
    """Photographs are interpolated; every other layer is a set of labels and is not."""
    return resample.photograph(frame, size) if layer == "images" else resample.mask(frame, size)


def _write_build_json(store, args, provenance, images, warnings) -> None:
    record = {
        "built_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "builder_version": BUILDER_VERSION,
        "sizes": args.sizes,
        "images": images,
        "partial": bool(args.limit),
        "sources": provenance,
        "warnings": warnings,
    }
    (store / "build.json").write_text(json.dumps(record, indent=2) + "\n")
