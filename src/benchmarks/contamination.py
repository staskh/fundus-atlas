# ABOUTME: Whether a model saw a dataset before it was scored on it, from what its catalogue page
# ABOUTME: states about its training data — never from a guess, and never merged with "unknown".

from dataclasses import dataclass

#: Every mark a result can carry. `unknown` is never merged with `out-of-sample`: one says the
#: model did not train on these images, the other says nobody established what it trained on.
OUT_OF_SAMPLE = "out-of-sample"
IN_SAMPLE = "in-sample"
IN_SAMPLE_UNCLEAR_SPLIT = "in-sample-unclear-split"
UNKNOWN = "unknown"

#: A dataset trained on without the authors saying which part of it.
ANY_SPLIT = "*"


@dataclass(frozen=True)
class Subsets:
    """A dataset trained on through some of its own subcollections and not the others.

    A compilation such as REYIA is several sources under one name, and a model can train on some
    of them while holding the rest out as a test — so the mark follows the subset, as it follows
    the split where a model trained on one split.
    """

    names: tuple[str, ...]


#: The REYIA subsets OCULAR trains on, by the store's subset names: ENRICH, FIVES-AV, GRAPE,
#: MAGREBHIA, MESSIDOR-AV and PAPILA. It holds out mBRSET and TREND-AV as out-of-distribution
#: tests, and AV-WIDE, which the store does not build.
OCULAR_REYIA = Subsets(("enrich", "fives", "grape", "magreb", "messidor", "papila"))

#: docs/models/ocularnet.md section 6, from the OCULAR README's training table and Plaza 2026.
#: FIVES, GRAPE, MESSIDOR and PAPILA are in it as REYIA's renditions of some of their photographs
#: — 75 of FIVES' 800, for instance — which is in-sample with the part not stated. DRIVE's
#: artery/vein labels are RITE's, so both names are the same photographs.
OCULAR_TRAINING: dict[str, object] = {
    "avrdb": ANY_SPLIT,
    "drive": ANY_SPLIT,
    "rite": ANY_SPLIT,
    "fives": ANY_SPLIT,
    "fundus-avseg": ANY_SPLIT,
    "gave": ANY_SPLIT,
    "grape": ANY_SPLIT,
    "hrf": ANY_SPLIT,
    "inspire-avr": ANY_SPLIT,
    "les-av": ANY_SPLIT,
    "leuven-haifa": ANY_SPLIT,
    "messidor": ANY_SPLIT,
    "papila": ANY_SPLIT,
    "reyia": OCULAR_REYIA,
}

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
    # docs/models/segan-vessel.md section 6: six vessel datasets at once, which the repository
    # names ALL-SIX, with no per-dataset split restated. DRIVE's photographs are RITE's, so the
    # artery/vein benchmark's `rite` is the same images under another dataset's labels.
    "segan-vessel": {
        "drive": ANY_SPLIT,
        "rite": ANY_SPLIT,
        "stare": ANY_SPLIT,
        "chase-db1": ANY_SPLIT,
        "hrf": ANY_SPLIT,
        "iostar": ANY_SPLIT,
        "les-av": ANY_SPLIT,
    },
    # docs/models/segformer-disc-cup.md section 6: fine-tuned on REFUGE, split not stated.
    "segformer-disc-cup": {"refuge": ANY_SPLIT},
    # docs/models/beal.md section 6: REFUGE labelled; Drishti-GS and RIM-ONE as unlabelled target
    # domains, then tested on them — which is in-sample by any reading this atlas can defend.
    "beal": {"refuge": ANY_SPLIT, "drishti-gs": ANY_SPLIT, "rim-one-dl": ANY_SPLIT},
    # docs/models/ocularnet.md and ocularnet-nano.md section 6: one training collection for both.
    "ocularnet": OCULAR_TRAINING,
    "ocularnet-nano": OCULAR_TRAINING,
    # docs/models/vascx-*.md section 6, from the VascX paper's Table 1. Each model is a five-fold
    # cross-validation ensemble, so the released ensemble has seen every image of its training
    # data. RAV is the Rotterdam Study's photographs, annotated by VascX's own group, and VascX
    # trains on Rotterdam Study images that are not published: the overlap is not established,
    # so RAV is not cleared.
    "vascx-vessels": {
        "chase-db1": ANY_SPLIT,
        "dr-hagis": ANY_SPLIT,
        "hrf": ANY_SPLIT,
        "reta": ANY_SPLIT,
        "fives": ANY_SPLIT,
        "leuven-haifa": ANY_SPLIT,
        "rav": ANY_SPLIT,
    },
    "vascx-artery-vein": {
        "rite": ANY_SPLIT,
        "drive": ANY_SPLIT,
        "hrf": ANY_SPLIT,
        "les-av": ANY_SPLIT,
        "leuven-haifa": ANY_SPLIT,
        "rav": ANY_SPLIT,
    },
    # PALM is the remaining disc dataset; it is not catalogued here.
    "vascx-disc": {
        "origa": ANY_SPLIT,
        "papila": ANY_SPLIT,
        "idrid": ANY_SPLIT,
        "adam": ANY_SPLIT,
        "refuge": ANY_SPLIT,
    },
    "vascx-fovea": {"idrid": ANY_SPLIT, "adam": ANY_SPLIT, "refuge": ANY_SPLIT},
    "vascx-quality": {"eyeq": ANY_SPLIT},
}

#: Models whose training data could not be established from their page: LUNet v2's page cannot
#: establish what it trained on at all.
UNESTABLISHED = {"lunetv2-odc"}


def mark(model: str, dataset: str, split: str = "", subset: str = "") -> str:
    """What a result is worth, for this model on this dataset — or on one split or subset of it.

    :param split: the split being reported.
    :param subset: the dataset's own subcollection being reported.
        Either left out, the answer is the one that hides least: a summary over a dataset whose
        training part is in it is not out-of-sample.
    """
    if model in UNESTABLISHED or model not in TRAINED_ON:
        return UNKNOWN
    trained = TRAINED_ON[model].get(dataset)
    if trained is None:
        return OUT_OF_SAMPLE
    if trained == ANY_SPLIT:
        return IN_SAMPLE_UNCLEAR_SPLIT
    if isinstance(trained, Subsets):
        if not subset:
            return IN_SAMPLE
        return IN_SAMPLE if subset in trained.names else OUT_OF_SAMPLE
    if not split:
        return IN_SAMPLE
    return IN_SAMPLE if split in trained else OUT_OF_SAMPLE


def splits_disagree(model: str, dataset: str, splits: list[str]) -> bool:
    """Whether this dataset's splits carry different marks for this model.

    Where they do, a report **must** break the dataset into its splits: one number over a training
    half and a test half is not a result.
    """
    return len({mark(model, dataset, split) for split in splits}) > 1


def subsets_disagree(model: str, dataset: str, subsets: list[str]) -> bool:
    """Whether this dataset's subsets carry different marks for this model.

    Where they do, a report **must** break the dataset into its subsets, for the reason it must
    break one into its splits.
    """
    return len({mark(model, dataset, subset=subset) for subset in subsets}) > 1
