# Artery and vein benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part,
what it excludes, how to run it, and what every column of its evidence means.

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark av --docs`, which measures nothing. The dataset table is read from
the stores on the machine that refreshed it. Everything else on the page is written by hand and is
never overwritten. What came out is a separate page: [av-results.md](av-results.md).

## 1. What this benchmark asks

<!-- generated: asks -->
**Which vessels are arteries and which are veins?** Each model's segmentation is compared with what an ophthalmologist drew on the same photograph — the arteries, the veins, and the vessels they make together — by overlap and by how much of the vessel network survives. Everything computed *from* a vessel map, a calibre or an arteriovenous ratio, belongs to the biomarker benchmark instead.
<!-- /generated -->

Whether a model's **arteries and veins** are where an ophthalmologist drew them. Retinal arteries
and veins look alike to an untrained eye and are told apart by calibre, colour and how they cross
one another; a vessel map that cannot separate them supports none of the measurements a clinic takes
from the vasculature. Three maps are scored: the arteries, the veins, and the vessels the two make
together.

**Segmentation only.** A vessel width, a central retinal artery equivalent, an arteriovenous ratio,
a tortuosity — every number computed *from* one of these maps by a further method — belongs to the
biomarker benchmark, which takes the masks this one keeps as its input. Measuring both here would
make a model's segmentation and a pipeline's arithmetic indistinguishable in one figure.

**Two scores, because neither is enough.** **Dice** is overlap with the expert's mask, 0 to 1.
**clDice** asks instead how much of each network's *centreline* falls inside the other, which is a
question about connectedness rather than area. The pair separates two failures that overlap alone
confuses: a vessel drawn three times too wide around the same centre scores 0.50 Dice and 0.97
clDice — wrong about width, right about the network — while the same vessel thickened to one side
scores the same 0.50 Dice and 0.03 clDice, its centreline no longer inside the expert's vessel at
all. A break in a vessel costs both alike.

**Everything is measured in the crop frame** — the full-resolution square the store built, where the
annotator drew (see [DATASETS.md](../DATASETS.md) section 5). A model working at 1024 or 1472 has
its probabilities carried back there and thresholded **after** arrival, because thresholding first
and resampling a binary mask throws away the boundary the score turns on.

**The outlines themselves are kept**, three images per photograph, under
`.atlas_runs/av/<model>/<dataset>/`. The biomarker benchmark measures from them, and a mask whose
fingerprint no longer matches its model is drawn again rather than read.

## 2. The models

<!-- generated: subjects -->
| Model | Pinned at | Grid it reads | Grid it runs at | Channels it emits | Read as | Ensemble | Took part |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [vascx-artery-vein](../models/vascx-artery-vein.md) | `d0cde1c7` | 1024² | 1024² | background, artery, vein, unclassified | artery, vein | one checkpoint holding several folds, with test-time flips | yes |
| [ocularnet](../models/ocularnet.md) | `34b1ecc3` | 1024² | 1024² | background, artery, vein, crossing | artery, vein | one model, averaged over four flips of the photograph | yes |
| [lunet](../models/lunet.md) | `0b0f383e` | 1472² | 1472² | vein, artery, vessels | artery, vein | 1 | yes |
| [automorph-artery-vein](../models/automorph-artery-vein.md) | `9a953e5e` | 1024² | 720² | background, artery, vein, crossing | artery, vein | 8 | yes |
| [bf-net](../models/bf-net.md) | `f7de674e` | 1024² | 720² | background, artery, vein, crossing | artery, vein | one seed, trained on DRIVE_AV | yes |
| [segan-vessel](../models/segan-vessel.md) | `9a953e5e` | 1024² | 912² | vessel | vessels | 10 | yes |
| [ocularnet-nano](../models/ocularnet-nano.md) | — | — | — | — | — | — | **no** — its five checkpoints answer HTTP 401 and the anonymous review account that served them now holds one repository — the weights cannot be obtained at all |
<!-- /generated -->

<!-- generated: subject_notes -->
- **segan-vessel** — does not separate arteries from veins, so its own vessel map is its answer and its artery and vein cells are left empty; a reference for the vessel column, not a competitor in it. Run at a threshold of **0.2**, where its own pipeline uses 0.5, to keep the thin vessels the higher one drops
<!-- /generated -->

**Two of these models do not document their channel order**, and both would have been read wrongly
from a reasonable guess: LUNet puts the veins first and emits logits rather than probabilities, and
VascX's fourth channel matches neither vessel. Every order here was settled the same way — by
scoring each output channel against [HRF](../datasets/hrf.md)'s artery and vein annotation —
including the ones the authors do name, because a documented order is still worth a measurement.

**A crossing belongs to both vessels.** Where a model emits crossings as their own class —
OCULARNet, BF-Net and AutoMorph's artery/vein model all do — the adapter answers with artery *plus*
crossing and vein *plus* crossing, because that is the region an annotator marked as both and a
model cannot be asked to reproduce an ambiguity of projection. The two fusion models call that class
*uncertainty* in their own evaluation code; scored against [HRF](../datasets/hrf.md) it is the
crossings exactly, matching this repository's own crossing layer pixel for pixel.

**Two grids, because an adapter reads one and a network wants another.** The photographs are read
from the crop at the grid the adapter declares, and where the network's own grid is smaller — BF-Net
and AutoMorph's artery/vein model both run at 720 and read at 1024 — the adapter resizes down to it
rather than up, so nothing is invented. The probabilities come back to the crop frame either way.

**The vessel map is derived, identically for every artery/vein model**, as the union of its own
artery and vein masks — not whatever vessel channel a model may also publish. LUNet publishes one;
it is declared above and not used, so that every artery/vein model's vessel score means the same
thing. A model that does not separate the classes at all, listed with a note above, is the
exception: its own vessel map is its answer, its artery and vein cells are left empty rather than
scored as nothing — empty says it was not asked, where a zero would say it answered and was wrong —
and a reader comparing its vessel score with another model's is comparing a prediction with a union.

## 3. The datasets

<!-- generated: material -->
| Dataset | Photographs | Readers | Vessel annotation | Excluded, and why | Available |
| --- | --- | --- | --- | --- | --- |
| [hrf](../datasets/hrf.md) | 45 | 1 | **the same tracing**: 0.004% of pixels differ from the artery/vein union | none | yes |
| [fundus-avseg](../datasets/fundus-avseg.md) | 100 | 1 | derived from the artery/vein labels by the authors | none | yes |
| [avrdb](../datasets/avrdb.md) | 100 | 1 | **drawn, but not independent**: it agrees with the union to within 0.4–0.6% | none | yes |
| [reyia](../datasets/reyia.md) | 559 | 1 | derived here as the union; the archive publishes no separate tracing | 4 no vessel annotation to score against | yes |
| [fives](../datasets/fives.md) | 798 | 1 | **its own tracing, and the only annotation it has**: no artery/vein labels at all | 2 no vessel annotation to score against | yes |
| [rav](../datasets/rav.md) | 206 | 1 | derived here as the union of the artery, vein and unknown layers; none published apart | none | yes |
| [les-av](../datasets/les-av.md) | — | — | — | — | **no** — no store built |
| [rite](../datasets/rite.md) | — | — | — | — | **no** — no store built |
<!-- /generated -->

**The vessel annotation column is the one to read before comparing scores.** In three of these
datasets the vessel map *is* the artery/vein map: Fundus-AVSeg and AVRDB derive theirs, and HRF's
hand-drawn gold standard differs from the union of its artery/vein maps by 0.004% of pixels across
all 45 photographs. A model's vessel score and its class scores there are **one measurement seen
twice**, and their agreement is not corroboration.

**[FIVES](../datasets/fives.md) annotates vessels and neither class**, so every model is scored
there on the vessel column alone and its artery and vein cells are empty for all of them. It earns
its place because it is the one dataset here that the vessel reference did not train on.

[REYIA](../datasets/reyia.md) is a compilation, and its subsets are named for the collections its
photographs came from — three of which this repository builds separately. Pooling a figure over
REYIA and those datasets counts the same eyes twice: **fives** and **reyia** share 75 photographs.

### 3.1 What is worth fetching next, and what each would settle

<!-- generated: worth_fetching -->
| Dataset | What it would settle | Cost |
| --- | --- | --- |
| [les-av](../datasets/les-av.md) | 22 photographs, direct, and it completes the contamination picture for BF-Net | direct |
| [rite](../datasets/rite.md) | the 40 DRIVE photographs every artery/vein paper reports, which is what makes a number here comparable with the literature | registration |
<!-- /generated -->

## 4. What is excluded, and by which rule

<!-- generated: exclusions -->
- **Below the size floor** — a photograph whose field of view is under 512 pixels, measured on the field's own size rather than the frame's
- **No artery/vein annotation** — a photograph the dataset published without one. Not a failure of the model, and never counted as one
- **An annotation a finding condemns** — anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a store. The map is excluded and the photograph stays
- **Excluded whole** — a dataset whose images are crops rather than photographs. No size floor catches that, because a crop can be large
<!-- /generated -->

REYIA has four photographs whose two published encodings of the same annotation contradict each
other by more pixels than the vessel network contains; their maps are excluded by a recorded
finding and the photographs stay.

These are **ours**: the benchmark would not ask. A model's own refusal to answer is `declined`,
which is a different statement, and the two are never added together.

## 5. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark av
python -m benchmarks --benchmark av --model vascx-artery-vein --dataset hrf
python -m benchmarks --benchmark av --max-samples 20
python -m benchmarks --benchmark av --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one model, or several separated by commas |
| `--dataset` | one dataset, or several separated by commas; one of each re-measures a pair |
| `--device` | cuda, mps or cpu; the fastest available by default |
| `--batch` | how many photographs go to the model at once; 1 by default |
| `--max-samples` | score at most the first N photographs of each dataset, for development; a sampled result says it is not complete, and a later run finishes it |
| `--random-samples` | choose those photographs at random rather than first |
| `--seed` | the seed a random sample uses, recorded in the run |
| `--data-root` | read the stores from somewhere other than `.atlas_data/` |
| `--force` | discard what is stored and measure it all again |
| `--rescore` | measure the kept masks afresh without running any model — for a new measurement of the same masks |
| `--no-report` | skip refreshing `docs/BENCHMARKS.md` after the run |
| `--config` | print what this benchmark reports about itself, as JSON, measuring nothing |
| `--docs` | refresh this page from that JSON, measuring nothing |
<!-- /generated -->

## 6. What each column of the evidence means

<!-- generated: columns -->
`results/av/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, as the store names it |
| `subset` | the dataset's own subcollection — for REYIA, the collection the photograph came from |
| `split` | the split the dataset published, or `unspecified` |
| `reader` | which annotator the row is scored against, where a dataset keeps them apart |
| `crop_side` | the side of the crop square, in pixels — every score below is measured in it |
| `outcome` | `graded`, or `failed` with the reason in `note` |
| `resampling` | how the model's output reached the crop frame |
| `artery_dice` | overlap with the reader's arteries, 0 to 1 — **empty** where the model or the dataset says nothing about the classes, which is not the same as a zero |
| `vein_dice` | overlap with the reader's veins, on the same terms |
| `vessels_dice` | overlap with the reader's vessels — **derived as artery ∪ vein on each side that has the two classes**, and the map itself on a side that has only vessels |
| `artery_cldice` | how much of each artery network's centreline lies inside the other's mask |
| `vein_cldice` | as above, for the veins |
| `vessels_cldice` | as above, for the vessels |
| `artery_betti` | **Betti matching error** for the arteries: how many topological features — connected components and loops — of either map have no counterpart in the other. 0 is perfect; unlike Dice and clDice it counts upwards and has no ceiling |
| `vein_betti` | as above, for the veins |
| `vessels_betti` | as above, for the vessels |
| `said_artery_px` | how many pixels the model called artery, so a score can be read beside the size of the thing scored |
| `said_vein_px` | how many it called vein |
| `truth_artery_px` | how many **this reader** drew as artery |
| `truth_vein_px` | how many as vein |
| `note` | what the model failed with |
<!-- /generated -->

