# landmarks

**The optic nerve head and the fovea.** The only family here that is not a measurement of blood
vessels — these describe the anatomy the vessels are arranged around, and are catalogued because
several vascular biomarkers are defined relative to them and cannot be read without them.

## 1. What it measures

The optic cup widens within the disc as glaucoma progresses, which makes the ratio between them the
most widely used structural measure in glaucoma screening. The distance between the disc and the
fovea is not a disease marker at all: it is a **per-eye ruler**, used to place measurement regions
and to normalise lengths on photographs whose scale is unknown.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `landmarks/CDR-vertical` | the cup's vertical diameter over the disc's | none |
| `landmarks/CDR-area` | the cup's area over the disc's | none |
| `landmarks/disc-fovea-distance` | the straight-line distance between the disc centre and the fovea | none |

**This family has no `structure` part.** An optic disc is not an artery or a vein, so the name stops
after the biomarker — `landmarks/CDR-vertical` is a complete name. That is the family override
described in `PLAN-BIOMARKER.md` §2.1.1.

## 3. Definitions of record

- **Cup-to-disc ratio:** a clinical measurement that predates automated analysis, so there is **no
  defining paper** and the entry carries a detailed description instead. Divide a measure of the cup
  by the same measure of the disc — the vertical diameter for the vertical ratio, the areas for the
  area ratio. The two are **not interchangeable**: a cup that is wide but shallow gives a large area
  ratio and a modest vertical one.
- **Disc–fovea distance:** [Vargas 2026](../papers/vargas-2026.md). The straight-line distance
  between the centre of the segmented optic disc and the detected fovea.

## 4. Inputs required

Disc and cup segmentations for the ratios; disc and fovea for the distance. No vessel mask is used
by anything on this page.

## 5. Measurement region

**Not applicable.** These are defined relative to landmarks rather than over an area, so the region
part does not apply and a name carrying one is an error.

## 6. Units and scale dependence

The two ratios are dimensionless and **scale-invariant** — they are the most robust numbers in this
catalogue for that reason, needing neither a scale nor a field of view.

The disc–fovea distance is a **length, in microns**. It is also the one biomarker whose relationship
to scale is circular in the common case: where a dataset publishes no microns-per-pixel figure, one
is inferred by assuming the disc is 1800 µm across — so a disc–fovea distance derived from that
scale is anchored to an assumption about the disc. It is reported, and the assumption is recorded
beside it.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | disc–fovea distance, in two variants — to the retina's centre and to the fovea | `vascx/fundus/features/` | Original |
| Others | **none** | — | — |

No biomarker adapter in this repository computes a cup-to-disc ratio yet, although several
catalogued **models** segment the cup — see [MODELS.md](../MODELS.md). The gap is in the biomarker
layer rather than in the segmentation.

## 8. Sensitivity and failure modes

- **The cup boundary is the hard part.** Readers disagree about it far more than about the disc, so
  a cup-to-disc ratio inherits that disagreement. Datasets with several readers —
  [RIGA](../datasets/riga.md) with six ophthalmologists, [Chákṣu](../datasets/chaksu.md) — are the
  only way to measure it rather than assume it.
- **A displaced disc moves everything anchored to it**, including the equivalents' rings on the
  [calibre](calibre.md) page.
- **Fovea detection fails on poor-quality photographs** with no distinct macular darkening, and a
  wrong fovea gives a confidently wrong distance.

## 9. Known defects

None recorded as of 2026-09-30 — an absence of findings rather than a clean bill of health. Nothing
in this family has been through the synthetic benchmark, because the shapes settle no value for
either ratio.

---

**Links and definitions last checked:** 2026-09-30.
