# Artery and vein benchmark — results

Five models were asked, of 804 photographs, to say which vessels in the retina are **arteries** and
which are **veins** — **4,020 scored segmentations in all**. Their answers are compared here with
what an ophthalmologist drew on the same photograph: the arteries, the veins, and the vessels the
two make together.

Every number comes from `results/av/`; the reading of them comes from
[notebooks/av.ipynb](../../notebooks/av.ipynb). How the benchmark is configured is a separate page:
[av-docs.md](av-docs.md).

**5 of 6 declared models** and **4 of 7 declared datasets** took part. OCULARNet-nano is declared
and not measured: its weights answer HTTP 401 and cannot be obtained at all. RAV, LES-AV and RITE
are declared and not yet fetched — RITE above all, since the 40 DRIVE photographs it carries are
what every artery/vein paper reports and what would make a number here comparable with the
literature.

*This page previously said that nothing had been measured yet, and listed what was ready and what
was not. Both of those sections have gone: the run they were waiting for has happened.*

## Contents

1. [Summary](#1-summary)
2. [Where overlap and connectedness disagree](#2-where-overlap-and-connectedness-disagree)
3. [Telling arteries from veins](#3-telling-arteries-from-veins)
   · [3.1 How much of it is swapping](#31-how-much-of-it-is-swapping)
4. [Dataset by dataset](#4-dataset-by-dataset)
   · [4.1 AVRDB, where every model fails at once](#41-avrdb-where-every-model-fails-at-once)
5. [What the models agree about](#5-what-the-models-agree-about)
6. [Which model to use](#6-which-model-to-use)
7. [What these numbers do not say](#7-what-these-numbers-do-not-say)

## 1. Summary

All four datasets pooled, one row per model. **Dice** measures overlap with what the annotator
drew, from 0 (nothing in common) to 1 (identical). **clDice** asks the connectedness question
instead — how much of each network's *centreline* falls inside the other's mask — so a model can
score well on one and badly on the other, which is the point of carrying both. **Vessels** is the
union of the model's own arteries and veins, derived identically for every model and for every
annotator.

| Model | Photographs | Coverage | Artery Dice | Vein Dice | Vessels Dice | Vessels clDice | Seconds each | Marked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ocularnet](../models/ocularnet.md) | 804 | 1.000 | **0.829** | **0.853** | **0.859** | **0.878** | 2.8 | unknown |
| [lunet](../models/lunet.md) | 804 | 1.000 | 0.778 | 0.804 | 0.846 | 0.855 | 20.2 | unknown |
| [vascx-artery-vein](../models/vascx-artery-vein.md) | 804 | 1.000 | 0.752 | 0.789 | 0.806 | 0.815 | 12.9 | unknown |
| [automorph-artery-vein](../models/automorph-artery-vein.md) | 804 | 1.000 | 0.708 | 0.774 | 0.776 | 0.784 | 3.4 | mixed |
| [bf-net](../models/bf-net.md) | 804 | 1.000 | 0.491 | 0.601 | 0.617 | 0.625 | **0.5** | out-of-sample |

**Coverage is 1.000 everywhere.** Every model produced a segmentation for every photograph, and
none of the 4,020 failed. These are segmentation networks: none has a way of declining. Four
photographs of REYIA were set aside by the benchmark for having no artery/vein annotation to score
against, which is ours and not a model's failure.

**The seconds are photograph-weighted here**, and for one model that matters. The index page
[BENCHMARKS.md](../BENCHMARKS.md) averages the four per-dataset figures instead, which lets HRF's
45 photographs weigh as much as REYIA's 559; VascX costs 54.3 seconds a photograph on HRF and 9.5
on REYIA, so the index reports 22.6 seconds against the 12.9 above. Both are right about different
questions. The figures were measured on Apple MPS, except LUNet, which runs on the CPU through
TensorFlow because its checkpoint is a Keras 2.11 file.

**A mean hides a tail.** BF-Net's artery mean of 0.491 is not 804 mediocre answers: **43% of its
artery maps score under Dice 0.5**, against 0.8% of OCULARNet's. The share of maps a model loses
outright is the number a study feels.

| Model | Artery maps under Dice 0.5 | Vein maps | Vessels maps |
| --- | --- | --- | --- |
| ocularnet | 0.8% | 0.1% | 0.1% |
| vascx-artery-vein | 5.0% | 1.2% | 0.6% |
| lunet | 10.0% | 5.5% | 0.9% |
| automorph-artery-vein | 11.3% | 2.7% | 3.1% |
| bf-net | 42.8% | 17.2% | 16.4% |

**OCULARNet is also the steadiest.** Its artery Dice has a standard deviation of 0.088 across the
804 photographs, against 0.162 for LUNet and 0.184 for BF-Net — so the gap between it and LUNet in
the table understates how differently the two behave on an unfamiliar photograph.

## 2. Where overlap and connectedness disagree

The two metrics separate failures that overlap alone confuses. A vessel drawn three times too wide
around the same centre scores 0.50 Dice and 0.97 clDice — wrong about width, right about the
network. The same vessel thickened to one side scores the same 0.50 Dice and 0.03 clDice.

| Model | Median clDice − Dice | Traced, not covered (gap > +0.05) | Covered, not traced (gap < −0.05) |
| --- | --- | --- | --- |
| ocularnet | +0.014 | 13.1% | **0.2%** |
| lunet | −0.007 | **19.7%** | 1.9% |
| vascx-artery-vein | +0.002 | 13.9% | 2.5% |
| automorph-artery-vein | +0.001 | 14.1% | 5.6% |
| bf-net | +0.008 | 14.7% | 9.0% |

**Two distinct failures show up here, and they are not the same models.** LUNet sits furthest above
the diagonal — on a fifth of the photographs it traces a network the annotator would recognise at a
width the annotator would not, which is the failure a calibre measurement feels and a connectivity
measurement does not. BF-Net sits furthest below it: on 9% of photographs it covers the vessel area
and loses the network, which is the opposite trade and the worse one, because a broken network
cannot be repaired by rescaling.

**OCULARNet almost never loses the network** — 0.2%, a tenth of the next model's rate. Read
beside its Dice, that is what makes its lead more than a hundredth or two: it is ahead on both
questions at once.

*What this suggests for the biomarker benchmark, and does not settle here:* a model that traces the
right network at the wrong width will carry that width into every calibre, and into any
arteriovenous ratio computed from it. Whether it cancels in a ratio of two widths is exactly the
kind of question the biomarker benchmark exists to measure, and nothing on this page answers it.

## 3. Telling arteries from veins

A vessel map cannot be got wrong the way an artery/vein map can. Where `vessels` is high and
`artery` and `vein` are low, the model **finds the vessels and cannot name them**.

| Model | Vessels Dice | Artery Dice | Vein Dice | Cost of naming them |
| --- | --- | --- | --- | --- |
| ocularnet | 0.859 | 0.829 | 0.853 | **0.017** |
| vascx-artery-vein | 0.806 | 0.752 | 0.789 | 0.035 |
| automorph-artery-vein | 0.776 | 0.708 | 0.774 | 0.035 |
| lunet | 0.846 | 0.778 | 0.804 | 0.055 |
| bf-net | 0.617 | 0.491 | 0.601 | 0.071 |

**LUNet finds the vessels nearly as well as OCULARNet and names them less well.** Its vessel Dice
is 0.846 against 0.859 — thirteen thousandths of a difference — while its artery Dice is 0.051
lower. What it loses is not the vessel; it is the label on the vessel.

**Every model is better at veins than at arteries**, by 0.024 (OCULARNet) to 0.110 (BF-Net). Veins
are wider and darker, so there is more of them to agree about and less to mistake; the arteriole is
where the disagreement lives, and the arteriole is what a calibre biomarker is usually after.

### 3.1 How much of it is swapping

Read from the masks the run kept under `.atlas_runs/av/` — a sample of 12 photographs per dataset,
48 per model, because it opens four full-resolution masks per photograph.

| Model | Expert's artery called vein | Expert's vein called artery | Expert's artery found at all |
| --- | --- | --- | --- |
| vascx-artery-vein | **2.9%** | **2.7%** | 68.5% |
| ocularnet | 5.3% | 4.0% | **80.8%** |
| automorph-artery-vein | 5.8% | 4.6% | 68.5% |
| lunet | 6.5% | 9.7% | 73.6% |
| bf-net | 11.6% | 7.0% | 55.6% |

**Most of the disagreement is missing, not swapping.** OCULARNet finds 81% of the expert's artery
pixels and calls 5% of them vein; the remaining ~14% it does not mark as a vessel at all. The same
holds for every model here — the "found at all" column is always much further from 1 than the swap
columns are from 0. A model that fails on this benchmark mostly fails by not seeing a vessel, not
by mistaking one kind for the other.

**VascX swaps least and sees least.** It has the cleanest naming of any model — under 3% either way
— and finds 68.5% of the expert's artery pixels, twelve points below OCULARNet. That is a
conservative model: what it marks, it marks correctly.

**LUNet is the one that swaps asymmetrically**, calling 9.7% of the expert's vein pixels artery
against 6.5% the other way. An arteriovenous ratio computed from a model that leans one direction
is biased rather than noisy, which is the more dangerous of the two.

**Crossings flatter every score a little.** Where an artery passes over a vein the pixel is
annotated as both, so a model calling it either is right. That is 4.4% of HRF's vessel pixels, 2.1%
of AVRDB's, 2.0% of REYIA's and 1.7% of Fundus-AVSeg's.

## 4. Dataset by dataset

The model is the row, the dataset the column, as everywhere else. Vessels Dice first, because it is
the one question every model is answering the same way.

**Vessels Dice**

| Model | avrdb | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- |
| ocularnet | **0.726** | **0.904** | 0.797 | 0.879 |
| lunet | 0.571 | 0.866 | 0.790 | **0.897** |
| vascx-artery-vein | 0.587 | 0.858 | 0.777 | 0.838 |
| automorph-artery-vein | 0.578 | 0.865 | **0.801** | 0.794 |
| bf-net | 0.559 | 0.767 | 0.660 | 0.597 |

**Artery Dice**

| Model | avrdb | fundus-avseg | hrf | reyia |
| --- | --- | --- | --- | --- |
| ocularnet | **0.670** | **0.875** | 0.750 | **0.856** |
| lunet | 0.441 | 0.805 | 0.686 | 0.840 |
| vascx-artery-vein | 0.491 | 0.817 | 0.718 | 0.790 |
| automorph-artery-vein | 0.469 | 0.823 | **0.761** | 0.725 |
| bf-net | 0.413 | 0.660 | 0.556 | 0.470 |

**The ordering is not stable across datasets.** OCULARNet leads three of the four on vessels and
three of four on arteries, but AutoMorph's artery/vein model leads on HRF and LUNet leads on REYIA —
and on HRF, AutoMorph's lead comes with a contamination mark (`in-sample-unclear-split`) that the
others do not carry, which is a reason to discount it rather than to read it.

**HRF compresses everything.** Four of the five models land between 0.777 and 0.801 vessels Dice
there, a range of 0.024 — on 3,269-pixel frames, nine times the area of AVRDB's. Whatever
separates these models, HRF's 45 photographs do not separate it.

**REYIA is where the models spread furthest** — 0.597 to 0.897 — and it is also the dataset to be
most careful with: it is a compilation, and three of the collections it draws from this repository
builds separately. Pooling a figure over REYIA and those datasets counts the same eyes twice.

### 4.1 AVRDB, where every model fails at once

Every model scores about a quarter of a Dice lower on AVRDB than on the other three. Five different
networks failing on the same hundred photographs, each in its own way, is not the likely
explanation, so the annotation is what section 5 says is worth a second look.

| Dataset | Annotated vessels, share of frame | Models' vessels, share of frame | Annotated ÷ model | Mean clDice − Dice |
| --- | --- | --- | --- | --- |
| avrdb | 10.7% | 6.4% | **1.73** | **+0.083** |
| fundus-avseg | 9.4% | 8.0% | 1.19 | +0.027 |
| reyia | 7.9% | 6.9% | 1.17 | −0.004 |
| hrf | 5.7% | 5.7% | 0.99 | −0.010 |

*Our finding, from the notebook's section 5.1:* **AVRDB's vessels are drawn about 1.7 times wider
than the vessels the models trace**, where on the other three datasets annotation and models agree
on area to within a fifth. The clDice column says what follows from that: on AVRDB the models score
8 points *higher* on connectedness than on overlap — they find the network and lose on width —
while on HRF and REYIA the two metrics agree.

The dataset page records that AVRDB's drawings ship as Illustrator files, which is consistent with
strokes of a chosen width rather than a tracing of each vessel's own width, though this repository
has not established that as the cause.

**What this means for reading the tables above.** AVRDB's rows measure how closely a model
reproduces a wide-stroke drawing, which is not the same question the other three ask. It is kept in
the pooled figures — it is a real annotation by four ophthalmologists, and dropping a dataset
because models score badly on it is how a benchmark becomes a leaderboard — but a model's AVRDB
row should not be read as its vessel-finding ability. AVRDB is also where 8 of the 10 photographs
every model found hardest come from.

## 5. What the models agree about

Where two models agree, that is a fact about the models and not evidence that either is right —
several of them trained on overlapping public data. Two comparisons, both from the notebook:
agreement between their **scores** (Spearman, over the 804 photographs) and between their **masks**
(Dice between one model's vessels and another's, on the section 3.1 sample).

- **OCULARNet and VascX rank photographs most alike** (0.914), and LUNet ranks with both (0.826,
  0.805). The four stronger models form one cluster: they find the same photographs hard.
- **BF-Net is outside it** — 0.168 with LUNet, 0.377 with OCULARNet. It is not a weaker version of
  the same behaviour; it is failing on different photographs.
- **The masks agree more than the scores do.** Every pair of the four stronger models draws vessels
  within 0.861–0.897 Dice of each other, which is *higher* than any of them scores against the
  annotator. Four models drawing the same vessels and all four disagreeing with the reference is
  the pattern behind section 4.1.

## 6. Which model to use

**For naming arteries and veins, use [OCULARNet](../models/ocularnet.md).** It leads every pooled
column — artery 0.829, vein 0.853, vessels 0.859, vessels clDice 0.878 — loses the network on 0.2%
of photographs against 1.9% for the next model, and has the narrowest spread of the five. It costs
2.8 seconds a photograph on Apple MPS.

**The second is LUNet, and it is not close on the question that matters here.** LUNet matches
OCULARNet on finding vessels (0.846 against 0.859) but is 0.051 behind on arteries, swaps
asymmetrically, and costs 20 seconds a photograph on the CPU — seven times OCULARNet's time for a
worse answer to the artery/vein question. Choose it over OCULARNet only for the thing it was built
for, which is fine vessels at a 1,472-pixel grid, and measure whether that matters for your
photographs before paying for it.

**If you have a very large collection, weigh [VascX](../models/vascx-artery-vein.md) rather than
BF-Net.** BF-Net is the only model here under a second a photograph — 0.5 seconds, six times
quicker than OCULARNet — but at 0.491 artery Dice, with 43% of its artery maps under 0.5, it is not
cheap so much as it is wrong quickly. VascX is the conservative choice: the cleanest naming of any
model (under 3% swapped either way), 12.9 seconds a photograph, and it misses more vessels than
OCULARNet rather than mislabelling them.

**Three caveats would change this answer.**

- **OCULARNet, LUNet and VascX are all marked `unknown`** — nobody has established what they trained
  on, so none of these four datasets can be called held-out for them. The only models here with a
  clean `out-of-sample` mark on every dataset are BF-Net and, on three of the four, AutoMorph's — and
  they are the two weakest. A recommendation resting on `unknown` marks is provisional by
  construction, and RITE or RAV would be what tests it.
- **No dataset here keeps its annotators apart**, so there is no reader-against-reader band. 0.859
  may be at the ceiling or well below it; nothing measured here can say which.
- **The seconds measure this machine.** Apple MPS for four of the models, CPU TensorFlow for LUNet;
  another processor reorders the cost column, though not by enough to make BF-Net accurate or LUNet
  quick.

## 7. What these numbers do not say

- **Contamination.** `unknown` is never merged with `out-of-sample`. OCULARNet, LUNet and VascX are
  `unknown` on all four datasets; BF-Net is `out-of-sample` on all four; AutoMorph's artery/vein
  model is `out-of-sample` on three and `in-sample-unclear-split` on HRF, which is why its HRF lead
  in section 4 is not read as one.
- **The vessel score is not a second opinion on the class scores.** In three of these four datasets
  the vessel annotation *is* the artery/vein annotation — Fundus-AVSeg and AVRDB derive theirs, and
  HRF's hand-drawn gold standard differs from the union of its artery/vein maps by 0.004% of pixels.
  Where the two columns agree, that is one measurement seen twice.
- **REYIA overlaps its own sources.** It is a compilation whose subsets are named for collections
  this repository builds separately, so a figure pooled over REYIA and those datasets counts the
  same eyes twice. REYIA is 559 of the 804 photographs behind every pooled number on this page.
- **Nothing here is about calibre, arteriovenous ratio or tortuosity.** Those are the biomarker
  benchmark's, computed from the masks this one kept under `.atlas_runs/av/`. Where a result above
  suggests something about them — LUNet's width, VascX's conservatism — it is a suggestion for that
  benchmark to measure.
- **Resampling is not separated out.** Every model works at a grid other than the annotator's and
  has its probabilities carried back to the native frame and thresholded there. The models read a
  pre-built rescaling of each photograph — 1,024 pixels for four of them, 1,472 for LUNet — and
  native frames here run from 1,056 to 3,271 pixels, so how far a model's grid sits from the
  photograph's own resolution varies by dataset and is not controlled for.
- **Four datasets are not a survey**, and the three declared and unfetched are the ones that would
  change the picture: RITE carries the 40 DRIVE photographs the literature reports, and RAV is 206
  photographs from a population cohort that no catalogued model names in training.

---

**Compiled from `notebooks/av.ipynb` on:** 2026-09-19 · **Measured by**
`python -m benchmarks --benchmark av`
