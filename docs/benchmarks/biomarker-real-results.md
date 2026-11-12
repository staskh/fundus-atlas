# Biomarkers on real segmentations — results

Five segmentation models drew arteries and veins on **996 photographs** that an expert had already
traced. Seven biomarker programs then measured every biomarker they compute twice per photograph:
once on the expert's map and once on each model's. That is **6 maps per photograph and 41,832
measured maps in all**. The program, the optic disc, the field of view and the microns-per-pixel
scale were the same both times, so any difference between a pair of numbers comes from the vessel
map alone.

The question is the one a Dice score cannot answer: **if a study replaced manual tracing with this
model, would the biomarker still tell one eye from another?**

Every number comes from `results/biomarker-real/`. The reading of them comes from
[notebooks/biomarker-real.ipynb](../../notebooks/biomarker-real.ipynb). How the benchmark is
configured is a separate page: [biomarker-real-docs.md](biomarker-real-docs.md).

**Everything declared took part.** All 7 implementations, all 5 segmentation models and all 5
datasets were measured, and every one of the 35 implementation × dataset results is complete. The
implementations are pinned at the commits listed in the configuration page §2.1.

**The headline numbers come from one implementation, fundus-biomarkers**, which names every column
against this catalogue. It refuses to guess a microns-per-pixel scale, so on the **111 photographs
with no scale** it returns nothing, not even its scale-free numbers. Those are 43 of RAV's 198 and
all 68 of REYIA's `magreb` subset. Its figures cover the other 885. The other six implementations
measured all 996 (section 4.2).

## Contents

