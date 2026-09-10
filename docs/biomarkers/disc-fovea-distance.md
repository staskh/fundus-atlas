# Optic disc to fovea distance

The distance between the optic nerve head and the centre of vision. On its own it is a modest
anatomical measurement; its importance is as a **ruler**. Every eye has both landmarks, the distance
between them varies far less between people than image magnification does, and so it can convert
pixel measurements into a scale that is comparable across cameras without any calibration data.

VascX uses it exactly that way, and reports it as a biomarker in its own right.

## 1. What it measures

- **In one sentence:** the distance from the optic disc centre to the fovea, and by extension the
  axis between them.
- **Also known as:** disc-fovea distance, DF distance, papillo-macular distance; the
  disc-fovea axis when used as an orientation.
- **Direction of concern:** not itself a disease marker in general use; it is an anatomical
  covariate and a normalisation factor.

## 2. Definition of record

- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B. *retinalysis-vascx: An
  explainable software toolbox for the extraction of retinal vascular biomarkers.* arXiv, 2026.
  [arXiv:2602.08580](https://arxiv.org/abs/2602.08580)
- **The formula, in words:** the straight-line distance between the centre of the segmented optic
  disc and the detected fovea location.

## 3. Variants

Only one definition among the catalogued projects.

An important alternative convention exists and is worth stating because it appears throughout the
older literature: distances and zones expressed in **disc diameters** rather than in disc-to-fovea
distances. Both are anatomical rulers; they are not the same ruler, and the disc diameter is the
more variable of the two.

**Comparability:** a value in pixels is comparable only within one grid; used as a normalisation
factor, it makes *other* biomarkers comparable across cameras, which is its real purpose.

## 4. Inputs required

- **Segmentations:** the optic **disc** and the **fovea**.
- **Derived geometry:** the disc centre, from the disc mask; the fovea point, from the fovea model.
- **Why this matters:** it needs the two landmark models and nothing else — no skeleton, no vessel
  mask. That independence is what makes it usable as a scale for everything else.

## 5. Measurement region

Not applicable — it is a distance between two points, not a measurement over a region. It is
instead what *defines* several regions: VascX's temporal-angle sampling circles and its
normalisation of sparsity and of tortuosity segment-length caps are all expressed as fractions of
this distance.

## 6. Units and scale dependence

- **Unit as computed:** pixels on VascX's 1024 grid.
- **Depends on the pixel grid:** Yes, as a raw value.
- **Depends on a physical scale:** No — and this is the point: it *substitutes* for a physical
  scale. Dividing a pixel measurement by this distance yields a number comparable between cameras
  without knowing microns per pixel.
- **Depends on field of view:** only through visibility — both landmarks must be in frame, which
  fails for photographs centred far from the posterior pole.
- **Scale-invariant:** no as a raw distance; it is the *means* by which other measures become
  scale-invariant.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | as defined, and as a normalisation factor | `vascx/fundus/features/disc_features.py` (`DiscFoveaDistance`) | Original |

No other catalogued project reports it. The AutoMorph family instead converts to microns using a
user-supplied per-image resolution, and PVBM leaves its measurements in pixels — so of the pipelines
here, only VascX has an internal anatomical ruler.

## 8. Sensitivity and failure modes

- **Fovea detection is the weak link.** The fovea is a low-contrast landmark, and unlike the disc
  it has no boundary to fit — see [VascX fovea](../models/vascx-fovea.md).
- **Disc-centred photographs** may not include the fovea at all, in which case this and everything
  normalised by it are unavailable.
- **Using it as a ruler assumes the distance is biologically stable**, which holds well enough
  between healthy adults but less well in high myopia, where the posterior pole is stretched.
- **Reported reproducibility:** covered by the VascX toolbox paper's general finding; no
  per-biomarker figure was established here.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- If the comparison tables ever need one convention for making pixel measurements comparable across
  pipelines, this is the strongest candidate: it needs no camera metadata, only two landmarks that
  every posterior-pole photograph contains.

---

**Links and definitions last checked:** 2026-09-10
