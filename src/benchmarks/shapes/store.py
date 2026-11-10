# ABOUTME: The synthetic store: rendering the shapes to files once, and reading them back. Masks,
# ABOUTME: a manifest of how each was framed, and the values its geometry requires.

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from . import library, scene

#: Where a generated store lives unless the caller says otherwise. It is in the repository rather
#: than in one of the git-ignored caches because these are our own shapes: committing them means a
#: measurement can be repeated against the exact pictures it was taken on, without regenerating
#: anything and without trusting that the generator has not changed underneath.
STORE = Path("data/synthetic/av")

#: The angles every family is rendered at: every 15° of a quarter turn, which holds every
#: orientation of the pixel lattice. 0 and 90 sit square with the grid and 45 is its diagonal, which
#: is the difference that exposes a measurement walking the lattice rather than the vessel.
ROTATIONS = (0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 90.0)

#: What the manifest says about each rendering. `key` names it, the disc is given in pixels for a
#: measurement and in microns for a reader, and the three mask files are named outright so nothing
#: has to reconstruct a filename from a convention.
COLUMNS = (
    "key",
    "family",
    "side",
    "rotation",
    "um_per_px",
    "disc_cx",
    "disc_cy",
    "disc_r",
    "disc_diameter_um",
    "artery_width_um",
    "vein_width_um",
    "fov_cx",
    "fov_cy",
    "fov_r",
    "artery",
    "vein",
    "fov",
)


@dataclass(frozen=True)
class Rendering:
    """One stored rendering, read back: the masks, where the disc is, and at what scale."""

    key: str
    family: str
    side: int
    rotation: float
    um_per_px: float
    artery: np.ndarray
    vein: np.ndarray
    fov: np.ndarray
    disc: tuple[float, float, float]


def key_of(family: str, side: int, rotation: float) -> str:
    """What one rendering is called, and what its rows and its files are named after."""
    return f"{family}-{side}-{round(rotation):03d}"


def write(
    into: Path,
    families: tuple[str, ...] | list[str] | None = None,
    side: int = library.SIDE,
    rotations: tuple[float, ...] | list[float] = ROTATIONS,
) -> list[dict[str, object]]:
    """Render every family at every angle, and write the masks, the manifest and the ground truth.

    Generating once and measuring many times is the point of a store: a rendering costs seconds of
    rasterising that no benchmark then has to repeat, and — more importantly — every run afterwards
    measures the same pictures rather than pictures a later change to the generator would alter.

    The ground truth is two tables of the same shape: `ground_truth.csv`, the value each rendering's
    geometry requires, and `ground_truth_kind.csv`, how that value is known. A cell with a kind and
    no value is a biomarker the geometry leaves **without** a value; a cell with neither is one it
    settles nothing about.
    """
    into = Path(into)
    into.mkdir(parents=True, exist_ok=True)
    chosen = list(families) if families else list(library.SHAPES)
    rows: list[dict[str, object]] = []
    values: list[dict[str, object]] = []
    kinds: list[dict[str, object]] = []
    for family in chosen:
        settled = library.truths(family)
        for rotation in rotations:
            shape = library.build(family, side=side, rotation=float(rotation))
            rows.append(_render(into, shape, family, rotation))
            key = rows[-1]["key"]
            values.append({"key": key, **{n: _cell(t.value) for n, t in settled.items()}})
            kinds.append({"key": key, **{n: t.kind for n, t in settled.items()}})
    columns = _truth_columns(kinds)
    _write_rows(into / "manifest.csv", COLUMNS, rows)
    _write_rows(into / "ground_truth.csv", columns, values)
    _write_rows(into / "ground_truth_kind.csv", columns, kinds)
    return rows


def _cell(value: float | str | None) -> str:
    """One value as the table spells it: a number to every place it has, a category as itself."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return repr(float(value))


def _render(into: Path, shape: library.Shape, family: str, rotation: float) -> dict[str, object]:
    """One rendering's three masks, and the manifest row that says how it was framed."""
    key = key_of(family, shape.side, rotation)
    names = {}
    for which, mask in (("artery", shape.artery), ("vein", shape.vein), ("fov", shape.fov)):
        names[which] = f"{key}-{which}.png"
        _save(into / names[which], mask)
    x, y, radius = shape.disc
    drawn = library.scene(family)
    # Pixel i's centre is at i, so the frame's centre is half a pixel short of side / 2.
    centre = shape.side / 2.0 - 0.5
    return {
        "key": key,
        "family": family,
        "side": shape.side,
        "rotation": f"{rotation:.1f}",
        "um_per_px": repr(shape.um_per_px),
        "disc_cx": f"{x:.4f}",
        "disc_cy": f"{y:.4f}",
        "disc_r": f"{radius:.4f}",
        "disc_diameter_um": scene.DISC_DIAMETER_UM,
        # The trunk's: a shape whose daughters narrow by Murray's law has more than one width.
        "artery_width_um": drawn.artery.segments[0].width,
        "vein_width_um": drawn.vein.segments[0].width,
        "fov_cx": f"{centre:.4f}",
        "fov_cy": f"{centre:.4f}",
        "fov_r": f"{shape.side / 2.0:.4f}",
        **names,
    }