1. [Summary](#1-summary) · [1.1 How to read the two statistics](#11-how-to-read-the-two-statistics)
2. [Dataset by dataset](#2-dataset-by-dataset) ·
   [2.1 AVRDB, and what it does to the pooled figures](#21-avrdb-and-what-it-does-to-the-pooled-figures) ·
   [2.2 REYIA by subset](#22-reyia-by-subset)
3. [Every catalogued biomarker, by family](#3-every-catalogued-biomarker-by-family)
4. [Where the programs disagree](#4-where-the-programs-disagree) ·
   [4.1 One biomarker, seven programs](#41-one-biomarker-seven-programs) ·
   [4.2 Coverage](#42-coverage)
5. [What the failures look like](#5-what-the-failures-look-like)
6. [What it costs](#6-what-it-costs)
7. [Which model to use](#7-which-model-to-use)
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

The table below pools **all five datasets on the photographs**: up to 885 of them, the photographs
with a scale (BF-Net's and AutoMorph's maps produced no value on a few, section 4.2). It is an average across datasets that
differ a great deal, and the detail is in section 2. The figures are from fundus-biomarkers.

| Model | CRAE | CRVE | AVR | Artery fractal dim. | Artery tortuosity | Contamination |
| --- | --- | --- | --- | --- | --- | --- |
| [vascx-artery-vein](../models/vascx-artery-vein.md) | 0.49 · 1.24 | 0.63 · 1.33 | 0.55 · 1.06 | 0.38 · 1.10 | 0.81 · 1.73 | mixed |
| [ocularnet](../models/ocularnet.md) | **0.83 · 1.94** | **0.87 · 2.14** | **0.73 · 1.47** | **0.80 · 1.71** | **0.88 · 2.17** | mixed, mostly in-sample |
| [lunet](../models/lunet.md) | 0.35 · 1.08 | 0.46 · 1.15 | 0.33 · 0.65 | 0.41 · 0.92 | 0.83 · 1.86 | unknown |
| [automorph-artery-vein](../models/automorph-artery-vein.md) | 0.41 · 1.12 | 0.56 · 1.23 | 0.42 · 0.91 | 0.31 · 0.91 | 0.80 · 1.53 | mixed |
| [bf-net](../models/bf-net.md) | 0.28 · 0.76 | 0.33 · 0.72 | 0.21 · 0.66 | 0.10 · 0.65 | 0.63 · 1.16 | out-of-sample |

Each cell is **ICC(A,1) · SNR**, both explained in section 1.1. An ICC below 0.75 means a study
could not use the model's number in place of the expert-map number. An SNR below 1 means the
model's error is larger than the difference between eyes the biomarker is there to detect.

**This table is not the answer, and section 2.1 says why.** One dataset, AVRDB, was annotated with
strokes much wider than the vessels. That pulls every model's pooled calibre and fractal-dimension
figures down, and it pulls them down least for OCULARNet, which trained on AVRDB. **Without AVRDB,
VascX's CRAE goes from 0.49 to 0.77 against OCULARNet's 0.81, and LUNet's fractal dimension from
0.41 to 0.84.**

**Most models make vessels look slightly thinner.** On the model's map, CRAE is lower than on the
expert's by 6% (VascX), 7% (LUNet) and 9% (AutoMorph), and by under 1% for OCULARNet and BF-Net.
That is a **bias**, a constant offset that a study could in principle correct, and it is why
ICC(A,1) sits a few hundredths below ICC(C,1) for those three. Most of what keeps the calibre ICCs
low is **scatter** rather than bias, and scatter cannot be corrected afterwards.

**Tortuosity survives every model's map but BF-Net's.** The median arc-to-chord ratio is the one
panel biomarker at 0.80 or above, pooled, under four of the five models, and it stays at 0.64 or
above on every dataset under those four.

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

The **IQR/MAPE** figure that fundus-biomarkers' own benchmark uses is in the notebook beside both.
Pooled, it puts OCULARNet's CRAE at 3.07 and BF-Net's at 1.09. Read beside the SNR it tells the
same story, because it counts a constant offset as error where the SNR does not.

## 2. Dataset by dataset

Pooling widens the signal. Eyes from five cohorts and many cameras differ more than eyes from one,
so a pooled ICC flatters, and these per-dataset figures are the primary evidence. Shown below is
ICC(A,1) from fundus-biomarkers. SNR and IQR/MAPE for the same cells are in notebook section 2.2.

| Model | Dataset | CRAE | CRVE | AVR | Artery FD | Artery tortuosity | Contamination |
| --- | --- | --- | --- | --- | --- | --- | --- |
| vascx-artery-vein | hrf | 0.53 | 0.31 | 0.66 | 0.38 | 0.75 | in-sample, unclear split |
| | fundus-avseg | 0.48 | 0.60 | 0.70 | 0.37 | 0.88 | out-of-sample |
| | avrdb | 0.09 | 0.13 | 0.09 | 0.02 | 0.77 | out-of-sample |
| | reyia | 0.80 | 0.84 | 0.75 | 0.80 | 0.81 | out-of-sample |
| | rav | **0.87** | **0.89** | 0.47 | 0.56 | 0.74 | in-sample, unclear split |
| ocularnet | hrf | 0.61 | 0.39 | 0.68 | 0.35 | 0.79 | in-sample, unclear split |
| | fundus-avseg | 0.60 | 0.72 | 0.78 | 0.66 | 0.92 | in-sample, unclear split |
| | avrdb | 0.39 | 0.51 | 0.41 | 0.13 | 0.81 | in-sample, unclear split |
| | reyia | 0.86 | 0.86 | 0.81 | 0.95 | 0.86 | mixed |
| | rav | 0.78 | 0.86 | 0.66 | 0.75 | 0.92 | out-of-sample |
| lunet | hrf | 0.30 | 0.25 | 0.24 | 0.29 | 0.74 | unknown |
| | fundus-avseg | 0.33 | 0.47 | 0.69 | 0.42 | 0.92 | unknown |
| | avrdb | 0.07 | 0.09 | 0.13 | 0.04 | 0.74 | unknown |
| | reyia | 0.82 | 0.86 | 0.31 | 0.91 | 0.82 | unknown |
| | rav | 0.78 | 0.79 | 0.60 | 0.63 | 0.81 | unknown |
| automorph-artery-vein | hrf | 0.69 | 0.53 | 0.67 | 0.45 | 0.84 | in-sample, unclear split |
| | fundus-avseg | 0.30 | 0.34 | 0.74 | 0.45 | 0.90 | out-of-sample |
| | avrdb | 0.07 | 0.10 | 0.03 | 0.01 | 0.64 | out-of-sample |
| | reyia | 0.61 | 0.77 | 0.47 | 0.69 | 0.76 | out-of-sample |
| | rav | 0.77 | 0.80 | 0.46 | 0.25 | 0.83 | out-of-sample |
| bf-net | hrf | 0.15 | 0.03 | 0.45 | 0.16 | 0.65 | out-of-sample |
| | fundus-avseg | 0.51 | 0.48 | 0.53 | 0.58 | 0.81 | out-of-sample |
| | avrdb | 0.09 | 0.19 | 0.03 | 0.01 | 0.62 | out-of-sample |
| | reyia | 0.18 | 0.21 | 0.15 | 0.12 | 0.57 | out-of-sample |
| | rav | 0.51 | 0.56 | 0.36 | 0.28 | 0.60 | out-of-sample |

**REYIA and RAV are where a model's map can stand in for the expert's.** On REYIA's 486 scaled
photographs, VascX, OCULARNet and LUNet all reach CRAE 0.80–0.86 and CRVE 0.84–0.86. On RAV, VascX
reaches 0.87 and 0.89, the best calibre agreement anywhere in the benchmark, but RAV is in its
training data with an unclear split.

**HRF and Fundus-AVSeg are harder, and not because of the models alone.** HRF's experts drew the
small vessels as hairlines, as the hard-case figure in section 5 shows. Its CRVE agreement under
VascX, OCULARNet and LUNet is 0.25 to 0.39, the lowest of any dataset but AVRDB.

**The AVR is more fragile than either of its parts.** The worst case is LUNet on REYIA: CRAE 0.82
and CRVE 0.86, but AVR 0.31. A ratio of two widths moves whenever either moves, and whenever an
artery is called a vein. That is the artery/vein classification error the
[artery/vein benchmark](av-results.md) §3.1 found LUNet makes asymmetrically.

### 2.1 AVRDB, and what it does to the pooled figures

**On AVRDB every model fails at once.** CRAE agreement is between 0.07 and 0.39, and fractal
dimension between 0.01 and 0.13. The [artery/vein results](av-results.md) §4.1 already found that
AVRDB's vessels are drawn about 1.6 times wider than any model traces them, as strokes of one chosen
width. The scatter plots in notebook section 2.3 show the consequence: AVRDB's points form a
separate cloud below the diagonal, with expert-map CRAE values of 175–240 µm where the model's
maps give about 150. A wide even stroke makes every vessel look like a major one, so calibre and
fractal dimension measured on it describe the drawing rather than the eye.

Pooled without AVRDB, computed in notebook section 7.4 by the run's own function:

| Model | CRAE | CRVE | AVR | Artery FD | Artery tortuosity |
| --- | --- | --- | --- | --- | --- |
| vascx-artery-vein | 0.77 *(0.49)* | 0.83 *(0.63)* | 0.65 *(0.55)* | 0.75 *(0.38)* | 0.81 *(0.81)* |
| ocularnet | 0.81 *(0.83)* | 0.85 *(0.87)* | 0.76 *(0.73)* | 0.91 *(0.80)* | 0.89 *(0.88)* |
| lunet | 0.68 *(0.35)* | 0.79 *(0.46)* | 0.36 *(0.33)* | 0.84 *(0.41)* | 0.84 *(0.83)* |
| automorph-artery-vein | 0.62 *(0.41)* | 0.74 *(0.56)* | 0.50 *(0.42)* | 0.64 *(0.31)* | 0.82 *(0.80)* |
| bf-net | 0.31 *(0.28)* | 0.31 *(0.33)* | 0.24 *(0.21)* | 0.26 *(0.10)* | 0.64 *(0.63)* |

*In brackets: the pooled figure with AVRDB, from section 1.*

**OCULARNet is the one model AVRDB barely moves**, and it is also the only one that trained on
AVRDB. Its 0.39 there against the others' 0.07–0.09 is most plausibly a model reproducing the
drawing style it was taught, not a model seeing vessels better. Without AVRDB the gap between
OCULARNet and VascX on calibre shrinks from 0.34 to 0.04. **AVRDB stays in the pooled figures**,
as it does on the artery/vein page: it is a real annotation by four ophthalmologists, and dropping a
dataset because models score badly on it is how a benchmark becomes a leaderboard.

### 2.2 REYIA by subset

REYIA is a compilation of collections from different cameras and clinics. Notebook section 7.3
breaks it down. **Two of its eight subsets, mBRSET (27 photographs) and TREND-AV (48), are hard
for every model.** OCULARNet's AVR there is 0.30 and 0.41 against 0.75–0.95 on its other subsets,
and LUNet's CRAE on mBRSET falls to 0.11. These are also the two subsets OCULARNet did not train on.
PAPILA is the third weak subset, for AutoMorph's model and BF-Net above all.

## 3. Every catalogued biomarker, by family

The panel is five numbers out of hundreds. fundus-biomarkers returns 629 catalogued columns that
have at least 20 paired photographs. Notebook section 3 shows the distribution of their pooled
ICC(A,1), SNR and IQR/MAPE, family by family.

| Model | Calibre | Tortuosity | Density | Topology |
| --- | --- | --- | --- | --- |
| vascx-artery-vein | 0.48 · 0% | 0.50 · 15% | 0.54 · 5% | 0.40 · 0% |
| ocularnet | 0.77 · 59% | 0.70 · 40% | 0.81 · 77% | 0.67 · 8% |
| lunet | 0.35 · 0% | 0.59 · 21% | 0.56 · 5% | 0.51 · 0% |
| automorph-artery-vein | 0.42 · 0% | 0.55 · 17% | 0.43 · 2% | 0.49 · 0% |
| bf-net | 0.21 · 0% | 0.28 · 0% | 0.24 · 0% | 0.19 · 0% |

*Each cell: median pooled ICC(A,1) across the family's columns · share of its columns at 0.75 or
above.* These are pooled with AVRDB (section 2.1).

- **No biomarker survives every model.** Not one of the 629 columns reaches ICC(A,1) 0.9 under all
  five models, and **133 stay below 0.5 under all five**.
- **The fragile ones are mostly standard deviations and counts**, listed in notebook section 3.1:
  the spread of tortuosity or branching angle within an eye, the number of separate vessel pieces,
  the number of vessel endpoints. They measure exactly what a segmentation model changes, which
  is how many short fragments it draws, so they move with the map rather than with the eye.
- **Topology does not transfer even where everything else does.** Under OCULARNet, 59% of calibre
  and 77% of density columns reach 0.75, but only 8% of topology columns.

**Which summary of a tortuosity is taken matters more than which model.** In fundus-biomarkers,
under each of the four stronger models, the **median** arc-to-chord ratio of the arteries agrees at
0.80–0.88, and the **mean** and **length-weighted mean** of the same measurement at 0.37–0.61
(section 4.1). A median ignores the few short, wiggly fragments a
model adds or drops; a mean takes them all in.

## 4. Where the programs disagree

### 4.1 One biomarker, seven programs

The same biomarker on the same pair of maps, computed by different programs. Where one program is
robust and another fragile, the difference is in the program's tracing and measuring, not in the
model. Pooled ICC(A,1), from notebook section 4:

| Biomarker | Program | vascx-artery-vein | ocularnet | lunet | automorph-artery-vein | bf-net |
| --- | --- | --- | --- | --- | --- | --- |
| CRAE | automorphalyzer | 0.60 | 0.86 | 0.44 | 0.57 | 0.39 |
| | fundus-biomarkers | 0.49 | 0.83 | 0.35 | 0.41 | 0.28 |
| | vascx | 0.56 | 0.85 | 0.40 | 0.50 | 0.33 |
| | pvbm | 0.08 | 0.17 | 0.12 | 0.08 | 0.06 |
| CRVE | automorphalyzer | 0.71 | 0.88 | 0.57 | 0.63 | 0.43 |
| | fundus-biomarkers | 0.63 | 0.87 | 0.46 | 0.56 | 0.33 |
| | vascx | 0.63 | 0.85 | 0.49 | 0.53 | 0.33 |
| | pvbm | 0.07 | 0.25 | 0.29 | 0.19 | 0.06 |
| AVR | fundus-biomarkers | 0.55 | 0.73 | 0.33 | 0.42 | 0.21 |
| | pvbm | 0.02 | 0.13 | 0.11 | 0.10 | −0.02 |
| Artery FD | automorphalyzer | 0.73 | 0.89 | 0.82 | 0.57 | 0.32 |
| | automorphclass | 0.72 | 0.88 | 0.82 | 0.52 | 0.31 |
| | automorph | 0.48 | 0.79 | 0.65 | 0.37 | 0.19 |
| | fundus-biomarkers | 0.38 | 0.80 | 0.41 | 0.31 | 0.10 |
| Artery tortuosity, median | fundus-biomarkers | 0.81 | 0.88 | 0.83 | 0.80 | 0.63 |
| | pvbm | 0.65 | 0.72 | 0.70 | 0.68 | 0.05 |
| | ocular | 0.65 | 0.72 | 0.70 | 0.68 | 0.05 |
| Artery tortuosity, length-weighted | vascx | 0.71 | 0.77 | 0.70 | 0.66 | 0.55 |
| | ocular | 0.61 | 0.81 | 0.69 | 0.72 | 0.14 |
| | automorphclass | 0.48 | 0.64 | 0.28 | 0.50 | 0.11 |
| | fundus-biomarkers | 0.39 | 0.58 | 0.37 | 0.41 | 0.28 |
| Artery tortuosity, mean | automorph | 0.48 | 0.52 | 0.50 | 0.37 | 0.38 |
| | automorphalyzer | 0.46 | 0.52 | 0.48 | 0.41 | 0.20 |
| | fundus-biomarkers | 0.45 | 0.61 | 0.42 | 0.47 | 0.36 |

**PVBM's central retinal equivalents do not survive a change of map under any model**: ICC(A,1)
0.06–0.29. The cause is visible on the expert's maps alone. PVBM's CRAE there has a standard
deviation of 79 µm on a mean of 124, against fundus-biomarkers' 33 µm on 147. It also produced an
equivalent for only 590–655 of the 885 photographs, against 884 for fundus-biomarkers. A
measurement that scattered on the reference cannot agree with itself on a second map. This is a
finding about PVBM's vessel selection for the equivalents, not about any model, and it matches the
[synthetic benchmark](biomarker-synthetic-results.md)'s caution about PVBM calibre.

**The three Knudtson implementations that do survive agree closely with each other**:
AutoMorphalyzer, fundus-biomarkers and VascX are within 0.16 of one another under every model.
AutoMorphalyzer is slightly the steadiest. VascX's figures were measured at the pinned commit
`d0cde1c`, which predates an upstream fix to its CRE pairing (section 8).

**PVBM and OCULAR return identical median tortuosities**, to two decimals under every model.
OCULAR's adapter reuses PVBM's code at the same commit, so this is one measurement, not two.

**Fractal dimension depends on the program as much as on the model.** Under LUNet, the same
box-counting fractal dimension of the same maps agrees at 0.82 in AutoMorphalyzer and AutoMorphClass
but at 0.41 in fundus-biomarkers. fundus-biomarkers' zone-B version is steadier than its
whole-picture one (0.57 against 0.41 under LUNet), which suggests the disagreement is concentrated
in the periphery of the photograph, where the smallest vessels are.

### 4.2 Coverage

**Where a model's map produced no panel number and the expert's did**, pooled, from notebook
section 1.1: none for VascX, OCULARNet or LUNet, except a single CRVE each. AutoMorph's model lost 3
to 7 per biomarker. **BF-Net lost 12 to 43**, most on artery tortuosity, where its fragmented
arteries leave nothing to measure.

**Maps on which a program returned nothing at all**:

| Implementation | Maps measured | Returned nothing | Why |
| --- | --- | --- | --- |
| pvbm, ocular, automorph, automorphclass | 5,976 each | 2 each | AutoMorph's model's maps of two REYIA PAPILA photographs |
| automorphalyzer | 5,976 | 13 | 11 in REYIA's PAPILA subset and 2 in AVRDB, all BF-Net's or AutoMorph's maps: a division by zero in its own code |
| vascx | 5,976 | 0 | |
| fundus-biomarkers | 5,976 | **666** | the 111 photographs with no microns-per-pixel scale × 6 maps, by design (above) |

## 5. What the failures look like

Notebook section 5 shows, for each dataset, the photograph where a model's map moved CRAE furthest
from the expert's: the photograph, the expert's map and the model's map side by side. **Every one
of the five is BF-Net's**, and they show two distinct failures:

- **It draws the edge of the field of view as a vein** (AVRDB `im004790`, RAV `rav_640937`). It
  loses nearly the whole network and outlines the camera's circular mask instead. CRAE falls by
  81–87%.
- **It inflates calibre** where it traces the network but thickens it (HRF `01_dr`, +109%; REYIA
  `trend_30_r`, +88%).

The same figure shows **why HRF is hard for everyone**. Its expert draws the small vessels as
hairlines and the major ones as narrow strokes, so the expert-map CRAE of `01_dr` is 76 µm, about
half the population mean of 147.

## 6. What it costs

**Seconds per map for each program**, averaged over every map it measured, on one core of this
machine, a 16-core x86 Linux server. This measures the machine as much as the program. The
benchmark ran ten or fifteen processes at once, one per core.

| Implementation | AVRDB | Fundus-AVSeg | HRF | RAV | REYIA |
| --- | --- | --- | --- | --- | --- |
| pvbm | 24.6 | 48.9 | 235.2 | 23.7 | 62.3 |
| ocular | 3.2 | 6.8 | 31.3 | 3.1 | 8.1 |
| automorph | 10.7 | 9.4 | 11.6 | 11.3 | 6.3 |
| automorphalyzer | 6.1 | 15.3 | 82.1 | 6.3 | 22.4 |
| automorphclass | 0.5 | 1.1 | 6.8 | 0.5 | 1.3 |
| vascx | 3.7 | 7.6 | 34.2 | 3.1 | 7.7 |
| fundus-biomarkers | 7.3 | 16.8 | 68.9 | 5.6 | 12.6 |

**Frame size dominates.** HRF's crops are about 3,300 pixels across, and every program but AutoMorph
takes about ten times as long there as on AVRDB. AutoMorph is flat because it resizes everything to
912 pixels before measuring. **PVBM is the slowest by a factor of about three**, at nearly four
minutes for one HRF map.

The models' own segmentation time is in the [artery/vein results](av-results.md) §1, measured on
Apple MPS except LUNet: OCULARNet 5.7 seconds a photograph, AutoMorph 10.9, VascX 11.4, LUNet 27.9
(on CPU) and BF-Net 0.5.

## 7. Which model to use

**The answer depends on the biomarker, and on whether your photographs resemble AVRDB.** Every
recommendation below is agreement with **one expert's map** per photograph. No dataset here has a
second reader, so nothing here says where the ceiling is, and no biomarker here is validated by
agreeing with it.

**For calibre (CRAE, CRVE, AVR), use [OCULARNet](../models/ocularnet.md), with VascX close behind
on typical photographs.** OCULARNet leads pooled (CRAE 0.83, CRVE 0.87, AVR 0.73, against VascX's
0.49, 0.63 and 0.55) and costs 5.7 seconds a photograph against VascX's 11.4. **But its lead is
mostly in-sample and mostly AVRDB.**

- Without AVRDB the margin is 0.04 on CRAE, 0.02 on CRVE and 0.11 on AVR.
- **On the photographs OCULARNet never saw** (notebook section 7.5), the comparison reverses or
  ties:

  | Photographs | Model | CRAE | CRVE | AVR |
  | --- | --- | --- | --- | --- |
  | RAV, 155 | VascX | 0.87 | 0.89 | 0.47 |
  | | OCULARNet | 0.78 | 0.86 | 0.66 |
  | REYIA mBRSET + TREND-AV, 75 | VascX | 0.69 | 0.72 | 0.54 |
  | | OCULARNet | 0.69 | 0.57 | 0.40 |

  On RAV, VascX is in-sample itself with an unclear split. On mBRSET and TREND-AV both are
  held out, and VascX is ahead on CRVE and AVR, on 75 photographs.

  A study whose photographs are unlike any training set should not treat OCULARNet's pooled lead as
  established. On held-out data the two are close, and VascX holds its AVR better.

**For fractal dimension, use OCULARNet, and pick the program as carefully as the model.** It leads
with or without AVRDB (0.80 pooled, 0.91 without). LUNet is second without AVRDB at 0.84. Under
AutoMorphalyzer or AutoMorphClass, LUNet's maps agree at 0.82 even with AVRDB included (section
4.1). LUNet's training data is undocumented (`unknown`), so its figures carry no contamination
mark either way.

**For tortuosity, any of the four stronger models will do, if you take the median.** Median
arc-to-chord tortuosity agrees at 0.80–0.88 pooled under VascX, OCULARNet, LUNet and AutoMorph's
model, and at 0.64–0.92 on every dataset. The margin between the best and the fourth is 0.08, too
small to choose on. Choose by cost or by what else the study needs. **The mean or length-weighted
mean of the same measurement is not safe under any model** (section 3).

**Do not use BF-Net for any biomarker.** Its SNR is below 1 on four of the five panel biomarkers:
its error is larger than the differences between eyes. It is the cheapest model by an order of
magnitude, at 0.5 seconds, but section 5 shows why that is not a saving.

**For the program**, the question is the synthetic benchmark's, not this one's. But two findings
here bear on it: **do not use PVBM's central retinal equivalents** (section 4.1), and prefer a
median to a mean wherever a program offers both.

**Caveats that would change these answers:**

- **Contamination.** OCULARNet trained on HRF, Fundus-AVSeg, AVRDB and six of REYIA's eight
  subsets. VascX's model trained on HRF and RAV. LUNet's training data is unknown.
- **AVRDB's annotation style** decides the pooled ranking on calibre and fractal dimension
  (section 2.1). Whether a model *should* reproduce a wide-stroke drawing is a question about the
  reference, not the model.
- **One reader per photograph.** A model disagreeing with the expert by as much as a second expert
  would has matched the reference, not failed it.
- **fundus-biomarkers' panel leaves out the 111 photographs with no scale.** The other programs'
  scale-free numbers include them, so section 4.1 compares slightly different photographs for
  dimensionless biomarkers.

## 8. What these numbers do not say

- **Nothing about the reference's own noise.** No dataset here publishes a second annotator, so the
  inter-reader band, which is the ceiling every ICC here should be read against, is unknown.
- **Nothing about whether a program is right.** Two maps agreeing under one program says the
  program is stable to the change of map. Whether it computes what it claims is the
  [synthetic benchmark](biomarker-synthetic-results.md)'s question.
- **Nothing about the optic disc.** Both maps of a photograph share one disc estimate from the
  SegFormer disc model, so a wrong disc moves both numbers alike and is invisible here. The
  [disc benchmark](disc-results.md) measures that.
- **Nothing anchored to the fovea.** No fovea is located for these photographs, so VascX's
  fovea-dependent features come back empty, as they should.
- **VascX's equivalents carry an upstream defect at the pinned commit.** At `d0cde1c`, VascX's
  Knudtson CRE sorts the vessel widths once instead of before every pairing round. Its authors
  fixed this on 2026-09-24 (upstream commit `5e76d60`). The fix changes VascX's CRAE, CRVE and AVR
  values. It moves the expert-map and model-map values of a pair together, so its effect on
  agreement here is expected to be small; its effect on accuracy is the synthetic benchmark's
  question. The atlas will move VascX to the fixed commit and measure again.
- **Pooled means pooled on the photographs**: 45 from HRF weigh as 45, and 486 scaled REYIA
  photographs as 486. REYIA therefore dominates every pooled figure.
- **A length on a photograph with no scale** is left out of its statistic. For fundus-biomarkers,
  that photograph is left out of every statistic.
