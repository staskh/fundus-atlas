# ABOUTME: QuickQual: a classifier published as a release asset and an inference recipe published
# ABOUTME: as five lines of README, cloned at a pinned commit so both can be read against our own.

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
