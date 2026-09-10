# Temporal angle

How widely the two main vessel arches spread across the macula. The temporal arcades — the large
vessels sweeping above and below the centre of vision — form a natural angle at the optic disc, and
that angle narrows or widens with conditions affecting the retina's development and vasculature.
It is the most anatomically specific measurement in this catalogue: it describes named vessels
rather than a statistic over all of them.

It is computed only by VascX among the catalogued projects.

## 1. What it measures

- **In one sentence:** the angle between the superior and inferior temporal arcades, seen from the
  optic disc.
- **Also known as:** temporal arcade angle, arcade angle.
- **Direction of concern:** narrowing has been described in retinopathy of prematurity and in
  conditions affecting macular development; widening is less discussed.

## 2. Definition of record

- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B. *retinalysis-vascx: An
  explainable software toolbox for the extraction of retinal vascular biomarkers.* arXiv, 2026.
  [arXiv:2602.08580](https://arxiv.org/abs/2602.08580)
- **The formula, in words:** on circles centred at the optic disc, starting two thirds of the way to
  the fovea and moving outward, find the two largest-calibre vessels on the fovea side of the disc
  that cross each circle, measure the angle between them, and take the median across circles.

## 3. Variants

Only one definition, VascX's, described above. No competing formula was found in the catalogued
projects — but the parameters are configurable and change the result: the inner and outer sampling
radii, both expressed as fractions of the disc-to-fovea distance, and how many circles are sampled
between them.

**Comparability:** comparable only between runs with the same radii and circle count. Since no other
pipeline computes it, cross-pipeline comparison does not arise yet.

## 4. Inputs required

- **Segmentations:** artery/vein (calibre is needed to pick the dominant vessels), the optic disc,
  and the **fovea** — this is the only biomarker here that cannot be computed without a fovea
  location.
- **Derived geometry:** the resolved vessel graph; the disc-to-fovea axis; circle intersections;
  a calibre per intersecting segment; an angular test for which vessels count as temporal
  (fovea-side, under 90° from the axis).
- **Why this matters:** it depends on four segmentations at once, so it inherits four sources of
  error — and a fovea detection failure removes the measurement entirely rather than degrading it.

## 5. Measurement region

Concentric circles around the optic disc, from two thirds of the disc-to-fovea distance outward to a
configurable outer radius. Because the radii are defined as fractions of an anatomical distance
rather than in pixels, the region adapts to each eye's own scale — the most principled region
convention in this catalogue.

## 6. Units and scale dependence

- **Unit as computed:** degrees.
- **Depends on the pixel grid:** No, beyond the grid's effect on the underlying segmentations.
- **Depends on a physical scale:** No — the sampling radii are relative to the disc-to-fovea
  distance, so no camera calibration is needed.
- **Depends on field of view:** only through visibility: if the sampling circles fall outside the
  retinal mask, VascX does not compute the value rather than estimating it.
- **Scale-invariant:** **Yes** — one of the few measurements here that genuinely is.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | as defined | `vascx/fundus/features/temporal_angles.py` | Original |

## 8. Sensitivity and failure modes

- **Fovea localisation is a single point of failure.** The whole geometry hangs off the disc-to-fovea
  axis, and the fovea is a low-contrast landmark — see [VascX fovea](../models/vascx-fovea.md).
- **Picking the wrong vessels.** The method selects by calibre, so a mislabelled or fragmented
  arcade can hand the measurement to a lesser branch.
- **Macula-centred versus disc-centred photographs** differ in how much of the arcade is visible,
  which changes how many circles yield a valid angle.
- **Reported reproducibility:** covered by the VascX toolbox paper's general finding; no
  per-biomarker figure for the temporal angle was established here.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- Its scale invariance and anatomical specificity make it attractive for cross-cohort work, and its
  dependence on four segmentations makes it the biomarker most likely to be simply absent from an
  output row. Treat missing values here as expected, not as failure.

---

**Links and definitions last checked:** 2026-09-10
