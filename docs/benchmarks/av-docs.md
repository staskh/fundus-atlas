# Artery and vein benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part, what it excludes, how to run it, and what every column of its evidence means. It is generated **before** a run measures anything, and again whenever the benchmark's code changes, so it describes the run that is happening rather than the one that happened to finish. A column added to the evidence and not explained here is a bug rather than an omission. What came out is a separate page: [av-results.md](av-results.md).

## 1. What this benchmark asks

Whether a model's **arteries and veins** are where an ophthalmologist drew them. Retinal arteries and veins look alike to an untrained eye and are told apart by calibre, colour and how they cross one another; a vessel map that cannot separate them supports none of the measurements a clinic takes from the vasculature. Three maps are scored: the arteries, the veins, and the vessels the two make together.

**Segmentation only.** A vessel width, a central retinal artery equivalent, an arteriovenous ratio, a tortuosity — every number computed *from* one of these maps by a further method — belongs to the biomarker benchmark, which takes the masks this one keeps as its input. Measuring both here would make a model's segmentation and a pipeline's arithmetic indistinguishable in one figure.

**Two scores, because neither is enough.** **Dice** is overlap with the expert's mask, 0 to 1. **clDice** asks instead how much of each network's *centreline* falls inside the other, which is a question about connectedness rather than area. The pair separates two failures that overlap alone confuses: a vessel drawn three times too wide around the same centre scores 0.50 Dice and 0.97 clDice — wrong about width, right about the network — while the same vessel thickened to one side scores the same 0.50 Dice and 0.03 clDice, its centreline no longer inside the expert's vessel at all. A break in a vessel costs both alike.

**Everything is measured in the native frame** — the full-resolution square the store built, where the annotator drew. A model working at 1024 or 1472 has its probabilities carried back there and thresholded **after** arrival, because thresholding first and resampling a binary mask throws away the boundary the score turns on.

**The outlines themselves are kept**, three images per photograph, under `.atlas_runs/av/<model>/<dataset>/`. The biomarker benchmark measures from them, and a mask whose fingerprint no longer matches its model is drawn again rather than read.

## 2. The models

| Model | Pinned at | Grid it reads | Grid it runs at | Channels it emits | Read as | Ensemble |
| --- | --- | --- | --- | --- | --- | --- |
| [automorph-artery-vein](../models/automorph-artery-vein.md) | `9a953e5e` | 1024² | 720² | background, artery, vein, crossing | artery, vein | 8 |
| [bf-net](../models/bf-net.md) | `f7de674e` | 1024² | 720² | background, artery, vein, crossing | artery, vein | one seed, trained on DRIVE_AV |
| [lunet](../models/lunet.md) | `0b0f383e` | 1472² | 1472² | vein, artery, vessels | artery, vein | 1 |
| [ocularnet](../models/ocularnet.md) | `34b1ecc3` | 1024² | 1024² | background, artery, vein, crossing | artery, vein | one model, averaged over four flips of the photograph |
| [segan-vessel](../models/segan-vessel.md) | `9a953e5e` | 1024² | 912² | vessel | vessels | 10 |
| [vascx-artery-vein](../models/vascx-artery-vein.md) | `d0cde1c7` | 1024² | 1024² | background, artery, vein, unclassified | artery, vein | one checkpoint holding several folds, with test-time flips |
| [ocularnet-nano](../models/ocularnet-nano.md) | **not measured** — its five checkpoints answer HTTP 401 and the anonymous review account that served them now holds one repository — the weights cannot be obtained at all | — | — | — | — | — |

**Two of these models do not document their channel order**, and both would have been read wrongly from a reasonable guess: LUNet puts the veins first and emits logits rather than probabilities, and VascX's fourth channel matches neither vessel. Every order here was settled the same way — by scoring each output channel against [HRF](../datasets/hrf.md)'s artery and vein annotation — including the ones the authors do name, because a documented order is still worth a measurement.

**A crossing belongs to both vessels.** Where a model emits crossings as their own class — OCULARNet, BF-Net and AutoMorph's artery/vein model all do — the adapter answers with artery *plus* crossing and vein *plus* crossing, because that is the region an annotator marked as both and a model cannot be asked to reproduce an ambiguity of projection. The two fusion models call that class *uncertainty* in their own evaluation code; scored against [HRF](../datasets/hrf.md) it is the crossings exactly, matching this repository's own crossing layer pixel for pixel.

**Two grids, because a store holds one and a network wants another.** The photographs are read at the size the store built nearest what the model was trained on, and where the network's own grid is not one of those — BF-Net and AutoMorph's artery/vein model both run at 720 — the adapter resizes down to it rather than up, so nothing is invented. The probabilities come back to the native frame either way.

**The vessel map is derived, identically for every artery/vein model**, as the union of its own artery and vein masks — not whatever vessel channel a model may also publish. LUNet publishes one; it is declared above and not used, so that every artery/vein model's vessel score means the same thing.

**One model here is the exception, and is carried as a reference rather than as a competitor.** [segan-vessel](../models/segan-vessel.md) does not separate arteries from veins, so it has no union to take and **its own vessel map is its answer**. Its artery and vein cells are left empty rather than scored as nothing — empty says it was not asked, where a zero would say it answered and was wrong — and a reader comparing its vessel score with another model's is comparing a prediction with a union.

