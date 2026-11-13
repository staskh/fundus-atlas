# Biomarkers on real segmentations — results

Experts had already traced the arteries and veins on **996 photographs**. Each biomarker project
here was run the way its authors ship it: on **its own segmentation model's map** of each
photograph, and on the expert's map of the same photograph. The program, the optic disc, the field
of view and the microns-per-pixel scale were the same both times, so any difference between a pair
of numbers comes from the vessel map alone.

The question is the one a Dice score cannot answer: **if a study replaced manual tracing with this
project's own pipeline, would the biomarker still tell one eye from another?**

Every number comes from `results/biomarker-real/`. The reading of them comes from
[notebooks/biomarker-real.ipynb](../../notebooks/biomarker-real.ipynb). How the benchmark is
configured is a separate page: [biomarker-real-docs.md](biomarker-real-docs.md).

**What is read here.** Six of the seven implementations, each on its own model (configuration page
§2.3). That makes three of the five segmentation models and all five datasets. Every one of the 30
project × dataset results is complete, which is **11,952 maps** (996 photographs × 2 maps × 6
projects):

| Project | Its own artery/vein model |
| --- | --- |
| [ocular](../projects/ocularnet.md) | [OCULARNet](../models/ocularnet.md) |
| [AutoMorph](../projects/automorph.md), [AutoMorphalyzer](../projects/automorphalyzer.md), [AutoMorphClass](../projects/automorphclass.md) | [AutoMorph's artery/vein model](../models/automorph-artery-vein.md) |
| [VascX](../projects/vascx.md) | [VascX's artery/vein ensemble](../models/vascx-artery-vein.md) |
| [fundus-biomarkers](../projects/fundus-biomarkers.md) | [OCULARNet](../models/ocularnet.md), which its command-line pipeline runs |

**PVBM is not read**: it ships no artery/vein model, and its users supply the masks. **LUNet's and
BF-Net's maps** belong to no project here. The run measured every program on every model's map,
41,832 maps in all, and those rows stay in `results/`.

*This page changed on 2026-11-13.* It used to compare all five models under every program, with
the model as the primary index. It now reads each project on its own model, with the project as
the primary index and the dataset inside it. The earlier reading is in the repository's history at
commit `5a9f566`. Every section keeps its heading and answers the same question for the native
pairs.

**fundus-biomarkers is not publicly available.** It is a proprietary implementation in a private
repository, catalogued because it names every column it returns against this atlas's vocabulary.
Its figures are shown beside the public projects', and the recommendation in section 7 says what a
reader can use without it. It returns nothing on the **111 photographs with no scale** (43 of RAV's
198 and all 68 of REYIA's `magreb` subset), so its figures cover the other 885.

## Contents

1. [Summary](#1-summary) · [1.1 How to read the two statistics](#11-how-to-read-the-two-statistics)
2. [Dataset by dataset](#2-dataset-by-dataset) ·
   [2.1 AVRDB, and what it does to the pooled figures](#21-avrdb-and-what-it-does-to-the-pooled-figures) ·
   [2.2 REYIA by subset](#22-reyia-by-subset)
3. [Every catalogued biomarker, by family](#3-every-catalogued-biomarker-by-family) ·
   [3.1 Why the IQRs fall into bands](#31-why-the-iqrs-fall-into-bands)
4. [Where the programs disagree](#4-where-the-programs-disagree) ·
   [4.1 One map, several programs](#41-one-map-several-programs) ·
   [4.2 Coverage](#42-coverage)
5. [What the failures look like](#5-what-the-failures-look-like)
6. [What it costs](#6-what-it-costs)
7. [Which project to use](#7-which-project-to-use)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)

## 1. Summary

**The panel** is five biomarkers a reader of a vascular-epidemiology paper is most likely to meet,
each with its own way of failing:

- **CRAE and CRVE** are Knudtson's central retinal artery and vein equivalents in zone B, the ring
  between two and three optic-disc radii from the disc centre. They are summary widths of the six
  widest arteries or veins, and they fail on a vessel's edge.
- **AVR** is their ratio. It fails on telling arteries from veins.
- **Artery fractal dimension** is box-counting over the arteries: how completely the branching
  fills the picture. It fails on the smallest vessels.
- **Artery tortuosity** is the median arc-to-chord ratio of the arteries. It fails on a broken
  centreline.

Each project computes some of these and not others. Where a project returns no median artery
tortuosity, its **length-weighted mean** (*lw*) or its **mean** stands in, marked as such. The
table pools **all five datasets on the photographs**, so it averages over datasets that differ a
great deal; the detail is in section 2.

| Project | Its model | CRAE | CRVE | AVR | Artery fractal dim. | Artery tortuosity | Contamination |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ocular | OCULARNet | — | — | — | — | 0.72 · 1.69 | mixed, mostly in-sample |
| AutoMorph | AutoMorph's | — | — | — | 0.37 · 0.83 | *mean* 0.37 · 0.72 | mixed |
| AutoMorphalyzer | AutoMorph's | 0.57 · 1.31 | 0.63 · 1.37 | — | 0.57 · 1.26 | *mean* 0.41 · 1.13 | mixed |
| AutoMorphClass | AutoMorph's | — | — | — | 0.52 · 1.09 | *lw* 0.50 · 0.98 | mixed |
| VascX | VascX's | 0.56 · 1.34 | 0.63 · 1.38 | — | — | *lw* 0.71 · 1.52 | mixed |
| fundus-biomarkers | OCULARNet | 0.83 · 1.94 | 0.87 · 2.14 | 0.73 · 1.47 | 0.80 · 1.71 | 0.88 · 2.17 | mixed, mostly in-sample |

Each cell is **ICC(A,1) · SNR**, both explained in section 1.1. An ICC below 0.75 means a study
could not use the pipeline's number in place of the expert-map number. An SNR below 1 means the
segmentation's error is larger than the difference between eyes the biomarker is there to detect.
A dash is a biomarker the project does not compute.

**This table is not the answer, and section 2.1 says why.** fundus-biomarkers' lead is mostly
OCULARNet's, and OCULARNet trained on four of these five datasets, AVRDB among them. AVRDB's
wide-stroke annotation pulls every other project's calibre down. **Without AVRDB, VascX's CRAE goes
from 0.56 to 0.74 against fundus-biomarkers' 0.81. On RAV, out of sample for OCULARNet and for
AutoMorph's model, the three calibre projects' CRAE agrees with the expert at 0.78–0.80.**

**The AutoMorph projects make vessels look thinner.** On AutoMorph's maps, CRAE is 7.9% lower than
on the expert's (AutoMorphalyzer), and fractal dimension 5–6% lower in all three. VascX's CRAE is
4.8% lower. fundus-biomarkers on OCULARNet is within 1% on every panel biomarker. Those offsets are
a **bias**, correctable in principle. It is why ICC(A,1) sits up to 0.25 below ICC(C,1) for the
AutoMorph projects' fractal dimension (notebook section 2.1). The rest of the shortfall is
**scatter**, which cannot be corrected afterwards.

**AutoMorph's own tortuosity is not usable** (section 3). On three of the five datasets it returns
a perfectly straight 1.0 for most eyes.

### 1.1 How to read the two statistics

- **ICC(A,1)**, the intraclass correlation for absolute agreement, asks: of all the spread in this
  biomarker across photographs, how much is real difference between eyes rather than disagreement
  between the two maps? 1 is perfect. Conventionally, below 0.5 is poor, 0.5–0.75 moderate,
  0.75–0.9 good and above 0.9 excellent. **ICC(C,1)**, the consistency form, forgives a constant
  offset. It is in the notebook, section 2.1.
- **SNR**, the signal-to-noise ratio, is how much eyes differ (the standard deviation across
  photographs on the expert's maps) divided by how much the model's map moves the number (the
  standard deviation of model minus expert, with any constant offset set aside).

**Read them together.** A high SNR with a low ICC(A,1) is a bias, which is correctable in
principle. A low SNR is scatter, which nothing downstream can correct.

The **IQR/MAPE** figure that fundus-biomarkers' own benchmark uses is in the notebook beside both
(sections 2.1, 2.2 and 3.2). It is the spread of the middle half of eyes, as a percentage of their
median, over the mean percentage error. Read beside the SNR it tells the same story, except that it
counts a constant offset as error where the SNR does not. Above 1 is a low bar: with no offset, an
IQR/MAPE of 1 is an SNR of about 0.6.

## 2. Dataset by dataset

Pooling widens the signal. Eyes from five cohorts and many cameras differ more than eyes from one,
so a pooled ICC flatters, and these per-dataset figures are the primary evidence. Shown below is
ICC(A,1), project by project. SNR and IQR/MAPE for the same cells are in notebook section 2.2.

| Project (model) | Dataset | CRAE | CRVE | AVR | Artery FD | Artery tortuosity | Contamination |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ocular (OCULARNet) | hrf | — | — | — | — | 0.63 | in-sample, unclear split |
| | fundus-avseg | — | — | — | — | 0.90 | in-sample, unclear split |
| | avrdb | — | — | — | — | 0.47 | in-sample, unclear split |
| | reyia | — | — | — | — | 0.72 | mixed |
| | rav | — | — | — | — | 0.66 | out-of-sample |
| AutoMorph (AutoMorph's) | hrf | — | — | — | 0.25 | *mean* 0.05 | in-sample, unclear split |
| | fundus-avseg | — | — | — | 0.47 | *mean* 0.80 | out-of-sample |
| | avrdb | — | — | — | 0.22 | *mean* 0.00 | out-of-sample |
| | reyia | — | — | — | 0.36 | *mean* 0.24 | out-of-sample |
| | rav | — | — | — | 0.46 | *mean* −0.06 | out-of-sample |
| AutoMorphalyzer (AutoMorph's) | hrf | 0.47 | 0.53 | — | 0.19 | *mean* 0.12 | in-sample, unclear split |
| | fundus-avseg | 0.32 | 0.48 | — | 0.55 | *mean* 0.84 | out-of-sample |
| | avrdb | 0.06 | 0.10 | — | 0.20 | *mean* 0.35 | out-of-sample |
| | reyia | 0.69 | 0.75 | — | 0.40 | *mean* 0.32 | out-of-sample |
| | rav | 0.80 | 0.83 | — | 0.60 | *mean* 0.62 | out-of-sample |
| AutoMorphClass (AutoMorph's) | hrf | — | — | — | 0.17 | *lw* 0.23 | in-sample, unclear split |
| | fundus-avseg | — | — | — | 0.55 | *lw* 0.94 | out-of-sample |
| | avrdb | — | — | — | 0.16 | *lw* 0.30 | out-of-sample |
| | reyia | — | — | — | 0.37 | *lw* 0.39 | out-of-sample |
| | rav | — | — | — | 0.45 | *lw* 0.78 | out-of-sample |
| VascX (VascX's) | hrf | 0.54 | 0.42 | — | — | *lw* 0.39 | in-sample, unclear split |
| | fundus-avseg | 0.38 | 0.56 | — | — | *lw* 0.88 | out-of-sample |
| | avrdb | 0.02 | 0.06 | — | — | *lw* 0.52 | out-of-sample |
| | reyia | 0.81 | 0.84 | — | — | *lw* 0.70 | out-of-sample |
| | rav | 0.80 | 0.80 | — | — | *lw* 0.74 | in-sample, unclear split |
| fundus-biomarkers (OCULARNet) | hrf | 0.61 | 0.39 | 0.68 | 0.35 | 0.79 | in-sample, unclear split |
| | fundus-avseg | 0.60 | 0.72 | 0.78 | 0.66 | 0.92 | in-sample, unclear split |
| | avrdb | 0.39 | 0.51 | 0.41 | 0.13 | 0.81 | in-sample, unclear split |
| | reyia | 0.86 | 0.86 | 0.81 | 0.95 | 0.86 | mixed |
| | rav | 0.78 | 0.86 | 0.66 | 0.75 | 0.92 | out-of-sample |

**REYIA and RAV are where a project's own pipeline can stand in for the expert's map.** CRAE
reaches 0.78–0.86 for fundus-biomarkers, 0.80–0.81 for VascX and 0.69–0.80 for AutoMorphalyzer on
those two, and CRVE 0.75–0.86. VascX's RAV figure is in its model's training data, with an unclear
split, and covers only 89 of RAV's 198 photographs (section 4.2).

**HRF and Fundus-AVSeg are harder for calibre.** HRF's expert drew the small vessels as hairlines,
as section 5 shows. Its CRVE agreement is 0.39 to 0.53 across the three projects that compute it,
and Fundus-AVSeg's CRAE is 0.32 to 0.60, though OCULARNet trained on both.

**Fractal dimension survives OCULARNet's map and not AutoMorph's.** fundus-biomarkers reaches
0.66–0.95 on Fundus-AVSeg, REYIA and RAV. The three AutoMorph projects measure the same
box-counting dimension on AutoMorph's maps at 0.16–0.60 on every dataset. That is the model, not
the program, as section 4.1 shows.

**Tortuosity depends on which summary a project returns as much as on the map.** fundus-biomarkers'
median holds at 0.79–0.92 on every dataset. ocular's median, on the same OCULARNet maps, ranges
from 0.47 to 0.90. The means and length-weighted means of the AutoMorph projects and VascX swing
from below 0.4 on HRF to 0.8–0.94 on Fundus-AVSeg.

### 2.1 AVRDB, and what it does to the pooled figures

**On AVRDB every calibre project fails but one.** CRAE agreement is 0.02 (VascX) and 0.06
(AutoMorphalyzer) against 0.39 for fundus-biomarkers. The [artery/vein results](av-results.md)
§4.1 already found that AVRDB's vessels are drawn about 1.6 times wider than any model traces them,
as strokes of one chosen width. The scatter plots in notebook section 2.3 show the consequence:
AVRDB's points form a separate cloud below the diagonal. A wide even stroke makes every vessel look
like a major one, so calibre measured on it describes the drawing rather than the eye.

Pooled without AVRDB, computed in notebook section 7.4 by the run's own function:

| Project | CRAE | CRVE | AVR | Artery FD | Artery tortuosity |
| --- | --- | --- | --- | --- | --- |
| ocular | — | — | — | — | 0.74 *(0.72)* |
| AutoMorph | — | — | — | 0.43 *(0.37)* | *mean* 0.36 *(0.37)* |
| AutoMorphalyzer | 0.66 *(0.57)* | 0.74 *(0.63)* | — | 0.63 *(0.57)* | *mean* 0.41 *(0.41)* |
| AutoMorphClass | — | — | — | 0.60 *(0.52)* | *lw* 0.52 *(0.50)* |
| VascX | 0.74 *(0.56)* | 0.81 *(0.63)* | — | — | *lw* 0.72 *(0.71)* |
| fundus-biomarkers | 0.81 *(0.83)* | 0.85 *(0.87)* | 0.76 *(0.73)* | 0.91 *(0.80)* | 0.89 *(0.88)* |

*In brackets: the pooled figure with AVRDB, from section 1.*

**fundus-biomarkers on OCULARNet is the one pipeline AVRDB barely moves on calibre**, and OCULARNet
is the only model here that trained on AVRDB. Its 0.39 there, against the others' 0.02–0.06, is
most plausibly a model reproducing the drawing style it was taught, not a model seeing vessels
better. Without AVRDB its lead over VascX on CRAE shrinks from 0.27 to 0.07. **AVRDB stays in the
pooled figures**: it is a real annotation by four ophthalmologists, and dropping a dataset because
pipelines score badly on it is how a benchmark becomes a leaderboard.

### 2.2 REYIA by subset

REYIA is a compilation of collections from different cameras and clinics. Notebook section 7.3
breaks it down. **Two of its eight subsets, mBRSET (27 photographs) and TREND-AV (48), are the
hardest for every project.** VascX's CRAE falls from 0.87–0.92 on four of the other subsets to 0.76
and 0.65 there. fundus-biomarkers' AVR falls from 0.75–0.95 to 0.30 and 0.41. These are also the two
subsets OCULARNet did not train on. **PAPILA** is the third weak subset for AutoMorphalyzer's
calibre (0.43–0.45) and VascX's (0.63–0.70), but not for fundus-biomarkers (0.86–0.88).

## 3. Every catalogued biomarker, by family

The panel is five numbers out of hundreds. Notebook section 3 reads every catalogued column each
project returns, family by family and dataset by dataset. The projects return very different
numbers of columns: fundus-biomarkers 629, AutoMorphalyzer 23, AutoMorph and AutoMorphClass 15,
ocular 10 and VascX 6. So the share in each cell below is over a different set in every row.

| Project | Calibre | Tortuosity | Density | Topology |
| --- | --- | --- | --- | --- |
| ocular | — | 0.61 · 25% | 0.78 · 50% | 0.58 · 0% |
| AutoMorph | 0.38 · 0% | 0.66 · 50% | 0.34 · 0% | — |
| AutoMorphalyzer | 0.39 · 0% | 0.63 · 50% | 0.47 · 0% | — |
| AutoMorphClass | 0.38 · 0% | 0.72 · 50% | 0.44 · 0% | — |
| VascX | 0.55 · 0% | 0.73 · 50% | — | — |
| fundus-biomarkers | 0.77 · 59% | 0.70 · 40% | 0.81 · 77% | 0.67 · 8% |

*Each cell: median pooled ICC(A,1) across the family's columns · share of its columns at 0.75 or
above.* These are pooled with AVRDB (section 2.1). Per dataset they are in notebook section 3.

- **No catalogued column survives every dataset in any project.** Not one reaches ICC(A,1) 0.9 on
  all five, under any project's own model (notebook section 3.1).
- **Those that fail everywhere are mostly spreads and counts.** In fundus-biomarkers, 41 of 629
  columns stay below 0.5 on every dataset: standard deviations of tortuosity within an eye, the
  number of separate vessel pieces, the number of vessel endpoints. They measure exactly what a
  segmentation model changes, which is how many short fragments it draws. In the AutoMorph
  projects, the length-weighted vessel width stays below 0.5 on every dataset.
- **AutoMorph's tortuosity has an IQR of zero on three datasets** (notebook section 3.2.7). On the
  expert's maps it returns exactly 1.0, a perfectly straight vessel, for 78 of Fundus-AVSeg's 100
  photographs, 90 of AVRDB's 99 and 182 of RAV's 198. On HRF it does so for none, and on REYIA for
  9 of 554. Its ICC of 0.80 on Fundus-AVSeg therefore rests on the few eyes that are not at 1.0.
  AutoMorphalyzer and AutoMorphClass, on the same maps, do not do this. AutoMorph's
  [project page](../projects/automorph.md) §8.1 records a tortuosity defect its successors fixed.
  Whether this is that defect is not checked here.
- **Pooled, IQR/MAPE clears 1 for most columns of every project on its own model. Dataset by
  dataset, AVRDB is where calibre falls below it.** There the median calibre column is at 0.42–0.43
  for the AutoMorph projects and VascX, against 1.41 for fundus-biomarkers (notebook section 3.2).

### 3.1 Why the IQRs fall into bands

In the IQR-against-MAPE plots of notebook section 3.2, the dots line up in horizontal bands. The
IQR (the spread of the middle half of eyes, over their median) is computed **from the expert's maps
alone**. The model does not move it: under one column and one dataset it is the same whichever map
it is compared with. Across the five models the run measured it differs by only 1–2%, through which
photographs both maps produced a number for, where the MAPE differs two- to three-fold. A dot's
height is therefore set by two things:

- **the kind of measure**: a fractal dimension sits between about 1.3 and 1.7 in every eye, so its
  IQR is a few percent, while a vessel area or length scales with how much vasculature was drawn
  and spreads by 30–45%;
- **the dataset**: a cohort, camera mix or annotation style that varies more has a wider IQR. That
  is also why a pooled IQR is wider than most single datasets' and pooled IQR/MAPE flatters, just as
  a pooled ICC does.

Only the MAPE, the horizontal position, says anything about the pipeline.

## 4. Where the programs disagree

### 4.1 One map, several programs

Two groups of projects ship the same model, so on those maps only the program differs. Pooled and
per-dataset ICC(A,1), from notebook section 4.1:

| Model | Biomarker | Program | hrf | fundus-avseg | avrdb | reyia | rav |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OCULARNet | Artery tortuosity, median | ocular | 0.63 | 0.90 | 0.47 | 0.72 | 0.66 |
| | | fundus-biomarkers | 0.79 | 0.92 | 0.81 | 0.86 | 0.92 |
| AutoMorph's | Artery fractal dimension | AutoMorph | 0.25 | 0.47 | 0.22 | 0.36 | 0.46 |
| | | AutoMorphalyzer | 0.19 | 0.55 | 0.20 | 0.40 | 0.60 |
| | | AutoMorphClass | 0.17 | 0.55 | 0.16 | 0.37 | 0.45 |
| | Artery tortuosity | AutoMorph, mean | 0.05 | 0.80 | 0.00 | 0.24 | −0.06 |
| | | AutoMorphalyzer, mean | 0.12 | 0.84 | 0.35 | 0.32 | 0.62 |
| | | AutoMorphClass, length-weighted | 0.23 | 0.94 | 0.30 | 0.39 | 0.78 |

**On the same OCULARNet maps, the program decides tortuosity.** ocular's median artery tortuosity
agrees at 0.47 on AVRDB and 0.66 on RAV, where fundus-biomarkers' median agrees at 0.81 and 0.92.
ocular's measuring code is a fork of PVBM's, so this is a difference in tracing the centreline and
cutting it into segments, not in the model.

**On AutoMorph's maps, fractal dimension is the model's and tortuosity is the program's.** The three
programs' fractal dimensions are within 0.15 of one another on every dataset, and all are low. Their
tortuosities are not: AutoMorph's straight-vessel values (section 3) are its own.

Section 4.2 of the notebook sets every project's own column under each panel biomarker side by
side. There the model and the program differ together, as they do for a study that adopts a project
whole.

### 4.2 Coverage

**Where the project's own map produced no panel number and the expert's did**, pooled, from
notebook section 1.1. fundus-biomarkers lost one CRVE. **AutoMorphalyzer lost 64 CRAE and 23
CRVE**, most of them on REYIA, AVRDB and RAV. VascX lost 18 CRAE and 4 CRVE, ocular 2 tortuosities.

**Where neither map produced a number.** **VascX returns its equivalents on only part of two
datasets**, on the expert's map and its own alike: CRAE on 44 of AVRDB's 99 photographs and 89 of
RAV's 198. Of those 198, 155 have a scale. Its figures on those datasets are over the photographs it
answered for.

**Maps on which a program returned nothing at all**, out of 1,992 per project (the expert's map and
its own model's, for each of 996 photographs):

| Project | Returned nothing | Why |
| --- | --- | --- |
| ocular, VascX | 0 | |
| AutoMorph, AutoMorphClass | 2 | AutoMorph's model's maps of two REYIA photographs |
| AutoMorphalyzer | 4 | three in REYIA and one in AVRDB, all on AutoMorph's model's maps |
| fundus-biomarkers | **222** | the 111 photographs with no microns-per-pixel scale × 2 maps, by design |

## 5. What the failures look like

Notebook section 5 shows, project by project and then dataset by dataset, the photograph where the
project's own map moved its first panel biomarker furthest from the expert's value: the photograph,
the expert's map and the model's map side by side. For the three calibre projects, the worst cases
share two causes:

- **The expert drew wide strokes and the model did not.** On AVRDB the model's CRAE is 41–49% below
  the expert's (fundus-biomarkers `im004538`, AutoMorphalyzer `im001126`, VascX `im002649`). The
  same happens on some RAV photographs whose expert strokes are wide, for example fundus-biomarkers
  `rav_656355`, at −48%.
- **The expert drew hairlines and the model did not.** On REYIA's TREND-AV subset, dark photographs
  of diseased eyes, the model's CRAE is 41–52% above the expert's (`trend_30_r`, `trend_31_r`). HRF
  `01_dr`, whose expert-map CRAE is 73–76 µm, about half a typical eye's, is +46% for
  fundus-biomarkers and +61% for VascX.

For tortuosity, the worst cases move by only 2–3%. Arc-to-chord ratios of real arteries span only
about 1.07 to 1.13, so a small relative move is a large share of the difference between eyes.

## 6. What it costs

Two costs, project by project. **The program's seconds per map** is averaged over the expert's and
its own model's maps, on one core of a 16-core x86 Linux server. **The model's seconds per
photograph** comes from the [artery/vein benchmark](av-results.md), measured on Apple MPS. Both
measure the machine as much as the software. Per dataset in notebook section 6:

| Project | Program, s per map | Its model, s per photograph |
| --- | --- | --- |
| ocular | 3.1–28.6 | OCULARNet 2.4–9.0 |
| AutoMorph | 6.4–12.6 | AutoMorph's 3.9–12.4 |
| AutoMorphalyzer | 6.4–82.0 | AutoMorph's 3.9–12.4 |
| AutoMorphClass | 0.5–7.1 | AutoMorph's 3.9–12.4 |
| VascX | 3.1–35.1 | VascX's 8.9–22.8 |
| fundus-biomarkers | 5.9–84.6 | OCULARNet 2.4–9.0 |

**Frame size dominates the program's cost.** The top of every range is HRF, whose crops are about
3,300 pixels across. AutoMorph is flat because it resizes everything to 912 pixels before
measuring. AutoMorphClass is the cheapest program by an order of magnitude.

## 7. Which project to use

**The answer depends on the biomarker, and on whether you can use fundus-biomarkers, which is not
publicly available.** Every recommendation below is agreement with **one expert's map** per
photograph. No dataset here has a second reader, so nothing here says where the ceiling is, and no
biomarker here is validated by agreeing with it.

**For calibre (CRAE, CRVE), among public projects, VascX and AutoMorphalyzer are close, and VascX
is slightly ahead on most photographs.**

- **Pooled, they tie.** CRAE is 0.56 for VascX against 0.57 for AutoMorphalyzer, and CRVE 0.63 for
  both.
- **Without AVRDB, VascX leads.** CRAE is 0.74 against 0.66, and CRVE 0.81 against 0.74.
- **On RAV they tie again**, at CRAE 0.80 and CRVE 0.80 against 0.83. But RAV is in VascX's
  training data, and VascX answered for only 89 of its photographs.
- **On REYIA's held-out mBRSET and TREND-AV photographs** (notebook section 7.5, 75 photographs),
  VascX is ahead on CRAE (0.71 against 0.58), and AutoMorphalyzer on CRVE (0.73 against 0.67).
- **Cost.** AutoMorphalyzer's model is the cheaper of the two, at 3.9–12.4 s a photograph against
  VascX's 8.9–22.8. Its program is slower on large frames: 82 s against 35 s a map on HRF.
- **Coverage.** VascX's partial coverage on AVRDB and RAV (section 4.2) is the caveat that would
  change this answer for a study whose photographs resemble them.

**fundus-biomarkers on OCULARNet leads calibre where it can be used**: CRAE 0.83, CRVE 0.87, and
it is the only project here that returns a Knudtson AVR (0.73). But its lead is mostly in-sample
and mostly AVRDB. Without AVRDB it is 0.81 against VascX's 0.74. On RAV, out of sample for
OCULARNet, it is 0.78 against 0.80 for VascX and AutoMorphalyzer. On mBRSET and TREND-AV it is 0.69
on CRAE, between the two public projects, and 0.57 on CRVE, below both. **On photographs unlike its training
data its lead is not established.**

**For fractal dimension, the model matters more than the program.** On AutoMorph's maps all three
AutoMorph programs agree at 0.16–0.60 per dataset. AutoMorphalyzer is the strongest of the three,
pooled (0.57 against 0.52 and 0.37) and on RAV (0.60). fundus-biomarkers on OCULARNet reaches 0.80
pooled, 0.91 without AVRDB and 0.75 on RAV, out of sample. No public project here measures fractal
dimension on OCULARNet's map.

**For tortuosity, take a median, and do not take AutoMorph's.** Among public projects, ocular's
median (0.72 pooled) and VascX's length-weighted mean (0.71) are a tie. VascX is steadier on
AVRDB (0.52 against 0.47) and RAV (0.74 against 0.66). ocular is steadier on HRF (0.63 against
0.39). Choose by cost or by what else the study needs. fundus-biomarkers' median reaches 0.88, and
0.92 on RAV, out of sample. **AutoMorph's own tortuosity should not be used** (section 3);
AutoMorphalyzer and AutoMorphClass return a corrected one.

**Caveats that would change these answers:**

- **Contamination.** OCULARNet trained on HRF, Fundus-AVSeg, AVRDB and six of REYIA's eight
  subsets. VascX's model trained on HRF and RAV. AutoMorph's model trained on HRF.
- **AVRDB's annotation style** decides much of the pooled calibre ranking (section 2.1). Whether a
  pipeline *should* reproduce a wide-stroke drawing is a question about the reference, not the
  pipeline.
- **One reader per photograph.** A pipeline disagreeing with the expert by as much as a second
  expert would has matched the reference, not failed it.
- **Different photographs behind different projects.** fundus-biomarkers leaves out the 111
  photographs with no scale, and VascX answers for about half of AVRDB and RAV.

## 8. What these numbers do not say

- **Nothing about the reference's own noise.** No dataset here publishes a second annotator, so the
  inter-reader band, which is the ceiling every ICC here should be read against, is unknown.
- **Nothing about whether a program is right.** Two maps agreeing under one program says the
  program is stable to the change of map. Whether it computes what it claims is the
  [synthetic benchmark](biomarker-synthetic-results.md)'s question.
- **Nothing about a project on another model's map.** Each project is read on its own model only.
  How it would fare on a map it does not ship with is in `results/`, not on this page. PVBM, which
  ships no model, is not read at all.
- **Nothing about the optic disc.** Both maps of a photograph share one disc estimate from the
  SegFormer disc model, so a wrong disc moves both numbers alike and is invisible here. A project's
  own disc model is not what ran. The [disc benchmark](disc-results.md) measures that.
- **Nothing anchored to the fovea.** No fovea is located for these photographs, so VascX's
  fovea-dependent features come back empty, as they should.
- **VascX's equivalents carry an upstream defect at the pinned commit.** At `d0cde1c`, VascX's
  Knudtson CRE sorts the vessel widths once instead of before every pairing round. Its authors
  fixed this on 2026-09-24 (upstream commit `5e76d60`). The fix changes VascX's CRAE and CRVE
  values. It moves the expert-map and model-map values of a pair together, so its effect on
  agreement here is expected to be small. Its effect on accuracy is the synthetic benchmark's
  question. The atlas will move VascX to the fixed commit and measure again.
- **Pooled means pooled on the photographs.** 45 from HRF weigh as 45, and REYIA's 554 (486 with a
  scale) as 554. REYIA therefore dominates every pooled figure.
- **A length on a photograph with no scale** is left out of its statistic. For fundus-biomarkers,
  that photograph is left out of every statistic.
