# ABOUTME: Native resolution in microns per pixel, its provenance, and the value at any built size.
# ABOUTME: Never guessed: a dataset that publishes none keeps none, and consumers report pixels.

from dataclasses import dataclass

#: How a resolution was arrived at, in the skill's order of preference.
SOURCES = ("published", "field_angle", "disc_anchored", "inherited", "unknown")

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
