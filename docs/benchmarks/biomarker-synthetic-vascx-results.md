# Synthetic biomarker benchmark — VascX

[VascX](../projects/vascx.md) measured against shapes whose values follow from their geometry —
**32 renderings, 81 comparable measurements** — on a 2048² grid at 5 µm per pixel.

VascX is the one implementation in this catalogue that shares no code with any other. PVBM is its
own lineage, the [three AutoMorph projects](biomarker-synthetic-automorph-results.md) descend from
retipy, and OCULAR imports PVBM outright. VascX reimplements every biomarker as a configurable
object with documented parameters, and it is the only one that works in **physical units**, because
it is the only one that takes a scale.

Every number here comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic-vascx.ipynb](../../notebooks/biomarker-synthetic-vascx.ipynb).

***This benchmark selects nothing.***

## Contents

1. [The most accurate calibre measured here](#1-the-most-accurate-calibre-measured-here)
2. [Tortuosity: exact on straight vessels, short on curved ones](#2-tortuosity-exact-on-straight-vessels-short-on-curved-ones)
3. [Where the disagreement is ours](#3-where-the-disagreement-is-ours)
4. [A disc that resizes itself to 1024](#4-a-disc-that-resizes-itself-to-1024)
5. [What these numbers do not say](#5-what-these-numbers-do-not-say)

## 1. The most accurate calibre measured here

| Quantity | Mean | Worst | Samples |
| --- | --- | --- | --- |
| `vessel-calibre/mean-width/artery` | +0.69% | 0.69% | 8 |
| `vessel-calibre/mean-width/vein` | +0.64% | 0.69% | 8 |
| `central-retinal-equivalents/knudtson/artery` | +0.67% | 0.68% | 8 |
| `central-retinal-equivalents/knudtson/vein` | +0.69% | 0.69% | 8 |

Four quantities, every shape, every angle, all within **seven-tenths of one per cent** and all in
the same direction — the signature of a mask a fraction of a pixel wider than the vessel drawn, and
nothing else.

For scale, on the same shapes: PVBM's Knudtson equivalent is 6.3% low on arteries and
AutoMorphalyzer's 0.5% low, while AutoMorph and AutoMorphClass compute none at all. On calibre,
AutoMorphalyzer and AutoMorphClass read 23% and 25% high at worst.

**It is also the only implementation whose lengths are physical.** It returns millimetres because it
is given a scale; the adapter converts the two mapped lengths back into pixels using the very scale
the shape was built with, which makes that conversion exact rather than an estimate. Nothing else is
converted.

*Our finding, 2026-09-22, from reading `cre.py`:* its `CRE` class combines pairs as
`c·√(d₁² + d₂²)` with c = 0.88 for arteries and 0.95 for veins — **that is Knudtson's formula**.
[`docs/projects/vascx.md`](../projects/vascx.md) §6 describes it as a "Hubbard reduction,
√(d₁²+d₂²), with the artery and vein constants 0.88 and 0.95", which is self-contradictory: Hubbard's
variant carries fitted constants and an additive term, and neither appears in the code. It is mapped
to the Knudtson name here on the strength of the formula rather than the label.

## 2. Tortuosity: exact on straight vessels, short on curved ones

| Shape | Artery | Vein |
| --- | --- | --- |
| straight | **+0.08%** | +0.02% |
| disjoint | −0.01% | +0.01% |
| artery-vein-pair | −0.00% | −0.00% |
| spokes-macula-centred | +0.03% | +0.01% |
| spokes-disc-centred | +0.03% | +0.05% |
| **arc** | **−9.92%** | — |
| **sinusoid** | **−17.18%** | −17.31% |

**On anything straight it is exact to a rounding error.** No other implementation here is within
four per cent of that: PVBM reads 7.3% high on a straight vessel at 30°, AutoMorphalyzer 4.5%,
AutoMorphClass 3.7%, and AutoMorph returns 0.

**On curved vessels it reads short**, and that is the cost of how it gets the straight case right.
It fits splines to the vessel and caps each segment at 0.2 disc diameters, so it smooths — and a
smoothed curve is shorter than the curve it was fitted to.

**The two errors are not interchangeable.** Every other implementation here *over*-reports
tortuosity, because it measures a digitised path by counting pixel steps and weighting a diagonal as
√2; that error depends on the vessel's angle to the camera. VascX *under*-reports, in proportion to
how curved the vessel actually is — which is the quantity being measured. Neither is noise and they
point opposite ways, so a study switching between these implementations would see tortuosity move
for two unrelated reasons at once.

## 3. Where the disagreement is ours

VascX's grids are oriented on the **disc-to-fovea axis**, and every feature fails with "Disc or
fovea location not set" without a fovea. A synthetic shape has no macula, and inventing one would
make the answer a property of the fixture.

The adapter therefore supplies a fovea from the *framing*: the frame centre, which is what
macula-centred means and the point every shape here is rotated about, or one standard separation
from a disc that is itself centred. That is a convention of this benchmark, not a measurement — so
**everything measured against that axis is left uncatalogued**: superior, inferior, temporal and
nasal fields, the temporal angle, and the disc-fovea distance. They are measured, stored under
VascX's own names, and compared against nothing. A test enforces it.

Two other columns are uncatalogued for plainer reasons: its vessel density is measured over a
disc-centred circle, which is neither the field of view nor the whole frame, and its sparsity is a
mean where the catalogued variant is a maximum.

**The region is not quite the others'.** VascX measures on a circle 1.1667 disc *diameters* from the
disc centre — 2.33 disc radii — where PVBM and AutoMorphalyzer measure over the annulus from 2 to 3
radii. That is inside their band rather than equal to it: near enough that the numbers are worth
comparing, far enough that part of any difference is the region.

## 4. A disc that resizes itself to 1024

***`rtnls_enface.disc.OpticDisc.__init__` takes `size=1024`, and nothing passes the retina's own
resolution to it.***

*Our finding, 2026-09-22.* Hand VascX a 2048-pixel retina and the disc mask is silently resized to
1024. Every feature measured on a circle around the disc then indexes outside the mask and fails —
**34 of the 36 otherwise computable features are lost**, leaving only the two that need no disc. It
raises nothing: each failure is a warning, and `calc_features` returns `None` in that column.

The adapter rebuilds the disc at the frame's own size, which is what makes VascX measurable here at
all. This is the same class of defect as [AutoMorph's 912-pixel
resize](biomarker-synthetic-automorph-results.md#4-width-and-a-resize-nobody-asked-for): a pipeline
assumption about image size, harmless inside the pipeline that always satisfies it, sharp for
anyone calling the library on their own masks.

## 5. What these numbers do not say

- **Nothing about photographs.** Every shape here is clean, binary and noiseless, and VascX's
  advantage on calibre may be larger or smaller on a segmentation with a ragged boundary.
- **Nothing about most of what VascX computes.** The shipped disc-centred set has 67 features, 36
  compute on these shapes, and 8 have a value to be checked against.
- **Nothing about the fovea-anchored biomarkers it is unusual in having** — the temporal angle and
  the disc-fovea distance are exactly the measurements a synthetic shape cannot test.
- **Nothing that selects.** No implementation passes or fails here.

---

**Compiled from `notebooks/biomarker-synthetic-vascx.ipynb` on:** 2026-09-22 · **Measured by**
`python -m benchmarks --benchmark biomarker-synthetic`
