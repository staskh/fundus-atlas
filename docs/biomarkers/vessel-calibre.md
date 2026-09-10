# Vessel calibre

How wide the retinal vessels are. It is the most direct measurement in this catalogue and the
foundation of several others — the central retinal equivalents and the artery-vein ratio are both
summaries of calibre. Narrowed arterioles have been associated with raised blood pressure and
cardiovascular risk, and widened venules with inflammation and metabolic disease.

It is also the measurement most sensitive to where a segmentation puts the vessel edge, which is
why two pipelines can disagree about calibre while producing masks that look identical.

## 1. What it measures

- **In one sentence:** the width of a blood vessel, measured across it, at one point or averaged
  along a stretch.
- **Also known as:** vessel width, vessel diameter, calibre; "local calibre" for per-segment values
  and "global calibre" for a whole-image average.
- **Direction of concern:** context-dependent — narrower arterioles and wider venules are both
  reported as adverse. The ratio between them is [AVR](avr.md).

## 2. Definition of record

No single origin: calibre is a physical width, and each method defines the edge differently. The
reference implementation for the modern literature is:

- Bankhead P, Scholfield CN, McGeown JG, Curtis TM. *Fast Retinal Vessel Detection and Measurement
  Using Wavelets and Edge Location Refinement.* PLoS ONE 2012;7(3):e32435. DOI:
  [10.1371/journal.pone.0032435](https://doi.org/10.1371/journal.pone.0032435)

- **The formula, in words:** find the vessel centreline, then at each point step perpendicular to it
  and locate the two edges; the distance between them is the width at that point. Everything
  contentious lives in "locate the two edges".

## 3. Variants

### 3.1 Edge location from the image (ARIA)

- **Formula, in words:** detect vessels with a wavelet transform, then refine each edge's position
  to sub-pixel precision using the image's intensity profile across the vessel.
- **Source:** the paper above.
- **Implemented by:** [ARIA](../projects/aria.md).

### 3.2 Width from a binary mask, per segment (VascX)

- **Formula, in words:** skeletonise the mask, split it into segments at junctions, fit a spline to
  each segment, sample perpendicular distances along it, and take the **median** diameter of each
  segment. Segment values are then aggregated over a region — by median, or weighted by each
  segment's arc length.
- **Source:** [VascX](../projects/vascx.md) `vascx/fundus/features/caliber.py`.
- **Implemented by:** VascX.

### 3.3 Width from a binary mask, whole image (retipy lineage)

- **Formula, in words:** measure widths along the skeleton within a sliding window and average them
  for the image, plus per-segment widths used for the central retinal equivalents.
- **Source:** retipy's `tortuosity_measures.evaluate_window`, which returns `Average_width` and the
  per-vessel width list `w1_list`.
- **Implemented by:** [AutoMorph](../projects/automorph.md),
  [AutoMorphalyzer](../projects/automorphalyzer.md) (rewritten for speed and correctness),
  [AutoMorphClass](../projects/automorphclass.md), [retipy](../projects/retipy.md).

**Comparability:** not interchangeable. A mask-derived width inherits the segmentation's dilation —
a model that draws vessels one pixel wider reports every vessel one pixel wider — while an
image-derived width (3.1) does not. Median-of-segments and length-weighted aggregation also answer
different questions: the first treats a tiny twig and a major arcade equally, the second does not.
Record the variant, the aggregation, and the model that produced the mask.

## 4. Inputs required

- **Segmentations:** vessels, or artery/vein when calibre is reported per class.
- **Derived geometry:** a skeleton; segments split at junctions; a perpendicular sampling direction
  at each point, usually from a spline fitted to the segment.
- **Why this matters:** how segments are split decides which pixels are averaged together. Two
  implementations of "median segment width" disagree whenever their junction handling differs, with
  the formula identical.

## 5. Measurement region

Varies, and the choice matters more than for most biomarkers because vessels narrow as they branch
outward:

- **Whole image** — AutoMorph's global calibre.
- **Disc-centred zones** — AutoMorph and AutoMorphalyzer report local calibre in zones B and C; PVBM
  measures within an annulus between 2 and 3 optic disc radii.
- **Grid fields** — VascX reports calibre over the full grid, the superior and inferior hemifields,
  and a disc-centred ring.

## 6. Units and scale dependence

- **Unit as computed:** pixels.
- **Depends on the pixel grid:** **Yes** — directly. The same vessel is about 1.8× wider in pixels
  on VascX's 1024 grid than on AutoMorph's 720 artery/vein grid. See the grid column in
  [MODELS.md](../MODELS.md).
- **Depends on a physical scale:** Yes, to reach microns. AutoMorph converts using a per-image
  resolution supplied in `resolution_information.csv`; without real values its micron columns are
  not physical. VascX leaves calibre in pixels on a fixed 1024 grid.
- **Depends on field of view:** indirectly — a wider field puts more small vessels in frame, which
  moves any whole-image average.
- **Scale-invariant:** **No.** This is the biomarker most often compared across studies when it
  should not be.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [ARIA](../projects/aria.md) | 3.1, image-based edges | `Vessel_Algorithms/` | Original |
| [VascX](../projects/vascx.md) | 3.2, per-segment median | `vascx/fundus/features/caliber.py` | Original |
| [AutoMorph](../projects/automorph.md) | 3.3 | retipy's `tortuosity_measures.py` | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | 3.3 | `automorph/measure/` | Rewritten from retipy; the authors state local calibre was measured inefficiently before |
| [AutoMorphClass](../projects/automorphclass.md) | 3.3 | `src/pytorch_automorph/feature_calculation.py` | Reimplemented from AutoMorph |
| [PVBM](../projects/pvbm.md) | per-segment widths, used only as input to the equivalents | `PVBM/CentralRetinalAnalysis.py` | Original |

## 8. Sensitivity and failure modes

- **Segmentation thickness dominates.** A model trained to draw slightly thicker vessels shifts
  every calibre value; this is a property of the model, not the eye.
- **Grid resampling** blurs edges: a mask produced at 512 and upsampled to the original size has
  softer boundaries than one produced at native resolution.
- **Small vessels near the resolution limit** are either missed or measured at the minimum
  detectable width, which biases whole-image averages upward.
- **Reported reproducibility:** the VascX toolbox paper reports moderate to excellent agreement
  (intraclass correlation above 0.5) for most of its biomarkers between repeat photographs, with
  differences between biomarkers — their measurement, not ours.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Note that the
tortuosity defect in retipy ([tortuosity.md](tortuosity.md) section 9) sits in the same module that
produces `Average_width`, but it concerns the *ordering* of segment points, which width measurement
does not depend on.

## 10. Notes

- Calibre is the input to [central retinal equivalents](central-retinal-equivalents.md) and
  therefore to [AVR](avr.md); an error here propagates to both.
- Because it is not scale-invariant, a calibre value published without both its grid and its micron
  conversion cannot be reused. That is the single most common gap in the literature this atlas
  covers.

---

**Links and definitions last checked:** 2026-09-10
