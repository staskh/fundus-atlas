# Vargas 2026

The paper that describes VascX as a biomarker toolbox: how it traces a vessel graph from an
artery-vein mask, which numbers it can compute, and how stable those numbers are when the same eye
is photographed twice on different cameras. It is the definition of record in this atlas for
sparsity, temporal angle and disc–fovea distance.

## 1. Citation

| | |
| --- | --- |
| Title | retinalysis-vascx: An explainable software toolbox for the extraction of retinal vascular biomarkers |
| Authors | Vargas Quiros JD, Beyeler MJ, Ortin Vela S, EyeNED Reading Center, Bergmann S, Klaver CCW, Liefers B, VascX Research Consortium |
| Venue | arXiv preprint, 2026 |
| DOI | none established — [arXiv:2602.08580](https://arxiv.org/abs/2602.08580) |
| Open copy | preprint — [arXiv:2602.08580](https://arxiv.org/abs/2602.08580) |
| PMID | None found |
| Code | [VascX](../projects/vascx.md) — https://github.com/Eyened/retinalysis-vascx |
| Dataset | none established — test-retest used existing photographs, not a new public deposit |
| Other | none established |

The segmentation networks are a separate paper: Vargas Quiros et al., *VascX Models…*, TVST 2025
(PMID [40699175](https://pubmed.ncbi.nlm.nih.gov/40699175/)). That paper stays on the model and
project pages. This page is the toolbox.

## 2. What it is about

Most pipelines hand back one number per biomarker. Vargas and colleagues start from an artery-vein
mask, skeletonise it, build a vessel graph, join segments into longer vessels, and then let the
user say *which* definition, *which* region of the retina, and *which* statistic to report — encoded
in the output column name. Density, central retinal equivalents and tortuosity are in the set;
spatially localised measures sit on grids placed from the disc and the fovea.

They also measured how much those numbers move when the same eye is photographed twice, on
different devices, and how they respond to image perturbations and to heuristic parameter choices.
The finding they emphasise is that robustness is per-biomarker, not a property of the pipeline as a
whole.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the definition of record for [sparsity](../biomarkers/sparsity.md),
  [temporal angle](../biomarkers/temporal-angle.md) and
  [disc–fovea distance](../biomarkers/disc-fovea-distance.md). Those measurements exist in this
  catalogue only because this toolbox published them. The software is catalogued as
  [VascX](../projects/vascx.md); this page is the argument, not the code.
- The test-retest claim is why later biomarker pages can say "most VascX numbers agree with
  themselves on a second photograph, and some do not" without treating that as this atlas's own
  measurement.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Most VascX biomarkers reach moderate to excellent agreement (intraclass correlation above 0.5) when the same eye is imaged twice on different devices, with important differences in robustness between biomarkers | Repeat photographs of the same eye, different cameras | Abstract |
| Sensitivity to image perturbations and to heuristic parameter values supports those robustness differences | Same analyses | Abstract |

These are the authors' measurements on their test-retest set. This atlas's own comparisons are
separate. Per-biomarker ICC figures, where a reader needs them, are on the corresponding biomarker
page if that page restates them; this page does not unpack the tables.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Sparsity](../biomarkers/sparsity.md) | Defines mean and maximum distance-to-nearest-vessel |
| [Temporal angle](../biomarkers/temporal-angle.md) | Defines the arcade-angle measure |
| [Disc–fovea distance](../biomarkers/disc-fovea-distance.md) | Defines the landmark distance used as a ruler |
| [VascX](../projects/vascx.md) | The software this paper describes |
| [Central retinal equivalents](../biomarkers/central-retinal-equivalents.md) | Implements Knudtson and related calibre summaries; does not replace [Knudtson 2003](knudtson-2003.md) |
| [Tortuosity](../biomarkers/tortuosity.md) | Implements published formulas; does not replace [Hart 1999](hart-1999.md) |

## 6. Notes

- This is a preprint. There is no journal DOI yet. The arXiv version used here is v4
  (2026-08-31).
- The TVST 2025 *VascX Models* paper is the segmentation ensembles, not this toolbox. Do not cite
  one for the other.
- The GitHub repository states no licence; the PyPI package leaves the field empty. Weights on
  Hugging Face are AGPL-3.0. See the project page.
- A companion preprint covers preprocessing:
  [arXiv:2512.16044](https://arxiv.org/abs/2512.16044) (*retinalysis-fundusprep*). It is not this
  paper.

---

**Links last checked:** 2026-09-21
