# Bifurcation angle

The angle at which a vessel splits into two. Branching geometry is not arbitrary — there is an
optimal angle for moving blood at least cost, and departures from it have been linked to
hypertension and to diabetic and cardiovascular disease. It is one of the few retinal biomarkers
with a physical theory behind it rather than an empirical association alone.

## 1. What it measures

- **In one sentence:** the angle between the two daughter vessels at a branch point.
- **Also known as:** branching angle, bifurcation angle, branch angle.
- **Direction of concern:** deviation from the expected angle, in either direction, rather than
  simply higher or lower.

## 2. Definition of record

No single ophthalmic origin; the measurement is geometric and the retinal literature inherits it
from vascular-branching theory.

- **The formula, in words:** at a branch point, take a direction for each daughter vessel and
  measure the angle between those two directions.

The whole difficulty is "take a direction": a vessel curves, so the angle depends on how far along
each daughter you look.

## 3. Variants

### 3.1 Angle sampled at a fixed distance along each branch (VascX)

- **Formula, in words:** at each bifurcation, walk a set distance `delta` along each outgoing
  branch, form a direction vector to that point, and measure the angle between the vectors. Angles
  above an internal 160° threshold are discarded as implausible, and the region's angles are then
  aggregated (mean or median). If too few valid bifurcations remain, no value is returned.
- **Source:** [VascX](../projects/vascx.md) `vascx/fundus/features/bifurcation_angles.py`.
- **Implemented by:** VascX, over the full grid and each hemifield.

### 3.2 Median branching angle over the vasculature (PVBM)

- **Formula, in words:** compute an angle at every detected branch point across the region of
  interest and report the median of the distribution.
- **Source:** [PVBM](../projects/pvbm.md) `PVBM/GeometryAnalysis.py` with
  `PVBM/helpers/branching_angle.py`; presented as one of the PVBM paper's algorithmic
  contributions.
- **Implemented by:** PVBM, and [OCULARNet](../projects/ocularnet.md) via its copy of PVBM's code.

**Comparability:** not interchangeable. The sampling distance is the crux — measure close to the
junction and you capture the true split but amplify skeleton noise; measure further out and you
capture the vessel's subsequent curvature instead. VascX exposes `delta` as a parameter; PVBM fixes
its own convention. Two "median branching angle" values from the two are different measurements.

## 4. Inputs required

- **Segmentations:** vessels, or artery/vein for per-class angles (PVBM computes arterioles and
  venules separately).
- **Derived geometry:** a skeleton; a graph of the vessel tree with identified bifurcation nodes;
  outgoing branch directions sampled at some distance from each node.
- **Why this matters:** which junctions are found at all. A crossing mistaken for a bifurcation
  contributes a meaningless angle, and thin-vessel skeletons produce spurious branch points — so
  the junction detector shapes the distribution before any angle is measured.

## 5. Measurement region

- **VascX:** full grid, superior hemifield, inferior hemifield.
- **PVBM:** the annulus between 2 and 3 optic disc radii.
- **AutoMorph family:** does not report branching angles.

## 6. Units and scale dependence

- **Unit as computed:** degrees.
- **Depends on the pixel grid:** Yes, indirectly and awkwardly. The sampling distance is in pixels,
  so the same `delta` reaches a different anatomical distance at a different grid — and skeleton
  staircasing perturbs short-range directions most.
- **Depends on a physical scale:** No.
- **Depends on field of view:** Yes, in aggregate — peripheral branches differ from central ones.
- **Scale-invariant:** the angle itself is, the sampling geometry is not.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | 3.1, `delta` configurable | `vascx/fundus/features/bifurcation_angles.py` | Original |
| [PVBM](../projects/pvbm.md) | 3.2 | `PVBM/GeometryAnalysis.py`, `helpers/branching_angle.py` | Original |
| [OCULARNet](../projects/ocularnet.md) | 3.2, via PVBM | `utils/GeometricalVBMs.py` | Modified copy of PVBM |

## 8. Sensitivity and failure modes

- **Junction detection errors dominate**, as in section 4.
- **Crossings masquerade as bifurcations.** An artery passing over a vein looks like a four-way node
  in a binary mask; only [OCULARNet](../models/ocularnet.md) segments crossings as their own class,
  which is precisely the information needed to exclude them.
- **Angle thresholds change the mean.** VascX discards angles above 160°; a pipeline without such a
  filter includes near-straight "branches" that are usually detector artefacts.
- **Reported reproducibility:** the VascX toolbox paper reports most biomarkers above 0.5 intraclass
  correlation with important differences between them — their measurement; angle-based measures are
  plausible candidates for the weaker end, since they depend on local geometry.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- Read with [junction counts](junction-counts.md): the same graph produces both, so a pipeline that
  finds more junctions is also averaging over a different population of angles.

---

**Links and definitions last checked:** 2026-09-10
