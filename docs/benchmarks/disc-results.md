# Disc-and-cup benchmark — results

Four models were asked, of 2,464 photographs, to draw the two outlines a glaucoma assessment rests
on: the **optic disc**, the pale area where the nerve leaves the eye, and the **cup**, the hollow
inside it. Their outlines are compared here with the ones ophthalmologists drew — **33,328
comparisons in all**, because a photograph five experts outlined is scored against each of them
separately.

Every number comes from `results/disc/`; the reading of them comes from
[notebooks/disc.ipynb](../../notebooks/disc.ipynb). How the benchmark is configured is a separate
page: [disc-docs.md](disc-docs.md).

**4 of 6 declared models** and **3 of 7 declared datasets** took part. BEAL and ISFA are declared and
not measured — ISFA publishes an ImageNet backbone rather than trained weights, BEAL's weights sit in
an unversioned Google Drive folder that nothing can pin. REFUGE, Drishti-GS, ORIGA and RIM-ONE DL are
declared and not yet fetched.

## Contents

1. [Summary](#1-summary)
2. [Where the boundary sits](#2-where-the-boundary-sits)
   · [2.1 What the outlines actually measure](#21-what-the-outlines-actually-measure)
3. [The cup-to-disc ratio](#3-the-cup-to-disc-ratio)
4. [Dataset by dataset](#4-dataset-by-dataset)
5. [Against the readers' own disagreement](#5-against-the-readers-own-disagreement)
6. [Which model to use](#6-which-model-to-use)
7. [What these numbers do not say](#7-what-these-numbers-do-not-say)

## 1. Summary

All three datasets pooled, one row per model. **Dice** measures overlap with the expert's outline,
from 0 (nothing in common) to 1 (identical). **Ratio error** is signed: positive means the model
reads the cup-to-disc ratio *higher* than the ophthalmologist did, which is the direction that sends
people to a clinic.

| Model | Photographs | Coverage | Disc Dice | Cup Dice | Ratio error | Marked |
| --- | --- | --- | --- | --- | --- | --- |
| [vascx-disc](../models/vascx-disc.md) | 2,464 | 1.000 | **0.951** | — | — | unknown |
| [lunetv2-odc](../models/lunetv2-odc.md) | 2,464 | 1.000 | 0.937 | **0.810** | **−0.001** | unknown |
| [segformer-disc-cup](../models/segformer-disc-cup.md) | 2,464 | 1.000 | 0.937 | 0.791 | −0.039 | out-of-sample |
| [automorph-disc-cup](../models/automorph-disc-cup.md) | 2,464 | 1.000 | 0.856 | 0.712 | −0.031 | out-of-sample |

**Coverage is 1.000 everywhere**: every model produced an outline for every photograph, and none of
the 33,328 comparisons failed. These are segmentation networks — unlike a quality grader, none of
them has a way of declining.

**VascX finds only the disc.** It is absent from every cup column rather than scored zero in them,
and the cup-to-disc ratio cannot be computed without a cup.

**A dash in the ratio column is not a good result.** The two models that look closest here — LUNet v2
at −0.001 and SegFormer at −0.039 — are separated by more than that number suggests once the sign is
taken off: section 3.

## 2. Where the boundary sits

Dice is the least informative number on this page, and the summary hides what separates models that
share it. LUNet v2 and SegFormer both sit at 0.937 on the disc and do quite different things with it.

**Is the structure in the right place?** The distance between the model's centre and the expert's,
measured in the expert's own disc diameters so that photographs of different sizes can be read
together:

| Model | Disc centre offset, in disc diameters (median) |
| --- | --- |
| vascx-disc | **0.015** |
| lunetv2-odc | 0.016 |
| segformer-disc-cup | 0.017 |
| automorph-disc-cup | 0.019 |

All four place the disc within two hundredths of a diameter — about 7 pixels on a typical
2,200-pixel photograph. **Nothing here is lost by mislocating the disc.** Whatever separates these
models is size and boundary, not position.

**Is it the right size?** Signed mean errors, in native pixels; negative means the model drew the
structure *smaller* than the ophthalmologist did:

| Model | Disc width | Disc height | Disc radius | Cup width | Cup height | Cup radius |
| --- | --- | --- | --- | --- | --- | --- |
| segformer-disc-cup | **+8.6** | **+2.2** | **+1.3** | −4.2 | −14.6 | −5.2 |
| vascx-disc | −7.7 | −9.7 | −4.4 | — | — | — |
| lunetv2-odc | −12.6 | −17.4 | −9.5 | −4.7 | −9.9 | −5.8 |
| automorph-disc-cup | −10.3 | −7.7 | −12.6 | +1.2 | −15.4 | −7.0 |

Two things worth reading here. **Every model draws the cup short** — between 10 and 15 pixels less
tall than the expert, consistently, all four — and a cup that is too short in a disc of about the
right height is a cup-to-disc ratio that reads low. And **only SegFormer's disc errs large**; the
other three draw both structures small, so their two errors partly cancel in the ratio while
SegFormer's compound.

**A signed bias is worse than scatter of the same size**, because it moves every patient the same
way. All the biases above are signed and none is negligible.

### 2.1 What the outlines actually measure

Errors are differences, and a difference is not a measurement. These are the outlines themselves,
as medians in the pixels of the original photograph — what the ophthalmologists drew, and what each
model drew on the same photographs.

What the readers drew:

| Dataset | Disc width | Disc height | Disc radius | Cup width | Cup height | Cup radius |
| --- | --- | --- | --- | --- | --- | --- |
| chaksu | 399 | 426 | 206.5 | 209 | 216 | 106.1 |
| grape | 224 | 260 | 120.9 | 120 | 137 | 63.6 |
| papila | 446 | 477 | 228.4 | 158 | 171 | 81.5 |

What each model drew:

| Model | Dataset | Disc width | Disc height | Disc radius | Cup width | Cup height | Cup radius |
| --- | --- | --- | --- | --- | --- | --- | --- |
| vascx-disc | chaksu | 388 | 415 | 200.0 | — | — | — |
| | grape | 239 | 283 | 130.0 | — | — | — |
| | papila | 446 | 472.5 | 228.7 | — | — | — |
| segformer-disc-cup | chaksu | 406 | 426 | 207.2 | 191 | 187 | 93.5 |
| | grape | 246 | 281 | 132.4 | 146 | 157 | 74.6 |
| | papila | 468 | 483 | 236.9 | 212 | 209 | 105.8 |
| lunetv2-odc | chaksu | 378 | 407 | 195.0 | 197 | 200 | 96.9 |
| | grape | 241 | 276 | 127.6 | 156 | 170 | 79.6 |
| | papila | 422.5 | 456.5 | 217.7 | 138 | 146 | 69.1 |
| automorph-disc-cup | chaksu | 391 | 427 | 201.0 | 205 | 191 | 95.3 |
| | grape | 240 | 276 | 128.9 | 139.5 | 157.5 | 74.1 |
| | papila | 410 | 416 | 194.6 | **234** | **224** | 110.5 |

Read the bottom row against the readers' PAPILA line: where the ophthalmologists drew a cup of
158 × 171 pixels, **AutoMorph drew 234 × 224** — about half again as wide — inside a disc it drew
*smaller* than they did (410 × 416 against 446 × 477). Both errors push the cup-to-disc ratio the
same way, which is why its PAPILA bias in section 3 is +0.166 rather than the near-zero its Chákṣu
figures might suggest.

The rest is calmer than the Dice scores imply. On Chákṣu and GRAPE every model's disc is within
about 5% of the readers' in each dimension, and the disagreement that matters is in the cup.

**Every number above is a column of the evidence** — `said_disc_width`, `said_cup_height`,
`said_disc_center_x` and their `truth_` counterparts, one row per reader — so a study that needs
the measurement rather than the error can take it from `results/disc/` without re-running anything.

## 3. The cup-to-disc ratio

This is the measurement that leaves the building. It is a quotient of two boundaries, so a model can
overlap both structures well and still get it wrong — the two errors need not cancel.

The summary's pooled figure flatters everything, because a bias of +0.09 on one dataset and −0.06 on
another averages to nearly nothing. Per dataset, with the *absolute* error beside the signed one:

| Model | Dataset | Bias (signed) | Spread | Mean \|error\| | Within 0.05 of the expert |
| --- | --- | --- | --- | --- | --- |
| lunetv2-odc | chaksu | −0.005 | 0.081 | 0.061 | **0.522** |
| | grape | +0.088 | 0.105 | 0.106 | 0.298 |
| | papila | −0.034 | 0.065 | **0.054** | **0.529** |
| segformer-disc-cup | chaksu | −0.062 | 0.079 | 0.077 | 0.396 |
| | grape | +0.034 | 0.104 | 0.085 | 0.384 |
| | papila | +0.083 | 0.098 | 0.102 | 0.272 |
| automorph-disc-cup | chaksu | −0.061 | 0.094 | 0.083 | 0.372 |
| | grape | +0.039 | 0.101 | 0.083 | 0.391 |
| | papila | +0.166 | 0.143 | 0.189 | 0.078 |

**The sign flips with the dataset for every model.** Each of the three reads the ratio low on Chákṣu
and high on GRAPE. That is not a property anyone can correct for with a constant: a model calibrated
on one collection carries the wrong correction to another.

### 3.1 How many patients this moves

A ratio error of 0.05 matters at 0.65 and not at 0.30. Taking **0.6** as the threshold — in common
use, and endorsed by nothing here — this is the share of comparisons where the model crosses it and
the ophthalmologist did not, or the reverse:

| Model | Dataset | Model over 0.6, expert under | Model under 0.6, expert over | Experts over 0.6 |
| --- | --- | --- | --- | --- |
| lunetv2-odc | chaksu | 0.061 | 0.105 | 0.193 |
| | grape | **0.263** | 0.022 | 0.301 |
| | papila | 0.011 | 0.017 | 0.077 |
| segformer-disc-cup | chaksu | 0.007 | **0.164** | 0.193 |
| | grape | 0.110 | 0.095 | 0.302 |
| | papila | 0.018 | 0.020 | 0.079 |
| automorph-disc-cup | chaksu | 0.013 | 0.171 | 0.193 |
| | grape | 0.120 | 0.069 | 0.302 |
| | papila | **0.177** | 0.012 | 0.072 |

**This is the table to read before choosing.** The two failure directions are not symmetric and no
model is good at both:

- **LUNet v2 on GRAPE flags 26% of eyes over the threshold that the expert placed under it** — on a
  glaucoma dataset where 30% genuinely are over. That is a lot of people sent forward.
- **SegFormer and AutoMorph on Chákṣu miss about one in six of the eyes the expert placed over the
  threshold**, the opposite and more dangerous error.
- **AutoMorph on PAPILA flags 18% falsely high** where only 7% of eyes are genuinely over — an error
  rate larger than the condition it is looking for.

## 4. Dataset by dataset

| Model | Chákṣu disc / cup | GRAPE disc / cup | PAPILA disc / cup |
| --- | --- | --- | --- |
| vascx-disc | 0.954 / — | 0.921 / — | 0.951 / — |
| segformer-disc-cup | **0.958** / 0.821 | 0.899 / 0.768 | 0.818 / 0.597 |
| lunetv2-odc | 0.938 / **0.831** | **0.929** / 0.746 | **0.936** / 0.703 |
| automorph-disc-cup | 0.895 / 0.753 | 0.907 / **0.772** | 0.554 / 0.396 |

The three datasets are not three samples of one thing. [Chákṣu](../datasets/chaksu.md) is 1,345
photographs from three cameras with five ophthalmologists each; [GRAPE](../datasets/grape.md) is 631
glaucoma follow-up photographs with one reader; [PAPILA](../datasets/papila.md) is 488 **disc-centred**
photographs with two.

### 4.1 AutoMorph collapses on PAPILA, and the others do not

AutoMorph's disc falls to **0.554** on PAPILA against 0.895 and 0.907 elsewhere — and its cup to
0.396. Nothing comparable happens to the other three: LUNet v2 scores 0.936 on the same photographs.

The notebook's size columns say what goes wrong rather than that something does: on PAPILA AutoMorph
draws the disc **51 pixels off centre and far too small**, and **9% of all its disc outlines land
below Dice 0.5** — not imprecise, but somewhere else. PAPILA is disc-centred at 30°, so the disc
fills a much larger share of the frame than in the macula-centred screening photographs AutoMorph
was fitted on. A model trained on one framing does not transfer to the other, and this is what that
looks like.

That has a practical consequence beyond this page: **AutoMorph's cup-to-disc ratio should not be
trusted on disc-centred photographs**, and AutoMorph's own pipeline has no check that would notice.

### 4.2 Where each model is strongest is not the same dataset

SegFormer has the best disc on Chákṣu and the third-best on PAPILA. LUNet v2 is the most even of the
four — 0.929 to 0.938 on the disc across all three — while being beaten on Chákṣu by two models that
are worse elsewhere. A single pooled ranking hides this, which is why section 1 has one table and
this section has another.

## 5. Against the readers' own disagreement

A model cannot be shown to be wrong by less than the ophthalmologists are wrong about each other.
Chákṣu's five readers and PAPILA's two were scored against each other exactly as the models were —
every reader against every other, on 60 photographs each, in the native frame:

| Dataset | Readers | Disc Dice | Cup Dice | Mean \|ratio difference\| |
| --- | --- | --- | --- | --- |
| chaksu | 5 (10 pairs) | 0.950 | 0.810 | 0.076 |
| papila | 2 (1 pair) | 0.933 | 0.846 | 0.033 |
| grape | 1 | — | — | — |

**GRAPE publishes one outline per photograph, so no ceiling can be computed for it at all**, and
nothing in section 4's GRAPE column can be called close to or far from human agreement.

Against those bands:

- **On Chákṣu's disc**, SegFormer (0.958) and VascX (0.954) are **at or above the readers' own
  agreement of 0.950**; LUNet v2 (0.938) sits just below.
- **On Chákṣu's cup**, LUNet v2 (0.831) and SegFormer (0.821) are **above the readers' 0.810**.
- **On PAPILA's disc**, VascX (0.951) and LUNet v2 (0.936) are above the readers' 0.933.
- **On PAPILA's cup, nothing is close**: the best model reaches 0.703 against a reader agreement of
  0.846.
- **On the ratio**, Chákṣu's readers differ from each other by 0.076 on average; LUNet v2 differs
  from them by 0.061, SegFormer by 0.077, AutoMorph by 0.083. On PAPILA the readers differ by 0.033
  and every model is worse than that.

**None of this means a model beat an expert**, and the page will not say so. A model that predicts
something like the average of the readers agrees with each of them better than two readers — each
with their own habits — agree with one another. What "at or above the band" means is the weaker and
still useful statement: **on that dataset and that structure, this model's disagreement with an
ophthalmologist is no larger than one ophthalmologist's disagreement with another, so the benchmark
cannot distinguish them.** Below the band, the room for improvement is unambiguously the model's.

The cup is the harder structure for people too: the readers agree on it far less than on the disc
(0.810 against 0.950 on Chákṣu), because its boundary is a judgement about where the nerve head
begins to slope. **Every cup number on this page rests on a softer reference than the disc numbers
do.**

## 6. Which model to use

**LUNet v2's ONNX file**, if you need a cup-to-disc ratio — with two caveats large enough to change
the answer, below. **VascX disc**, if you need only the disc and can afford five times the compute.

- **[LUNet v2](../models/lunetv2-odc.md)** has the best cup (0.810 pooled), the most even disc across
  the three datasets (0.929 to 0.938), the smallest ratio bias (−0.001 pooled, and the only model
  inside the readers' own ratio disagreement on Chákṣu), and the most photographs within 0.05 of the
  expert's ratio (0.52 on Chákṣu, 0.53 on PAPILA). It runs in **0.24 to 0.27 seconds per
  photograph** on a CPU, the cheapest here. Two caveats: it is marked **`unknown`** — nothing
  published says what it trained on, so none of these datasets can be called clean for it — and its
  own project, [PVBM](../projects/pvbm.md), **never reads the cup channel these numbers come from**,
  so nobody has evidenced it before. Its licence is unstated and its ancestor is non-commercial.
- **[VascX disc](../models/vascx-disc.md)** has the best disc on two of three datasets and the best
  pooled disc Dice (0.951), and is the steadiest: it never once drops below Dice 0.5 on more than
  0.3% of outlines. It finds **no cup**, so it cannot produce a cup-to-disc ratio at all, and it
  costs **1.2 to 1.3 seconds per photograph on an Apple GPU** against a quarter of a second for the
  other three. It also carries `unknown`.
- **[SegFormer](../models/segformer-disc-cup.md)** is the close second for a full disc-and-cup
  answer: the best disc on Chákṣu (0.958, above the readers' band) and a cup at 0.791 against LUNet
  v2's 0.810. It is the only model whose licence is clean — **Apache-2.0 on both code and weights** —
  and the only one of the four marked `out-of-sample` on every dataset with a published training
  list. If licensing or provenance matters more to you than a hundredth of Dice, this is the one to
  take. Watch its ratio: it misses one in six of Chákṣu's eyes over the 0.6 threshold.
- **[AutoMorph's disc-and-cup model](../models/automorph-disc-cup.md)** is last on every pooled
  measure here and unusable on disc-centred photographs (section 4.1). If you are running AutoMorph
  on macula-centred screening images, its 0.895/0.907 disc is serviceable; on anything disc-centred,
  it is not.

The choice between the top two is not about Dice. **If you need the cup-to-disc ratio, VascX cannot
give it to you at any score.** If you need only a disc — for a region of interest, a zone, a
measurement mask — VascX is the most accurate and the slowest, and LUNet v2 is within 0.014 of it at
a fifth of the cost.

All timings were measured on one Apple laptop (`mps` for three models, `cpu` for the ONNX file) and
measure that machine as much as the model. One figure on this page was first recorded at 5.9 seconds
per photograph and re-measured at 1.3 on an idle machine, with the scores identical to four decimal
places; treat the seconds as an order of magnitude, not a specification.

## 7. What these numbers do not say

- **`unknown` is not `out-of-sample`.** Both models recommended in section 6 carry it: neither VascX
  nor LUNet v2 publishes what it trained on, so neither can be shown not to have seen these
  photographs. The two `out-of-sample` models are the two that came third and fourth.
- **A model inside the readers' band has not been shown to be better than a reader**, for the reason
  in section 5. No sentence on this page should be quoted as "the model outperformed the
  ophthalmologists".
- **Two of the models emit exclusive classes** — a disc *ring* and the cup inside it — and this
  repository's adapters put ring and cup back together, because an expert's disc contour contains
  the cup. That decision is visible in `src/models/` and in nothing the models' own authors wrote.
- **Every score depends on the resampling path.** All four models emit probabilities that are carried
  to the full-resolution frame and thresholded there. Thresholding first and resampling the mask
  would give different numbers, and not by a constant — see [disc-docs.md](disc-docs.md) §1.
- **Chákṣu publishes each expert's own cup-to-disc ratio as a number, and this benchmark does not use
  it.** Every ratio here is computed from a contour by this repository. The store does not yet carry
  the published values, so the strongest available check on section 3 has not been made.
- **Three datasets are not a survey.** One is disc-centred, one is glaucoma follow-up, one is a
  five-reader screening set from three cameras. The four datasets this benchmark declares and has not
  fetched — REFUGE above all, which three of these models trained on — are what would turn
  "out-of-sample" from a label into a measured contrast.
- **Nothing here is a claim about glaucoma.** Every number is agreement with an outline somebody
  drew, and a cup-to-disc ratio is one input to a diagnosis rather than the diagnosis.

---

**Compiled from `notebooks/disc.ipynb` on:** 2026-09-17 · **Measured by**
`python -m benchmarks --benchmark disc`
