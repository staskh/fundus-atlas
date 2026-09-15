# ABOUTME: The photographs of a quality benchmark, with the grade the dataset itself published and
# ABOUTME: every reader's own grade where the dataset keeps its readers apart.

import csv
from pathlib import Path

from .base import Photographs

#: The field in ``labels.csv`` that holds a reader's quality verdict.
FIELD = "quality"

#: Why a photograph is excluded from a quality benchmark though the dataset published it.
NO_REFERENCE = "no reference to score against"


class QualityLoader(Photographs):
    """One dataset's photographs and the grade each was given.

    A photograph the dataset never graded is excluded with its own reason: there is nothing to
    score against, which is not a failure of the model and is never counted as one.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.readers = _readers(self.store)

    def _with_reference(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        graded = [row for row in rows if row[FIELD]]
        self._exclude(NO_REFERENCE, len(rows) - len(graded))
        return graded

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        sample = super().__getitem__(index)
        sample["grade"] = row[FIELD]
        sample["readers"] = self.readers.get(row["key"], {})
        return sample


def _readers(store: Path) -> dict[str, dict[str, str]]:
    """Every reader's quality verdict, by photograph, where the dataset published them."""
    labels = store / "labels.csv"
    if not labels.exists():
        return {}
    found: dict[str, dict[str, str]] = {}
    with open(labels, newline="") as f:
        for entry in csv.DictReader(f):
            if entry["field"] == FIELD:
                found.setdefault(entry["key"], {})[entry["reader"]] = entry["value"]
    return found
