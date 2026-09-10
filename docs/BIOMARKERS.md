# Biomarkers

Measurements computed from the segmentations of a colour-fundus photograph — the numbers that end up
in a spreadsheet column. Each row links to a detail page describing that measurement: what it means,
who defined it, which competing definitions share its name, what it needs as input, and which
pipelines compute it.

**A biomarker name is not a definition.** "Tortuosity" names at least three incompatible formulas
and "CRAE" two; papers usually report the name and omit the choice. The Variants column below is
therefore the most important one in the table: two numbers under the same heading are comparable
only when their variant, their measurement region and their scale convention all match.

## 1. Summary

Grouped by family; alphabetical within each family.

### 1.1 Calibre — how wide the vessels are

| Biomarker | What it measures | Inputs | Region | Units | Variants | Computed by | Defined in | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Vessel calibre](biomarkers/vessel-calibre.md) | Vessel width | Vessels, or A/V | Varies — whole image, zones, grid fields | Pixels (microns with a resolution) | 3 (image edges, per-segment median, window average) | ARIA, VascX, AutoMorph, AutoMorphalyzer, AutoMorphClass, PVBM | Bankhead 2012 | 2026-09-10 |
| [Central retinal equivalents](biomarkers/central-retinal-equivalents.md) | Estimated trunk calibre near the disc (CRAE, CRVE) | A/V + disc | Ring around the disc; radii differ | Pixels or microns | 2 (Hubbard, Knudtson) | AutoMorph, AutoMorphalyzer (Knudtson only), VascX, PVBM, OCULARNet | Hubbard 1999; Knudtson 2003 | 2026-09-10 |
| [AVR](biomarkers/avr.md) | Arteriolar calibre relative to venular | A/V + disc | Same ring as its inputs | Dimensionless, **scale-invariant** | 2, inherited from the equivalents | AutoMorph, AutoMorphalyzer, VascX, PVBM (by division) | Hubbard 1999; Knudtson 2003 | 2026-09-10 |

### 1.2 Tortuosity — how twisted the vessels are

| Biomarker | What it measures | Inputs | Region | Units | Variants | Computed by | Defined in | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Tortuosity](biomarkers/tortuosity.md) | How far vessels deviate from straight | Vessels, or A/V | Varies — whole image, zones, grid fields | Mostly dimensionless; one is a count | **9+** (Hart τ1–τ7, Grisan density, and three implementation-only forms) | retipy, AutoMorph, AutoMorphalyzer, AutoMorphClass, VascX, PVBM, OCULARNet | No definition of record | 2026-09-10 |

### 1.3 Density and complexity — how much retina the vessels cover

| Biomarker | What it measures | Inputs | Region | Units | Variants | Computed by | Defined in | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Fractal dimension](biomarkers/fractal-dimension.md) | How thoroughly vessels fill the retina | Vessels, or A/V | Whole image (AutoMorph); disc annulus (PVBM) | Dimensionless | 2 (boundary-box counting, multifractal D₀/D₁/D₂ + singularity length) | AutoMorph, AutoMorphalyzer, AutoMorphClass, PVBM, OCULARNet | Standard box counting | 2026-09-10 |
| [Sparsity](biomarkers/sparsity.md) | How far tissue sits from the nearest vessel | Vessels + retinal mask | Full mask or any grid field | Pixels, or fraction of disc-fovea distance | 2 (mean, max) | VascX | VascX toolbox paper 2026 | 2026-09-10 |
| [Vascular density](biomarkers/vascular-density.md) | Fraction of retina covered by vessels | Vessels, or A/V | Whole image (AutoMorph); grid fields (VascX) | Dimensionless fraction | 2 (over retinal mask, over image) | VascX, AutoMorph, AutoMorphalyzer, AutoMorphClass, retipy | No single origin | 2026-09-10 |
| [Vessel area and length](biomarkers/vessel-area-and-length.md) | Total vessel area and skeleton length | A/V + disc | Annulus, 2–3 disc radii | Square pixels; pixels | 1 each | PVBM, OCULARNet | PVBM 2022 | 2026-09-10 |

