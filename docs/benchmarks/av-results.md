# Artery and vein benchmark — results

Six models were asked, of 1,602 photographs, to find the blood vessels in the retina, and five of
them to say which are **arteries** and which are **veins** — **9,612 scored segmentations in all**.
Their answers are compared here with what an ophthalmologist drew on the same photograph, by three
measurements: how much of the area they agree on, how much of each network's centreline lies inside
the other, and how many topological features of either have no counterpart in the other.

Every number comes from `results/av/`; the reading of them comes from
[notebooks/av.ipynb](../../notebooks/av.ipynb). How the benchmark is configured is a separate page:
[av-docs.md](av-docs.md).

**6 of 7 declared models** and **5 of 8 declared datasets** took part. OCULARNet-nano is declared and
not measured: its weights answer HTTP 401 and cannot be obtained at all. RAV, LES-AV and RITE are
declared and not yet fetched — RITE above all, since the 40 DRIVE photographs it carries are what
every artery/vein paper reports.

*This page previously said that nothing had been measured yet, and listed what was ready and what
was not. Both of those sections have gone: the run they were waiting for has happened.*

## Contents

1. [Summary](#1-summary) · [1.1 The vessel reference](#11-the-vessel-reference)
2. [Where overlap and connectedness disagree](#2-where-overlap-and-connectedness-disagree)
   · [2.1 What topology says that neither of them says](#21-what-topology-says-that-neither-of-them-says)
3. [Telling arteries from veins](#3-telling-arteries-from-veins)
   · [3.1 How much of it is swapping](#31-how-much-of-it-is-swapping)
4. [Dataset by dataset](#4-dataset-by-dataset)
   · [4.1 AVRDB, where every model fails at once](#41-avrdb-where-every-model-fails-at-once)
   · [4.2 FIVES, and the annotations nobody drew](#42-fives-and-the-annotations-nobody-drew)
5. [What the models agree about](#5-what-the-models-agree-about)
6. [Which model to use](#6-which-model-to-use)
7. [What these numbers do not say](#7-what-these-numbers-do-not-say)

## 1. Summary

All five datasets pooled, one row per model. **Dice** measures overlap with what the annotator
drew, from 0 to 1. **clDice** asks the connectedness question instead — how much of each network's
*centreline* falls inside the other's mask — so a model can score well on one and badly on the
other, which is why both are carried.

| Model | Photographs | Coverage | Artery Dice | Vein Dice | Vessels Dice | Vessels clDice | Vessels Betti | Seconds each | Marked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ocularnet](../models/ocularnet.md) | 1,602 | 1.000 | **0.829** | **0.853** | **0.854** | **0.884** | 97 | 2.6 | unknown |
| [lunet](../models/lunet.md) | 1,602 | 1.000 | 0.778 | 0.804 | 0.838 | 0.864 | **57** | 20.0 | unknown |
| [segan-vessel](../models/segan-vessel.md) | 1,602 | 1.000 | — | — | 0.832 | 0.862 | **172** | 1.9 | mixed |
| [vascx-artery-vein](../models/vascx-artery-vein.md) | 1,602 | 1.000 | 0.752 | 0.789 | 0.804 | 0.829 | 157 | 11.1 | unknown |
| [automorph-artery-vein](../models/automorph-artery-vein.md) | 1,602 | 1.000 | 0.708 | 0.774 | 0.747 | 0.757 | 104 | 3.5 | mixed |
| [bf-net](../models/bf-net.md) | 1,602 | 1.000 | 0.491 | 0.601 | 0.614 | 0.625 | 162 | **0.4** | out-of-sample |

***The Betti matching error is not normalised, and is not suitable for comparison between
datasets — only between models on the same dataset.*** Measured on the readers' own tracings, the
count runs at about 0.39 of the centreline length in pixels in every dataset here, so a dataset's
figures say as much about its frame size and how finely it was traced as about any model. HRF's
3,269-pixel frames carry roughly six times AVRDB's count before a model is asked anything.

**The Betti column counts downwards and the others count upwards.** **Betti matching error** is how
many topological features — connected components and loops — of either map have no counterpart in
the other, after the two maps' features have been paired by where they lie. 0 is perfect, there is
no ceiling, and the figure quoted is the **median** because a count with no ceiling has a tail that
drags a mean wherever the worst photograph went. It is **a count, not a fraction**: it is compared
between models on one dataset, never between datasets, since a bigger frame with a denser
annotation has more features to leave unmatched (section 4).

**It reorders the table.** LUNet is second on overlap and first on topology by a wide margin, 57
against OCULARNet's 97; the vessel reference is third on overlap and **last** on topology. Within a
dataset the two measurements are close to independent — per photograph, Dice and Betti correlate
+0.04 on AVRDB and −0.01 on FIVES, and only −0.25 to −0.40 on the other three — so a model's
overlap tells you little about whether its vessel network is in one piece.

**The artery and vein columns cover 804 photographs, not 1,602.** [FIVES](../datasets/fives.md)
annotates vessels and neither class, so no model is scored on arteries or veins there. The vessel
columns cover all five datasets.

**Coverage is 1.000 everywhere.** Every model produced a segmentation for every photograph it was
asked about, and none of the 9,612 failed. Six photographs were set aside by the benchmark for
having nothing to score against — four in REYIA, two in FIVES (section 4.2) — which is ours and not
a model's failure.

**The seconds are photograph-weighted here**, and for one model that matters. The index page
[BENCHMARKS.md](../BENCHMARKS.md) averages the five per-dataset figures instead, which lets HRF's 45
photographs weigh as much as REYIA's 559; VascX costs 54.3 seconds a photograph on HRF and 9.3 on
FIVES, so the index reports 19.9 seconds against the 11.1 above. Both are right about different
questions. Measured on Apple MPS, except LUNet, which runs on the CPU through TensorFlow because its
checkpoint is a Keras 2.11 file.

**A mean hides a tail.** The share of photographs a model loses outright separates models that look
close in the table:

| Model | Vessels maps under Dice 0.5 | Artery maps | Vein maps |
| --- | --- | --- | --- |
| ocularnet | **0.5%** | 0.8% | 0.1% |
| segan-vessel | 1.2% | — | — |
| lunet | 1.3% | 10.0% | 5.5% |
| vascx-artery-vein | 1.4% | 5.0% | 1.2% |
| automorph-artery-vein | 7.9% | 11.3% | 2.7% |
| bf-net | 19.9% | 42.8% | 17.2% |

### 1.1 The vessel reference

**[segan-vessel](../models/segan-vessel.md) is not a competitor in this benchmark; it is a
reference for one column of it.** It is the vessel stage of AutoMorph — the masks that pipeline's
own biomarkers are computed from — and it does not separate arteries from veins. Three things
follow, and every table above is already written to respect them:

- **Its artery and vein cells are empty, not zero.** Empty says it was never asked; a zero would
  say it answered and was wrong.
- **Its vessel map is its own prediction.** Every other row's vessel column is *derived*, as the
  union of that model's arteries and veins, which is what makes the column mean one thing across
  the artery/vein models. It cannot take part in that derivation, so comparing its 0.832 with
  ocularnet's 0.854 is comparing a prediction with a union.
- **It is run at a threshold this repository chose.** A pixel becomes vessel at **0.2** here, where
  AutoMorph's own pipeline writes its binary masks at **0.5**. The lower figure keeps thin vessels
  the higher one drops. Every score recorded for it is therefore a score of the model at 0.2, and
  **no sweep measured what that is worth per dataset** — section 7.

**The topology column is where that choice shows.** The vessel reference is third of six on overlap
and **sixth of six on unmatched features**, on every dataset, by a margin — 172 against LUNet's 57
pooled. A low threshold keeps thin, uncertain fragments, and a fragment that answers nothing in the
reader's tracing is exactly what this metric counts. That is consistent with the threshold being
the cause and does not prove it: the sweep that would settle it was not run. Read as a statement
about the model as its authors ship it, at 0.5, none of these topology figures applies.

## 2. Where overlap and connectedness disagree

The two metrics separate failures that overlap alone confuses. A vessel drawn three times too wide
around the same centre scores 0.50 Dice and 0.97 clDice — wrong about width, right about the
network. The same vessel thickened to one side scores the same 0.50 Dice and 0.03 clDice.

| Model | Median clDice − Dice | Traced, not covered (gap > +0.05) | Covered, not traced (gap < −0.05) |
| --- | --- | --- | --- |
| lunet | +0.031 | **30.9%** | 1.0% |
| ocularnet | +0.030 | 23.8% | **0.2%** |
| segan-vessel | +0.026 | 25.2% | 0.8% |
| vascx-artery-vein | +0.024 | 23.0% | 1.4% |
| bf-net | +0.011 | 9.7% | 4.7% |
| automorph-artery-vein | +0.008 | 9.7% | 3.3% |

**Every model sits above the diagonal on average**, and the four strongest sit well above it: on a
quarter to a third of photographs they trace a network the annotator would recognise at a width the
annotator would not. That is the failure a calibre measurement feels and a connectivity measurement
does not.

**The two weakest models are the two least often above it**, which is not a virtue. BF-Net and
AutoMorph's artery/vein model have the smallest median gaps because they lose *both* — they are
below the diagonal four to five times as often as OCULARNet, covering vessel area while losing the
network, which is the worse trade: a broken network cannot be repaired by rescaling.

**OCULARNet almost never loses the network** — 0.2%, a quarter of the next model's rate.

*What this suggests for the biomarker benchmark, and does not settle here:* a model that traces the
right network at the wrong width carries that width into every calibre, and into any arteriovenous
ratio computed from it. Whether it cancels in a ratio of two widths is exactly what the biomarker
benchmark exists to measure.

### 2.1 What topology says that neither of them says

Dice and clDice both measure agreement pixel by pixel; neither counts *features*. A vessel broken
in two is one component where the reader drew one — in this repository's own test case a break of
two pixels in seventy-two costs 0.03 of Dice and one whole unmatched feature — and a loop a model
invents is a hole nobody asked for.

| Model | Median | Mean | 75th percentile | 95th percentile | Worst photograph |
| --- | --- | --- | --- | --- | --- |
| lunet | **57** | **67** | **73** | **108** | 1,641 |
| ocularnet | 97 | 107 | 122 | 185 | 1,716 |
| automorph-artery-vein | 104 | 125 | 138 | 247 | 1,896 |
| vascx-artery-vein | 157 | 172 | 197 | 282 | 1,821 |
| bf-net | 162 | 167 | 195 | 257 | 1,753 |
| segan-vessel | 172 | 186 | 215 | 304 | 1,759 |

**The mean is the column the index quotes**, because a mean over photographs pools exactly and a
median does not: a median of five per-dataset medians is not the median of the photographs. Both
orderings are the same, and the mean is the higher of the two everywhere, which is the tail showing.
The rest of this page uses medians.

**LUNet's lead is not a hundredth or two.** Its median photograph leaves 57 features unmatched where
OCULARNet's leaves 97 and the vessel reference's 172, and its 95th percentile — 108 — is below every
other model's *median but one*. It is also the model that most often traces the right network at the
wrong width (section 2), which is the same fact from the other side: it keeps the network and
misses on calibre.

**Every model has the same worst case.** The maximum is between 1,641 and 1,896 for all six, on the
photographs of section 5 — where a sparse or absent annotation leaves hundreds of the *reader's*
features unmatched no matter what the model drew. That is the tail a mean would hide, and the reason
the median leads this table.

## 3. Telling arteries from veins

Five models answer this; the vessel reference does not. Where `vessels` is high and `artery` and
`vein` are low, a model **finds the vessels and cannot name them**.

| Model | Vessels Dice | Artery Dice | Vein Dice | Cost of naming them |
| --- | --- | --- | --- | --- |
| ocularnet | 0.854 | 0.829 | 0.853 | 0.012 |
| lunet | 0.838 | 0.778 | 0.804 | 0.047 |
| vascx-artery-vein | 0.804 | 0.752 | 0.789 | 0.033 |
| automorph-artery-vein | 0.747 | 0.708 | 0.774 | **0.006** |
| bf-net | 0.614 | 0.491 | 0.601 | 0.068 |

**Read the last column with the first.** AutoMorph's 0.006 is the smallest cost of naming here and
does not make it the best namer: it pays little because its vessel score is already low, so there
is little left to lose. OCULARNet pays 0.012 from 0.854, which is the number that matters.

**LUNet finds the vessels nearly as well as OCULARNet and names them less well** — 0.838 against
0.854 on vessels, but 0.051 behind on arteries. What it loses is the label, not the vessel.

**Every model is better at veins than at arteries**, by 0.024 (OCULARNet) to 0.110 (BF-Net). Veins
are wider and darker; the arteriole is where the disagreement lives, and the arteriole is what a
calibre biomarker is usually after.

**Topology says the same thing about the classes, and more sharply.** Median unmatched features per
photograph, arteries against veins:

| Model | Artery Betti | Vein Betti |
| --- | --- | --- |
| lunet | **28** | **29** |
| ocularnet | 43 | 47 |
| automorph-artery-vein | 51 | 61 |
| bf-net | 72 | 94 |
| vascx-artery-vein | 73 | 81 |

Each class is a sparser network than the two together, so the counts are smaller than the vessel
column's and the ordering is the same: LUNet keeps the most of each network in one piece, and the
two fusion-based models and VascX shed the most of it.

### 3.1 How much of it is swapping

Read from the masks the run kept, on a sample of 12 photographs from each of the four datasets that
annotate the classes — 48 per model.

| Model | Expert's artery called vein | Expert's vein called artery | Expert's artery found at all |
| --- | --- | --- | --- |
| vascx-artery-vein | **2.9%** | **2.7%** | 68.5% |
| ocularnet | 5.3% | 4.0% | **80.8%** |
| automorph-artery-vein | 5.8% | 4.6% | 68.5% |
| lunet | 6.5% | 9.7% | 73.6% |
| bf-net | 11.6% | 7.0% | 55.6% |

**Most of the disagreement is missing, not swapping.** OCULARNet finds 81% of the expert's artery
pixels and calls 5% of them vein; the remaining ~14% it does not mark as vessel at all. The
"found at all" column is always much further from 1 than the swap columns are from 0.

**VascX swaps least and sees least** — under 3% either way, and twelve points below OCULARNet on
finding arteries at all. **LUNet is the one that swaps asymmetrically**, calling 9.7% of veins
artery against 6.5% the other way; a ratio computed from a model that leans one direction is biased
rather than noisy.

**Crossings flatter every score a little.** Where an artery crosses a vein the pixel is annotated as
both, so either answer is right: 4.4% of HRF's vessel pixels, 2.1% of AVRDB's, 2.0% of REYIA's,
1.7% of Fundus-AVSeg's.

## 4. Dataset by dataset

**Vessels Dice**

| Model | avrdb | fives | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- | --- |
| ocularnet | **0.726** | 0.848 | **0.904** | 0.797 | 0.879 |
| segan-vessel | 0.720 | **0.855** | 0.886 | 0.744 | 0.816 |
| lunet | 0.571 | 0.829 | 0.866 | 0.790 | **0.897** |
| vascx-artery-vein | 0.587 | 0.802 | 0.858 | 0.777 | 0.838 |
| automorph-artery-vein | 0.578 | 0.717 | 0.865 | **0.801** | 0.794 |
| bf-net | 0.559 | 0.612 | 0.767 | 0.660 | 0.597 |

**Vessels clDice**

| Model | avrdb | fives | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- | --- |
| ocularnet | **0.808** | **0.890** | **0.932** | 0.798 | **0.887** |
| segan-vessel | 0.776 | 0.865 | 0.915 | **0.820** | 0.868 |
| lunet | 0.673 | 0.872 | 0.917 | 0.809 | 0.881 |
| vascx-artery-vein | 0.673 | 0.843 | 0.884 | 0.750 | 0.833 |
| automorph-artery-vein | 0.664 | 0.730 | 0.896 | 0.777 | 0.786 |
| bf-net | 0.617 | 0.625 | 0.766 | 0.641 | 0.600 |

**Vessels Betti matching error**, median per photograph — **read down a column, never across
one**: 3,269-pixel HRF has more features to leave unmatched than 1,062-pixel AVRDB whatever a model
does.

| Model | avrdb | fives | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- | --- |
| lunet | 62 | **56** | **84** | **142** | **50** |
| ocularnet | **60** | 93 | 144 | 249 | 100 |
| automorph-artery-vein | 111 | 93 | 192 | 404 | 112 |
| vascx-artery-vein | 180 | 141 | 254 | 342 | 168 |
| bf-net | 150 | 160 | 204 | 260 | 155 |
| segan-vessel | 206 | 162 | 216 | 305 | 166 |

**LUNet leads four of five**, OCULARNet the fifth, and the ordering barely moves between datasets —
which the Dice tables above cannot say of themselves. **AutoMorph's model is the extreme case of the
two metrics disagreeing**: on HRF it has the *best* Dice of any model, 0.801, and the *worst*
topology, 404 — it covers the vessel area better than anything else there while leaving four hundred
features of one map or the other with nothing to answer them.

**Artery Dice**, on the four datasets that publish the classes:

| Model | avrdb | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- |
| ocularnet | **0.670** | **0.875** | 0.750 | **0.856** |
| vascx-artery-vein | 0.491 | 0.817 | 0.718 | 0.790 |
| automorph-artery-vein | 0.469 | 0.823 | **0.761** | 0.725 |
| lunet | 0.441 | 0.805 | 0.686 | 0.840 |
| bf-net | 0.413 | 0.660 | 0.556 | 0.470 |

**No model leads everywhere.** OCULARNet leads four of five on vessels and three of four on
arteries; the vessel reference leads FIVES, LUNet leads REYIA, and AutoMorph leads HRF — where its
mark is `in-sample-unclear-split`, which is a reason to discount that lead rather than to read it.

**HRF compresses everything.** Five of six models land between 0.744 and 0.801 on 3,269-pixel
frames — a range of 0.057 where FIVES spreads 0.24. Whatever separates these models, HRF's 45
photographs do not separate it.

**The vessel reference's own two datasets do not flatter it.** HRF is in-sample for it and it scores
0.744 there, its second-worst; it leads only on FIVES, which is the one dataset here it did not
train on. That is the opposite of the pattern contamination usually produces, and this page has no
explanation for it.

### 4.1 AVRDB, where every model fails at once

Every model scores far lower on AVRDB than on the other four. Six models failing on the same hundred
photographs, each in its own way, is not the likely explanation, so the annotation is what section 5
says is worth a second look.

| Dataset | Annotated vessels, share of frame | Models' vessels, share of frame | Annotated ÷ model | Mean clDice − Dice |
| --- | --- | --- | --- | --- |
| avrdb | 10.7% | 6.8% | **1.64** | **+0.078** |
| fives | 7.0% | 5.5% | **1.64** | +0.027 |
| fundus-avseg | 9.4% | 8.4% | 1.14 | +0.027 |
| reyia | 7.9% | 7.5% | 1.10 | +0.006 |
| hrf | 5.7% | 6.1% | 0.94 | +0.004 |

*Our finding, 2026-09-19:* **AVRDB's vessels are drawn about 1.6 times wider than the vessels the
models trace**, where on HRF and REYIA annotation and models agree on area to within a tenth. Its
clDice sits 8 points above its Dice — the models find the network and lose on width — while on HRF
and REYIA the two metrics agree.

**But width alone does not explain AVRDB, and this page previously implied it did.** FIVES carries
*the same ratio*, 1.64, and the models still reach 0.85 there against 0.73 on AVRDB, with a gap of
+0.027 rather than +0.078. So a reference drawn wider than the models trace is not on its own worth
a quarter of a Dice. Something further distinguishes AVRDB — its drawings ship as Illustrator files,
which is consistent with strokes of a chosen width rather than a tracing of each vessel's own width,
and a uniformly wide stroke costs differently from a proportionally wide one. **This repository has
not established that**, and the question is open.

**What this means for reading the tables.** AVRDB's rows measure how closely a model reproduces a
wide-stroke drawing, which is not quite the question the other four ask. It is kept in the pooled
figures — it is a real annotation by four ophthalmologists, and dropping a dataset because models
score badly on it is how a benchmark becomes a leaderboard.

### 4.2 FIVES, and the annotations nobody drew

FIVES joined this benchmark because it is the only dataset here outside the six the vessel reference
trained on, and because it annotates vessels without separating the classes — so it tests the vessel
column and nothing else.

**Two of its 800 vessel masks hold zero pixels.** *Our finding, 2026-09-19:* `train_447_g` and
`train_448_g` are annotated with nothing at all, against a median of 8.10% of the frame and no other
mask in the set below 0.73%. Both photographs are real fundus images — dark, and graded `bad` by
FIVES' own quality sheet — so it is the annotation that was never drawn rather than a photograph
with no vessels in it. Every model scored 0.000 on both, which measured the empty reference rather
than the model. They are now recorded in `src/datasets/exclusions/fives.json` and excluded from
every figure on this page. A sweep of all 1,608 native masks in the five built stores found no
others.

**Four more FIVES annotations fall under 1% of the frame**, and thirty under 3%. Those are sparse
rather than empty and have **not** been excluded — but they are most of the hardest photographs in
section 5, and whether they are sparse vasculature or partial tracings is not established.

## 5. What the models agree about

Where two models agree, that is a fact about the models and not evidence that either is right.
Two comparisons: agreement between their **scores** (Spearman, over 1,602 photographs) and between
their **masks** (Dice between one model's vessels and another's, on the section 3.1 sample).

- **OCULARNet and VascX rank photographs most alike** (0.910), with LUNet close to both (0.853,
  0.818). The four artery/vein models form one cluster: they find the same photographs hard.
- **The vessel reference is outside that cluster** — 0.324 with LUNet, 0.595 with OCULARNet, its
  highest 0.627 with VascX. It is not a weaker or stronger version of the same behaviour; it fails
  on *different photographs*. That is what makes it useful as a reference rather than as a rival.
- **The masks agree more than the scores do.** Every pair of the strong models draws vessels within
  0.77–0.88 Dice of each other — higher than any of them scores against the annotator. Models
  drawing the same vessels and all disagreeing with the reference is the pattern behind sections 4.1
  and 4.2.
- **Seven of the ten photographs every model found hardest are FIVES**, and most are its sparsely
  annotated glaucoma images: `test_122_g` at 0.032 mean Dice, `test_123_g` at 0.058, `train_316_g`
  at 0.084 — the same photographs whose annotations cover under 2% of the frame.

## 6. Which model to use

**The answer now depends on which question you are asking, and the two answers differ.**

**For naming arteries and veins, use [OCULARNet](../models/ocularnet.md).** It leads every pooled
overlap column — artery 0.829, vein 0.853, vessels 0.854, vessels clDice 0.884 — loses the network
on 0.2% of photographs against 1.0% for the next model, has the narrowest spread of the six, and
costs 2.6 seconds a photograph on Apple MPS.

**For a vessel network that will be measured rather than looked at, use
[LUNet](../models/lunet.md).** It leaves 57 features unmatched on the median photograph against
OCULARNet's 97, leads four of the five datasets on that measure, and does the same for each class
separately. A biomarker computed from a segmentation reads its *structure* — a branch that is
broken is a branch that is not counted — and topology is the measurement that sees that. The costs
are real: 0.051 behind on artery Dice, it swaps veins for arteries asymmetrically (section 3.1),
and it takes 20 seconds a photograph on CPU against OCULARNet's 2.6 on MPS, eight times the time.

**Where the two disagree, say which question you asked.** OCULARNet is ahead on overlap and LUNet on
topology, and the per-photograph correlation between the two measurements is near zero within a
dataset — so neither number substitutes for the other, and a table sorted by Dice alone would have
hidden the whole of this.

**For vessels alone, OCULARNet's union still edges the dedicated vessel model** — 0.854 against
0.832 pooled, and it leads on four of five datasets. That is worth stating plainly because it is
surprising: a model built for one job, scored on that job, does not beat artery/vein models' derived
unions here. **The exception is FIVES**, the only dataset neither contaminated for the reference nor
carrying a derived annotation, where [segan-vessel](../models/segan-vessel.md) leads 0.855 to 0.848
— seven thousandths, which is not a gap — while OCULARNet leads clDice there by 0.025. Read
together: the vessel model covers marginally more area, OCULARNet traces a better-connected network.
And the vessel model is cheap, at 1.9 seconds a photograph.

**If cost dominates, weigh VascX rather than BF-Net.** BF-Net is the only model under a second —
0.4 seconds, six times quicker than OCULARNet — but at 0.614 vessels Dice with a fifth of its vessel
maps under 0.5, it is not cheap so much as wrong quickly.

**Four caveats would change this answer.**

- **OCULARNet, LUNet and VascX are all marked `unknown`** — nobody established what they trained on,
  so none of these datasets is held-out for them. The models with clean marks are the weakest two.
- **The vessel reference runs at a threshold we chose**, 0.2 rather than its own 0.5, and how much
  that is worth per dataset was not measured — while its topology figures are the worst of the six,
  which is what that choice would be expected to cost (section 1.1).
- **No dataset here keeps its annotators apart**, so there is no reader-against-reader band. 0.854
  may be at the ceiling or well below it.
- **The seconds measure this machine**, Apple MPS for five models and CPU TensorFlow for LUNet.

## 7. What these numbers do not say

- **Contamination.** `unknown` is never merged with `out-of-sample`. OCULARNet, LUNet and VascX are
  `unknown` on all five datasets; BF-Net is `out-of-sample` on all five; AutoMorph's model and the
  vessel reference are `out-of-sample` on four and `in-sample-unclear-split` on HRF.
- **A threshold this repository chose.** Every artery/vein model is thresholded at its own
  upstream's 0.5; the vessel reference at 0.2, which is ours. Its masks are therefore thicker than
  its authors would draw them, its Dice and clDice both move with that choice, and **no sweep was
  run to say by how much on each dataset**. Where its HRF score shows the over-prediction signature
  — 0.744 Dice against 0.820 clDice, its largest gap — that is an observation, not a measurement of
  the threshold's effect.
- **The Betti matching error is a count and not a rate.** It grows with the size of the frame and
  the density of the annotation as well as with the mistake, so it compares models *within* a
  dataset and says nothing across them: HRF's figures are the largest for every model, and HRF is
  also the largest frame. The matching computes how many features were *paired* as well as how many
  were left over, which would give a comparable rate; this run did not store it, and doing so means
  measuring every pair again.
- **It counts a feature, not its size.** A missing arteriole and a missing main branch are one
  unmatched component each. That is the point — it is the measurement that does not care about area
  — but it is why it is read beside Dice rather than instead of it.
- **The vessel score is not a second opinion on the class scores.** In three of the four datasets
  that publish classes, the vessel annotation *is* the artery/vein annotation.
- **Two datasets here share photographs.** REYIA reuses 75 of FIVES' images, among others, so a
  figure pooled over both counts those eyes twice. REYIA and FIVES together are 1,357 of the 1,602
  photographs behind every pooled number on this page.
- **Nothing here is about calibre, arteriovenous ratio or tortuosity.** Those are the biomarker
  benchmark's, computed from the masks this one kept.
- **Resampling is not separated out.** Every model works at a grid other than the annotator's;
  native frames here run from 1,056 to 3,271 pixels, and how far a model's grid sits from the
  photograph's own resolution varies by dataset and is not controlled for.
- **Five datasets are not a survey**, and the three declared and unfetched are the ones that would
  change the picture: RITE carries the 40 DRIVE photographs the literature reports, and RAV is 206
  photographs from a population cohort no catalogued model names in training.

---

**Compiled from `notebooks/av.ipynb` on:** 2026-09-20 · **Measured by**
`python -m benchmarks --benchmark av`, and the topology by `--rescore` from the masks it kept
