# ABOUTME: Writes and reads manifest.csv and labels.csv: the fixed schema, a dataset's own tail
# ABOUTME: columns, and the rule that picks one value for a cell when several readers spoke.

import csv
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

#: Every manifest has these columns, with these names, in this order. A consumer can then read any
#: store without special-casing one dataset.
CORE_COLUMNS = (
    "key",
    "subset",
    "split",
    "native_width",
    "native_height",
    "fov_cx",
    "fov_cy",
    "fov_r",
    "fov_source",
    "crop_x0",
    "crop_y0",
    "crop_side",
    "pad_fraction",
    "um_per_px",
    "resolution_source",
    "maps",
    "readers",
    "multi_reader",
    "patient",
    "visit",
    "eye",
    "disease",
    "quality",
    "quality_source",
    "source_image",
    "sha256",
    "notes",
)

#: The reader id a dataset uses for a value it publishes as agreed.
CONSENSUS = "consensus"

MANIFEST = "manifest.csv"
LABELS = "labels.csv"


@dataclass(frozen=True)
class Column:
    """A column only this dataset has, appended after the fixed ones.

    :param name: lowercase, and not a second spelling of something the schema already holds.
    :param description: one line, repeated in the dataset page's "How to fetch".
    """

    name: str
    description: str

    def __post_init__(self) -> None:
        if self.name in CORE_COLUMNS:
            raise ValueError(f"{self.name!r} is already a fixed column")
        if not self.name.replace("_", "").isalnum() or self.name != self.name.lower():
            raise ValueError(f"{self.name!r} should be lowercase letters, digits and underscores")


@dataclass(frozen=True)
class Reading:
    """One reader's opinion about one field of one image."""

    key: str
    field: str
    reader: str
    value: str


def spell_out(code: str, legend: dict[str, str], field: str) -> str:
    """The dataset's own words for one of its own codes.

    A bare integer in a manifest is not self-describing: nobody reading `disease` as `3` knows
    whether that is worse than `1`, and `0` is one typo away from being read as "no value". Where
    the dataset publishes a legend, the legend's wording is what the cell holds. This is not a
    remapping to a common vocabulary — the words stay the dataset's own — it is the difference
    between storing a label and storing a footnote marker.

    :param code: the published code, or empty where the dataset graded nothing.
    :param legend: the dataset's own code-to-meaning table, as its documentation gives it.
    :param field: the column, named so an unexplained code says where it came from.
    :raises ValueError: for a code the legend does not explain, rather than passing it through. A
        dataset that has grown a new grade since the fetcher was written must be looked at.
    """
    if code == "":
        return ""
    if code not in legend:
        raise ValueError(f"{field} is {code!r}, which the dataset's own legend does not explain")
    return legend[code]


def write(
    store: Path,
    rows: Iterable[dict[str, str]],
    extra_columns: list[Column],
    readings: Iterable[Reading] = (),
) -> None:
    """Write ``manifest.csv``, and ``labels.csv`` where a field has more than one reader.

    The cells a reading decides are filled here rather than by the fetcher, so the manifest and
    `labels.csv` cannot come to disagree: one set of readings, two renderings of it.

    :param store: the dataset's directory in the store.
    :param rows: one per image, holding the fixed columns it knows and any declared tail column.
    :param extra_columns: this dataset's own columns, in the order they should appear.
    :param readings: every reader's value, where the dataset names its readers.
    """
    columns = list(CORE_COLUMNS) + [column.name for column in extra_columns]
    rows = [dict(row) for row in rows]
    by_key = _readings_by_key(readings)

    for row in rows:
        unknown = sorted(set(row) - set(columns))
        if unknown:
            raise ValueError(f"{unknown} are not declared columns; add them to EXTRA_COLUMNS")
        _apply_readings(row, by_key.get(row["key"], {}))

    store.mkdir(parents=True, exist_ok=True)
    with open(store / MANIFEST, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, restval="")
        writer.writeheader()
        writer.writerows(rows)

    readings = sorted(readings, key=lambda r: (r.key, r.field, r.reader))
    if readings:
        with open(store / LABELS, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["key", "field", "reader", "value"])
            writer.writeheader()
            writer.writerows(vars(reading) for reading in readings)


def read(store: Path) -> Iterator[dict[str, str]]:
    """Every row of a store's manifest, including any exclusions.

    Callers wanting a usable dataset want :func:`datasets.utils.exclusions.usable_rows`, which
    applies the findings recorded in the repository.
    """
    with open(store / MANIFEST, newline="") as f:
        yield from csv.DictReader(f)


def _readings_by_key(readings: Iterable[Reading]) -> dict[str, dict[str, list[Reading]]]:
    grouped: dict[str, dict[str, list[Reading]]] = defaultdict(lambda: defaultdict(list))
    for reading in readings:
        grouped[reading.key][reading.field].append(reading)
    return grouped


def _apply_readings(row: dict[str, str], fields: dict[str, list[Reading]]) -> None:
    """Fill the cells the readings decide, and say which fields had more than one opinion."""
    multi, readers = [], set()
    for field, entries in sorted(fields.items()):
        if row.get(field):
            raise ValueError(f"{field!r} is set on row {row['key']!r} and also has readings")
        graders = [entry for entry in entries if entry.reader != CONSENSUS]
        readers.update(entry.reader for entry in graders)
        if len(entries) > 1:
            multi.append(field)
        row[field] = _agreed(entries)
    if multi:
        row["multi_reader"] = ";".join(multi)
    if readers and not row.get("readers"):
        row["readers"] = ";".join(sorted(readers))


def _agreed(entries: list[Reading]) -> str:
    """The one value a cell may hold: the consensus, or unanimity, or nothing.

    Never a majority vote. Which grader to believe is the consumer's research decision, and a
    manufactured verdict would hide the disagreement the dataset went to the trouble of recording.
    """
    for entry in entries:
        if entry.reader == CONSENSUS:
            return entry.value
    values = {entry.value for entry in entries}
    return values.pop() if len(values) == 1 else ""
