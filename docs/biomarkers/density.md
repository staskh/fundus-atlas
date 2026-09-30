# density

**How much vasculature there is, and how it is spread over the retina.** Ten biomarkers running
from raw extent — total area, total centreline length — through the fraction of retina covered, to
how completely the tree fills the space it occupies.

They are one family because they answer one question at different levels of normalisation. A
density *is* an area over a reference area; sparsity is the same question asked from the retina's
side, as the distance to the nearest vessel; a fractal dimension is how the covering scales as you
look more closely.

## 1. What it measures

Vessel rarefaction — fewer and thinner vessels covering less retina — accompanies hypertension,
diabetic retinopathy and ageing. A single width says nothing about it; these do. The fractal
dimensions add something the densities cannot: two retinas can cover the same fraction of the field
while one branches far more finely, and the dimension separates them.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `density/area/{artery,vein,vessels}` | total vessel area | none |
| `density/skeleton-length/{artery,vein,vessels}` | total centreline length | none |
| `density/over-fov/{artery,vein,vessels}` | vessel area as a fraction of the field of view | none |
| `density/over-image/{artery,vein,vessels}` | the same over the whole frame, lit or not | none |
| `density/sparsity/{artery,vein,vessels}` | distance from retina to the nearest vessel | `mean`, `max` |
| `density/box-counting/{artery,vein,vessels}` | box-counting dimension | none |
| `density/multifractal-d0/{artery,vein,vessels}` | capacity dimension of the multifractal spectrum | none |
| `density/multifractal-d1/…` | information dimension | none |
| `density/multifractal-d2/…` | correlation dimension | none |

**`mean` and `max` sparsity are one biomarker pooled two ways.** The mean distance and the furthest
distance answer different questions about the same map, and the statistic part is what says which.

### 2.1 Over the field of view, or over the frame

These are **different numbers** and the difference is not small. `over-image` divides by every pixel
in the frame, including the black surround outside the circular field; `over-fov` divides by the lit
field only. A photograph with a large black border reports a much lower `over-image` density for the
same eye. Two implementations reporting "vessel density" may be reporting either.

### 2.2 Box counting is not the multifractal dimension

`density/box-counting` is a single dimension from a plain box count. The three multifractal
dimensions — capacity, information and correlation — come from a spectrum, and coincide only for a
*monofractal*. PVBM computes the multifractal set and **not** the plain box count, which is why its
columns map to `multifractal-*` and not to `box-counting`.

## 3. Definitions of record

- **Density** has **no single origin** — it is arithmetic that many papers report, so the entry
  carries the detailed description above rather than a citation.
- **Area and length:** [Martinez-Perez 2000](../papers/martinez-perez-2000.md), the tree-sum
  measurements, as [Fhima 2022](../papers/fhima-2022.md) runs them.
- **Fractal dimension:** [Stosic 2006](../papers/stosic-2006.md) for the multifractal treatment of
  retinal vessels. The plain box count is older and has no single retinal origin.
- **Sparsity:** [Vargas 2026](../papers/vargas-2026.md).

## 4. Inputs required

A vessel or artery/vein mask for area and the densities. A centreline for skeleton length. A field
of view mask for `over-fov` and for sparsity, which needs to know which retina to measure distance
from.

## 5. Measurement region

`fov` by default. `over-image` is the exception that names its own denominator rather than taking a
region, and is kept as a separate biomarker for exactly that reason.

## 6. Units and scale dependence

| Biomarker | Unit | Scale-invariant? |
| --- | --- | --- |
| `area` | **µm²** | no |
| `skeleton-length` | **µm** | no |
| `over-fov`, `over-image` | dimensionless fraction | **yes** |
| `sparsity` | **µm** | no |
| all four dimensions | dimensionless | yes in principle |

**Never pixels.** An implementation returning pixel areas has its output multiplied by the square of
the store's scale by its adapter.

**A fractal dimension is dimensionless and still not comparable across resolutions**, which is
worth stating because the unit suggests otherwise. A box count over a bounded raster depends on the
range of box sizes available, and a thickened vessel adds area-like scaling below its own width —
so the same eye at two resolutions gives two dimensions. This repository has measured that:
AutoMorph's box-counting dimension moves by 20% and its descendants' by 80% when a shape is merely
rotated.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | `over-image` density, box-counting dimension | retipy's `retina.py` | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | the same, **per zone** | `automorph/measure/` | Rewritten from retipy |
| [AutoMorphClass](../projects/automorphclass.md) | AutoMorph's set | `src/pytorch_automorph/` | Reimplemented |
| [PVBM](../projects/pvbm.md) | area, skeleton length, the three multifractal dimensions and a singularity length | `PVBM/GeometryAnalysis.py`, `FractalAnalysis.py` | Original |
| [VascX](../projects/vascx.md) | density and sparsity over a disc-centred circle | `vascx/fundus/features/` | Original |

## 8. Sensitivity and failure modes

- **Segmentation thickness sets the area directly.** A model drawing thicker vessels reports a
  higher density for the same eye, and nothing about the number reveals it.
- **The field of view decides the denominator.** A 30° and a 45° photograph of one eye give
  different densities, because the peripheral retina is less vascular than the posterior pole.
- **Fractal dimensions depend on the scale range**, per §6, and on the mask's resolution more than
  on the vasculature.
- **Sparsity is dominated by the largest avascular area**, so the foveal avascular zone and any
  segmentation gap compete to set the maximum.
- **PVBM's area and length are lost entirely on a dense tree**, because the geometry call raises —
  see [topology](topology.md) §8.

## 9. Known defects

- **PVBM's skeleton length excludes vessels that do not reach the optic disc.** *Our finding,
  2026-09-26.* Its current class walks each tree from the disc, so a segment lying away from it is
  not measured at all and the length reads zero. Correct for a disc-anchored measurement, and
  **not** what the catalogued name means.
- **The AutoMorph family's box-counting dimension is strongly rotation-dependent.** *Our finding,
  2026-09-24.* Up to 80% spread across four angles of a shape that did not change.

---

**Links and definitions last checked:** 2026-09-30.
