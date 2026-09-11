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

    def grade(self, row: dict[str, str]) -> tuple[str, str]:
        value = row[self.column]
        if value == "":
            return "", "published"
        if value not in self.mapping:
            raise ValueError(f"{self.column} is {value!r}, which the mapping does not cover")
        return self.mapping[value], "published"


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


Rule = Published | FromComponents


def grade_of(rule: Rule | None, row: dict[str, str]) -> tuple[str, str]:
    """Apply a fetcher's quality rule, or return no grade where it declares none.

    :param rule: the fetcher's `QUALITY`, or `None` for a dataset that grades nothing.
    :param row: the manifest row, holding the dataset's own columns.
    :return: the grade and the `quality_source` that explains where it came from.
    """
    if rule is None:
        return "", ""
    return rule.grade(row)
