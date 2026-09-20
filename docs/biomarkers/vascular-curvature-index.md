# Vascular curvature index

A tortuosity number that Giesser et al. 2024 introduced under the name **vascular curvature
index (VCI)** and reported as more stable, on a short-interval retest of healthy eyes, than the
published tortuosity formulas they compared it against. The formula itself is unpublished: the
paper calls it proprietary. No catalogued pipeline computes it, and a VCI value found in a paper
cannot be reproduced from the public description.

The same three letters also name an unrelated OCT-angiography measure, the *vessel complexity
index*. That is a different quantity; see section 10.

## 1. What it measures

- **In one sentence:** how sharply a vessel's path turns, according to a change-of-angular-momentum
  construction that the authors have not published in full.
- **Also known as:** VCI; vascular curvature index. Not the OCTA *vessel complexity index*, which
  shares the abbreviation.
- **Direction of concern:** higher is treated as more tortuous, in the same sense as the other
  curvature metrics the authors compared it with. The paper does not report a clinical association
  of its own: the study is a retest on healthy eyes.

## 2. Definition of record

- Giesser SD, Turgut F, Saad A, Sommer C, Zhou Y, Wagner SK, Keane PA, Becker M, Cabrera DeBuc D,
  Somfai GM. *A new retest-stable tortuosity metric for retinal vessel analyses.* Investigative
  Ophthalmology & Visual Science 2024;65(12):30. DOI:
  [10.1167/iovs.65.12.30](https://doi.org/10.1167/iovs.65.12.30) ·
  [PMC11500049](https://pmc.ncbi.nlm.nih.gov/articles/PMC11500049/).
- **The formula, in words:** the paper does not give one that can be computed. It states that VCI
  is proprietary, that it is based on the change in angular momentum of a point travelling along
  the vessel (`L = Iω`; in a simplified point-mass example, `dL/dt = mv r'(t)`), and that
  it is designed to resist errors that arise in segmentation, thresholding and skeletonisation. The
  accompanying figure is a sketch of trajectories under high and low angular-momentum change, not
  an algorithm. A reader cannot recover the number from that description.

## 3. Variants

There is one named definition, and it is unpublished.

### 3.1 Giesser 2024 (proprietary)

- **Formula, in words:** unknown beyond the angular-momentum sketch in section 2.
- **Source:** Giesser et al. 2024, as above.
- **Implemented by:** no catalogued project. The paper used
  [AutoMorph](../projects/automorph.md) only to produce vessel and artery/vein masks; AutoMorph's
  own tortuosity columns (arc-chord, squared curvature, tortuosity density) were the comparators,
  not VCI. See [tortuosity](tortuosity.md).

**Comparability:** a VCI value cannot be compared with any published tortuosity formula, because
the mapping from the mask to the number is not public. The authors' own claim is that, on their
healthy retest set, VCI correlated most strongly with inverse-radius tortuosity (Pearson 0.7,
Spearman 0.72) and almost not at all with angle-based tortuosity (Pearson 0.05, Spearman 0.07).
That is their observation, on that sample; it is not a conversion.

## 4. Inputs required

- **Segmentations:** vessels, classified as artery or vein. The paper ran AutoMorph on
  macula-centred colour-fundus photographs and reports VCI separately for arterioles, venules and
  the combined tree.
- **Derived geometry:** a skeleton, by the authors' own account — they say the metric is built to
  resist skeletonisation error. The exact trace, the reference point they call *O*, and how
  segments are split at junctions are not described.
- **Why this matters:** tortuosity is a measurement of a trace, not of a mask. Without the tracing
  step, two groups with identical AutoMorph masks could still disagree. See
  [vessel-tracing.md](vessel-tracing.md). AutoMorph's own tracer returns points in discovery order
  rather than path order ([tortuosity](tortuosity.md) section 9.1); whether VCI was computed on
  those traces, or on a separate reconstruction, is unknown.

## 5. Measurement region

Whole image. The photographs were 45° foveal-centred frames from a Zeiss Visucam Pro NM. The paper
does not mention Zone B, Zone C, or any other disc-centred ring.

## 6. Units and scale dependence

- **Unit as computed:** Unknown. The paper plots VCI on a histogram alongside dimensionless
  tortuosity metrics but does not name a unit.
- **Depends on the pixel grid:** Unknown. AutoMorph's vessel and artery/vein models work on a
  1,024-pixel grid; whether VCI was evaluated on that grid or on a resampled skeleton is not
  stated.
- **Depends on a physical scale:** Unknown. The angular-momentum sketch involves a radius from a
  reference point, which would ordinarily carry a length unit, but the published description is
  not enough to say whether that length cancels.
- **Depends on field of view:** Unknown. The study used a single camera and a single 45° field.
- **Scale-invariant:** Unknown.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| None catalogued | — | — | — |

No public repository from the authors was found (checked 2026-09-20). The definition of record
calls the metric proprietary.

## 8. Sensitivity and failure modes

- The authors' **claim** is that VCI is less sensitive to segmentation, thresholding and
  skeletonisation error than the published tortuosity formulas they compared. The construction that
  would make that true is not in the paper, so the claim cannot be checked from the public record.
- **Reported reproducibility (authors' claim, healthy eyes, five-minute retest, n = 44):** Spearman
  test–retest 0.92 / 0.86 / 0.87 on arteries / veins / combined vessels; Pearson 0.86 / 0.94 /
  0.89. They report that, on Box–Cox-transformed z-scores of the absolute test–retest difference,
  VCI beat every comparator at *p* < 0.05 except inverse-radius tortuosity (Bullitt 2003). The
  study excluded ocular disease and used one camera; the paper itself lists those as limits on
  how far the figures travel.
- Inverse-radius tortuosity, the published metric they did not outperform, is itself implemented
  by no project in this catalogue.

## 9. Known defects

None recorded as of 2026-09-20 — there is no public implementation to inspect. That is an absence
of findings, not a clean bill of health.

## 10. Notes

- **The abbreviation collides.** Chu et al. 2016 defined a *vessel complexity index* (also VCI)
  on OCT angiograms: `(ΣP)² / (4π ΣA)`, the isoperimetric quotient of vessel perimeter
  against vessel area. That is an occupancy-and-outline measure of a binary mask, not a tortuosity
  of a trace, and it belongs to OCTA rather than colour-fundus photography. A paper that writes
  "VCI" without expanding it is not enough to tell the two apart.
- AutoMorph appearing in the methods section of Giesser et al. does not mean AutoMorph computes
  VCI. It means the masks came from AutoMorph and the VCI numbers came from somewhere else.
- The nearest *published* comparator the authors themselves identify is inverse-radius tortuosity
  (Bullitt EG, Gerig G, Pizer SM, Lin W, Aylward SR. *Measuring tortuosity of the intracerebral
  vasculature from MRA images.* IEEE Transactions on Medical Imaging 2003;22:1163–1171. DOI:
  [10.1109/TMI.2003.816964](https://doi.org/10.1109/TMI.2003.816964)). That formula is public;
  VCI's is not. See [tortuosity](tortuosity.md) for the measures that catalogued pipelines actually
  compute.

---

**Links and definitions last checked:** 2026-09-20
