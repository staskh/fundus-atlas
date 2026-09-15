# ABOUTME: QuickQual: a classifier published as a release asset and an inference recipe published
# ABOUTME: as five lines of README, cloned at a pinned commit so both can be read against our own.

import re
from dataclasses import dataclass
from pathlib import Path

from .utils import paths, source, weights

CODE = source.Checkout(
    "quickqual",
    "https://github.com/justinengelmann/QuickQual",
    "a94feb02a79efa5380f6b0d863d1b80ab4c73e4e",
)

#: The fitted support vector machine, from release 1.0. Nothing in the repository loads it for us:
#: the published inference is a README example, which the model adapter follows.
CLASSIFIER = (
    "https://github.com/justinengelmann/QuickQual/releases/download/1.0/quickqual_dn121_512.pkl"
)

#: What that file is, pinned. Loading a joblib pickle runs the code inside it, so the digest is
#: checked before anything opens it, and a file that does not match is deleted rather than loaded.
CLASSIFIER_SHA256 = "7ed87654ba6b6003d35aa06b8318c5ad4b713409f50187872151414380f3bcca"

#: The feature extractor, used frozen and off the shelf. Nothing about it is QuickQual's.
BACKBONE = "densenet121.tv_in1k"


@dataclass(frozen=True)
class Meme:
    """The MEga Minified Estimator: nine of the backbone's features and ten numbers over them.

    :param features: which of the backbone's outputs it reads, by index.
    :param weights: one weight per feature.
    :param bias: the intercept; the sum through a sigmoid is the probability of `bad`.
    """

    features: tuple[int, ...]
    weights: tuple[float, ...]
    bias: float


def meme(readme: Path | None = None) -> Meme:
    """The MEME variant's parameters, read out of the pinned repository's own README.

    They are read rather than copied here for two reasons: the repository states no licence, and a
    number transcribed by hand is a number that can be transcribed wrongly. Reading them at the
    pinned commit means what runs is what that commit publishes.

    :raises LookupError: if the README does not carry them, rather than falling back on a guess.
    """
    path = readme or (CODE.obtain() / "README.md")
    text = path.read_text()
    found = {
        name: re.search(pattern, text, re.DOTALL)
        for name, pattern in (
            ("features", r"feats\[:,\s*\[(.*?)\]\]"),
            ("weights", r"w\s*=\s*torch\.tensor\(\[(.*?)\]\)"),
            ("bias", r"b\s*=\s*torch\.tensor\(\[(.*?)\]\)"),
        )
    }
    missing = sorted(name for name, match in found.items() if match is None)
    if missing:
        raise LookupError(
            f"{path} does not publish the MEME variant's {', '.join(missing)}; this README is not "
            f"the one the pinned commit carries"
        )
    return Meme(
        features=tuple(int(part) for part in found["features"].group(1).split(",")),
        weights=tuple(float(part) for part in found["weights"].group(1).split(",")),
        bias=float(found["bias"].group(1)),
    )


def classifier() -> Path:
    """The fitted classifier, fetched once and checked against the digest above."""
    CODE.obtain()
    return weights.fetch(
        CLASSIFIER,
        paths.weights("quickqual") / "quickqual_dn121_512.pkl",
        CLASSIFIER_SHA256,
    )


def provenance() -> dict[str, object]:
    return CODE.provenance()
