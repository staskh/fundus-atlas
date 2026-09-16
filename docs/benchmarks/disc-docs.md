# Disc benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part, what it excludes, how to run it, and what every column of its evidence means. It is generated **before** a run measures anything, and again whenever the benchmark's code changes, so it describes the run that is happening rather than the one that happened to finish. A column added to the evidence and not explained here is a bug rather than an omission. What came out is a separate page: [disc-results.md](disc-results.md).

## 1. What this benchmark asks

How close a model's optic disc and optic cup are to **the outline an ophthalmologist drew on that photograph**, and how far the difference travels into the numbers a clinic would read off it. Overlap is measured as the Dice score — twice the area the two outlines share, divided by the sum of their areas, so 1 is perfect agreement and 0 no overlap at all. Beside it are the measurements a report actually quotes: where the centre of the disc sits, how wide and how tall each structure is, the radius of a circle of the same area, and the **cup-to-disc ratio**, which is the number a glaucoma referral rests on. Comparing the models with each other is a second, weaker question, and it is there to raise suspicions about the outlines rather than to rank the software.

**Every measurement is made in the native frame** — the full-resolution square the store built, which is where the expert drew. A model working at 512 pixels has its answer carried back there first, and how it was carried is recorded per photograph: a probability map is resampled and thresholded **after** it arrives, because thresholding first and resampling the mask throws away the boundary detail the model produced, and the boundary is what every one of these numbers turns on.

**Signed errors are kept signed.** A model whose discs are three pixels too wide and one whose discs are three pixels too narrow do not average to agreement, and a cup-to-disc ratio that reads high sends the wrong patients to a clinic.

**The outlines themselves are kept**, one image per structure per photograph, under `.atlas_runs/disc/<model>/<dataset>/` beside the fingerprint of the model that drew them. A score is a summary of a shape, and the shape is what the next benchmark measures biomarkers from; a mask whose fingerprint no longer matches its model is drawn again rather than read.

## 2. The models

| Model | Pinned at | Grid it reads | Grid the network sees | Finds | Emits |
| --- | --- | --- | --- | --- | --- |
| [automorph-disc-cup](../models/automorph-disc-cup.md) | `9a953e5e` | 512² | 512² | disc, cup | probabilities, thresholded in the native frame |
| [lunetv2-odc](../models/lunetv2-odc.md) | `f72f6c9e` | 512² | 512² | disc, cup | probabilities, thresholded in the native frame |
| [segformer-disc-cup](../models/segformer-disc-cup.md) | `a0463fb6` | 512² | 512² | disc, cup | probabilities, thresholded in the native frame |
| [vascx-disc](../models/vascx-disc.md) | `d0cde1c7` | 1024² | 512² | disc | probabilities, thresholded in the native frame |
| [beal](../models/beal.md) | **not measured** — no adapter yet: its weights are an unversioned Google Drive folder, so nothing can be pinned, and its inference expects the authors' own preprocessed directory layout | — | — | — | — |
| [isfa](../models/isfa.md) | **not measured** — its repository publishes an ImageNet backbone under `pretrained_model/`, not trained weights — checked against the repository, and its own weights link now 404s | — | — | — | — |

A model named here that has no adapter is **declared, not forgotten**: the benchmark asks for it, and the run says so every time until somebody writes it.

A model that finds only the disc is scored on the disc alone. Its rows carry no cup columns rather than empty ones, and it is never counted as having got the cup wrong.

## 3. The datasets

| Dataset | Photographs | Readers | Black canvas | Excluded, and why |
| --- | --- | --- | --- | --- |
| [chaksu](../datasets/chaksu.md) | 1345 | 5: expert1, expert2, expert3, expert4, expert5 | 0.000 | none |
| [grape](../datasets/grape.md) | 631 | 1: expert1 | 0.000 | none |
| [papila](../datasets/papila.md) | 488 | 2: expert1, expert2 | 0.188 | none |
| [drishti-gs](../datasets/drishti-gs.md) | **not measured** — no store built | — | — | — |
| [origa](../datasets/origa.md) | **not measured** — no store built | — | — | — |
| [refuge](../datasets/refuge.md) | **not measured** — no store built | — | — | — |
| [rim-one-dl](../datasets/rim-one-dl.md) | **not measured** — no store built | — | — | — |

**Readers are never merged.** A photograph five ophthalmologists outlined makes five rows of evidence, one per reader, and a model is scored against each of them separately. Averaging the outlines first would invent a consensus nobody drew and would hide the range the readers themselves disagree over — which, on these structures, is often wider than the gap between two models.

**Black canvas** is the share of the square the store built that is not photograph. A fundus cut off at top and bottom leaves bands there, and a model sees the square it is handed.

**Every reference here is a contour somebody drew**, and the ratios are computed from it. [Chákṣu](../datasets/chaksu.md) also publishes each expert's own cup-to-disc ratio **as a number**, which would be the strongest available check that a ratio derived from a contour means what this benchmark thinks it means — but its store does not carry those numbers yet, so nothing here is scored against them. That is a gap in the fetcher rather than in the dataset.

### 3.1 What is worth fetching next, and what each would settle

| Dataset | What it would settle | Cost |
| --- | --- | --- |
| [refuge](../datasets/refuge.md) | three of the models here trained on it, so it is what turns an in-sample suspicion into a measured contrast | registration |
| [drishti-gs](../datasets/drishti-gs.md) | four experts **and soft probability maps** — the only dataset here publishing annotator uncertainty as a map rather than as separate outlines | direct |
| [origa](../datasets/origa.md) | publishes `ExpCDR`, an expert cup-to-disc ratio **as a number**, which is the strongest available check that a ratio derived from contours means what this benchmark thinks | needs an archive by hand |
| [rim-one-dl](../datasets/rim-one-dl.md) | BEAL's other unlabelled target domain; it completes the contamination picture for that model once there is an adapter for it | direct |

