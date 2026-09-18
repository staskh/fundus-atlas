# ABOUTME: The artery/vein benchmark: how close a model's arteries, veins and the vessels they make
# ABOUTME: together are to what an expert drew, by overlap and by connectedness.

from collections.abc import Iterable
from pathlib import Path

from models.utils import catalogue

from . import report
from .loaders.av import ArteryVeinLoader
from .loaders.base import CROPS, available

#: What this benchmark is called in a heading, where its slug does not read as English.
TITLE = "Artery and vein"

#: What this benchmark is called: in `results/`, in `docs/benchmarks/` and in a run record.
NAME = "av"

#: The benchmark's own version. Changing what is measured, or how, changes this.
VERSION = 1

#: What this benchmark asks, in the two sentences the index has room for.
GOAL = (
    "**Which vessels are arteries and which are veins?** Each model's segmentation is compared with "
    "what an ophthalmologist drew on the same photograph — the arteries, the veins, and the vessels "
    "they make together — by overlap and by how much of the vessel network survives. Everything "
    "computed *from* a vessel map, a calibre or an arteriovenous ratio, belongs to the biomarker "
    "benchmark instead."
)

#: The datasets this benchmark wants. A name here is intent, not inventory.
DATASETS = ("hrf", "fundus-avseg", "avrdb", "reyia", "rav", "les-av", "rite")

#: The models, by the slug of their catalogue page.
MODELS = (
    "vascx-artery-vein",
    "ocularnet",
    "lunet",
    "automorph-artery-vein",
    "bf-net",
    "ocularnet-nano",
)

#: Why a declared model has no adapter, where the reason is worth more than "nobody wrote one".
WHY_NOT = {
    "ocularnet-nano": (
        "its five checkpoints answer HTTP 401 and the anonymous review account that served them now "
        "holds one repository — the weights cannot be obtained at all"
    ),
}

#: Datasets worth fetching next, and what each would settle.
WORTH_FETCHING = (
    (
        "rav",
        (
            "206 photographs no catalogued model names in training, from a population cohort with "
            "quality mixed on purpose — the closest thing here to a held-out test set"
        ),
        "direct, but its host's bot gate refuses some networks",
    ),
    (
        "les-av",
        "22 photographs, direct, and it completes the contamination picture for BF-Net",
        "direct",
    ),
    (
        "rite",
        (
            "the 40 DRIVE photographs every artery/vein paper reports, which is what makes a number "
            "here comparable with the literature"
        ),
        "registration",
    ),
)

#: How many photographs go to the model at once. One: these models work at 1024 and 1472, and their
#: output is resampled to native, which is where the memory goes.
BATCH = 1

#: What a model declares that could change its numbers.
FINGERPRINTED = (
    "slug",
    "purpose",
    "grid",
    "network_grid",
    "structures",
    "channels",
    "emits_probabilities",
    "resampling",
    "threshold",
    "ensemble",
)


def adapters(slugs: list[str], device: str | None = None) -> tuple[list, dict[str, str]]:
    """The model adapters that exist, and what was declared without one."""
    found, missing = [], {}
    for slug in slugs:
        try:
            found.append(catalogue.load(slug, **({"device": device} if device else {})))
        except LookupError:
            missing[slug] = WHY_NOT.get(slug, "no adapter written")
    return found, missing


def missing_datasets(slugs: list[str], root: Path | None = None) -> dict[str, str]:
    """What was declared that this run cannot measure, and why."""
    missing = {}
    for slug in slugs:
        if slug in CROPS:
            missing[slug] = "excluded whole: its images are crops rather than photographs"
        elif not available(slug, root):
            missing[slug] = "no store built"
    return missing


def configuration(models: list, datasets: list[str], root: Path | None = None) -> dict[str, object]:
    """What this run is about to do, without doing any of it."""
    absent = missing_datasets(datasets, root)
    described = []
    for slug in (name for name in datasets if name not in absent):
        loader = ArteryVeinLoader(slug, size=models[0].grid if models else 1024, root=root)
        readers = sorted(
            {reader for row in loader.rows for reader in row["readers"].split(";") if reader}
        )
        described.append(
            {
                "slug": slug,
                "total": loader.total,
                "excluded": dict(loader.excluded),
                "readers": readers,
                "vessels": DERIVED.get(slug, "unknown"),
            }
        )
    return {
        "models": [{"slug": model.slug, "declared": model.declare()} for model in models],
        "datasets": described,
    }


