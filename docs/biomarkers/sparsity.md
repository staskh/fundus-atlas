# Sparsity

How far the retina's tissue sits from the nearest blood vessel. Where
[vascular density](vascular-density.md) measures the vessels, sparsity measures the gaps between
them — the same information seen from the other side, and more sensitive to where vessels are
missing rather than how many pixels they occupy.

It is a VascX-only measurement in this catalogue, and the closest thing here to the avascular-area
measures used in OCT angiography.

## 1. What it measures

- **In one sentence:** the typical, or the worst, distance from a point of retina to the nearest
  vessel.
- **Also known as:** vessel sparsity; conceptually related to avascular area and to
  nearest-vessel distance measures.
- **Direction of concern:** higher is treated as adverse — larger gaps mean less perfused tissue.

## 2. Definition of record

- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B. *retinalysis-vascx: An
  explainable software toolbox for the extraction of retinal vascular biomarkers.* arXiv, 2026.
  [arXiv:2602.08580](https://arxiv.org/abs/2602.08580)
- **The formula, in words:** compute, for every retinal pixel, the distance to the nearest vessel
  pixel — a distance transform of the vessel mask — then summarise those distances over the region.

## 3. Variants

Two aggregation modes, both from VascX (`SparsityMode`):

### 3.1 Mean sparsity

- **Formula, in words:** the average distance-to-nearest-vessel over the selected pixels.
- **Implemented by:** [VascX](../projects/vascx.md).

### 3.2 Maximum sparsity

- **Formula, in words:** find each vessel-free patch, take the distance at the point deepest inside
  it, and report the largest such value — the radius of the biggest hole in the vasculature.
- **Implemented by:** VascX.

**Comparability:** the two answer different questions. Mean sparsity moves with overall vessel
coverage; maximum sparsity is driven by a single worst gap and is therefore far more sensitive to
one missed vessel. They are not substitutes, and a "sparsity" value needs its mode named.

## 4. Inputs required

- **Segmentations:** vessels, plus the retinal mask that defines which pixels count.
- **Derived geometry:** a distance transform of the vessel mask; for the maximum mode, the
  connected components of vessel-free space and one peak per component. Optionally the optic
  disc-to-fovea distance, used for normalisation.
- **Why this matters:** no skeleton and no segment splitting, so like density its errors come from
  the mask — but unlike density, a single missed vessel can dominate the maximum mode.

## 5. Measurement region

The full retinal mask, or any VascX grid field — hemifields, disc-centred rings, ETDRS fields. VascX
ships a dedicated `sparsity` feature set alongside its general ones.

## 6. Units and scale dependence

- **Unit as computed:** pixels, or a fraction of the disc-to-fovea distance when the normalisation
  is applied.
- **Depends on the pixel grid:** Yes in raw pixels — a gap is twice as many pixels wide at twice the
  resolution. VascX's fixed 1024 grid makes its own values internally consistent.
- **Depends on a physical scale:** only to reach physical units. The optional normalisation by
  disc-to-fovea distance is the more useful route, since that distance is an anatomical ruler
  present in every photograph — see [disc-fovea distance](disc-fovea-distance.md).
- **Depends on field of view:** Yes — the periphery is sparser, so a wider field raises both modes.
- **Scale-invariant:** only in the normalised form.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | both modes | `vascx/fundus/features/sparsity.py` | Original |

No other catalogued project computes it.

## 8. Sensitivity and failure modes

- **A single missed vessel creates a large hole**, which the maximum mode reports at full weight.
  That makes 3.2 an unusually direct probe of segmentation recall — useful diagnostically, risky as
  a clinical variable.
- **The retinal mask defines the denominator of the region**, so a poor field-of-view mask puts
  black frame corners into the "retina" and inflates sparsity.
- **Reported reproducibility:** covered by the VascX toolbox paper's general finding — most
  biomarkers above 0.5 intraclass correlation, with important differences between them; their
  measurement, and no per-biomarker figure for sparsity was established here.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- Because it is defined on the gaps, sparsity is the natural partner to density in a comparison:
  two pipelines can agree on density while disagreeing on where the vessels are, and sparsity
  catches that.

---

**Links and definitions last checked:** 2026-09-10