[RIGA](../datasets/riga.md) is the painful exclusion: 750 photographs each outlined by **six** ophthalmologists, and every one of its images is a crop rather than a photograph, so the crop rule of section 4 excludes it whole.

## 4. What is excluded, and by which rule

- **Below the size floor** — a photograph whose field of view is under 512 pixels, measured on the field's own size rather than the frame's.
- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a store. An outline a finding condemns is dropped on its own, leaving the other readers' outlines of that photograph in place.
- **No outline to score against** — a photograph the dataset published but nobody outlined. It is not a failure of the model and is never counted as one.
- **Excluded whole** — a dataset whose images are crops rather than photographs. No size floor catches that, because a crop can be large.

These are **ours**: the benchmark would not ask. A model's own refusal to answer is `declined`, which is a different statement, and the two are never added together.
## 5. How to run it

```bash
python -m benchmarks --benchmark disc
python -m benchmarks --benchmark disc --model automorph-disc-cup --dataset chaksu
python -m benchmarks --benchmark disc --max-samples 20
```

`--model` and `--dataset` each take one name or a comma-separated list, and naming one of each re-measures a single pair. `--max-samples N` scores the first N photographs of each dataset — `--random-samples` chooses them at random from a recorded seed — which is for development: a sampled result says it is not complete, and a later run finishes it rather than starting again. `--force` discards what is stored and measures everything afresh.

## 6. What each column of the evidence means

`results/disc/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, as the store names it |
| `subset` | the dataset's own subcollection: a camera, a site, a challenge release |
| `split` | the split the dataset published, or `unspecified` |
| `reader` | **which expert drew the outline this row is scored against**; a photograph with five readers makes five rows |
| `native_side` | the side of the native square, in pixels — every measurement below is in it |
| `outcome` | `graded`, or `failed` with the reason in `note` |
| `resampling` | how the model's output reached the native frame: probabilities interpolated and then thresholded, or a binary mask resampled nearest |
| `disc_dice` | overlap with this reader's disc, 0 to 1 |
| `cup_dice` | overlap with this reader's cup; absent for a model that finds no cup |
| `disc_centre_offset` | distance between the two disc centres, in native pixels |
| `cup_centre_offset` | as above, for the cup |
| `disc_centre_offset_diameters` | the same distance **in the expert's own disc diameters**, which is the only camera-independent form: ten pixels means one thing on a 2,576-pixel photograph and another on a 1,444-pixel one |
| `cup_centre_offset_diameters` | the cup's offset, measured in that same disc diameter rather than in the cup's own — the disc is the ruler |
| `disc_width_error` | signed: the model's disc width less the reader's, in pixels |
| `disc_height_error` | signed, likewise |
| `cup_width_error` | signed, for the cup |
| `cup_height_error` | signed, for the cup |
| `disc_radius_error` | signed: the radius of a circle of the same area, less the reader's |
| `cup_radius_error` | as above, for the cup |
| `truth_disc_width` | how wide the expert drew the disc, in native pixels — the size every error above is an error of |
| `truth_disc_height` | how tall, likewise |
| `truth_disc_radius` | the radius of a circle of the same area as the expert's disc |
| `truth_cup_width` | how wide the expert drew the cup |
| `truth_cup_height` | how tall |
| `truth_cup_radius` | the radius of a circle of the same area as the expert's cup |
| `said_vertical_ratio` | the model's cup height over its disc height |
| `truth_vertical_ratio` | this reader's own vertical cup-to-disc ratio |
| `cup_vertical_ratio_error` | **signed**: the model's vertical ratio less the reader's — the number a referral rests on |
| `said_area_ratio` | the model's cup area over its disc area |
| `truth_area_ratio` | this reader's own area ratio |
| `cup_area_ratio_error` | signed, likewise |
| `cup_outside_its_disc` | the share of the model's cup that falls outside its own disc, measured rather than repaired |
| `note` | what the model failed with |

A model that has no opinion to record leaves a column **absent** rather than blank: a binary grader emits no class probabilities, and none are invented for it.

## 7. What a re-run repeats, and what it does not

Each `(model, dataset)` result is stored beside a **fingerprint** of everything that could change it: the facts the model declares — its grids, its ensemble, the thresholds it acts on — the sha256 of the weights actually loaded, the patches applied by content, the store's builder version, and this benchmark's own version. A fingerprint that differs means the stored scores describe something that no longer exists, and the pair is measured again from nothing.

**How much was done is not part of that**, because it does not change what any photograph scored. A complete result is never re-run; a partial one is finished by measuring only the photographs it is missing; and nothing is ever truncated — asking for twenty against a file that holds four hundred leaves all four hundred alone.

## 8. The counts every result carries

| Recorded | Means |
| --- | --- |
| `processed` | how many photographs this model has actually scored |
| `total` | how many the benchmark would ask about, after the exclusions of section 4 |
| `excluded` | how many those exclusions removed, by reason |
| `seconds_per_photograph` | how long the model itself took per photograph, on the device the result names |
| `timed_photographs` | how many photographs that timing covers |

`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is either one the benchmark asks about or one it excluded, never both and never neither.

The timing covers the model's own call and nothing around it — not reading the photograph, not scoring the answer. The batch that loads the weights is left out of it whenever there is another batch to average over, and a run that measured nothing keeps the timing it already had rather than reporting none. It is **not** part of the fingerprint: how fast a model answered does not change what it said, and the same weights on another machine would give another number.

---

**Generated by `python -m benchmarks --benchmark disc` on:** 2026-09-16
