# ABOUTME: Images a dataset published that turned out to be unusable, recorded in the repository.
# ABOUTME: Applied when a store is read, never when it is built, so the store stays a faithful copy.

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from datasets.utils import manifest

#: Why an image is excluded. A fixed vocabulary, so findings can be counted across datasets.
REASONS = (
    "ground-truth-wrong",
    "annotation-incomplete",
    "image-corrupt",
    "not-a-fundus",
    "duplicate-within-dataset",
    "mismatched-pair",
    "wrong-modality",
)

#: Where findings live: in the repository, reviewed like code, surviving any rebuild of the store.
DIRECTORY = Path(__file__).resolve().parents[1] / "exclusions"

#: An exclusion covering the whole image rather than named maps.
EVERYTHING = "*"


@dataclass(frozen=True)
class Exclusion:
    """One finding about one image.

    :param maps: :data:`EVERYTHING`, or the maps that are wrong — an image whose artery/vein map is
        broken may still be a perfectly good vessel case.
    """

    key: str
    maps: str | list[str]
    reason: str
    detail: str
    evidence: str
    found: str

    def __post_init__(self) -> None:
        if self.reason not in REASONS:
            raise ValueError(f"{self.reason!r} is not one of {REASONS}")


def load(slug: str, directory: Path = DIRECTORY) -> list[Exclusion]:
    """Read a dataset's findings, or none where nothing has been found."""
    path = directory / f"{slug}.json"
    if not path.exists():
        return []
    record = json.loads(path.read_text())
    return [Exclusion(**entry) for entry in record["exclusions"]]


def usable_rows(
    store: Path,
    findings: Iterable[Exclusion] | None = None,
    slug: str | None = None,
    include_excluded: bool = False,
) -> Iterator[dict[str, str]]:
    """The manifest rows a consumer should trust.

    :param findings: the exclusions to apply; by default those recorded for ``slug``.
    :param include_excluded: return everything unchanged, for re-examining a finding rather than
        relying on it.
    """
    if findings is None:
        findings = load(slug) if slug else []
    by_key = {finding.key: finding for finding in findings}

    for row in manifest.read(store):
        finding = by_key.get(row["key"])
        if finding is None or include_excluded:
            yield row
            continue
        if finding.maps == EVERYTHING:
            continue
        kept = [name for name in row.get("maps", "").split(";") if name not in finding.maps]
        yield {**row, "maps": ";".join(kept)}
