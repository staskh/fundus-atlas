# ABOUTME: The synthetic store: rendering the shapes to files once, and reading them back. Masks,
# ABOUTME: a manifest of how each was framed, and the values its geometry requires.

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from . import library

#: Where a generated store lives unless the caller says otherwise. It is in the repository rather
#: than in one of the git-ignored caches because these are our own shapes: committing them means a
#: measurement can be repeated against the exact pictures it was taken on, without regenerating
#: anything and without trusting that the generator has not changed underneath.
STORE = Path("data/synthetic/av")

#: The angles every family is rendered at. 0 and 90 sit square with the pixel grid and 30 and 60
#: do not, which is the difference that exposes a measurement walking the lattice rather than the
#: vessel.
ROTATIONS = (0.0, 30.0, 60.0, 90.0)

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
    side: int = 2048,
    um_per_px: float = 5.0,
    rotations: tuple[float, ...] | list[float] = ROTATIONS,
    artery_um: float = library.ARTERY_WIDTH_UM,
    vein_um: float = library.VEIN_WIDTH_UM,
) -> list[dict[str, object]]:
    """Render every family at every angle, and write the masks, the manifest and the ground truth.

    Generating once and measuring many times is the point of a store: a rendering costs seconds of
    rasterising that no benchmark then has to repeat, and — more importantly — every run afterwards
    measures the same pictures rather than pictures a later change to the generator would alter.
    """
    into = Path(into)
    into.mkdir(parents=True, exist_ok=True)
    chosen = list(families) if families else list(library.SHAPES)
    rows: list[dict[str, object]] = []
    truths: list[dict[str, object]] = []
    for family in chosen:
        for rotation in rotations:
            shape = library.build(
                family,
                side=side,
                rotation=float(rotation),
                um_per_px=um_per_px,
                artery_um=artery_um,
                vein_um=vein_um,
            )
            rows.append(_render(into, shape, family, rotation))
            truths.append({"key": rows[-1]["key"], **shape.theory})
    _write_rows(into / "manifest.csv", COLUMNS, rows)
    _write_rows(into / "ground_truth.csv", _truth_columns(truths), truths)
    return rows


def _render(into: Path, shape: library.Shape, family: str, rotation: float) -> dict[str, object]:
    """One rendering's three masks, and the manifest row that says how it was framed."""
    key = key_of(family, shape.side, rotation)
    names = {}
    for which, mask in (("artery", shape.artery), ("vein", shape.vein), ("fov", shape.fov)):
        names[which] = f"{key}-{which}.png"
        _save(into / names[which], mask)
    x, y, radius = shape.disc
    return {
        "key": key,
        "family": family,
        "side": shape.side,
        "rotation": f"{rotation:.1f}",
        "um_per_px": shape.um_per_px,
        "disc_cx": f"{x:.4f}",
        "disc_cy": f"{y:.4f}",
        "disc_r": f"{radius:.4f}",
        "disc_diameter_um": library.DISC_DIAMETER_UM,
        "artery_width_um": shape.parameters.get("artery_width", 0.0) * shape.um_per_px,
        "vein_width_um": shape.parameters.get("vein_width", 0.0) * shape.um_per_px,
        "fov_cx": f"{shape.side / 2.0:.4f}",
        "fov_cy": f"{shape.side / 2.0:.4f}",
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


def read(store: Path = STORE) -> list[dict[str, str]]:
    """The manifest, as it was written."""
    with (Path(store) / "manifest.csv").open() as handle:
        return list(csv.DictReader(handle))


def truth(store: Path = STORE) -> dict[str, dict[str, float]]:
    """What each rendering's geometry requires, by key, with the empty cells left out."""
    with (Path(store) / "ground_truth.csv").open() as handle:
        return {
            row["key"]: {
                name: float(value) for name, value in row.items() if name != "key" and value != ""
            }
            for row in csv.DictReader(handle)
        }


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
    return np.asarray(Image.open(path)).astype(bool)