A model that has no opinion to record leaves a column **absent** rather than blank, and none is
invented for it.

***The Betti matching error is not normalised, and is not suitable for comparison between datasets
— only between models on the same dataset.*** It counts features rather than scoring a fraction,
and the count rises with the length of the vessel network, which is a property of the frame and of
the annotation rather than of the model. Measured on the readers' own tracings, the count runs at
about 0.39 of the centreline length in pixels in every dataset here, so HRF's 3,269-pixel frames
carry six times AVRDB's figure before any model is asked anything.

## 7. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- the facts each model declares that bear on its numbers: slug, purpose, grid, network_grid, structures, channels, emits_probabilities, resampling, threshold, ensemble
- the sha256 of the weights actually loaded
- the store's slug and builder version
- this benchmark's name, `VERSION` (2) and size floor (512 pixels)
- the first three alone also name the masks kept under `.atlas_runs/av/<model>/<dataset>/`, so `--rescore` measures them afresh without running a model, and a mask its model no longer agrees with is drawn again

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any photograph scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

## 8. The counts every result carries

<!-- generated: counts -->
| Count | What it answers |
| --- | --- |
| `processed` | how many photographs this model has actually scored |
| `total` | how many the benchmark would ask about, after the exclusions |
| `excluded` | how many those exclusions removed, by reason; `total + excluded` is what the store holds |
| `seconds_per_photograph` | how long the model's own call took per photograph, on the device the result names — not part of the fingerprint |
| `timed_photographs` | how many photographs that timing covers |
<!-- /generated -->

`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is either one the
benchmark asks about or one it excluded, never both and never neither. The timing covers the model's
own call and nothing around it, and leaves out the batch that loaded the weights whenever there is
another to average over.