### 1.4 Junctions and angles — how the vessels branch

| Biomarker | What it measures | Inputs | Region | Units | Variants | Computed by | Defined in | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Bifurcation angle](biomarkers/bifurcation-angle.md) | Angle at which a vessel splits | Vessels, or A/V | Grid fields (VascX); disc annulus (PVBM) | Degrees | 2 (fixed-distance sampling, median over vasculature) | VascX, PVBM, OCULARNet | Vascular branching theory | 2026-09-10 |
| [Junction counts](biomarkers/junction-counts.md) | Number of branch points, endpoints, crossings | Vessels, or A/V; disc; crossings class | Disc annulus (PVBM); grid fields (VascX) | Counts | 3 (PVBM's three classes, VascX bifurcations, OCULAR ROI masks) | PVBM, VascX, OCULARNet, retipy | PVBM 2022 | 2026-09-10 |
| [Temporal angle](biomarkers/temporal-angle.md) | Spread of the two temporal arcades | A/V + disc + **fovea** | Circles from ⅔ of the disc-fovea distance outward | Degrees, **scale-invariant** | 1 | VascX | VascX toolbox paper 2026 | 2026-09-10 |

### 1.5 Other

| Biomarker | What it measures | Inputs | Region | Units | Variants | Computed by | Defined in | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Cup-to-disc ratio](biomarkers/cup-to-disc-ratio.md) | Size of the optic cup relative to the disc | Disc **and cup** | Optic nerve head | Dimensionless, **scale-invariant** | 1 (height/width ratios) | AutoMorph, AutoMorphalyzer, AutoMorphClass | Clinical measure | 2026-09-10 |
| [Disc-fovea distance](biomarkers/disc-fovea-distance.md) | Distance between the two landmarks — and the ruler other measures use | Disc + fovea | Not applicable | Pixels; used as a normalisation factor | 1 | VascX | VascX toolbox paper 2026 | 2026-09-10 |

## 2. Traps found in the implementations

These came out of reading the code behind the pages above, not out of the papers. Each one can make
two numbers look comparable when they are not.

### 2.1 The Hubbard formula's constants are in microns, so it cannot be used on pixel widths

The two central-retinal-equivalent formulas are not the same kind of object. Knudtson combines a
pair of vessel widths as `0.88·√(w₁² + w₂²)` for arterioles and `0.95·√(w₁² + w₂²)` for venules —
purely multiplicative, so it can be computed on pixel widths and rescaled afterwards. Hubbard uses
`√(0.87·w₁² + 1.01·w₂² − 0.22·w₁·w₂ − 10.76)` and `√(0.72·w₁² + 0.91·w₂² + 450.05)`, and those
**additive** terms were fitted in microns. Feeding pixel widths into them is dimensionally wrong
rather than merely unscaled: the result is not a rescaled Hubbard value, it is a different number
that happens to look plausible.

[AutoMorph](projects/automorph.md) computes both variants, so its Hubbard columns are only
meaningful when a real pixel resolution was supplied.
[AutoMorphalyzer](projects/automorphalyzer.md) dropped Hubbard and kept Knudtson only — a choice its
authors present as simplification, and which this reading suggests was the right call. See
[central retinal equivalents](biomarkers/central-retinal-equivalents.md).

### 2.2 Tortuosity is six formulas wearing one name, and they do not agree on rank order

