# ABOUTME: Turns a fetcher's list of source images into the standard store: native, each size,
# ABOUTME: the manifest, and build.json recording what this build actually is.

import io
import json
import shutil
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from datasets.utils import (
    archives,
    contours,
    crop,
    fov,
    manifest,
    paths,
    quality,
    resample,
    resolution,
)

#: Bumped when the crop, resample or grading rules change. A store built under an older number was
#: built to different rules, and a consumer can refuse to mix the two.
BUILDER_VERSION = 4

#: The maps a store can hold, in the order they appear in the `maps` column. `disc` and `cup` mean
#: polygons in `contours/<key>.csv`, never a raster.
LAYERS = ("vessels", "av", "fov", "disc", "cup")

#: The layers that live in `contours/<key>.csv` as polygons rather than in a directory of rasters.
OUTLINED = ("disc", "cup")

#: An outline whose trace reproduces its own mask less faithfully than this is worth a note in the
#: row: the shape was not a single clean blob. About 0.98 is as good as the convention allows.
POOR_TRACE = 0.95


class Unreadable(Exception):
    """A file the dataset published that cannot be decoded.

    Datasets do ship broken files — one of FQS's 2,246 originals is cut short mid-image — and that
    is a fact about the dataset rather than a reason to abandon the build or, worse, to load the
    readable part and pass the invented remainder off as retina.
    """


