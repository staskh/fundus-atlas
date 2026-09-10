# Central retinal equivalents (CRAE and CRVE)

A single number summarising how wide the arterioles — or the venules — are near the optic disc. You
cannot measure the central retinal artery itself in a photograph: it is hidden inside the optic
nerve. So the branches crossing a ring around the disc are measured and combined back, pair by pair,
into the width the parent trunk would have. CRAE is that estimate for arterioles, CRVE for venules.

Their ratio is the [artery-vein ratio](avr.md), and they are the summary in which retinal
arteriolar narrowing has been most often reported.

## 1. What it measures

- **In one sentence:** the estimated calibre of the central retinal arteriole (CRAE) or venule
  (CRVE), reconstructed from the branches visible around the optic disc.
- **Also known as:** central retinal arteriolar/venular equivalent; the Parr-Hubbard and Knudtson
  formulas; "arteriolar equivalent".
- **Direction of concern:** lower CRAE (narrower arterioles) and higher CRVE (wider venules) are
  both reported as adverse.

## 2. Definition of record

Two publications define the two formulas in use, and the field never converged on one:

- Hubbard LD, et al. *Methods for evaluation of retinal microvascular abnormalities associated with
  hypertension/sclerosis in the Atherosclerosis Risk in Communities study.* Ophthalmology 1999.
- Knudtson MD, Lee KE, Hubbard LD, Wong TY, Klein R, Klein BEK. *Revised formulas for summarizing
  retinal vessel diameters.* Current Eye Research 2003.

- **The formula, in words:** take the widths of the vessels crossing a ring around the disc, sort
  them, pair the widest with the narrowest, combine each pair into one estimated parent width, and
  repeat on the resulting list until one number remains.

## 3. Variants

### 3.1 Hubbard

- **Formula, in words:** each pair combines with a fitted quadratic expression carrying **additive
  constants** — for arterioles `√(0.87·w₁² + 1.01·w₂² − 0.22·w₁·w₂ − 10.76)`, for venules
  `√(0.72·w₁² + 0.91·w₂² + 450.05)`.
- **Source:** Hubbard et al. 1999.
- **Implemented by:** [PVBM](../projects/pvbm.md) (`crae_hubbard`, `crve_hubbard`),
  [AutoMorph](../projects/automorph.md) via retipy's `Hubbard_cal`.
- **The trap:** those constants were fitted in **microns**. Feeding pixel widths into them is
  dimensionally wrong — the −10.76 and +450.05 terms do not scale — so a Hubbard value computed on
  pixel widths is not a rescaled Hubbard value, it is a different number. AutoMorph's Hubbard
  columns are therefore only meaningful when a real pixel resolution was supplied.

### 3.2 Knudtson

- **Formula, in words:** each pair combines as a constant times the root of the sum of squares —
  `0.88·√(w₁² + w₂²)` for arterioles, `0.95·√(w₁² + w₂²)` for venules. Knudtson's revision also
  fixed the number of vessels used at the six largest, so the result stops depending on how many
  small branches the software happened to find.
- **Source:** Knudtson et al. 2003.
- **Implemented by:** [PVBM](../projects/pvbm.md) (`crae_knudtson`, `crve_knudtson`),
  [AutoMorph](../projects/automorph.md) via retipy's `Knudtson_cal`,
  [AutoMorphalyzer](../projects/automorphalyzer.md) (**Knudtson only** — its authors removed
  Hubbard), [VascX](../projects/vascx.md) (`CRE`, described in code as a Hubbard-style recursion
  using the 0.88 and 0.95 constants, which is the Knudtson formula).
- Being purely multiplicative, this variant **is** scale-invariant: it can be computed on pixel
  widths and rescaled afterwards.

**Comparability:** the two variants are **not** interchangeable, and the gap is not a constant
factor. Knudtson's own paper presents the revision as producing different, more stable values than
Hubbard's. A CRAE without its variant named is unusable; a Hubbard CRAE without a micron conversion
is worse than unusable, because it looks like a number.

