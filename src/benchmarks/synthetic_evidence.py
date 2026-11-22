# ABOUTME: Reading the synthetic biomarker benchmark's evidence for its notebooks: what each program
# ABOUTME: said, what the geometry and each program's own description require, and how far apart.

"""What every synthetic-benchmark notebook reads, said once.

The analysis is split into a notebook per lineage and one across them, and four notebooks that each
defined their own error would disagree about it within a month. So the joins, the noise floor and
the two comparisons live here, and a notebook calls them and argues about what they show.

Nothing here measures anything or writes anything. It reads three inputs and joins them:

| Input | Where | What it gives |
| --- | --- | --- |
| Evidence | `results/biomarker-synthetic/<implementation>/<shape>.csv` | what each program said, under its own names |
| The mapping | each adapter's `declare()["names"]` | which catalogued biomarker each column is believed to be |
| Ground truth | the store's `ground_truth.csv`, and `ground_truth_claimed.csv` beside it | what the geometry requires, by canonical name and by each program's own description |
"""

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks import biomarker_synthetic as benchmark
from benchmarks.shapes import claims, store
from benchmarks.shapes.truth import TURN_WITH_THE_IMAGE
from biomarkers import canonical
from biomarkers.utils import catalogue

#: A spread across angles wider than this, as a fraction of the quantity's own size, is a finding.
ROTATION_TOLERANCE = 0.10
#: A value further than this from the geometry, as a fraction of the truth, is a fault.
GROUND_TRUTH_TOLERANCE = 0.25
#: The noise floor, as a fraction of a biomarker's own size: a difference smaller than this is
#: agreement, and no percentage is taken against a denominator smaller than this. Why it is 1%, and
#: what that costs, is argued in the summary notebook's first cell.
NOISE = 0.01