@dataclass
class SourceRecord:
    """One image as the dataset published it, before anything has been done to it.

    :param maps: layer name to the file holding it, for the layers this dataset publishes. A file
        is a path, or an `archives.Member` for one left inside its archive.
    :param outlines: (structure, reader) to either a mask to trace or an array of published
        coordinates. Structures are `disc` and `cup`; readers are the dataset's own ids.
    :param readers: annotators who contributed something other than an outline — a grade, say.
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
    quality_source: str = ""
    maps: dict[str, object] = field(default_factory=dict)
    outlines: dict[tuple[str, str], object] = field(default_factory=dict)
    readers: list[str] = field(default_factory=list)
    extras: dict[str, str] = field(default_factory=dict)
    readings: list[manifest.Reading] = field(default_factory=list)


def run(
    slug: str,
    sources: list,
    discover: Callable[[dict[str, Path]], list[SourceRecord]],
    resolution_of: resolution.Declared,
    args,
    fov_strategy: str = fov.DETECT,
    quality_rule: quality.Rule | None = None,
    extra_columns: list[manifest.Column] | None = None,
    skipped: Iterable[str] = (),
) -> int:
    """Build the store for one dataset.

    :param discover: given each layer's tree or archive by name, what the dataset holds.
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

    layers, provenance = _obtain(sources, store, args)
    raw = next(iter(layers.values()))
    records = discover(layers)
    if args.limit:
        records = records[: args.limit]

    built = {} if args.force else {row["key"]: row for row in _previous_rows(store)}
    rows, readings = [], []
    for n, record in enumerate(records, 1):
        try:
            rows.append(
                _reusable(built[record.key], record)
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
        except Unreadable as broken:
            warnings.append(f"not built: {record.key} — {broken}")
            print(f"\nwarning: {warnings[-1]}", file=sys.stderr)
            continue
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


def _reusable(row: dict[str, str], record: SourceRecord) -> dict[str, str]:
    """A row from an earlier build, ready for this run's readings.

    Whatever the readers decide is cleared first. Those cells were filled from readings the last
    time too, and a fetcher that has since corrected a label — a decision column read under the
    wrong heading, say — must be able to reach a store whose images are already built without
    rebuilding them.
    """
    decided = {reading.field for reading in record.readings}
    if not decided:
        return row
    return {**row, **dict.fromkeys(decided, ""), "multi_reader": "", "readers": ""}


def _previous_build(store: Path) -> dict | None:
    """What an earlier run left here, or `None` for a store that does not exist yet."""
    record = store / "build.json"
    return json.loads(record.read_text()) if record.exists() else None


def _previous_rows(store: Path) -> list[dict[str, str]]:
    """The rows an earlier run wrote, so an interrupted build keeps its finished work."""
    return list(manifest.read(store)) if (store / manifest.MANIFEST).exists() else []


def _is_built(key: str, store: Path, sizes: list[int], built: dict[str, dict[str, str]]) -> bool:
    """Whether this image is finished: described in the manifest and present at every size.

    Disc and cup are one contour file rather than two rasters, so looking for `disc/<key>.png`
    would call every outlined image unbuilt and trace all ten of its masks again on every run.
    """
    row = built.get(key)
    if row is None:
        return False
    named = [name for name in row.get("maps", "").split(";") if name]
    rasters = ["images", *(name for name in named if name not in OUTLINED)]
    wanted = [(layer, f"{key}.png") for layer in rasters]
    if any(name in OUTLINED for name in named):
        wanted.append(("contours", f"{key}.csv"))
    return all(
        paths.layer(store, size, layer).joinpath(file).exists()
        for size in [paths.NATIVE, *sizes]
        for layer, file in wanted
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


def _obtain(sources: list, store: Path, args) -> tuple[dict[str, Path], list[dict[str, str]]]:
    """Get the dataset onto disk, however this run was asked to.

    :return: where each declared layer ended up, by name, and what to record about it. A tree
        handed over with ``--raw`` or ``--archive`` stands in for every layer: someone supplying
        one by hand is supplying the dataset.
    """
    raw_dir = store / "raw"
    given = args.raw or args.archive
    if given:
        where = Path(args.raw) if args.raw else archives.extract(Path(given), raw_dir / "archive")
        layers = {source.layer: where for source in sources} or {"local": where}
        return layers, [{"layer": "local", "path": str(given)}]

    layers, provenance = {}, []
    for source in sources:
        try:
            where, record = source.obtain(raw_dir, verify=args.verify)
        except PermissionError:
            if source.optional:
                continue
            raise
        layers[source.layer] = where
        provenance.append(record)
    if not layers:
        raise ValueError(
            "nothing to build from: this fetcher declares no source, so it needs --raw"
        )
    return layers, provenance


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
    photograph = _handle(record.image, raw)
    image = _read(photograph, "RGB")
    height, width = image.shape[:2]

    if fov_strategy == fov.FROM_MASK and "fov" in record.maps:
        published = _read(_handle(record.maps["fov"], raw), "L")
        circle = fov.detect(np.dstack([published] * 3))
        footprint = np.where(published > 0, 255, 0).astype(np.uint8)
    else:
        circle = fov.detect(image)
        footprint = fov.mask_of(image)

    square = crop.square_around(circle)
    frames = {"images": crop.apply(image, square), "fov": crop.apply(footprint, square)}
    for name, source in record.maps.items():
        if name == "fov":
            continue
        frames[name] = crop.apply(_read(_handle(source, raw), "L"), square)

    for size in [paths.NATIVE, *sizes]:
        for name, frame in frames.items():
            out = paths.layer(store, size, name)
            out.mkdir(parents=True, exist_ok=True)
            written = out / f"{record.key}.png"
            if written.exists() and not force:
                continue
            frame_at = frame if size == paths.NATIVE else _resize(name, frame, size)
            Image.fromarray(frame_at).save(written)

    drawn, notes = _outlines(record, raw, square)
    for size in [paths.NATIVE, *sizes]:
        if drawn:
            scale = 1.0 if size == paths.NATIVE else size / square.side
            contours.write(paths.layer(store, size, "contours") / f"{record.key}.csv", drawn, scale)

    structures = {structure for structure, _ in drawn}
    readers = sorted({reader for _, reader in drawn} | set(record.readers))
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
        "maps": ";".join(name for name in LAYERS if name in frames or name in structures),
        "readers": ";".join(readers),
        "patient": record.patient,
        "visit": record.visit,
        "eye": record.eye,
        "disease": record.disease,
        "source_image": photograph.label,
        "sha256": archives.sha256_of(photograph),
        "notes": "; ".join(filter(None, [record.notes, *notes])),
        **record.extras,
    }
    if record.quality_source:
        # The graders' own verdicts decide the cell, in manifest.write; this only records that the
        # grade is theirs rather than ours.
        row["quality_source"] = record.quality_source
    else:
        graded, source = quality.grade_of(quality_rule, row)
        if graded or source:
            row["quality"], row["quality_source"] = graded, source
    return row


def _handle(source, raw: Path) -> archives.Handle:
    """Whatever a fetcher gave for a file, as something that can be opened and can name itself."""
    if isinstance(source, (archives.File, archives.Member)):
        return source
    return archives.File(Path(source), root=raw if raw.is_dir() else None)


def _read(handle: archives.Handle, mode: str) -> np.ndarray:
    """One image, wherever it lives.

    The bytes are read whole before decoding: a member of a zip is a stream that cannot be seeked
    about cheaply, and an image decoder does exactly that.
    """
    try:
        with handle.open() as f:
            return np.asarray(Image.open(io.BytesIO(f.read())).convert(mode))
    except (OSError, ValueError) as broken:
        raise Unreadable(f"{handle.label} could not be read: {broken}") from broken


def _outlines(
    record: SourceRecord, raw: Path, square: crop.Square
) -> tuple[dict[tuple[str, str], np.ndarray], list[str]]:
    """Every disc and cup outline this image has, in the native frame.

    Traced or transformed exactly once, here: each size is scaled from these nodes, so a size
    added years later is identical to the same size built today.
    """
    drawn, notes = {}, []
    for (structure, reader), source in sorted(record.outlines.items()):
        if isinstance(source, np.ndarray):
            drawn[(structure, reader)] = source - np.array([square.x0, square.y0])
            continue
        try:
            mask = crop.apply(_read(_handle(source, raw), "L"), square)
        except Unreadable:
            notes.append(f"{structure} by {reader} could not be read")
            continue
        nodes = contours.trace(mask)
        if len(nodes) == 0:
            notes.append(f"{reader} drew no {structure}")
            continue
        faithful = contours.fidelity(mask, nodes)
        if faithful < POOR_TRACE:
            notes.append(f"{structure} by {reader} traces at IoU {faithful:.2f}")
        drawn[(structure, reader)] = nodes
    return drawn, notes


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
