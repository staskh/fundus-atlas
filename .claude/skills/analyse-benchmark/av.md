# Analysing the artery/vein benchmark

Load this beside `SKILL.md` when changing `notebooks/av.ipynb`. The model is the primary index
throughout; the dataset, the reader and the structure sit inside it.

## 1. The sections, in order

| # | Section | Must show |
| --- | --- | --- |
| 1 | Coverage | what each model produced a segmentation for, and what it failed on |
| 2 | Overlap | Dice per structure, pooled and then per dataset — briefly, and never alone |
| 3 | Connectedness | clDice beside Dice, and **where the two disagree**, which is section 3 below |
| 4 | Artery against vein | whether a model's mistakes are about finding vessels or about naming them |
| 5 | Against the readers | the ceiling, where a dataset publishes more than one annotator |
| 6 | Model against model | agreement on the same photographs, and where it is not evidence |
| 7 | The hard cases | segmentations drawn over the photograph, up to eight per dataset, labelled |
| 8 | What each model costs | seconds per photograph, beside the device |
| 9 | What this cannot say | contamination, derived ground truths, resampling |

## 2. Dice and clDice are read together or not at all

Plot them **against each other**, one point per photograph, with the diagonal drawn. The interesting
photographs are off it:

- **high Dice, low clDice** — the model covered the vessels and lost the network: broken strands, a
  centreline displaced by asymmetric thickening;
- **low Dice, high clDice** — it traced the right network at the wrong width, which is what a
  calibre biomarker will feel and a topology one will not.

A model's mean of each is two numbers; the shape of that scatter is the finding. Say which failure
each model tends towards, because that is what decides whether it suits a width measurement or a
connectivity one.

## 3. Artery against vein is the question this benchmark exists for

A vessel map alone cannot be got wrong in the way an artery/vein map can. Show, per model:

- **the vessel score beside the two class scores.** Where `vessels` is high and `artery`/`vein` are
  low, the model finds vessels and cannot tell them apart — a different failure from missing them;
- **how much of the disagreement is swapping.** The share of the expert's artery pixels the model
  called vein, and the reverse. A model that swaps a whole branch is not making small errors, and
  an arteriovenous ratio computed from it is wrong in a way no overlap number reveals;
- **crossings separately**, where the ground truth marks them: they are annotated as both, so a
  model cannot be wrong there, and including them flatters every score a little.

## 4. The ground truths are not independent of each other

Three of the built datasets derive their vessel annotation from their artery/vein annotation, and
[HRF](../../docs/datasets/hrf.md)'s hand-drawn gold standard turns out to *be* its artery/vein map —
they differ by 0.004% of pixels. So a model's vessel Dice and its artery/vein Dice on those datasets
are one measurement seen twice. Say so wherever both are shown, and never present their agreement as
corroboration.

## 5. Where the same eyes appear twice

[REYIA](../../docs/datasets/reyia.md) is a compilation: its subsets are named for the collections
its photographs came from, and three of those — GRAPE, PAPILA, FIVES — are built here in their own
right. **A pooled number over REYIA and its sources counts those eyes twice.** Group by subset, say
which subsets overlap which datasets, and never average across the two without saying it.

## 6. What this analysis must not conclude

- That a model is best because its Dice is highest, without saying what its clDice does.
- That a vessel score and an artery/vein score on one of these datasets agree, when they are the
  same annotation measured twice.
- That a model beat the annotators, on a dataset whose annotators disagree with each other by more
  than the model disagrees with them.
- Anything about calibre, ratio or tortuosity. Those are the biomarker benchmark's, computed from
  the masks this one kept.
