# Cup-to-disc ratio

How large the pale central hollow of the optic nerve head is relative to the nerve head itself. It
is the most clinically established measurement in this catalogue — ophthalmologists estimate it by
eye at the slit lamp — and an enlarging cup is the structural signature of glaucoma.

It is also the one biomarker here that is not about blood vessels at all, which is why it comes from
a different model and carries different failure modes.

## 1. What it measures

- **In one sentence:** the size of the optic cup as a fraction of the optic disc.
- **Also known as:** CDR, cup-disc ratio; vertical CDR when measured on height alone.
- **Direction of concern:** higher is adverse. Values above roughly 0.7 are commonly treated as
  suspicious for glaucoma, though the threshold depends on disc size.

## 2. Definition of record

A clinical measurement predating automated analysis; the automated form follows the clinical one.

- **The formula, in words:** divide a measure of the cup by the same measure of the disc — the
  vertical diameter for the vertical ratio, or the areas for the area ratio.

## 3. Variants

### 3.1 Height and width ratios (AutoMorph family)

- **Formula, in words:** measure the disc and the cup height and width from their masks and report
  the ratios, alongside the raw heights and widths.
- **Source:** [AutoMorph](../projects/automorph.md)'s measurement stage.
- **Implemented by:** AutoMorph, [AutoMorphalyzer](../projects/automorphalyzer.md),
  [AutoMorphClass](../projects/automorphclass.md).

**Comparability:** a vertical ratio and an area ratio are different numbers for the same eye, the
area ratio being roughly the square of the linear one for a circular cup. Any CDR should state
which it is. Within the AutoMorph family the definition is shared, so their values are comparable
in definition — though not necessarily in value, since all three run the same masks through
differently rewritten measurement code.

## 4. Inputs required

- **Segmentations:** the optic **disc and cup** — both, which narrows the field sharply: of the
  models catalogued here only [AutoMorph's disc-and-cup model](../models/automorph-disc-cup.md) and
  the [Hugging Face SegFormer](../models/segformer-disc-cup.md) produce a cup at all. VascX
  segments the disc only, which is why VascX reports no CDR.
- **Derived geometry:** the extent of each mask along the vertical and horizontal axes, or their
  areas.
- **Why this matters:** the cup boundary is genuinely ambiguous — it is defined by a change in
  depth, and a photograph has no depth. Human graders disagree about it, so the reference
  annotations the models learn from are themselves uncertain.

## 5. Measurement region

The optic nerve head only. No zone convention applies.

## 6. Units and scale dependence

- **Unit as computed:** dimensionless ratio. AutoMorph also reports the raw disc and cup heights and
  widths, which are in pixels or in microns where a resolution is supplied.
- **Depends on the pixel grid:** No for the ratio; yes for the raw dimensions.
- **Depends on a physical scale:** No for the ratio.
- **Depends on field of view:** No, provided the disc is fully in frame.
- **Scale-invariant:** **Yes** for the ratio — which is why it has survived as a clinical measure
  across every imaging device.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | 3.1 | `M3_feature_whole_pic`, `M3_feature_zone` | Original to the pipeline |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | 3.1 | `automorph/measure/` | Rewritten from AutoMorph |
| [AutoMorphClass](../projects/automorphclass.md) | 3.1 | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |

## 8. Sensitivity and failure modes

- **Cup boundary ambiguity is intrinsic**, not a software defect: depth is not visible in a colour
  photograph, so both models and humans infer it from pallor.
- **Small training sets.** The AutoMorph family's disc-and-cup model was trained on 900 images
  (REFUGE and GAMMA) — an order of magnitude fewer than its vessel models — so its masks are the
  least well-supported in that pipeline.
- **Disc size confounds interpretation:** a large disc naturally has a large cup, so a raw CDR
  without disc size is clinically incomplete.
- **A displaced cup can mislabel laterality** in AutoMorphalyzer, which infers which eye a
  photograph shows from vessel density either side of the cup.
- **Reported reproducibility:** Unknown for these implementations; the AutoMorph paper reports disc
  segmentation performance rather than CDR repeatability.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- This is the biomarker a clinician is most likely to check against their own judgement, which
  makes it the best candidate for a sanity comparison between pipeline output and expert reading.
- Nothing in the vascular part of this catalogue depends on it, so an unreliable CDR does not
  contaminate the other biomarkers.

---

**Links and definitions last checked:** 2026-09-10
