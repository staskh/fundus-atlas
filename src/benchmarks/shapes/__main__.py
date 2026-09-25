# ABOUTME: The command that draws the synthetic store: `python -m benchmarks.shapes`. It renders
# ABOUTME: the shapes to files once, so that measuring them many times costs no rasterising.

import argparse
from argparse import Namespace
from pathlib import Path

from . import library, store


def parse(argv: list[str] | None = None) -> Namespace:
    """Read the command line."""
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks.shapes",
        description=(
            "Draw the synthetic artery/vein shapes to a store: one binary mask per class, a field "
            "of view, a manifest saying how each was framed, and the values their geometry "
            "requires."
        ),
    )
    parser.add_argument("--into", default=str(store.STORE), help="where to write the store")
    parser.add_argument(
        "--family",
        help="one family, or several separated by commas; all of them by default",
    )
    parser.add_argument("--side", type=int, default=2048, help="the square grid, in pixels")
    parser.add_argument(
        "--um-per-px", type=float, default=5.0, help="microns per pixel the shapes are drawn at"
    )
    parser.add_argument(
        "--rotations",
        default=",".join(f"{angle:g}" for angle in store.ROTATIONS),
        help="the angles each family is drawn at, in degrees, separated by commas",
    )
    parser.add_argument(
        "--artery-um",
        type=float,
        default=library.ARTERY_WIDTH_UM,
        help="how wide an artery is, in microns",
    )
    parser.add_argument(
        "--vein-um",
        type=float,
        default=library.VEIN_WIDTH_UM,
        help="how wide a vein is, in microns",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    asked = parse(argv)
    families = (
        [name.strip() for name in asked.family.split(",") if name.strip()] if asked.family else None
    )
    rotations = [float(angle) for angle in asked.rotations.split(",") if angle.strip()]
    written = store.write(
        Path(asked.into),
        families=families,
        side=asked.side,
        um_per_px=asked.um_per_px,
        rotations=rotations,
        artery_um=asked.artery_um,
        vein_um=asked.vein_um,
    )
    drawn = sorted({str(row["family"]) for row in written})
    print(
        f"{len(written)} renderings of {len(drawn)} families at {asked.side}px, "
        f"{asked.um_per_px:g} µm/px, into {asked.into}"
    )
    for family in drawn:
        print(f"  {family}")


if __name__ == "__main__":
    main()