#: Colours for the implementations within one group, in its lineage order: the first three slots
#: of the categorical palette, so a group's ancestor is always blue.
COLOURS = ("#2a78d6", "#eb6834", "#1baf7a")
#: One per group, for the summary, in the same order.
GROUP_COLOURS = {"automorph": "#2a78d6", "pvbm": "#eb6834", "vascx": "#1baf7a"}
#: A single-hue ramp, light to dark, for a heat map of error.
RAMP = ("#f0efec", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b")


def repository() -> Path:
    """The repository, found by walking up rather than assumed from where a notebook was opened."""
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").is_dir():
            return candidate
    raise RuntimeError(f"nothing above {Path.cwd()} looks like the fundus-atlas repository")


# the arithmetic --------------------------------------------------------------------------------


def floor(size: float) -> float:
    """The smallest difference worth reporting for a biomarker of this size."""
    return NOISE * size if size and np.isfinite(size) else NOISE


def spread(values: pd.Series, size: float) -> float:
    """How far a quantity moved when the same shape was turned, relative to its own size.

    The floor twice over: a movement under it is agreement, and the denominator never falls below
    it either, so a quantity hovering around nought cannot report a large percentage for having
    moved an amount nobody could measure.
    """
    values = values.dropna()
    if len(values) < 2:
        return np.nan
    width = values.max() - values.min()
    smallest = floor(size)
    if width < smallest:
        return 0.0
    return width / max(abs(values.mean()), smallest)


def error(value: float, truth: float, size: float) -> float:
    """How far one measurement is from what is required of it, as a fraction of the truth.

    A disagreement smaller than the floor is not one, and a percentage is never taken against a
    truth smaller than the floor, which is what would produce an infinity wherever the geometry
    requires exactly nought.
    """
    gap = abs(value - truth)
    smallest = floor(size)
    if gap < smallest:
        return 0.0
    return gap / max(abs(truth), smallest)


def signed(value: float, truth: float, size: float) -> float:
    """The same, keeping its direction: positive where the program said more than the geometry."""
    gap = value - truth
    smallest = floor(size)
    if abs(gap) < smallest:
        return 0.0
    return gap / max(abs(truth), smallest)


# each lineage's own names ----------------------------------------------------------------------

#: OCULAR's columns under the names PVBM gives the same ones. OCULAR runs PVBM's geometry, so its
#: columns are PVBM's; the one it renames is the tortuosity index. Its length-weighted tortuosity
#: has no PVBM counterpart and keeps its own name.
_OCULAR = {"pooled_tortuosity": "tortuosity_index"}

#: AutoMorphalyzer's whole-picture quantities, under the names AutoMorph gives the same ones. Both
#: rewrote AutoMorph's measuring stage, so most of their columns are AutoMorph's under new names.
_AUTOMORPHALYZER = {
    "fractal_dimension": "fractal_dimension",
    "vessel_density": "vessel_density",
    "average_global_calibre": "average_width",
    "tortuosity_distance": "distance_tortuosity",
    "tortuosity_density": "tortuosity_density",
}

#: The disc and cup columns, which the three spell three ways.
_DISC = {
    "disc_height": "Disc_height",
    "disc_width": "Disc_width",
    "cup_height": "Cup_height",
    "cup_width": "Cup_width",
    "cdr_vertical": "CDR_vertical",
    "cdr_horizontal": "CDR_horizontal",
    "CDR_vertical": "CDR_vertical",
    "CDR_horizontal": "CDR_horizontal",
}


def native(slug: str, own: str) -> str:
    """A column under the name its lineage's root gives the same quantity, so a lineage's members
    stand on one row as that project's users know them: AutoMorph's names for AutoMorphalyzer and
    AutoMorphClass, PVBM's for OCULAR, and VascX's own for VascX.

    A column is matched only where it measures the same quantity over the same map and the same
    region; a different **statistic** still matches (AutoMorphClass length-weights where AutoMorph
    takes a mean), because the row's canonical names say so beside it. Where there is no
    counterpart the column keeps its own name, followed by its implementation's, so it can never be
    mistaken for AutoMorph's column of the same spelling: AutoMorphClass's `…_zone_c` is **3 to 5**
    disc radii and AutoMorph's 2 to 5, so those never share a row. A root's column is its own name.
    """
    if slug in ("automorph", "pvbm", "vascx"):
        return own
    if slug == "ocular":
        found = re.fullmatch(r"(?P<column>.+)_(?P<map>artery|vein)", own)
        if found and found["column"] != "length_weighted_tortuosity":
            return f"{_OCULAR.get(found['column'], found['column'])}_{found['map']}"
        return f"{own} ({slug})"
    if slug == "automorphclass":
        if own in _DISC:
            return _DISC[own]
        found = re.fullmatch(r"(?P<column>.+)_(?P<map>vessels|artery|vein)(?P<zone>_zone_b)?", own)
        if found:
            mapped = "binary" if found["map"] == "vessels" else found["map"]
            return f"{found['column']}_{mapped}{found['zone'] or ''}"
        return f"{own} ({slug})"
    if slug == "automorphalyzer":
        if own in _DISC:
            return _DISC[own]
        if own in ("AVR_B", "AVR_C"):
            return f"AVR_Knudtson_zone_{own[-1].lower()}"
        found = re.fullmatch(
            r"(?P<column>\w+)@(?P<zone>whole|B|C)_(?P<map>binary|artery|vein)", own
        )
        if found:
            zone = "" if found["zone"] == "whole" else f"_zone_{found['zone'].lower()}"
            if found["column"] in _AUTOMORPHALYZER:
                return f"{_AUTOMORPHALYZER[found['column']]}_{found['map']}{zone}"
            # AutoMorph keeps each equivalent only from its own class's map, inside a zone.
            pairs = {"CRAE_Knudtson": "artery", "CRVE_Knudtson": "vein"}
            if zone and pairs.get(found["column"]) == found["map"]:
                return f"{found['column']}{zone}"
        return f"{own} ({slug})"
    return own


def comments(evidence: "Evidence") -> pd.Series:
    """For each row of a lineage's own names, the canonical name each member's column answers to —
    one name where all agree, each member's where they differ, `—` where none has one."""
    said = evidence.said.drop_duplicates(["implementation", "native"])
    written = {}
    for row, group in said.groupby("native"):
        named = {
            slug: name
            for slug, name in zip(group["implementation"], group["canonical"], strict=True)
            if isinstance(name, str)
        }
        if not named:
            written[row] = "—"
        elif len(set(named.values())) == 1 and len(named) == len(group):
            written[row] = next(iter(named.values()))
        else:
            written[row] = "; ".join(f"{slug}: {name}" for slug, name in named.items())
    return pd.Series(written, name="canonical")


# reading ---------------------------------------------------------------------------------------


@dataclass
class Evidence:
    """Everything a notebook reads, for the implementations it was asked about.

    :param said: one row per (implementation, rendering, own column), the number converted to the
        catalogue's units where the column claims a canonical name.
    :param categories: the answers that are words rather than numbers.
    :param truth: what the geometry requires, by canonical name, where it is a number.
    :param words: what it requires where the answer is a word.
    :param none: what it settles as having no value.
    :param claimed: what each program's own description requires of each unnamed column.
    """

    implementations: list[str]
    measured: dict[str, pd.DataFrame]
    names: dict[str, dict[str, str | None]]
    said: pd.DataFrame
    categories: pd.DataFrame
    truth: pd.DataFrame
    words: pd.DataFrame
    none: pd.DataFrame
    claimed: pd.DataFrame
    scales: pd.Series
    turning: set[tuple[str, str]]

    @property
    def shapes(self) -> list[str]:
        return sorted(self.said["shape"].unique())

    def in_order(self, table: pd.DataFrame) -> pd.DataFrame:
        """Columns in lineage order, which is never re-sorted."""
        return table.reindex(columns=[c for c in self.implementations if c in table.columns])


def read(implementations: list[str] | tuple[str, ...], root: Path | None = None) -> Evidence:
    """Read the evidence for these implementations, and the truths it is judged against."""
    root = root or repository()
    results = root / "results" / benchmark.NAME
    where = root / store.STORE
    missing = [slug for slug in implementations if not any((results / slug).glob("*.csv"))]
    if missing:
        raise FileNotFoundError(
            f"no evidence for {', '.join(missing)} in {results}: run "
            f"`python -m benchmarks --benchmark {benchmark.NAME} --model {','.join(missing)}`"
        )
    measured = {slug: _measured(results, slug) for slug in implementations}
    names = {slug: catalogue.load(slug).declare()["names"] for slug in implementations}
    scales = pd.DataFrame(store.read(where)).set_index("key")["um_per_px"].astype(float)

    longs = {slug: _answers(measured[slug]) for slug in implementations}
    said = pd.concat(
        [_tidy(longs[slug], names[slug], scales) for slug in implementations], ignore_index=True
    )
    categories = pd.concat(
        [long[_worded(long)] for long in longs.values()], ignore_index=True
    ).drop(columns=["said"])

    kind = pd.DataFrame(
        [
            {"key": key, "canonical": name, "kind": known}
            for key, values in store.kinds(where).items()
            for name, known in values.items()
        ]
    )
    values = pd.DataFrame(
        [
            {"key": key, "canonical": name, "truth": value}
            for key, row in store.truth(where).items()
            for name, value in row.items()
        ]
    )
    truth = (
        values[values["truth"].map(lambda value: not isinstance(value, str))]
        .astype({"truth": float})
        .merge(kind, on=["key", "canonical"], how="left")
    )
    words = values[values["truth"].map(lambda value: isinstance(value, str))]
    none = pd.DataFrame(
        [
            {"key": key, "canonical": name}
            for key, names_ in store.undefined(where).items()
            for name in names_
        ]
    )

    size = truth.assign(size=truth["truth"].abs()).groupby("canonical")["size"].max()
    own_size = (
        said.assign(size=said["value"].abs()).groupby(["implementation", "own"])["size"].max()
    )
    said["size"] = said["canonical"].map(size)
    said["size"] = said["size"].fillna(
        pd.Series(
            pd.MultiIndex.from_arrays([said["implementation"], said["own"]]).map(own_size),
            index=said.index,
        )
    )
    return Evidence(
        implementations=list(implementations),
        measured=measured,
        names=names,
        said=said,
        categories=categories,
        truth=truth,
        words=words,
        none=none,
        claimed=_claimed(where, said, implementations),
        scales=scales,
        turning=claims.turning(where),
    )


def _measured(results: Path, slug: str) -> pd.DataFrame:
    frames = [pd.read_csv(path) for path in sorted((results / slug).glob("*.csv"))]
    frame = pd.concat(frames, ignore_index=True)
    frame.insert(0, "implementation", slug)
    return frame


def _answers(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [column for column in frame.columns if column.startswith("said_")]
    long = frame.melt(
        id_vars=["implementation", "key", "shape", "rotation", "outcome", "seconds"],
        value_vars=columns,
        var_name="said",
        value_name="returned",
    )
    long["own"] = long["said"].str[len("said_") :]
    return long


def _worded(long: pd.DataFrame) -> pd.Series:
    """Which answers are a word rather than a number; a word has no size."""
    return long["returned"].notna() & pd.to_numeric(long["returned"], errors="coerce").isna()


def _tidy(long: pd.DataFrame, names: dict, scales: pd.Series) -> pd.DataFrame:
    """One row per (rendering, quantity), with the canonical name beside it, and pixels made
    microns by `canonical.from_pixels`, the rule the ground truth was built with."""
    long = long[~_worded(long)].astype({"returned": float})
    long["canonical"] = long["own"].map(names)
    long["native"] = [
        native(slug, own) for slug, own in zip(long["implementation"], long["own"], strict=True)
    ]
    long["um_per_px"] = long["key"].map(scales)
    long["value"] = [
        canonical.from_pixels(name, number, scale)
        if isinstance(name, str) and pd.notna(number)
        else number
        for name, number, scale in zip(
            long["canonical"], long["returned"], long["um_per_px"], strict=True
        )
    ]
    return long.drop(columns=["said"])


def _claimed(where: Path, said: pd.DataFrame, implementations) -> pd.DataFrame:
    """Each unnamed column against what its own description requires, one row per rendering."""
    values, kinds = claims.read(where)
    rows = []
    for claim in claims.CLAIMS:
        if claim.slug not in implementations:
            continue
        for key, known in kinds.items():
            if claim.label not in known:
                continue
            rows.append(
                {
                    "implementation": claim.slug,
                    "own": claim.column,
                    "key": key,
                    "claimed": values[key].get(claim.label),
                    "kind": known[claim.label],
                    "claims": claim.claims,
                    "as": claim.canonical or "derived from the geometry",
                    "power": claim.power,
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "implementation",
                "own",
                "native",
                "key",
                "claimed",
                "kind",
                "claims",
                "as",
                "power",
            ]
        )
    table = pd.DataFrame(rows)
    joined = table.merge(
        said[
            ["implementation", "own", "native", "key", "shape", "rotation", "returned", "um_per_px"]
        ],
        on=["implementation", "own", "key"],
        how="left",
    )
    joined["value"] = joined["returned"] * joined["um_per_px"] ** joined["power"]
    sizes = joined.assign(size=joined["claimed"].abs()).groupby(["implementation", "own"])["size"]
    joined["size"] = sizes.transform("max")
    return joined


# the two comparisons ---------------------------------------------------------------------------


def rotation(evidence: Evidence, named: bool = True, by: str | None = None) -> pd.Series:
    """The worst spread across angles each quantity showed on any shape, by (implementation, name).

    Named quantities are indexed by canonical name, unnamed ones by their own, unless `by` names
    another key — `native`, AutoMorph's own name, for its lineage. What turning the
    photograph is *meant* to move is left out: the cup-to-disc ratios read along the image's axes,
    and the unnamed columns whose own claimed value changes with the angle (`claims.turning`).
    """
    said = evidence.said[evidence.said["value"].notna()]
    if named:
        said = said[said["canonical"].notna() & ~said["canonical"].isin(TURN_WITH_THE_IMAGE)]
        index = by or "canonical"
    else:
        said = said[said["canonical"].isna()]
        moves = [
            (slug, own) in evidence.turning
            for slug, own in zip(said["implementation"], said["own"], strict=True)
        ]
        said = said[~np.array(moves, dtype=bool)]
        index = by or "own"
    if said.empty:
        return pd.Series(dtype=float)
    by_shape = said.groupby(["implementation", index, "shape"], group_keys=True).apply(
        lambda group: spread(group["value"], group["size"].iloc[0]), include_groups=False
    )
    return by_shape.groupby(["implementation", index]).max()


def rotation_by_shape(evidence: Evidence, by: str = "canonical") -> pd.DataFrame:
    """Spread across angles per (implementation, name, shape), for a heat map.

    By canonical name, only the named columns; by `native` or `own`, every column, unnamed ones
    included. Either way, what turning the photograph is meant to move is left out.
    """
    said = evidence.said[evidence.said["value"].notna()]
    said = said[~said["canonical"].isin(TURN_WITH_THE_IMAGE)]
    if by == "canonical":
        said = said[said["canonical"].notna()]
    else:
        turns = [
            (slug, own) in evidence.turning
            for slug, own in zip(said["implementation"], said["own"], strict=True)
        ]
        said = said[~np.array(turns, dtype=bool)]
    return (
        said.groupby(["implementation", by, "shape"], group_keys=True)
        .apply(lambda group: spread(group["value"], group["size"].iloc[0]), include_groups=False)
        .rename("spread")
        .reset_index()
    )


def agreement(evidence: Evidence) -> pd.DataFrame:
    """Every named measurement beside the value the geometry requires, with its error."""
    named = evidence.said[evidence.said["canonical"].notna()]
    against = named.merge(evidence.truth, on=["key", "canonical"], how="inner").dropna(
        subset=["value"]
    )
    against["error"] = [
        error(v, t, s)
        for v, t, s in zip(against["value"], against["truth"], against["size"], strict=True)
    ]
    against["signed"] = [
        signed(v, t, s)
        for v, t, s in zip(against["value"], against["truth"], against["size"], strict=True)
    ]
    return against


def claimed_agreement(evidence: Evidence) -> pd.DataFrame:
    """Every unnamed measurement beside the value its own description requires, with its error."""
    frame = evidence.claimed.dropna(subset=["value", "claimed"]).copy()
    frame["error"] = [
        error(v, t, s)
        for v, t, s in zip(frame["value"], frame["claimed"], frame["size"], strict=True)
    ]
    frame["signed"] = [
        signed(v, t, s)
        for v, t, s in zip(frame["value"], frame["claimed"], frame["size"], strict=True)
    ]
    return frame


def invented(evidence: Evidence) -> pd.DataFrame:
    """Every named answer where the geometry offers no value, and whether a number came back."""
    named = evidence.said[evidence.said["canonical"].notna()]
    asked = named.merge(evidence.none, on=["key", "canonical"], how="inner")
    return asked.assign(invented=asked["value"].notna())


def troubles(evidence: Evidence) -> pd.DataFrame:
    """Every exception an adapter caught, and every rendering nothing came back for."""
    found = []
    for slug in evidence.implementations:
        frame = evidence.measured[slug]
        noted = frame[frame["note"].notna() & (frame["note"].astype(str).str.strip() != "")]
        for _, row in noted.iterrows():
            for complaint in str(row["note"]).split("; "):
                what, _, why = complaint.partition(": ")
                found.append(
                    {
                        "implementation": slug,
                        "shape": row["shape"],
                        "rotation": row["rotation"],
                        "what it could not answer": what,
                        "what it raised": why,
                    }
                )
        for _, row in frame[frame["outcome"] == "failed"].iterrows():
            found.append(
                {
                    "implementation": slug,
                    "shape": row["shape"],
                    "rotation": row["rotation"],
                    "what it could not answer": "everything",
                    "what it raised": str(row["note"]) if pd.notna(row["note"]) else "nothing",
                }
            )
    return pd.DataFrame(
        found,
        columns=[
            "implementation",
            "shape",
            "rotation",
            "what it could not answer",
            "what it raised",
        ],
    )


def coverage(evidence: Evidence) -> pd.DataFrame:
    """How much each implementation produced, how much of it can be judged, and against what."""
    rows = {}
    for slug in evidence.implementations:
        said = evidence.said[evidence.said["implementation"] == slug]
        with_value = set(said.loc[said["value"].notna(), "own"])
        with_value |= set(
            evidence.categories.loc[evidence.categories["implementation"] == slug, "own"]
        )
        named = {own for own, name in evidence.names[slug].items() if name}
        mine = claims.claimed(slug)
        settled = {own for own, claim in mine.items() if not claim.unsettled}
        rows[slug] = {
            "columns it returns": len(evidence.names[slug]),
            "…that returned a value": len(with_value),
            "matching a canonical name": len(named),
            "…of those, returning a value": len(with_value & named),
            "unnamed, but returning a value": len(with_value - named),
            "…held to their own description": len((with_value - named) & settled),
            "…whose description the shapes cannot settle": len(
                (with_value - named) & (set(mine) - settled)
            ),
            "seconds per image": round(evidence.measured[slug]["seconds"].astype(float).mean(), 1),
        }
    return pd.DataFrame(rows)


def best_and_worst(
    against: pd.DataFrame,
    slug: str,
    top: int = 5,
    tolerance: float = GROUND_TRUTH_TOLERANCE,
    by: str = "canonical",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One implementation's catalogued biomarkers ordered by how close they came to the geometry.

    A biomarker is judged by its **worst** case over every shape and angle, then by its median, so
    a quantity right on twelve shapes and wrong on one is not counted as right.

    *Best* is every biomarker inside the noise floor everywhere, and at least the closest few
    besides — up to half of what it answers, so a short list is not all "best". *Worst* is only
    what is out by more than `tolerance` somewhere, furthest first: a biomarker 2% out is not a
    worst case because it happens to be the last of six. No biomarker is listed twice.
    """
    mine = against[against["implementation"] == slug]
    if mine.empty:
        empty = pd.DataFrame(columns=["worst", "median", "renderings", "worst on"])
        return empty, empty
    grouped = mine.groupby(by)
    table = pd.DataFrame(
        {
            "worst": grouped["error"].max(),
            "median": grouped["error"].median(),
            "renderings": grouped.size(),
            "worst on": grouped.apply(
                lambda group: (
                    f"{group.loc[group['error'].idxmax(), 'shape']} "
                    f"{group.loc[group['error'].idxmax(), 'rotation']:.0f}°"
                ),
                include_groups=False,
            ),
        }
    )
    ordered = table.sort_values(["worst", "median"])
    inside = int((ordered["worst"] == 0.0).sum())
    best = ordered.head(max(inside, min(top, (len(ordered) + 1) // 2)))
    rest = ordered.drop(index=best.index)
    worst = rest[rest["worst"] > tolerance].tail(top).iloc[::-1]
    return best, worst


def as_percent(table: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return (table * 100).round(1)


def readable(fraction: float) -> str:
    """An error for a reader: a percentage up to ten times the truth, a multiple beyond it, where a
    percentage with eight digits would be read as noise rather than as a number."""
    if pd.isna(fraction):
        return "—"
    if fraction < 10:
        return f"{100 * fraction:.1f}%"
    return f"{fraction:,.0f}×"


def legible(table: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """A table of fractions with every cell `readable`."""
    return table.map(readable)


def over(table: pd.DataFrame, tolerance: float) -> pd.DataFrame:
    """Only the rows where at least one implementation is outside the tolerance."""
    return table[(table > tolerance).any(axis=1)]


# figures ---------------------------------------------------------------------------------------


def heat(table: pd.DataFrame, title: str, cap: float = 1.0, ax=None):
    """A table of fractions as a heat map in one hue, light at nought and dark at `cap` or more,
    each cell labelled with its percentage. Blank where nothing was measured."""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    ramp = LinearSegmentedColormap.from_list("error", RAMP)
    ramp.set_bad("#ffffff")
    rows, columns = table.shape
    if ax is None:
        width = 1.6 + (0.75 if columns > 6 else 1.25) * columns
        _, ax = plt.subplots(figsize=(width, 0.6 + 0.27 * rows))
    shown = np.clip(table.to_numpy(dtype=float), 0, cap)
    ax.imshow(np.ma.masked_invalid(shown), cmap=ramp, vmin=0, vmax=cap, aspect="auto")
    # Many columns — shapes rather than implementations — are tilted so their names do not collide.
    tilt = 35 if columns > 6 else 0
    ax.set_xticks(
        range(columns), table.columns, rotation=tilt, ha="right" if tilt else "center", fontsize=9
    )
    ax.set_yticks(range(rows), table.index, fontsize=8)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(rows):
        for j in range(columns):
            value = table.iat[i, j]
            if pd.isna(value):
                continue
            ink = "#ffffff" if min(value, cap) > 0.55 * cap else "#0b0b0b"
            text = f"{100 * value:.0f}%" if value < 10 else f"{value:.0f}×"
            ax.text(j, i, text, ha="center", va="center", fontsize=7.5, color=ink)
    ax.set_title(title, fontsize=10, loc="left", color="#0b0b0b")
    return ax


def strips(
    frame: pd.DataFrame,
    order: list[str],
    implementations: list[str],
    title: str,
    value: str = "signed",
    index: str = "canonical",
):
    """Every signed error as a dot, one row per quantity, one colour per implementation, on a
    symmetric log scale so a few percent and a factor of ten are both legible. The band around
    nought is the ground-truth tolerance."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(9, 0.8 + 0.3 * len(order)))
    offsets = np.linspace(-0.22, 0.22, len(implementations)) if len(implementations) > 1 else [0]
    for colour, offset, slug in zip(COLOURS, offsets, implementations, strict=False):
        mine = frame[frame["implementation"] == slug]
        rows = mine[index].map({name: i for i, name in enumerate(order)})
        ax.scatter(
            mine[value] * 100,
            rows + offset,
            s=14,
            color=colour,
            alpha=0.7,
            linewidths=0,
            label=slug,
        )
    ax.axvspan(
        -100 * GROUND_TRUTH_TOLERANCE, 100 * GROUND_TRUTH_TOLERANCE, color="#f0efec", zorder=0
    )
    ax.axvline(0, color="#898781", linewidth=0.8)
    ax.set_xscale("symlog", linthresh=10)
    reach = max(30.0, float(np.nanmax(np.abs(frame[value]))) * 100 * 1.3) if len(frame) else 30.0
    ticks = [t for t in (10, 25, 100, 1000, 10000, 100000) if t <= reach]
    ax.set_xticks([-t for t in ticks[::-1]] + [0] + ticks)
    ax.set_xticklabels([f"{-t:,}" for t in ticks[::-1]] + ["0"] + [f"+{t:,}" for t in ticks])
    ax.set_xlim(-reach, reach)
    ax.set_yticks(range(len(order)), order, fontsize=8)
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_xlabel("error against the required value, % (symmetric log scale)", fontsize=9)
    ax.grid(axis="x", color="#e4e3df", linewidth=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.set_title(title, fontsize=10, loc="left")
    if len(implementations) > 1:
        ax.legend(loc="lower right", fontsize=8, frameon=False)
    return ax