**It is also run at a threshold this repository chose rather than inherited.** A pixel becomes vessel at **0.2** here, where its own pipeline writes its binary mask at 0.5. The lower figure keeps the thin vessels the higher one drops, which is what a reference for this column is wanted for; the cost is that every score recorded for it is a score of the model at 0.2 rather than of the model as its authors run it.

## 3. The datasets

| Dataset | Photographs | Readers | Vessel annotation | Excluded, and why |
| --- | --- | --- | --- | --- |
| [avrdb](../datasets/avrdb.md) | 100 | 1 | **drawn, but not independent**: it agrees with the union to within 0.4–0.6% | none |
| [fives](../datasets/fives.md) | 800 | 1 | **its own tracing, and the only annotation it has**: no artery/vein labels at all | none |
| [fundus-avseg](../datasets/fundus-avseg.md) | 100 | 1 | derived from the artery/vein labels by the authors | none |
| [hrf](../datasets/hrf.md) | 45 | 1 | **the same tracing**: 0.004% of pixels differ from the artery/vein union | none |
| [reyia](../datasets/reyia.md) | 559 | 1 | derived here as the union; the archive publishes no separate tracing | 4 no vessel annotation to score against |
| [les-av](../datasets/les-av.md) | **not measured** — no store built | — | — | — |
| [rav](../datasets/rav.md) | **not measured** — no store built | — | — | — |
| [rite](../datasets/rite.md) | **not measured** — no store built | — | — | — |

**The vessel annotation column is the one to read before comparing scores.** In three of these datasets the vessel map *is* the artery/vein map: Fundus-AVSeg and AVRDB derive theirs, and HRF's hand-drawn gold standard differs from the union of its artery/vein maps by 0.004% of pixels across all 45 photographs. A model's vessel score and its class scores there are **one measurement seen twice**, and their agreement is not corroboration.

**[FIVES](../datasets/fives.md) annotates vessels and neither class**, so every model is scored there on the vessel column alone and its artery and vein cells are empty for all of them. It earns its place because it is the one dataset here that the vessel reference did not train on.

[REYIA](../datasets/reyia.md) is a compilation, and its subsets are named for the collections its photographs came from — three of which this repository builds separately. Pooling a figure over REYIA and those datasets counts the same eyes twice: **fives** and **reyia** share 75 photographs.

### 3.1 What is worth fetching next, and what each would settle

| Dataset | What it would settle | Cost |
| --- | --- | --- |
| [rav](../datasets/rav.md) | 206 photographs no catalogued model names in training, from a population cohort with quality mixed on purpose — the closest thing here to a held-out test set | direct, but its host's bot gate refuses some networks |
| [les-av](../datasets/les-av.md) | 22 photographs, direct, and it completes the contamination picture for BF-Net | direct |
| [rite](../datasets/rite.md) | the 40 DRIVE photographs every artery/vein paper reports, which is what makes a number here comparable with the literature | registration |

## 4. What is excluded, and by which rule

- **Below the size floor** — a photograph whose field of view is under 512 pixels.
- **No artery/vein annotation** — a photograph the dataset published without one. Not a failure of the model, and never counted as one.
- **An annotation a finding condemns** — anything in `src/datasets/exclusions/`. REYIA has four photographs whose two published encodings of the same annotation contradict each other by more pixels than the vessel network contains; their maps are excluded and the photographs stay.
- **Excluded whole** — a dataset whose images are crops rather than photographs.

These are **ours**: the benchmark would not ask. A model's own refusal to answer is `declined`, which is a different statement, and the two are never added together.
## 5. How to run it

```bash
python -m benchmarks --benchmark av
python -m benchmarks --benchmark av --model automorph-artery-vein --dataset avrdb
python -m benchmarks --benchmark av --max-samples 20
```

`--model` and `--dataset` each take one name or a comma-separated list, and naming one of each re-measures a single pair. `--max-samples N` scores the first N photographs of each dataset — `--random-samples` chooses them at random from a recorded seed — which is for development: a sampled result says it is not complete, and a later run finishes it rather than starting again. `--force` discards what is stored and measures everything afresh.

## 6. What each column of the evidence means

`results/av/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, as the store names it |
| `subset` | the dataset's own subcollection — for REYIA, the collection the photograph came from |
| `split` | the split the dataset published, or `unspecified` |
| `reader` | which annotator the row is scored against, where a dataset keeps them apart |
| `native_side` | the side of the native square, in pixels — every score below is measured in it |
| `outcome` | `graded`, or `failed` with the reason in `note` |
| `resampling` | how the model's output reached the native frame |
| `artery_dice` | overlap with the reader's arteries, 0 to 1 — **empty** where the model or the dataset says nothing about the classes, which is not the same as a zero |
| `vein_dice` | overlap with the reader's veins, on the same terms |
| `vessels_dice` | overlap with the reader's vessels — **derived as artery ∪ vein on each side that has the two classes**, and the map itself on a side that has only vessels |
| `artery_cldice` | how much of each artery network's centreline lies inside the other's mask |
| `vein_cldice` | as above, for the veins |
| `vessels_cldice` | as above, for the vessels |
| `said_artery_px` | how many pixels the model called artery, so a score can be read beside the size of the thing scored |
| `said_vein_px` | how many it called vein |
| `truth_artery_px` | how many **this reader** drew as artery |
| `truth_vein_px` | how many as vein |
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

**Generated by `python -m benchmarks --benchmark av` on:** 2026-09-19