#: Whether a dataset's vessel annotation is its own tracing or its artery/vein annotation seen
#: again. Established per dataset, by measuring, and recorded on each dataset's page.
DERIVED = {
    "hrf": "**the same tracing**: 0.004% of pixels differ from the artery/vein union",
    "fundus-avseg": "derived from the artery/vein labels by the authors",
    "avrdb": "**drawn, but not independent**: it agrees with the union to within 0.4–0.6%",
    "reyia": "derived here as the union; the archive publishes no separate tracing",
}


def docs_sections(
    configured: dict[str, object],
    missing_models: dict[str, str],
    missing_datasets_of: dict[str, str],
) -> Iterable[str]:
    """Sections 1 to 4 of the page saying how this benchmark is run."""
    models = sorted(configured["models"], key=lambda entry: entry["slug"])
    datasets = sorted(configured["datasets"], key=lambda entry: entry["slug"])
    yield "## 1. What this benchmark asks"
    yield ""
    yield (
        "Whether a model's **arteries and veins** are where an ophthalmologist drew them. Retinal "
        "arteries and veins look alike to an untrained eye and are told apart by calibre, colour "
        "and how they cross one another; a vessel map that cannot separate them supports none of "
        "the measurements a clinic takes from the vasculature. Three maps are scored: the arteries, "
        "the veins, and the vessels the two make together."
    )
    yield ""
    yield (
        "**Segmentation only.** A vessel width, a central retinal artery equivalent, an "
        "arteriovenous ratio, a tortuosity — every number computed *from* one of these maps by a "
        "further method — belongs to the biomarker benchmark, which takes the masks this one keeps "
        "as its input. Measuring both here would make a model's segmentation and a pipeline's "
        "arithmetic indistinguishable in one figure."
    )
    yield ""
    yield (
        "**Two scores, because neither is enough.** **Dice** is overlap with the expert's mask, 0 "
        "to 1. **clDice** asks instead how much of each network's *centreline* falls inside the "
        "other, which is a question about connectedness rather than area. The pair separates two "
        "failures that overlap alone confuses: a vessel drawn three times too wide around the same "
        "centre scores 0.50 Dice and 0.97 clDice — wrong about width, right about the network — "
        "while the same vessel thickened to one side scores the same 0.50 Dice and 0.03 clDice, its "
        "centreline no longer inside the expert's vessel at all. A break in a vessel costs both "
        "alike."
    )
    yield ""
    yield (
        "**Everything is measured in the native frame** — the full-resolution square the store "
        "built, where the annotator drew. A model working at 1024 or 1472 has its probabilities "
        "carried back there and thresholded **after** arrival, because thresholding first and "
        "resampling a binary mask throws away the boundary the score turns on."
    )
    yield ""
    yield (
        "**The outlines themselves are kept**, three images per photograph, under "
        "`.atlas_runs/av/<model>/<dataset>/`. The biomarker benchmark measures from them, and a "
        "mask whose fingerprint no longer matches its model is drawn again rather than read."
    )
    yield ""
    yield "## 2. The models"
    yield ""
    yield (
        "| Model | Pinned at | Grid it reads | Grid it runs at | Channels it emits | Read as | "
        "Ensemble |"
    )
    yield "| --- | --- | --- | --- | --- | --- | --- |"
    for entry in models:
        slug, declared = entry["slug"], entry["declared"]
        yield (
            f"| [{slug}](../models/{slug}.md) | {report.pin(declared.get('upstream', {}))} | "
            f"{declared['grid']}² | {declared['network_grid']}² | "
            f"{', '.join(declared.get('channels', [])) or '—'} | "
            f"{', '.join(declared.get('structures', []))} | {declared.get('ensemble', '—')} |"
        )
    for model, why in sorted(missing_models.items()):
        yield f"| [{model}](../models/{model}.md) | **not measured** — {why} | — | — | — | — | — |"
    yield ""
    yield (
        "**Two of these models do not document their channel order**, and both would have been "
        "read wrongly from a reasonable guess: LUNet puts the veins first and emits logits rather "
        "than probabilities, and VascX's fourth channel matches neither vessel. Every order here "
        "was settled the same way — by scoring each output channel against "
        "[HRF](../datasets/hrf.md)'s artery and vein annotation — including the ones the authors do "
        "name, because a documented order is still worth a measurement."
    )
    yield ""
    yield (
        "**A crossing belongs to both vessels.** Where a model emits crossings as their own class — "
        "OCULARNet, BF-Net and AutoMorph's artery/vein model all do — the adapter answers with "
        "artery *plus* crossing and vein *plus* crossing, because that is the region an annotator "
        "marked as both and a model cannot be asked to reproduce an ambiguity of projection. The "
        "two fusion models call that class *uncertainty* in their own evaluation code; scored "
        "against [HRF](../datasets/hrf.md) it is the crossings exactly, matching this "
        "repository's own crossing layer pixel for pixel."
    )
    yield ""
    yield (
        "**Two grids, because a store holds one and a network wants another.** The photographs are "
        "read at the size the store built nearest what the model was trained on, and where the "
        "network's own grid is not one of those — BF-Net and AutoMorph's artery/vein model both run "
        "at 720 — the adapter resizes down to it rather than up, so nothing is invented. The "
        "probabilities come back to the native frame either way."
    )
    yield ""
    yield (
        "**The vessel map is derived, identically for every model**, as the union of its own artery "
        "and vein masks — not whatever vessel channel a model may also publish. LUNet publishes "
        "one; it is declared above and not used, so that every model's vessel score means the same "
        "thing."
    )
    yield ""
    yield "## 3. The datasets"
    yield ""
    yield "| Dataset | Photographs | Readers | Vessel annotation | Excluded, and why |"
    yield "| --- | --- | --- | --- | --- |"
    for entry in datasets:
        slug = entry["slug"]
        yield (
            f"| [{slug}](../datasets/{slug}.md) | {entry['total']} | "
            f"{len(entry.get('readers') or []) or 1} | {entry.get('vessels', 'unknown')} | "
            f"{report.excluded(entry['excluded'])} |"
        )
    for dataset, why in sorted(missing_datasets_of.items()):
        yield f"| [{dataset}](../datasets/{dataset}.md) | **not measured** — {why} | — | — | — |"
    yield ""
    yield (
        "**The vessel annotation column is the one to read before comparing scores.** In three of "
        "these datasets the vessel map *is* the artery/vein map: Fundus-AVSeg and AVRDB derive "
        "theirs, and HRF's hand-drawn gold standard differs from the union of its artery/vein maps "
        "by 0.004% of pixels across all 45 photographs. A model's vessel score and its class scores "
        "there are **one measurement seen twice**, and their agreement is not corroboration."
    )
    yield ""
    yield (
        "[REYIA](../datasets/reyia.md) is a compilation, and its subsets are named for the "
        "collections its photographs came from — three of which this repository builds separately. "
        "Pooling a figure over REYIA and those datasets counts the same eyes twice."
    )
    yield ""
    yield "### 3.1 What is worth fetching next, and what each would settle"
    yield ""
    yield "| Dataset | What it would settle | Cost |"
    yield "| --- | --- | --- |"
    for slug, why, cost in WORTH_FETCHING:
        yield f"| [{slug}](../datasets/{slug}.md) | {why} | {cost} |"
    yield ""
    yield "## 4. What is excluded, and by which rule"
    yield ""
    yield (
        "- **Below the size floor** — a photograph whose field of view is under 512 pixels.\n"
        "- **No artery/vein annotation** — a photograph the dataset published without one. Not a "
        "failure of the model, and never counted as one.\n"
        "- **An annotation a finding condemns** — anything in `src/datasets/exclusions/`. REYIA has "
        "four photographs whose two published encodings of the same annotation contradict each "
        "other by more pixels than the vessel network contains; their maps are excluded and the "
        "photographs stay.\n"
        "- **Excluded whole** — a dataset whose images are crops rather than photographs."
    )
    yield ""
    yield (
        "These are **ours**: the benchmark would not ask. A model's own refusal to answer is "
        "`declined`, which is a different statement, and the two are never added together."
    )


#: Every column of this benchmark's evidence, and what it means.
COLUMNS = {
    "key": "the photograph, as the store names it",
    "subset": "the dataset's own subcollection — for REYIA, the collection the photograph came from",
    "split": "the split the dataset published, or `unspecified`",
    "reader": "which annotator the row is scored against, where a dataset keeps them apart",
    "native_side": "the side of the native square, in pixels — every score below is measured in it",
    "outcome": "`graded`, or `failed` with the reason in `note`",
    "resampling": "how the model's output reached the native frame",
    "artery_dice": "overlap with the reader's arteries, 0 to 1",
    "vein_dice": "overlap with the reader's veins",
    "vessels_dice": "overlap with the reader's vessels — **both derived as artery ∪ vein**",
    "artery_cldice": "how much of each artery network's centreline lies inside the other's mask",
    "vein_cldice": "as above, for the veins",
    "vessels_cldice": "as above, for the vessels",
    "said_artery_px": "how many pixels the model called artery, so a score can be read beside the "
    "size of the thing scored",
    "said_vein_px": "how many it called vein",
    "truth_artery_px": "how many **this reader** drew as artery",
    "truth_vein_px": "how many as vein",
    "note": "what the model failed with",
}
