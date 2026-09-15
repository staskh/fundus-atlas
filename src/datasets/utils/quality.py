# ABOUTME: Turns what a dataset says about image quality into one of good, usable or bad.
# ABOUTME: A published grade is mapped; component ratings are graded by the rule in the skill, 5.4.

from dataclasses import dataclass

#: The only values `quality` may hold. A column whose vocabulary changed per dataset could not be
#: filtered across datasets, which is the only reason to have the column.
VOCABULARY = ("good", "usable", "bad")


@dataclass(frozen=True)
class Published:
    """A dataset's own overall grade, mapped into the common vocabulary.

    The authors' token stays verbatim in its own manifest column; this only translates it, so that
    a consumer filtering on `good` sees every dataset rather than the ones that happen to use the
    word.

    :param mapping: the dataset's grade as it writes it, to one of :data:`VOCABULARY`.
    :param column: the manifest column holding the dataset's own token.
    """

    mapping: dict[str, str]
    column: str = "overall_quality"

    def __post_init__(self) -> None:
        unknown = sorted(set(self.mapping.values()) - set(VOCABULARY))
        if unknown:
            raise ValueError(f"quality mapping produces {unknown}, not one of {VOCABULARY}")

    def word(self, value: str) -> str:
        """One published grade in the common vocabulary.

        Used directly where a dataset publishes each grader's verdict as well as the agreed one:
        the readers' grades go through the same declared mapping as the cell, so the manifest and
        `labels.csv` cannot come to disagree about what a code meant.
        """
        if value == "":
            return ""
        if value not in self.mapping:
            raise ValueError(f"{self.column} is {value!r}, which the mapping does not cover")
        return self.mapping[value]

    def grade(self, row: dict[str, str]) -> tuple[str, str]:
        return self.word(row[self.column]), "published"


@dataclass(frozen=True)
class FromComponents:
    """A grade derived from per-aspect ratings, for datasets that publish no overall verdict.

    All components at their best is `good`, exactly one short is `usable`, anything else is `bad`.
    An unrated component counts as short of best: an unrated aspect is not evidence of a good one.

    :param best: each component's manifest column, to the value that counts as full marks. Best is
        not always the highest number — a rating of artefacts is best at zero.
    """

    best: dict[str, str]

    def grade(self, row: dict[str, str]) -> tuple[str, str]:
        short = sum(1 for column, full_marks in self.best.items() if row[column] != full_marks)
        if short == 0:
            return "good", "derived"
        if short == 1:
            return "usable", "derived"
        return "bad", "derived"


@dataclass(frozen=True)
class Assumed:
    """A grade nobody published, taken as read for a dataset that grades nothing.

    Some datasets carry no quality annotation at all and yet were plainly curated — every
    photograph disc-centred, one camera, a clinical study that would have discarded an unreadable
    frame. Assuming they are all sound makes them usable as a reference for one particular
    question: how much of a sound dataset a quality model would throw away.

    It is the weakest of the three sources and is marked as such in every row, because it is this
    repository's assumption rather than the dataset's statement, and `CLAUDE.md` section 4.4 keeps
    those two apart. A consumer filtering on `quality == "good"` across datasets is otherwise
    mixing an expert's verdict with our supposition.

    :param because: why the assumption is defensible, recorded on the dataset page beside it.
    """

    grade_for_every_image: str
    because: str

    def __post_init__(self) -> None:
        if self.grade_for_every_image not in VOCABULARY:
            raise ValueError(f"{self.grade_for_every_image!r} is not one of {VOCABULARY}")
        if not self.because.strip():
            raise ValueError("an assumed grade must say why it is assumed")

    def grade(self, row: dict[str, str]) -> tuple[str, str]:
        return self.grade_for_every_image, "assumed"


Rule = Published | FromComponents | Assumed


def grade_of(rule: Rule | None, row: dict[str, str]) -> tuple[str, str]:
    """Apply a fetcher's quality rule, or return no grade where it declares none.

    :param rule: the fetcher's `QUALITY`, or `None` for a dataset that grades nothing.
    :param row: the manifest row, holding the dataset's own columns.
    :return: the grade and the `quality_source` that explains where it came from.
    """
    if rule is None:
        return "", ""
    return rule.grade(row)