def _save(path: Path, mask: np.ndarray) -> None:
    """A mask as a one-bit PNG: it is a yes or a no per pixel, and nothing else should read as one.

    Saved through mode ``1`` rather than as 0-and-255 grey, so a reader cannot mistake a mask for
    an image and threshold it at some value of their own choosing.
    """
    Image.fromarray(np.asarray(mask, dtype=bool)).save(path, optimize=True)


def _write_rows(path: Path, columns: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _truth_columns(truths: list[dict[str, object]]) -> tuple[str, ...]:
    """`key`, then every canonical name any family pins, in the catalogue's own order.

    A family that pins nothing for a column leaves it **empty** rather than zero: a straight vessel
    does not have a central retinal equivalent of nought, it has none, and a zero there would be
    averaged into somebody's table as a measurement.
    """
    seen = {name for truth in truths for name in truth if name != "key"}
    from biomarkers import canonical

    ordered = [name for name in canonical.names() if name in seen]
    return ("key", *ordered, *sorted(seen - set(ordered)))


def digest(family: str, store: Path = STORE) -> str:
    """A sha256 of the pictures one family is drawn as, so a redrawing cannot go unnoticed.

    A benchmark fingerprints everything that could change a score, and for this benchmark the thing
    most able to change one is the drawing itself. Nothing else in the fingerprint would catch it:
    the grid, the scale and the angles are all unchanged when a shape is redrawn from different
    parameters, so a stored result would quietly go on describing a picture that no longer exists.

    It hashes **the masks and the manifest rows, and not the ground truth**, which is the line this
    benchmark draws everywhere: a run never reads what the geometry requires, so correcting a
    derivation must not throw away hours of measurement. Only redrawing does.
    """
    rows = [row for row in read(store) if row["family"] == family]
    if not rows:
        return "unbuilt"
    running = hashlib.sha256()
    for row in sorted(rows, key=lambda entry: entry["key"]):
        running.update("|".join(f"{column}={row[column]}" for column in COLUMNS).encode())
        for which in ("artery", "vein", "fov"):
            running.update((store / row[which]).read_bytes())
    return running.hexdigest()


def read(store: Path = STORE) -> list[dict[str, str]]:
    """The manifest, as it was written."""
    with (Path(store) / "manifest.csv").open() as handle:
        return list(csv.DictReader(handle))


def truth(store: Path = STORE) -> dict[str, dict[str, float | str]]:
    """What each rendering's geometry requires, by key, where it requires a value.

    A number is read as one; a category — the photograph's centring — is kept as the word it is.
    """
    return {
        key: {name: _value(cell) for name, cell in row.items() if cell != ""}
        for key, row in _table(store, "ground_truth.csv").items()
    }


def kinds(store: Path = STORE) -> dict[str, dict[str, str]]:
    """How each value is known — `exact`, `numerical`, `asymptotic` or `convention` — by key, for
    every biomarker the geometry settles, including those it settles as having no value."""
    return {
        key: {name: cell for name, cell in row.items() if cell != ""}
        for key, row in _table(store, "ground_truth_kind.csv").items()
    }


def undefined(store: Path = STORE) -> dict[str, list[str]]:
    """By key, the biomarkers the geometry leaves without a value: no piece to pool, no junction to
    take an angle at. An implementation is right to decline these, and wrong to answer them."""
    values = _table(store, "ground_truth.csv")
    return {
        key: sorted(name for name in known if values[key].get(name, "") == "")
        for key, known in kinds(store).items()
    }


def _table(store: Path, name: str) -> dict[str, dict[str, str]]:
    with (Path(store) / name).open() as handle:
        return {
            row["key"]: {k: v for k, v in row.items() if k != "key"}
            for row in csv.DictReader(handle)
        }


def _value(cell: str) -> float | str:
    try:
        return float(cell)
    except ValueError:
        return cell


def load(store: Path = STORE, key: str | None = None) -> Rendering:
    """One stored rendering, read back as the masks an implementation is handed."""
    store = Path(store)
    rows = {row["key"]: row for row in read(store)}
    if key not in rows:
        raise LookupError(f"no rendering named {key!r} in {store}")
    row = rows[key]
    return Rendering(
        key=row["key"],
        family=row["family"],
        side=int(row["side"]),
        rotation=float(row["rotation"]),
        um_per_px=float(row["um_per_px"]),
        artery=_read_mask(store / row["artery"]),
        vein=_read_mask(store / row["vein"]),
        fov=_read_mask(store / row["fov"]),
        disc=(float(row["disc_cx"]), float(row["disc_cy"]), float(row["disc_r"])),
    )


def _read_mask(path: Path) -> np.ndarray:
    """One stored mask, as a plain boolean array.

    **Through `convert("L")`, which is not decoration.** A one-bit PNG opens as a mode ``1`` image,
    and handing that straight to NumPy yields an array whose contents read back correctly — the
    right shape, the right sum, equal to the mask that was written — but whose memory is not what it
    claims. Anything that walks it in C, `skimage.morphology.skeletonize` among them, reads past the
    end of the buffer and the process dies without an exception. Converting to 8-bit first gives a
    real byte per pixel, and the comparison against zero makes the boolean array this returns.
    """
    return np.asarray(Image.open(path).convert("L")) > 0
