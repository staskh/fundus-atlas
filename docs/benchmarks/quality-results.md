# Quality benchmark — results

Five models were asked, of 4,079 photographs, the question a quality gate exists to answer: is this
one good enough to measure? Their answers are compared here with the grade the dataset's own
readers gave. Every number comes from `results/quality/`; the reading of them comes from
[notebooks/quality.ipynb](../../notebooks/quality.ipynb). How the benchmark is configured is a
separate page: [quality-docs.md](quality-docs.md).

**5 of 5 declared models** and **4 of 6 declared datasets** took part. EyeQ and DRIMDB are declared
and not yet fetched.

*Measured again on 2026-10-15 on FIVES, FQS and MSHF, whose stores were rebuilt at builder version
7, and every figure on this page refreshed from the notebook. Most moved by a hundredth or less;
QuickQual's κ on FIVES rose from 0.471 to 0.500, which widens its pooled lead over VascX from five
thousandths to sixteen. Two statements that did not match the notebook before this run are
corrected where they stand (sections 4.3 and 4.4).*

## Contents

1. [Summary](#1-summary)
2. [Which mistake each model makes](#2-which-mistake-each-model-makes)
3. [Dataset by dataset](#3-dataset-by-dataset)
4. [What the analysis found](#4-what-the-analysis-found)
5. [Which model to use](#5-which-model-to-use)
6. [What these numbers do not say](#6-what-these-numbers-do-not-say)

## 1. Summary

Every dataset in one table, one row per model. The three graded datasets —
[FIVES](../datasets/fives.md), [FQS](../datasets/fqs.md), [MSHF](../datasets/mshf.md), 3,591
photographs — are pooled into the accuracy and κ columns.
[PAPILA](../datasets/papila.md) has its own column because its reference is **assumed**, not
published: every one of its 488 photographs is taken as sound, so there is nothing there to be
right about and what a model does with it is a keep-rate, not an accuracy.

| Model | Coverage | Accuracy | Cohen's κ | PAPILA kept | Marked |
| --- | --- | --- | --- | --- | --- |
| [quickqual](../models/quickqual.md) | 1.000 | 0.847 | **0.679** | 0.424 | out-of-sample |
| [vascx-quality](../models/vascx-quality.md) | 1.000 | **0.852** | 0.663 | 0.555 | out-of-sample |
| [automorph-quality-grader](../models/automorph-quality-grader.md) | 1.000 | 0.840 | 0.646 | 0.391 | out-of-sample |
| [quickqual-meme](../models/quickqual-meme.md) | 1.000 | 0.769 | 0.546 | 0.527 | out-of-sample |
| [fit-quality](../models/fit-quality.md) | 1.000 | 0.739 | 0.506 | 0.279 | out-of-sample |

**Accuracy and κ are read together.** Accuracy flatters a model on a dataset where one class
dominates — a grader that keeps everything scores well on a collection that is mostly gradeable
while agreeing with nobody about anything. Cohen's κ is what is left after chance agreement is
taken out. Where the two disagree, κ is the one to believe.

**Coverage is 1.000 everywhere**: none of these models declines a photograph on its own judgement.
Where a pipeline refuses one, that refusal belongs to the pipeline, and this benchmark runs the
models without the pipelines around them.

## 2. Which mistake each model makes

The summary hides the thing that matters most. Two models within a hundredth of each other on
accuracy can be doing opposite things, and a study feels the difference as either a lost sample or
unusable measurements.

Pooled over the three graded datasets:

| Model | Of the photographs readers called worth measuring, kept | Of the rest, discarded |
| --- | --- | --- |
| vascx-quality | **0.959** | 0.668 |
| automorph-quality-grader | 0.908 | 0.722 |
| quickqual | 0.846 | 0.848 |
| quickqual-meme | 0.688 | 0.910 |
| fit-quality | 0.604 | **0.972** |

Read the two columns against each other. **VascX keeps almost every usable photograph and lets a
third of the unusable ones through. The Fundus Image Toolbox ensemble does the reverse: it lets
almost nothing bad past and throws away two usable photographs in five.** QuickQual is the only one
of the five that is close to balanced.

Neither end is wrong in itself — it depends which costs you more — but neither is visible in an
accuracy column, which is why this section comes before the per-dataset detail.

## 3. Dataset by dataset

| Model | FIVES | FQS | MSHF | PAPILA |
| --- | --- | --- | --- | --- |
| | acc / κ | acc / κ | acc / κ | kept |
| quickqual | 0.859 / 0.500 | 0.824 / 0.640 | 0.923 / 0.843 | 0.424 |
| vascx-quality | 0.935 / 0.672 | 0.806 / 0.578 | 0.919 / 0.837 | 0.555 |
| automorph-quality-grader | 0.854 / 0.497 | 0.815 / 0.602 | 0.921 / 0.839 | 0.391 |
| quickqual-meme | 0.715 / 0.304 | 0.773 / 0.554 | 0.832 / 0.652 | 0.527 |
| fit-quality | 0.576 / 0.185 | 0.793 / 0.598 | 0.756 / 0.484 | 0.279 |

No model has seen any of these four datasets in training, so far as their pages state. VascX's
quality model is among them: its paper names EyeQ as its only training set, which matches what its
own checkpoint names.

### 3.1 By camera and split

MSHF is two kinds of camera, and they are not interchangeable — 245 tabletop photographs and 301
from handhelds, which the store keeps as two subsets, `local1` and `local2`, after the two folders
the deposit publishes them in; they are read together here. Accuracy and κ per kind of camera:

| Model | tabletop (cfp) | handheld (portable) | κ lost to the handheld |
| --- | --- | --- | --- |
| vascx-quality | 0.959 / κ 0.905 | 0.887 / κ 0.711 | 0.195 |
| automorph-quality-grader | 0.955 / κ 0.901 | 0.894 / κ 0.708 | 0.193 |
| quickqual | 0.943 / κ 0.876 | 0.907 / κ 0.750 | 0.125 |
| quickqual-meme | 0.747 / κ 0.521 | 0.900 / κ 0.749 | **−0.228** |
| fit-quality | 0.722 / κ 0.483 | 0.784 / κ 0.286 | 0.197 |

Three of the five lose about 0.19 of κ on the handheld camera, which is the largest single effect
in this benchmark and is invisible in MSHF's dataset-level row. **QuickQual-MEME runs the other
way**, scoring markedly better on the handheld group than on the tabletop one — the only model that
does, and not something this benchmark can explain.

FIVES's own train and test halves agree closely for every model — within about 0.05 of accuracy and
0.04 of κ — so its split is not doing any work here. FQS publishes no split.

## 4. What the analysis found

From [notebooks/quality.ipynb](../../notebooks/quality.ipynb) and
[notebooks/quality-humans.ipynb](../../notebooks/quality-humans.ipynb).

### 4.1 Blur costs a photograph more than illumination does

FIVES publishes three binary component scores rather than one grade, so it can say **which defect a
model reacts to**. The share each model keeps, by what is wrong with the photograph:

| illumination & contrast | blur | low contrast | photographs | vascx | automorph | quickqual | meme | toolbox |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sound | sound | sound | 592 | 0.992 | 0.944 | 0.938 | 0.782 | 0.637 |
| **bad** | sound | sound | 76 | 0.921 | 0.421 | 0.592 | 0.368 | 0.039 |
| sound | **bad** | sound | 51 | 0.549 | 0.294 | 0.235 | 0.000 | 0.000 |
| bad | bad | sound | 46 | 0.391 | 0.087 | 0.130 | 0.000 | 0.000 |
| two or three defects | | | 35 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

Every model treats blur as more disqualifying than poor illumination, and every model discards
everything with two defects. They differ on the single-defect photographs, which is where a gate
earns its keep: VascX keeps 92% of the badly-illuminated ones, the toolbox ensemble keeps 4%.

### 4.2 Models that learned from the same labels agree with each other

QuickQual, QuickQual-MEME and the AutoMorph grader were all fitted on EyeQ's labels. On the graded
datasets, AutoMorph's grader and VascX agree on **0.919** of photographs and AutoMorph's grader and
QuickQual on 0.862, while the toolbox ensemble — trained on DeepDRiD and DRIMDB instead — sits apart
from everything at 0.654 to 0.835. Agreement among models fitted on one set of labels is not independent evidence.

On PAPILA the whole matrix flattens to 0.70–0.87 and the toolbox ensemble moves **towards** the
others. Where there is no quality to judge, what separates these models disappears.

### 4.3 Models fail where the readers failed

MSHF and FQS kept their readers apart, so the photographs the readers themselves disagreed about
can be separated from the ones they were sure of. Where all three readers agreed, every model is
right 0.87 to 0.92 of the time on FQS and 0.78 to 0.95 on MSHF; where they did not, 0.67 to 0.76
on FQS and 0.36 to 0.57 on MSHF. *This page said 0.87 to 0.95 and 0.36 to 0.57 for both datasets
together, which covered neither the toolbox ensemble on MSHF (0.778) nor any model on FQS's
unsettled photographs.*

That matters for how a score is read: a model marked wrong on a photograph its own readers could
not settle is in different trouble from one marked wrong on an easy photograph.

### 4.4 The references are not equally firm

[notebooks/quality-humans.ipynb](../../notebooks/quality-humans.ipynb) measures what the grades are
worth. On the two-class question this benchmark asks, FQS's three graders agree with each other at
**κ 0.486 – 0.626**, and MSHF's three annotators at **κ 0.857 – 0.877**.

Against those bands: on FQS four of the five models sit inside the human range and QuickQual
(0.640) sits above the best human pair — matching a committee whose members disagree with each
other more than the model disagrees with their vote. On MSHF **no model has reached the human
floor** (best 0.843 against 0.857), so there is real room there and none on FQS.

### 4.5 Every model rejects most of a curated dataset

On PAPILA — 488 disc-centred photographs, every one outlined by two ophthalmologists — the share
kept runs from 0.279 to 0.555. The black bands of its square crop are not the cause: trimming them
and handing the model the photograph's own rectangle instead makes the rejection *worse*, because
the square is the familiar shape for models fitted on screening photographs.

### 4.6 A model's score does not mean the same thing on two datasets

Every model's ability to *order* photographs looks better one dataset at a time than it does across
all three at once. Averaging each dataset's own area under the ROC curve, against computing it over
the 3,591 photographs pooled:

| Model | Averaged per dataset | Pooled over all three | Lost |
| --- | --- | --- | --- |
| automorph-quality-grader | 0.962 | 0.924 | **0.038** |
| fit-quality | 0.965 | 0.940 | 0.025 |
| quickqual | 0.955 | 0.934 | 0.021 |
| quickqual-meme | 0.937 | 0.914 | 0.023 |
| vascx-quality | 0.954 | **0.941** | **0.013** |

The pooled figure is the harder and more useful test: it asks whether a confidence of 0.6 means the
same thing on FIVES as on MSHF. For every model it does not, and the ordering changes — averaged per
dataset, **fit-quality** ranks best; pooled, **vascx-quality** does, with fit-quality one
thousandth behind and the two indistinguishable.

That is the same fact as section 2 seen from another angle. A model whose scores shift between
collections cannot carry one threshold across them, which is exactly why fit-quality's published
threshold discards two usable photographs in five here. **The index in
[docs/BENCHMARKS.md](../BENCHMARKS.md) quotes the pooled figures**, so its "at ordering
photographs" line names vascx-quality where an earlier version of this page named fit-quality; both
numbers are above, and neither model is clearly ahead of the other at it.

## 5. Which model to use

**QuickQual**, for a general-purpose gate — and **VascX quality** is within two hundredths of it on
κ and ahead of it on accuracy, so the choice between them is about which mistake you would rather
make than about which is better.

- **QuickQual** has the highest agreement beyond chance (κ 0.679) and is the only model here that is
  close to balanced: it keeps 0.846 of the usable photographs and discards 0.848 of the unusable.
  It is `out-of-sample` on all four datasets, it is small and fast — 0.04 seconds a photograph on
  Apple MPS — and its licence is **not stated** — which is the reason to check before shipping it, not a reason against measuring it.
- **VascX quality** has the highest accuracy (0.852) and κ 0.663, 0.016 behind. It keeps
  0.959 of usable photographs, at 0.07 seconds a photograph, so it is the choice where losing a photograph costs more than
  measuring a bad one. It is `out-of-sample` here — its paper names EyeQ alone — so its lead is a
  clean one. The caveat is its licence: its weights are AGPL-3.0.
- **AutoMorph's grader** is a close third (κ 0.646) and behaves like VascX, keeping 0.908 and
  discarding 0.722. If you are already running AutoMorph, there is no measured reason here to
  replace it.
- **The toolbox ensemble** should not be used at its published threshold: it discards two usable
  photographs in five. It ranks photographs about as well as anything here — its area under the ROC
  curve is 0.94 to 0.98 within a dataset, though 0.940 once the datasets are pooled (section 4.6) —
  so **re-fit the threshold on your own images**, on images from your own cameras, and it becomes a
  different proposition.
- **QuickQual-MEME** is the one to avoid unless you need its size: it is strictly behind its own
  three-class sibling on every dataset, for the same backbone and one extra matrix multiply.

None of this survives a change of question. A gate in front of a disc-and-cup pipeline on
disc-centred photographs should read section 4.5 first, where every model discards most of PAPILA.

## 6. What these numbers do not say

- **Every model here is marked from a published training list**, so none of these results is
  `unknown`; all five are `out-of-sample` on all four datasets.
- **The three references are different statements.** FQS's grade is its own, FIVES's is derived by
  this repository from three component scores, PAPILA's is assumed. A model measured against a
  derived grade is measured against that rule as much as against the dataset.
- **An assumed reference measures what a model discards**, not whether it is right.
- **A pooled number is an average over four collections** with different cameras, different
  populations and different graders. Section 3 is where it comes apart.
- **Coverage is 1.000 because these models are run without their pipelines.** What a pipeline would
  carry into measurement is a different question, answered in [quality-docs.md](quality-docs.md)
  §2.1.
- **Nothing here is a claim about clinical usefulness.** Every number is agreement with a grade some
  readers wrote down, and section 4.4 says how much those grades are worth.

---

**Compiled from `notebooks/quality.ipynb` on:** 2026-10-15 · **Measured by**
`python -m benchmarks --benchmark quality`