## 4. Inputs required

- **Segmentations:** artery/vein (the arterioles and venules must be told apart), plus the optic
  disc to place the ring and set its radii.
- **Derived geometry:** the disc centre and radius; a set of concentric circles; the intersections
  of vessel segments with each circle; a width per intersecting segment.
- **Why this matters:** three choices before any formula runs — where the ring sits, how many
  vessels are kept, and how the width at a crossing is measured — and implementations differ on all
  three.

## 5. Measurement region

Every implementation uses a ring around the disc, in different units:

- **AutoMorph and AutoMorphalyzer:** zones B and C, disc-centred, following the classical
  convention expressed in disc **diameters**.
- **PVBM:** the annulus between **2 and 3 optic disc radii** — that is 1.0 to 1.5 disc diameters
  from the centre, built as filled circles in `DiscSegmenter.post_processing` (zone A = 1 radius,
  B = 2, C = 3) with the region of interest taken as zone C minus zone B.
- **VascX:** several concentric circles between a configurable inner and outer radius given in disc
  **diameters**, keeping the largest 6 vessels per circle in full mode and 4 in temporal or nasal
  mode, and taking the median equivalent across circles; a circle not fully inside the retinal mask
  is discarded.

The same formula over a different ring is a different number, and radii in disc *radii* versus disc
*diameters* is a factor-of-two trap when reading code.

## 6. Units and scale dependence

- **Unit as computed:** pixels, or microns where a resolution is supplied.
- **Depends on the pixel grid:** Yes, through the widths it consumes.
- **Depends on a physical scale:** for Knudtson, only if you want microns. For **Hubbard, yes
  fundamentally** — its constants presuppose microns.
- **Depends on field of view:** no, provided the ring is inside the image.
- **Scale-invariant:** Knudtson yes; Hubbard no.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [PVBM](../projects/pvbm.md) | both | `PVBM/CentralRetinalAnalysis.py` | Original |
| [VascX](../projects/vascx.md) | Knudtson constants, configurable rings | `vascx/fundus/features/cre.py`, `cre_knudtson.py` | Original |
| [AutoMorph](../projects/automorph.md) | both | retipy's `tortuosity_measures.py` (`Hubbard_cal`, `Knudtson_cal`) | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Knudtson only | `automorph/measure/` | Rewritten from retipy |
| [AutoMorphClass](../projects/automorphclass.md) | AutoMorph's set | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |
| [OCULARNet](../projects/ocularnet.md) | via PVBM | `utils/GeometricalVBMs.py` | Modified copy of PVBM |

## 8. Sensitivity and failure modes

- **Artery-vein confusion is the dominant error.** One venule labelled as an arteriole enters the
  CRAE recursion as a large width and moves it substantially — which is why crossings, where
  labelling fails most, matter (see [OCULARNet](../models/ocularnet.md), the one model that
  segments them explicitly).
- **Vessel count.** Pre-Knudtson formulas drift with how many branches were detected; Knudtson's
  fixed count of six exists to stop that, so an implementation that keeps a different number has
  changed the measurement.
- **Ring placement** depends on the disc segmentation; a displaced or mis-sized disc moves the ring
  onto a different part of the vascular tree.
- **Reported reproducibility:** the VascX toolbox paper reports intraclass correlations above 0.5
  for most of its biomarkers, central retinal equivalents included, between repeat photographs of
  one eye — their measurement.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. The Hubbard
unit problem in section 3.1 is a misuse hazard rather than an implementation bug: the code computes
what it says it computes.

## 10. Notes

- If you only record one thing about a CRAE value, record the variant. If you can record two, add
  the ring.
- [AVR](avr.md) inherits everything on this page twice over, once through each equivalent.

---

**Links and definitions last checked:** 2026-09-10
