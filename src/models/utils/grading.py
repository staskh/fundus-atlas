# ABOUTME: The vocabulary a quality adapter answers in: the atlas's three grades, the three
# ABOUTME: outcomes a prediction can have, and what a model is allowed to leave unsaid.

from dataclasses import dataclass, field

#: The atlas's own grade names. Every model's codes are translated into these by its adapter, so
#: that a table of results does not have to explain three vocabularies at once.
GOOD = "good"
USABLE = "usable"
BAD = "bad"
GRADES = (GOOD, USABLE, BAD)

#: What became of one prediction. A model that refuses a photograph has not got it wrong, and a
#: model that crashed on one has not judged it: both are counted, and neither is scored.
GRADED = "graded"
DECLINED = "declined"
FAILED = "failed"
OUTCOMES = (GRADED, DECLINED, FAILED)


@dataclass(frozen=True)
class Grade:
    """One model's answer about one photograph.

    A binary grader fills :attr:`gradeable` and leaves :attr:`verdict` empty; a three-way grader
    fills all three fields. Nothing here is a score: the benchmark compares this against the
    dataset's own grade, and the adapter that produced it never sees the answer.

    :param gradeable: the model's confidence that the photograph is worth measuring — good or
        usable against bad — which is the one number every quality model in this catalogue can
        produce and therefore the one they can be compared on.
    :param classes: the probability of each atlas grade, where the model emits three.
    :param gated: what the model's **own project** would do with this photograph — carry it into
        measurement, or drop it. It is not the model's verdict and not the atlas's reading of it:
        a pipeline is free to admit a merely usable photograph, or to refuse one, and several do
        it by a rule that is not the model's own argmax. ``None`` where no catalogued pipeline
        gates on this model at all.
    :param note: why it declined, or what it failed with.
    """

    key: str
    outcome: str = GRADED
    verdict: str = ""
    gradeable: float | None = None
    classes: dict[str, float] = field(default_factory=dict)
    gated: bool | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"{self.outcome!r} is not one of {OUTCOMES}")
        if self.verdict and self.verdict not in GRADES:
            raise ValueError(f"{self.verdict!r} is not one of {GRADES}")
        unknown = sorted(set(self.classes) - set(GRADES))
        if unknown:
            raise ValueError(f"{unknown} are not grades; the vocabulary is {GRADES}")
        if self.outcome != GRADED and (
            self.verdict or self.gradeable is not None or self.gated is not None
        ):
            raise ValueError(
                f"{self.key} is {self.outcome} and cannot also carry a grade: a photograph the "
                f"model would not answer for has no answer to record"
            )
