# ABOUTME: Whether a model saw a dataset before it was scored on it, from what its catalogue page
# ABOUTME: states about its training data — never from a guess, and never merged with "unknown".

from .loaders.base import Unit

#: Every mark a result can carry. `unknown` is never merged with `out-of-sample`: one says the
#: model did not train on these images, the other says nobody established what it trained on.
OUT_OF_SAMPLE = "out-of-sample"
IN_SAMPLE = "in-sample"
IN_SAMPLE_UNCLEAR_SPLIT = "in-sample-unclear-split"
UNKNOWN = "unknown"

#: The datasets each model's page names in its training-data section, and whether the split it
#: trained on was stated. A model missing from here has no page saying, which is `unknown`.
TRAINED_ON: dict[str, dict[str, str]] = {
    # docs/models/fit-quality.md section 6: DeepDRiD and DRIMDB, a test split reported for each,
    # but the page does not say which images fell in it.
    "fit-quality": {"deepdrid": IN_SAMPLE_UNCLEAR_SPLIT, "drimdb": IN_SAMPLE_UNCLEAR_SPLIT},
    # docs/models/automorph-quality-grader.md section 6: EyeQ's own training split.
    "automorph-quality-grader": {"eyeq": IN_SAMPLE},
    # docs/models/quickqual.md section 6: EyeQ's train split, evaluated on EyeQ's test split.
    "quickqual": {"eyeq": IN_SAMPLE},
    # docs/models/quickqual-meme.md section 6: the same ten parameters, fitted on the same split.
    "quickqual-meme": {"eyeq": IN_SAMPLE},
}

#: Models whose training data could not be established from their page. VascX names "more than
#: fifteen published annotated datasets" without listing them, so no dataset can be cleared.
UNESTABLISHED = {"vascx-quality"}


def mark(model: str, unit: Unit) -> str:
    """What a result on this unit is worth, for this model."""
    if model in UNESTABLISHED:
        return UNKNOWN
    trained = TRAINED_ON.get(model)
    if trained is None:
        return UNKNOWN
    return trained.get(unit.slug, OUT_OF_SAMPLE)
