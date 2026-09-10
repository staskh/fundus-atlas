# Vessel area and length

Two elementary quantities: how many pixels the vessels occupy, and how far you would travel walking
along every vessel. They are PVBM's most basic outputs and the raw material behind
[vascular density](vascular-density.md), which is area divided by the region's area.

They are catalogued together because they share every property, and both come with the same warning:
**PVBM reports them in pixels**, so a value is meaningless without the grid and the region it was
computed on.

## 1. What it measures

- **In one sentence:** the total area covered by the vessel segmentation, and the total length of
  its skeleton.
- **Also known as:** vessel area, blood vessel area; overall length, total vessel length, skeleton
  length.
- **Direction of concern:** lower is generally treated as adverse, mirroring density.

## 2. Definition of record

- Fhima J, Van Eijgen J, Stalmans I, Men Y, Freiman M, Behar JA. *PVBM: A Python Vasculature
  Biomarker Toolbox Based on Retinal Blood Vessel Segmentation.* ECCV 2022 Workshops. DOI:
  [10.1007/978-3-031-25066-8_15](https://doi.org/10.1007/978-3-031-25066-8_15)
- **The formula, in words:** area is the count of segmented vessel pixels. Length is the distance
  required to traverse the whole skeleton — the number of skeleton steps, diagonal steps counting
  more than orthogonal ones.

## 3. Variants

Only one definition each, as implemented by PVBM. No competing formulas were found in the
catalogued projects.

- **Area** — sum of vessel pixels within the region of interest, in square pixels.
- **Length** — traversal distance over the skeleton within the region of interest, in pixels.

**Comparability:** comparable only between runs on the same grid, the same region and the same
segmentation source. Because both scale with resolution — area with its square, length linearly —
they are the least portable numbers in this catalogue.

## 4. Inputs required

- **Segmentations:** arteries and veins separately; PVBM computes all fifteen of its biomarkers
  independently on each class.
- **Derived geometry:** the mask for area; a skeleton for length; the optic disc centre and radius
  to place the region of interest.
- **Why this matters:** the skeletonisation algorithm sets the length. A different thinning method
  gives a different total on identical masks, and PVBM's is `skimage.morphology.skeletonize`, applied
  by the caller before the biomarker functions run.

## 5. Measurement region

PVBM's region of interest: the annulus between **2 and 3 optic disc radii**, built in
`DiscSegmenter.post_processing` as zone C minus zone B. Anything outside it is excluded before
counting.

## 6. Units and scale dependence

- **Unit as computed:** square pixels (area), pixels (length).
- **Depends on the pixel grid:** **Yes, most strongly of any biomarker here.** Area scales with the
  square of resolution and length linearly, so the same eye measured on PVBM's 512-pixel disc
  segmentation grid and on a 1024 mask returns values differing roughly fourfold and twofold.
- **Depends on a physical scale:** Yes, to convert to physical units, and PVBM performs no such
  conversion.
- **Depends on field of view:** Yes.
- **Scale-invariant:** **No.**

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [PVBM](../projects/pvbm.md) | area and length | `PVBM/GeometryAnalysis.py` (`compute_geomVBMs`), with `PVBM/helpers/perimeter.py` | Original |
| [OCULARNet](../projects/ocularnet.md) | the same, via PVBM | `utils/GeometricalVBMs.py` | Modified copy of PVBM |

No AutoMorph-family pipeline reports raw area or length; they report
[vascular density](vascular-density.md) instead, which normalises area away.

## 8. Sensitivity and failure modes

- **Everything that changes the mask changes these directly**, with no normalisation to absorb it —
  segmentation thickness for area, completeness for both.
- **Skeleton spurs** add length: small artefacts on the mask boundary become short branches that
  count toward the total.
- **Region clipping** dominates comparisons: a vessel crossing the annulus boundary contributes only
  its inside portion, so a disc segmentation error moves both numbers.
- **Reported reproducibility:** Unknown — no repeatability figure for these two was established.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- If you need a portable number, use density rather than area: dividing by the region's pixel count
  removes the grid dependence that makes area unusable across pipelines.
- PVBM's fifteen biomarkers are computed per vessel class, so "area" appears twice in its output —
  once for arterioles, once for venules.

---

**Links and definitions last checked:** 2026-09-10
