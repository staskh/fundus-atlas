# Vascular density

What fraction of the retina is covered by blood vessels. It is the simplest summary of how much
vasculature a photograph contains, and a drop in it has been associated with diabetic retinopathy
and other diseases that cause capillary loss.

Its simplicity is deceptive: because it counts vessel pixels, it measures the segmentation as much
as the eye. A model that draws vessels a pixel thicker raises density everywhere.

## 1. What it measures

- **In one sentence:** the proportion of the analysed area occupied by vessel pixels.
- **Also known as:** vessel density, vessel area density, VD.
- **Direction of concern:** lower is generally treated as adverse.

## 2. Definition of record

No single origin — the measure is elementary and appears independently across the literature.

- **The formula, in words:** count the pixels marked as vessel, divide by the number of pixels in
  the region being analysed.

The contentious part is the denominator: the whole image, the circular retinal area inside the
field of view, or a defined zone.

## 3. Variants

### 3.1 Over the retinal mask

- **Formula, in words:** vessel pixels divided by the pixels inside the retinal (field-of-view)
  mask, so the black corners of the photograph do not count.
- **Source:** [VascX](../projects/vascx.md) `vascx/fundus/features/vascular_densities.py`, which
  states the denominator as the valid masked pixels — the full fundus mask, or one grid field's mask
  when a region is given.
- **Implemented by:** VascX.

### 3.2 Over the image or window

- **Formula, in words:** the fraction of vessel pixels in the analysed array, whether that is the
  whole image or a sliding window.
- **Source:** retipy's `vessel_density` in `tortuosity_measures.py`.
- **Implemented by:** [AutoMorph](../projects/automorph.md),
  [AutoMorphalyzer](../projects/automorphalyzer.md) (whole image only, not per zone),
  [AutoMorphClass](../projects/automorphclass.md), [retipy](../projects/retipy.md).

**Comparability:** the two differ by whatever share of the frame is not retina, which varies with
camera and field of view — so 3.2 reads systematically lower than 3.1 on the same photograph, by an
amount nobody reports. Comparable only within a variant.

## 4. Inputs required

- **Segmentations:** vessels (or artery/vein for per-class density).
- **Derived geometry:** none beyond the mask itself, plus a retinal field-of-view mask for variant
  3.1 and a zone mask where regions are used. That makes density the cheapest biomarker here and the
  only one needing no skeleton.
- **Why this matters:** with no skeleton and no segment splitting, density avoids the failure modes
  that dominate tortuosity — its errors come entirely from the mask and the denominator.

## 5. Measurement region

- **AutoMorph and AutoMorphalyzer:** whole image. AutoMorphalyzer's authors state explicitly that
  density, fractal dimension and global calibre are *not* computed per zone, unlike tortuosity and
  local calibre.
- **VascX:** the full retinal mask, or any grid field — hemifields, disc-centred rings, ETDRS
  fields.
- **PVBM:** not reported as a density; its area measure is the closest equivalent, see
  [vessel area and length](vessel-area-and-length.md).

## 6. Units and scale dependence

- **Unit as computed:** dimensionless fraction (or a percentage).
- **Depends on the pixel grid:** **Yes**, more than it appears. Vessel width in pixels does not
  scale linearly with resolution once vessels approach one pixel, so the same eye yields different
  densities at 512 and 1024. Thin peripheral vessels drop out entirely at coarse grids.
- **Depends on a physical scale:** No.
- **Depends on field of view:** **Yes, strongly.** A 45° photograph and a 30° photograph of one eye
  contain different proportions of dense central and sparse peripheral retina.
- **Scale-invariant:** No, despite being a ratio.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | 3.1 | `vascx/fundus/features/vascular_densities.py` | Original |
| [AutoMorph](../projects/automorph.md) | 3.2 | retipy's `tortuosity_measures.py` (`vessel_density`) | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | 3.2, unchanged | `automorph/measure/measure.py` | Kept from AutoMorph — its authors state density was left as it was |
| [AutoMorphClass](../projects/automorphclass.md) | 3.2 | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |

## 8. Sensitivity and failure modes

- **Segmentation thickness sets the level.** Density is essentially a measure of total vessel area,
  so any systematic bias in mask thickness passes through undiluted. This is the biomarker most
  directly coupled to the model.
- **Image quality moves it in one direction:** a blurred or underexposed photograph loses thin
  vessels, lowering density — which can look like disease.
- **The denominator must be stated.** A density over the image and a density over the retinal mask
  differ by a fixed but unreported factor.
- **Reported reproducibility:** the VascX toolbox paper reports intraclass correlations above 0.5
  for most of its biomarkers between repeat photographs — their measurement.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Density does
not use the vessel-point ordering that the retipy defect corrupts
([tortuosity.md](tortuosity.md) section 9.1), so AutoMorph's density columns are unaffected by it.

## 10. Notes

- Because it needs no skeleton, density is the natural first target for a segmentation-versus-
  biomarker comparison: differences between pipelines are attributable almost entirely to the mask.
- Pair it with [fractal dimension](fractal-dimension.md), which asks a related but distinct question
  — not how much vessel there is, but how it fills space.

---

**Links and definitions last checked:** 2026-09-10
