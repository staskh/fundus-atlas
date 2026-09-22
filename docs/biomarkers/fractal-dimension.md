# Fractal dimension

How thoroughly the vascular tree fills the retina. Branching structures repeat a similar pattern at
different sizes, and the fractal dimension puts a number — or a small family of numbers — on that
space-filling behaviour, roughly between 1 (a line) and 2 (a filled plane) for a retinal
vasculature. Reductions have been associated with diabetic retinopathy and with cardiovascular and
cognitive outcomes.

It is attractive because it is dimensionless and needs no scale calibration, and treacherous
because its value depends on how it is computed to an extent rarely acknowledged.

## 1. What it measures

- **In one sentence:** the degree to which the vascular tree fills the plane, as a dimensionless
  number or a small family of them.
- **Also known as:** box-counting dimension, Minkowski-Bouligand dimension, capacity dimension
  (D₀); the multifractal set adds the entropy dimension (D₁), correlation dimension (D₂) and
  singularity length.
- **Direction of concern:** lower is generally treated as adverse.

## 2. Definition of record

- [Stosic 2006](../papers/stosic-2006.md). Stosić T, Stosić BD. *Multifractal Analysis of Human
  Retinal Vessels.* IEEE Transactions on Medical Imaging 2006;25(8):1101–1107. DOI:
  [10.1109/TMI.2006.879316](https://doi.org/10.1109/TMI.2006.879316).
  The implementation later pipelines run for the multifractal set is [Fhima 2022](../papers/fhima-2022.md).
- **The formula, in words (one dimension):** cover the vessel mask with a grid of boxes of side
  *k*, count how many boxes contain vessel, repeat for a range of *k*, and take the slope of the
  count against the box size on a log-log plot. That slope is the capacity dimension D₀.
- **The formula, in words (the hierarchy):** weight those boxes by how much vessel they contain, and
  the slope becomes a family D_q. D₀, D₁ and D₂ are the capacity, entropy and correlation
  dimensions; the f(α) singularity spectrum records how local space-filling varies across the
  retina. A monofractal would have all D_q equal and an infinitely narrow spectrum.

A single box-counting dimension is standard mathematics rather than an ophthalmic invention.
[Stosic 2006](../papers/stosic-2006.md) is the retinal paper that showed one number is not enough.
What differs between implementations is which boxes get counted, over what range of sizes, and
whether the boxes sit on a grid or are grown around vessel pixels.

## 3. Variants

### 3.1 Box-counting, boundary-box convention (retipy lineage)

- **Formula, in words:** as above, but the count includes only boxes that are **neither empty nor
  completely full** — the code's comment is "We count non-empty (0) and non-full boxes (k*k)". Box
  sizes are successive powers of two down from the largest that fits.
- **Source:** `fractal_dimension` in AutoMorph's `M2_Vessel_seg/FD_cal.py` and in retipy's
  `tortuosity_measures.py`.
- **Implemented by:** [AutoMorph](../projects/automorph.md),
  [AutoMorphalyzer](../projects/automorphalyzer.md) (unchanged),
  [AutoMorphClass](../projects/automorphclass.md), [retipy](../projects/retipy.md).
- **Worth knowing:** excluding full boxes makes this a measure of the vasculature's *boundary*
  rather than of its occupancy. On a thin structure like a vessel tree the two nearly coincide,
  which is why the convention passes unnoticed — but it is not the textbook box-counting dimension,
  and it will diverge from one on thick or densely packed masks.

### 3.2 Multifractal dimensions (PVBM)

- **Formula, in words:** generalise box-counting to a family of dimensions D_q, weighting boxes by
  how much vessel they contain. D₀ is the capacity dimension (the classical one), D₁ the entropy
  dimension, D₂ the correlation dimension. The **singularity length** summarises the spread of the
  f(α) singularity spectrum — how varied the local space-filling is across the retina.
- **Source:** [Stosic 2006](../papers/stosic-2006.md) for the retinal claim that D₀ > D₁ > D₂ and
  that an f(α) spectrum is the object of interest; [Fhima 2022](../papers/fhima-2022.md) /
  [PVBM](../projects/pvbm.md) `PVBM/FractalAnalysis.py` for the computation this atlas actually
  runs (Chhabra / FracLac box-counting, 10 box scales and 25 rotations by default — not Stosic's
  sandbox).
- **Implemented by:** PVBM, and [OCULARNet](../projects/ocularnet.md) through its copy of PVBM.

**Comparability:** D₀ from 3.2 and the value from 3.1 answer the same question but by different
conventions and over different box ranges, and PVBM's rotation averaging makes its estimate more
stable than a single-orientation count. Treat them as different measurements. D₁, D₂ and singularity
length have no counterpart in the retipy lineage at all.

## 4. Inputs required

- **Segmentations:** vessels (or artery/vein for per-class dimensions — PVBM computes its set
  independently on arterioles and venules).
- **Derived geometry:** none. Like density, fractal dimension consumes the binary mask directly,
  with no skeleton and no segment splitting. PVBM applies its region of interest and, for the
  multifractal set, rotates the mask.
- **Why this matters:** no skeleton means none of the ordering and junction problems that afflict
  tortuosity. The failure modes are all about the mask and the box range.

## 5. Measurement region

- **AutoMorph and AutoMorphalyzer:** whole image only — AutoMorphalyzer's authors state fractal
  dimension is not computed per zone.
- **PVBM:** the annulus between 2 and 3 optic disc radii, as for its other geometric measures.
- **VascX:** does not report a fractal dimension. Its nearest measure is
  [sparsity](sparsity.md), which asks about vessel-free space instead.

## 6. Units and scale dependence

- **Unit as computed:** dimensionless.
- **Depends on the pixel grid:** **Yes.** The box range is bounded below by one pixel and above by
  the image size, so a coarser grid offers fewer usable scales and a shallower log-log slope. This
  is the standard criticism of box-counting on finite images, and it applies to every value here.
- **Depends on a physical scale:** No.
- **Depends on field of view:** Yes — more peripheral retina in frame changes the pattern being
  filled.
- **Scale-invariant:** in theory yes, in practice only between masks on the same grid and field of
  view.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | 3.1 | `M2_Vessel_seg/FD_cal.py`, retipy's module | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | 3.1, unchanged | `automorph/measure/measure.py` | Kept from AutoMorph |
| [AutoMorphClass](../projects/automorphclass.md) | 3.1 | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |
| [PVBM](../projects/pvbm.md) | 3.2 — D₀, D₁, D₂, singularity length | `PVBM/FractalAnalysis.py` | Implements [Stosic 2006](../papers/stosic-2006.md) by Chhabra / FracLac box-counting, not the sandbox |
| [OCULARNet](../projects/ocularnet.md) | 3.2, via PVBM | `utils/GeometricalVBMs.py` | Modified copy of PVBM |

## 8. Sensitivity and failure modes

- **Few usable box scales.** A fundus mask supports perhaps six to ten meaningful box sizes; the
  slope estimated from so few points is not very stable, and the choice of range shifts it.
- **Segmentation completeness matters more than thickness:** losing thin peripheral vessels removes
  the small-scale structure the dimension is measuring.
- **Orientation.** A single-orientation box count depends slightly on how the grid happens to fall
  across the vessels, which is why PVBM averages over rotations and the retipy lineage does not.
- **Reported reproducibility:** the VascX toolbox paper's repeatability findings do not cover this
  biomarker, since VascX does not compute it; no independent figure was established.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. The
boundary-box convention in 3.1 is a documented deviation rather than a bug: the code does what its
comment says.

## 10. Notes

- Reported as one of the more robust retinal biomarkers, which is plausible for a dimensionless
  whole-image measure — but the grid and box-range dependence above means "robust" holds within a
  pipeline, not across pipelines.
- Read alongside [vascular density](vascular-density.md): density says how much vessel there is,
  fractal dimension says how it is arranged.
- [Stosic 2006](../papers/stosic-2006.md) also reports the *location* and *height* of the f(α)
  peak, and D_q at q = ±10. Catalogued pipelines keep only D₀, D₁, D₂ and the width Δα. A shift of
  the spectrum with unchanged width — the contrast that paper emphasises — would not appear in
  those columns.

---

**Links and definitions last checked:** 2026-09-22
