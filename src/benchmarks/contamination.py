# ABOUTME: Whether a model saw a dataset before it was scored on it, from what its catalogue page
# ABOUTME: states about its training data — never from a guess, and never merged with "unknown".

#: Every mark a result can carry. `unknown` is never merged with `out-of-sample`: one says the
#: model did not train on these images, the other says nobody established what it trained on.
OUT_OF_SAMPLE = "out-of-sample"
IN_SAMPLE = "in-sample"
IN_SAMPLE_UNCLEAR_SPLIT = "in-sample-unclear-split"
UNKNOWN = "unknown"

#: A dataset trained on without the authors saying which part of it.
ANY_SPLIT = "*"

#: What each model's page names in its training-data section, and which splits of it. A model
#: missing from here has no page saying, which is `unknown`.
TRAINED_ON: dict[str, dict[str, object]] = {
    # docs/models/fit-quality.md section 6: DeepDRiD and DRIMDB, a test split reported for each,
    # but the page does not say which images fell in it.
    "fit-quality": {"deepdrid": ANY_SPLIT, "drimdb": ANY_SPLIT},
    # docs/models/automorph-quality-grader.md section 6: EyeQ's own training split.
    "automorph-quality-grader": {"eyeq": ("train",)},
    # docs/models/quickqual.md section 6: EyeQ's train split, evaluated on EyeQ's test split.
    "quickqual": {"eyeq": ("train",)},
    # docs/models/quickqual-meme.md section 6: the same ten parameters, fitted on the same split.
    "quickqual-meme": {"eyeq": ("train",)},
    # docs/models/automorph-disc-cup.md section 6: REFUGE and GAMMA.
    "automorph-disc-cup": {"refuge": ANY_SPLIT, "gamma": ANY_SPLIT},
    # docs/models/automorph-artery-vein.md section 6: all three artery/vein datasets at once, with
    # no split restated for the combined set.
    "automorph-artery-vein": {"rite": ANY_SPLIT, "hrf": ANY_SPLIT, "les-av": ANY_SPLIT},
    # docs/models/bf-net.md section 6: one dataset per archive, and the benchmark runs the
    # DRIVE-trained one — whose repository ships DRIVE's own training split as what it trained on.
    "bf-net": {"rite": ("train",)},
    # docs/models/segformer-disc-cup.md section 6: fine-tuned on REFUGE, split not stated.
    "segformer-disc-cup": {"refuge": ANY_SPLIT},
    # docs/models/beal.md section 6: REFUGE labelled; Drishti-GS and RIM-ONE as unlabelled target
    # domains, then tested on them — which is in-sample by any reading this atlas can defend.
    "beal": {"refuge": ANY_SPLIT, "drishti-gs": ANY_SPLIT, "rim-one-dl": ANY_SPLIT},
}

#: Models whose training data could not be established from their page. VascX names "more than
#: fifteen published annotated datasets" without listing them, so no dataset can be cleared;
#: LUNet v2's page cannot establish what it trained on at all.
UNESTABLISHED = {"vascx-quality", "vascx-disc", "lunetv2-odc"}


def mark(model: str, dataset: str, split: str = "") -> str:
    """What a result is worth, for this model on this dataset — or on one split of it.

    :param split: the split being reported. Left out, the answer is the one that hides least: a
        summary over a dataset whose training half is in it is not out-of-sample.
    """
    if model in UNESTABLISHED or model not in TRAINED_ON:
        return UNKNOWN
    trained = TRAINED_ON[model].get(dataset)
    if trained is None:
        return OUT_OF_SAMPLE
    if trained == ANY_SPLIT:
        return IN_SAMPLE_UNCLEAR_SPLIT
    if not split:
        return IN_SAMPLE
    return IN_SAMPLE if split in trained else OUT_OF_SAMPLE


def splits_disagree(model: str, dataset: str, splits: list[str]) -> bool:
    """Whether this dataset's splits carry different marks for this model.

    Where they do, a report **must** break the dataset into its splits: one number over a training
    half and a test half is not a result.
    """
    return len({mark(model, dataset, split) for split in splits}) > 1
