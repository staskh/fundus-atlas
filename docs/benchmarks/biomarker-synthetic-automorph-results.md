# Synthetic biomarker benchmark — the AutoMorph family

Three implementations of one lineage, measured against shapes whose values follow from their
geometry — **96 renderings, 372 comparable measurements** — on a 2048² grid at 5 µm per pixel.

[AutoMorph](../projects/automorph.md) measures a fundus photograph with code it inherited from
[retipy](../projects/retipy.md). [AutoMorphalyzer](../projects/automorphalyzer.md) rewrote that
measuring stage because its authors judged it wrong. [AutoMorphClass](../projects/automorphclass.md)
reimplemented it to package the pipeline as a PyTorch module.

**They share a page because they share a lineage.** Two of them are rewrites of the first, so they
compute the same quantities and a difference between their numbers is a change somebody made on
purpose. [PVBM](biomarker-synthetic-pvbm-results.md) shares no code with any of them and has a page
of its own.

Every number here comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic-automorph.ipynb](../../notebooks/biomarker-synthetic-automorph.ipynb).

***This benchmark selects nothing.*** Which implementation is fit to measure a real segmentation is
a judgement made by a person on this evidence.

## Contents

1. [The headline: a claimed fix, confirmed](#1-the-headline-a-claimed-fix-confirmed)
2. [Summary](#2-summary)
3. [What each reaches, and what it does not](#3-what-each-reaches-and-what-it-does-not)
4. [Width, and a resize nobody asked for](#4-width-and-a-resize-nobody-asked-for)
5. [The central retinal equivalents](#5-the-central-retinal-equivalents)
6. [Where the disagreement is ours](#6-where-the-disagreement-is-ours)
7. [What these numbers do not say](#7-what-these-numbers-do-not-say)

## 1. The headline: a claimed fix, confirmed

AutoMorphalyzer's authors state that AutoMorph extracted some vessel segments incorrectly, that
this exaggerated tortuosity, and that they corrected it. AutoMorphClass's author claims the same
fix in an issue thread. Neither claim had been checked against a tortuosity whose value is known.

τ1 is arc length over chord length, so a straight vessel's is exactly 1.

| Implementation | Worst error in τ1 | Median |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | **+587%** | 6.9% |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | **8.7%** | 5.0% |
| [AutoMorphClass](../projects/automorphclass.md) | **7.4%** | 5.1% |

**The rewrites work.** AutoMorph reads 3.41 where a 90° arc requires 1.11, and **0 on a straight
vessel** — which is not a value a ratio of two lengths can take. Both successors bring every shape
under 9%, and most of what remains is the naive chain code every implementation in this catalogue
shares (see [PVBM's page](biomarker-synthetic-pvbm-results.md) §3).

**It is not a small correction.** AutoMorph's error changes sign between shapes — +162% on the arc,
−63% on a straight vessel — so it cannot be calibrated away. A study using it is not reporting a
noisy version of the right number; it is reporting a different number whose relationship to the
vessel depends on the vessel.

This is what the synthetic shapes are for: an author's claim about their own software, tested
against a value neither party chose.

## 2. Summary

| Implementation | Comparable measurements | Within 2% | Columns | Catalogued |
| --- | --- | --- | --- | --- |
| AutoMorph | 120 | 32 | 18 | 15 |
| AutoMorphalyzer | 132 | 28 | 54 | 17 |
| AutoMorphClass | 120 | 21 | 18 | 15 |

The counts differ because the three reach different things, not because one was measured less
thoroughly — section 3.

**One implementation raised**: AutoMorphalyzer fails with `ZeroDivisionError` on every angle of the
bifurcation when measuring the artery. A Y of three arms and one junction is the simplest branching
structure there is. Nothing else in the family raised on anything.

## 3. What each reaches, and what it does not

| | AutoMorph | AutoMorphalyzer | AutoMorphClass |
| --- | --- | --- | --- |
| The six retipy measurements | yes | yes | yes |
| Measured in zones | zone stage, not reachable | **whole, B and C** | no |
| Central retinal equivalents | not reachable | **yes, Knudtson** | no |
| Measures at | **912², always** | the size it is given | the size it is given |

Three differences carry into every number above.

- **AutoMorph measures at 912² whatever it is handed.** `Retina._open_image` resizes every file it
  opens with bicubic interpolation, so what reaches its measuring code is a resampled copy of the
  mask. Section 4 is what that costs.
- **Only AutoMorphalyzer computes the equivalents.** AutoMorph assembles its own in a driver script
  rather than a callable, so no adapter can reach them without reimplementing them — which would be
  measuring this repository's CRAE rather than AutoMorph's. AutoMorphClass's vessel features take
  no disc at all.
- **Only AutoMorphalyzer measures in zones**, and *our finding, 2026-09-21, from reading
  `generate_zonal_masks`:* its **zone B is the annulus between two and three disc radii — exactly
  the region PVBM measures over**, while its zone C is two to five radii, which is nobody else's.
  Zone B is catalogued here and zone C keeps its own name, so the two are never silently equated.

## 4. Width, and a resize nobody asked for

| Implementation | Worst | Median |
| --- | --- | --- |
| AutoMorph | **+21,881%** | 7.4% |
| AutoMorphalyzer | +23.3% | 9.7% |
| AutoMorphClass | +25.5% | 13.1% |

**AutoMorph's width on a straight vessel is out by a factor of thirty on average and 219 at worst**,
and the cause is not its arithmetic. `Retina._open_image` puts every input through
`cv2.resize(..., (912, 912), INTER_CUBIC)`, and `global_cal` then divides the vessel area by the
skeleton length. A one-pixel-wide skeleton bicubically resampled to 45% of its size very nearly
disappears, so the denominator collapses and the ratio explodes.

**Its own pipeline never sees this**, because it hands the measuring stage images that are already
912². This is a property of the code rather than of any published result. But it is a sharp edge for
anyone calling that stage on their own masks, and it is silent: nothing raises, and a width of 3,517
pixels comes back looking like a measurement.

The two rewrites are steadier — 7% to 16% high on every shape, in one direction, which is what a
mask slightly wider than the vessel drawn looks like.

## 5. The central retinal equivalents

Only AutoMorphalyzer reaches them, and it is good at them.

| Quantity | AutoMorphalyzer | PVBM, same shapes |
| --- | --- | --- |
| `central-retinal-equivalents/knudtson/artery` | **0.5%** low | 6.3% low |
| `central-retinal-equivalents/knudtson/vein` | **2.8%** low | 2.6% low |

Both measure over the same annulus — two to three disc radii — so the two numbers are comparable,
and neither is wrong. They differ in how they measure the widths that go into Knudtson's recursion.

## 6. Where the disagreement is ours

All three carry a column named `squared_curvature_tortuosity`, and this repository mapped it to
Hart's τ3, the total squared curvature ∫κ² ds.

*Our finding, 2026-09-21, from reading retipy:* **it squares nothing.** It accumulates discrete
curvature at each sample and integrates it over the sample *index* rather than over arc length. The
shapes disagreed with the mapping by five orders of magnitude, and it does not match Hart's τ2
either — its ratio to the total curvature is 10.3 on the arc and 2.0 on the sinusoid, so no constant
relates them.

**The mapping is withdrawn.** The column is still measured and stored, under the implementations'
own name, and claims to be no catalogued biomarker. What is missing is a catalogued definition of
what discrete curvature summed over a pixel skeleton actually is. This is the second mapping a shape
has overturned; the first was PVBM's branching angle.

## 7. What these numbers do not say

- **Nothing about photographs.** Every shape here is clean, binary and noiseless. The differences
  between these three on a real segmentation may be larger or smaller.
- **Nothing about AutoMorph's published results.** Its resize defect is reached by handing its
  measuring stage a frame it would never be handed inside its own pipeline. What the tortuosity
  finding implies for published results is a separate question, and it was its successors' authors
  who raised it, not this repository.
- **Nothing about the fractal dimension or the vessel density**, which all three compute and no
  shape here pins a value for. They are recorded and compared against nothing.
- **Nothing that selects.** No implementation passes or fails here.

---

**Compiled from `notebooks/biomarker-synthetic-automorph.ipynb` on:** 2026-09-21 · **Measured by**
`python -m benchmarks --benchmark biomarker-synthetic`