[Hart et al. 1999](https://www.siue.edu/~sumbaug/RetinalProjectPapers/Measurement%20and%20classification%20of%20retinal%20vascular%20tortuosity.pdf)
defines seven measures, τ1 to τ7; Grisan et al. define tortuosity density; three more exist only
inside implementations. They are not rescalings of one another, and the disagreement is not even
monotonic: two vessels can be ranked one way by the arc-chord ratio and the opposite way by
tortuosity density, because one measures total excess length and the other serpentine structure per
unit length. **Hart's own recommendation — the compositional pair τ4 and τ5 — is implemented by no
project in this catalogue**, and AutoMorph reports τ3, which Hart marks non-compositional and which
grows with vessel length by construction.

[VascX](projects/vascx.md) adds three further axes on top of the formula — per **segment** or per
whole **vessel**, arc length from a **spline** or from the **skeleton**, and optional caps on
segment length and on implausible values — each of which changes the number. A tortuosity value is
therefore not interpretable without its formula and those options. See
[tortuosity](biomarkers/tortuosity.md).

### 2.3 "Zone B" and "Zone C" differ by a factor of two between pipelines

Measurements near the disc are taken in a ring, and the pipelines describe their rings in different
units. [PVBM](projects/pvbm.md) builds zones at 1, 2 and 3 optic disc **radii** and measures in the
annulus between the second and third — that is 1.0 to 1.5 disc *diameters* from the centre. The
classical convention that [AutoMorph](projects/automorph.md) follows expresses Zone B and Zone C in
disc **diameters**. The words are the same, the rings are not, and the same formula over a different
ring is a different number. See
[central retinal equivalents](biomarkers/central-retinal-equivalents.md) section 5.

### 2.4 AutoMorph's fractal dimension measures the vessels' boundary, not their occupancy

Box-counting covers the vessel mask with boxes and counts how many contain vessel. The
implementation in AutoMorph's `FD_cal.py`, inherited from [retipy](projects/retipy.md), counts only
boxes that are **neither empty nor completely full** — its own comment says so. On a structure as
thin as a vessel tree almost every occupied box is partly empty, so the two conventions nearly
coincide and the difference passes unnoticed; but it is not the textbook box-counting dimension, and
it will diverge on thick or densely packed masks. [PVBM](projects/pvbm.md) computes a different
thing again — a multifractal set (D₀, D₁, D₂ and singularity length), averaged over 25 rotations.
See [fractal dimension](biomarkers/fractal-dimension.md).

### 2.5 Only two catalogued models segment the optic cup, which is why most pipelines report no cup-to-disc ratio

The cup-to-disc ratio needs a cup, and a cup boundary is defined by depth — which a colour
photograph does not record. Of the nineteen models in [MODELS.md](MODELS.md), only
[AutoMorph's disc-and-cup model](models/automorph-disc-cup.md) and the
[Hugging Face SegFormer](models/segformer-disc-cup.md) produce one; every other disc model,
[VascX's](models/vascx-disc.md) included, segments the disc alone. That is the reason VascX reports
no cup-to-disc ratio, and it is a capability gap rather than an oversight. See
[cup-to-disc ratio](biomarkers/cup-to-disc-ratio.md).

## 3. How to read this table

- **Variants** — how many competing definitions share this name. A value computed with one variant
  is not interchangeable with a value computed with another; each detail page says whether they can
  be compared at all.
- **Inputs** — which segmentations the measurement consumes. A biomarker is only as good as the mask
  beneath it, so trace this back to the model that produced it in [MODELS.md](MODELS.md), including
  the pixel grid that model works on.
- **Region** — whole image, a named disc-centred zone, or `varies` where implementations disagree.
  The same formula over a different region is a different number.
- **Units** — as computed. A measurement in pixels depends on the grid the segmentation was produced
  on and, for physical units, on the camera's resolution; `scale-invariant` marks the
  dimensionless measurements that avoid both problems.
- **Computed by** — the pipelines in [PROJECTS.md](PROJECTS.md) that produce it. Where several share
  one implementation, the detail page records the lineage: pipelines agreeing because they run the
  same code is weaker evidence than it appears.
- **Known defects** are not in this table. Every detail page carries a section 9 recording bugs that
  change the number. `None recorded` there means no finding, not a clean bill of health.

## 4. Adding a biomarker

Biomarker pages follow a fixed structure so they can be read against each other. Load the
`document-biomarker` skill, which defines that structure and this table's columns, before adding or
changing an entry.
