# ABOUTME: fundus-biomarkers' measuring code, reached from this repository: it answers under the
# ABOUTME: catalogue's own names, so its table maps each name to itself or to its own spelling.

import numpy as np

from biomarkers import canonical
from upstreams import fundus_biomarkers as upstream


class FundusBiomarkers:
    """Pheno's reference implementation, catalogued and measured like any other project.

    **It reports in microns and is converted here, towards pixels**, exactly as the VascX adapter
    converts its millimetres: every adapter hands the analysis pixel values and
    `canonical.from_pixels` is the one conversion back, so this one divides by `um_per_px` raised
    to each name's length power. The library refuses to guess a scale, so with `um_per_px=None`
    every value is `None`.

    **It is written against this catalogue**, so its names *are* catalogued names. Any name the
    vocabulary does not accept is answered under the library's own spelling, the slashes replaced
    by dots, so it is stored and measured but claims nothing.

    **One answer is a category, not a number**: the photograph's centring — disc, macula or
    unknown. It is answered as the library says it, with no conversion, and only if the
    vocabulary's record lists it.
    """

    slug = "fundus-biomarkers"
    needs = ("artery", "vein", "disc")
    invariant = ("rotation",)

    def __init__(self, device: str | None = None) -> None:
        self.device = "cpu"
        self.trouble: dict[str, str] = {}
        self._library = None

    def declare(self) -> dict[str, object]:
        names = self._names()
        return {
            "slug": self.slug,
            "needs": list(self.needs),
            "invariant": list(self.invariant),
            # The columns its evidence carries, which are the answered names: fingerprinted, so a
            # name the vocabulary comes to accept reads as a different result rather than as an
            # old column under a new heading.
            "keys": list(names.values()),
            # Each answered name is its own catalogued name, or claims none when it carries no
            # slash.
            "names": {
                answered: answered if "/" in answered else None for answered in names.values()
            },
            "unnamed": [answered for answered in names.values() if "/" not in answered],
            "units": "pixels to the length power of each catalogued name",
            "device": self.device,
            "upstream": upstream.provenance(),
        }

    def identity(self) -> str:
        return str(upstream.COMMIT)

    def keys(self) -> tuple[str, ...]:
        return tuple(self._names().values())

    def measure(
        self,
        artery: np.ndarray | None,
        vein: np.ndarray | None,
        fov: np.ndarray,
        disc: tuple[float, float, float],
        um_per_px: float | None,
    ) -> dict[str, float | str | None]:
        """Everything the library computes, under catalogued names, in pixels."""
        self.trouble = {}
        names = self._names()
        answers: dict[str, float | str | None] = dict.fromkeys(names.values())
        if um_per_px is None:
            return answers
        retina, circle = self._loaded()
        blank = np.zeros(fov.shape, dtype=bool)
        try:
            found = retina(
                artery=blank if artery is None else np.asarray(artery, dtype=bool),
                vein=blank if vein is None else np.asarray(vein, dtype=bool),
                fov=np.asarray(fov, dtype=bool),
                um_per_px=float(um_per_px),
                disc=circle(cx=float(disc[0]), cy=float(disc[1]), r=float(disc[2])),
            ).biomarkers
        except Exception as failure:  # one failure must not lose the row; its reason is kept
            self.trouble["measure"] = repr(failure)
            return answers
        missing = {"artery"} if artery is None else set()
        missing |= {"vein"} if vein is None else set()
        for own, answered in names.items():
            value = found.get(own)
            structure = own.split("/")[2] if own.count("/") >= 2 else ""
            if value is None or structure in missing or (structure == "both" and missing):
                continue
            if isinstance(value, str):
                if value in _categories(answered):
                    answers[answered] = value
                else:
                    self.trouble[answered] = f"answered {value!r}, which its record does not list"
                continue
            answers[answered] = float(value) / um_per_px ** _length_power(answered)
        return answers

    def _names(self) -> dict[str, str]:
        """The library's name → the name answered under: itself where catalogued, else its own
        spelling with dots, which carries no slash and so claims no catalogued biomarker.

        The library answers its full set of names whatever the photograph, None where a value
        cannot be had, so an empty retina lists them all."""
        retina, circle = self._loaded()
        blank = np.zeros((64, 64), dtype=bool)
        empty = retina(artery=blank, vein=blank, fov=~blank, um_per_px=10.0, disc=circle(32, 32, 4))
        return {
            own: own if canonical.known(own) and _checks(own) else own.replace("/", ".")
            for own in sorted(empty.biomarkers)
        }

    def _loaded(self):
        if self._library is None:
            self._library = upstream.library()
        return self._library

    def release(self) -> None:
        self._library = None


def _checks(name: str) -> bool:
    try:
        canonical.check(name)
    except LookupError:
        return False
    return True


def _categories(answered: str) -> tuple[str, ...]:
    """The categories a catalogued name may answer with; none for a name the catalogue lacks."""
    return canonical.values(answered) if "/" in answered else ()


def _length_power(answered: str) -> int:
    """The length power of a catalogued name; a name the catalogue lacks is reported unconverted."""
    return canonical.length_power(answered) if "/" in answered else 0


def implementation(**arguments: object) -> FundusBiomarkers:
    return FundusBiomarkers(**arguments)
