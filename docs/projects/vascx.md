# VascX (retinalysis-vascx)

VascX takes colour-fundus photographs and returns a table of vascular biomarkers, in two commands:
one that runs the segmentation models, and one that computes biomarkers from those segmentations.
Its authors emphasise two things — deep ensembles trained on a large and varied mix of images, and
biomarkers that can be computed in more than one published variant, so a user can state exactly
which definition a number follows.

Its distinguishing feature is explicitness. Most pipelines offer one number per biomarker; VascX
asks which version of that biomarker you want — measured over which part of the retina, aggregated
by which statistic, along vessel segments or whole vessel trees — and encodes the answer in the
output column name. That makes results reproducible and comparable within VascX, at the cost of
requiring the user to make choices they may not have known existed.

## 1. Code reference

- **Repository:** https://github.com/Eyened/retinalysis-vascx
- **Version described here:** commit `d0cde1c7` (2026-08-07); the most recent repository tag is
  `v0.2.0`. The Python package is published on PyPI as `retinalysis-vascx` (version 1.4.0 at the
  time of checking), and the tag and package version numbers do not correspond.
- **Most recent commit:** 2026-08
- **Training code included:** No — inference and biomarker code only. The repository ships the
  model-running stage (`vascx run-models`, via the separate `retinalysis-inference` package) and the
  biomarker stage; no training script is present, so the ensembles cannot be retrained from this
  repository.
- **Language and how it runs:** Python with PyTorch, installed with
  `pip install retinalysis-vascx retinalysis-inference`. Two command-line stages:
  `vascx run-models` then `vascx calc-biomarkers`. It selects a CUDA GPU, Apple MPS, or CPU
  automatically, and `--n-jobs` controls the CPU parallelism of the biomarker stage.
- **Related packages by the same group**, installed alongside and worth knowing about because
  behaviour depends on them: `retinalysis-inference` (model execution),
  [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) (image bounds,
  cropping, contrast enhancement) and
  [retinalysis-enface](https://github.com/Eyened/retinalysis-enface) (the optic disc, the fundus,
  and the grid definitions used to place regions on the retina).
- **How this atlas runs it:** as **four pinned clones** rather than four pip installs, from
  2026-10-01. VascX is the upstream this repository has had to read most often, and every
  correction below came from reading these files rather than any documentation — that the quality
  checkpoint resizes to 224 and names EyeQ, that the "Hubbard reduction" is Knudtson's formula,
  that `mean_sparsity` is normalised by the disc-to-fovea distance and so is not a distance.
  Cloning is what keeps that code where a reader can find it instead of inside somebody's
  `site-packages`. The pins:

  | Repository | Pinned at | Carries |
  | --- | --- | --- |
  | [retinalysis-vascx](https://github.com/Eyened/retinalysis-vascx) | `d0cde1c` | the measuring code |
  | [retinalysis-inference](https://github.com/Eyened/retinalysis-inference) | `e5823fe` | model execution, release 0.7.1 |
  | [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) | `ff47bfb` | preparation, release 1.3.0 |
  | [retinalysis-enface](https://github.com/Eyened/retinalysis-enface) | `ec1ca00` | the disc and the grids, release 1.2.0 |

  *Our finding, 2026-10-01:* the inference package's release **0.7.1 is not tagged**. Its
  repository tags 0.7.0 and stops, and PyPI carries a 0.7.1 built one commit later. The pin above
  names that commit, identified by what it did — it added the `pydantic` requirement, which
  0.7.1's metadata carries and 0.7.0's does not.

  A clone brings the code and none of the dependency metadata, so the seventeen ordinary packages
  these four declare — `lightning`, `monai`, `albumentations`, `opencv`, `simplejpeg` and the rest
  — are now pinned directly in this repository's `pyproject.toml` instead of arriving behind them.
  That is a cost of the choice and worth knowing: if a later VascX needs a different `lightning`,
  nothing here will say so.

## 2. License

- **Code:** Not stated. The repository contains no LICENSE file, and the PyPI package metadata
  leaves the license field empty. Do not assume it is open source until the authors state a
  license — ask them. (A closely related package by the same group,
  [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep), is AGPL-3.0, but that
  says nothing binding about this one.)
- **Model weights:** AGPL-3.0, as stated on the
  [Hugging Face model page](https://huggingface.co/Eyened/vascx). AGPL is a strong copyleft license
  and has consequences if the models are served over a network, so read it before deploying.

## 3. Major publications by the authors

- Vargas Quiros JD, Liefers B, van Garderen KA, Vermeulen JP, Klaver CCW. *VascX Models: Deep
  Ensembles for Retinal Vascular Analysis From Color Fundus Images.* Translational Vision Science &
  Technology 2025;14(7):19. [PMC12306690](https://pmc.ncbi.nlm.nih.gov/articles/PMC12306690/) ·
  [PubMed 40699175](https://pubmed.ncbi.nlm.nih.gov/40699175/) — the segmentation models.
- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B.
  *[retinalysis-vascx](../papers/vargas-2026.md): An explainable software toolbox for the extraction
  of retinal vascular biomarkers.* arXiv preprint, 2026.
  [arXiv:2602.08580](https://arxiv.org/abs/2602.08580) — the biomarker toolbox. Its
  reproducibility analysis reports that most VascX biomarkers reach moderate to excellent agreement
  (intraclass correlation above 0.5) when the same eye is imaged twice, with, in the authors' words,
  "important differences in the level of robustness of different biomarkers". That is their
  measurement, and it is a useful warning: robustness is per-biomarker, not a property of the
  pipeline as a whole.
- A companion paper covers the preprocessing package:
  [arXiv:2512.16044](https://arxiv.org/pdf/2512.16044), *retinalysis-fundusprep: A python package
  for robust color fundus image bounds extraction*.

## 4. Segmentation models used

Each model is catalogued separately.

| Model | Weight file | Segments | Origin |
| --- | --- | --- | --- |
| [VascX vessels](../models/vascx-vessels.md) | `vessels/vessels_july24.pt` | Blood vessels | Introduced here |
| [VascX artery/vein](../models/vascx-artery-vein.md) | `artery_vein/av_july24.pt` | Arteries against veins | Introduced here |
| [VascX disc](../models/vascx-disc.md) | `disc/disc_july24.pt` | Optic disc | Introduced here |
| [VascX fovea](../models/vascx-fovea.md) | `fovea/fovea_july24.pt` | Fovea location (a point, not a region) | Introduced here |
| [VascX quality](../models/vascx-quality.md) | `quality/quality.pt` | Image quality assessment, not anatomy | Introduced here |
| fundusprep preprocessing | — | Image bounds, cropping, contrast enhancement — not a segmentation | Borrowed from [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) (AGPL-3.0), by the same group |

Unlike pipelines assembled from other people's models, every model here comes from the same authors
and the same training effort, which is the main structural difference between VascX and AutoMorph
(see [automorph.md](automorph.md)). Each model can be replaced at the command line
(`--model-dir`, the `VASCX_MODEL_DIR` environment variable, or a per-model path), so a user can
substitute their own weights — useful, and a reason to record which weights produced a given result.

## 5. Models introduced here

### 5.1 VascX model ensembles (vessels, artery/vein, disc, fovea, quality)

- **Training data:** the VascX Models paper reports combining more than 15 published annotated
  datasets with colour-fundus images from Dutch cohort studies, principally the Rotterdam Study,
  training U-Net ensembles with a new preprocessing algorithm and strong data augmentation.
  Per-model training and validation splits are in the paper; they are not restated here.
- **Weights publicly available:** Yes.
- **Download URL:** https://huggingface.co/Eyened/vascx — the authors' own Hugging Face model
  repository. The five files are listed in the table above, under the folders `vessels/`,
  `artery_vein/`, `disc/`, `fovea/` and `quality/`. The inference code resolves and downloads them
  automatically; they are not copied into this atlas.
- **Weight file dating:** four of the five files are stamped `july24`, so the segmentation models
  predate the 2026 toolbox work. Toolbox updates do not imply new models.
- **Training code:** Not published as far as could be established. The training procedure is
  described in the VascX Models paper, but no training script was found in this repository.

## 6. Biomarkers computed

Each biomarker is a configurable object rather than a fixed formula. The families below correspond
to the modules in `vascx/fundus/features/`.

> **Read §8.3 before taking a per-vessel number from this table.** VascX's own artery/vein model
> cannot mark an arteriovenous crossing, so it cuts the losing vessel at every one, and VascX's
> tracer never rejoins a cut vessel — a gap of one pixel is permanent. Every row below that is
> counted or aggregated per vessel or per segment is therefore computed on fragments of vessels
> rather than on vessels: the tortuosities, the bifurcation counts, the densities' skeleton
> lengths. Calibre is largely spared, because width is measured locally.

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| [Caliber (vessel width)](../biomarkers/calibre.md) | Prior literature | — | Reimplemented; aggregated by median or weighted by vessel length |
| [Central retinal equivalents](../biomarkers/calibre.md) (CRAE, CRVE) | **Knudtson's** combination, `c·√(d₁²+d₂²)` with c = 0.88 for arteries and 0.95 for veins — in both `cre.py` and `cre_knudtson.py`; see §6.3 | — | Reimplemented twice, differing in protocol rather than formula: `cre.py` applies the combination over configurable concentric circles (number of circles, inner and outer radius in disc-diameter multiples, how many largest vessels per circle, orientation mode), and `cre_knudtson.py` follows Knudtson's own zone-B protocol — the 6 largest zone-B segments in full mode, 4 in temporal or nasal, diameters as segment medians |
| Artery-vein ratio | Ratio of the two equivalents above | — | Derived from the CRE values |
| [Tortuosity](../biomarkers/tortuosity.md) | Three published families: distance ratio (arc length over chord length), mean curvature along a spline, and inflection counts | — | Reimplemented; selectable per segment or per whole vessel, spline or skeleton length, with optional caps on segment length and on implausible values |
| [Vascular density](../biomarkers/density.md) | Prior literature | — | Reimplemented |
| [Sparsity](../biomarkers/density.md) | [Vargas 2026](../papers/vargas-2026.md) | — | Reimplemented, with mode options |
| [Bifurcation angles](../biomarkers/topology.md) and [counts](../biomarkers/topology.md) | Prior literature | — | Reimplemented |
| [Temporal angles](../biomarkers/topology.md) | [Vargas 2026](../papers/vargas-2026.md) | — | Reimplemented |
| Disc and fovea geometry (including [disc-to-fovea distance](../biomarkers/landmarks.md)) | [Vargas 2026](../papers/vargas-2026.md) | — | Implemented here; also the scale reference for other biomarkers |
| Image quality metrics (edge strength, sharpness, variance of Laplacian) | Standard image-quality measures | — | Implemented here, alongside the learned quality model |

### 6.1 It implements Knudtson's formula, and no Hubbard variant

*Our finding, 2026-09-22, from reading the source:* this project computes the central retinal
equivalents by **Knudtson's** formula only. Both classes combine a pair of calibres as
`c·√(d₁² + d₂²)` with c = 0.88 for arteries and 0.95 for veins, which is Knudtson's revision.

**Hubbard's variant is not implemented anywhere in the package.** His formula is
`√(a·w₁² + b·w₂² + c·w₁w₂ + d)` with constants fitted in microns — −10.76 for arterioles, +450.05
for venules — and none of those constants appears in the code. The word "Hubbard" occurs exactly
once in the whole package: in `cre.py`'s own docstring, which calls `√(d₁²+d₂²)` scaled by 0.88 and
0.95 "the Hubbard reduction". That is the upstream's label rather than its arithmetic, and an
earlier version of this page repeated it.

The distinction matters because the two variants are not interchangeable: Knudtson's is purely
multiplicative and therefore scale-free, while Hubbard's carries an additive term that does not
scale, so a value computed under one name is not convertible into the other. The
[synthetic benchmark](../benchmarks/biomarker-synthetic-results.md) maps VascX's equivalents
to the Knudtson name on the strength of the formula rather than the label, and measures them within
0.7% of what the geometry requires.

### 6.2 Regions

Biomarkers can be restricted to a region rather than the whole photograph, using grids placed
relative to the optic disc and the fovea (the centre of vision). The grids available in the shipped
feature sets are:

- **Hemifields** — the retina split into superior (upper) and inferior (lower) halves.
- **Disc-centred rings** — concentric annuli around the optic disc, the classical geometry for
  calibre and CRE measurements.
- **ETDRS grid** — the standard macular grid used in ophthalmic trials.
- **Ellipse field** — an elliptical region around the disc–fovea axis.

If the region a biomarker needs is not visible in the photograph, the biomarker is not computed
rather than estimated. Circles that fall partly outside the retinal mask are discarded from CRE
aggregation for the same reason.

### 6.3 Feature sets

`--feature_set` selects a bundle of biomarker-and-region combinations. The repository ships
`full`, `full_v2`, `full_v3` (the set the README recommends), `od_centered`, `od_centered_narrow`,
`macula_centered`, `sparsity` and `bergmann`. `full_v3` combines, for example, bifurcation angles
and calibre over the full grid and each hemifield, calibre again length-weighted, CRE in temporal,
nasal and full modes, and tortuosity by both distance and curvature.

Two consequences for a reader: a VascX number is comparable only to another VascX number computed
with the same feature set and options, and the feature set name belongs in the methods section of
any paper reporting these values. A separate `faz` (foveal avascular zone) feature family also
exists in the package; whether it applies to colour-fundus photographs or only to other imaging is
Unknown.

### 6.4 Every column it writes

*Added 2026-11-22.* Every number the implementation returns, under its own name, beside the
canonical name it answers to — or, where it answers to none, the nearest one and what keeps
it from being that name.

<!-- generated: columns -->
**132 columns**: 6 answer to a canonical name exactly, 125 are close to one and 1 to none. A close name is a pointer for a reader, never a mapping: nothing is compared against it. Rendered from the naming table in `src/biomarkers/vascx.py` by `python -m biomarkers.pages`.

<details><summary>All 132 columns</summary>

| Its column | Canonical name | Match | What differs |
| --- | --- | :-: | --- |
| `lw_diam_crcl_multiplier_1p16666666667_full_arteries` | `calibre/width/artery/length-weighted` | exact |  |
| `full_cre_arteries` | `calibre/CRE-knudtson/artery/B` | exact |  |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | exact |  |
| `lw_tort_dist_max_segment_len_0p15_crcl_multiplier_1p16666666667_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.15 disc diameters, over its circle at 2.33 disc radii |
| `lw_tort_dist_max_segment_len_0p25_crcl_multiplier_1p16666666667_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.25 disc diameters, over its circle at 2.33 disc radii |
| `lw_tort_curv_crcl_multiplier_1p16666666667_full_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over its circle at 2.33 disc radii |
| `vd_crcl_multiplier_1p16666666667_full_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over its circle at 2.33 disc radii |
| `median_temporal_angle_arteries` | `topology/temporal-angle/artery` | close | measured from the disc–fovea axis; on a synthetic shape that axis is this atlas's convention, so the column is kept under VascX's name |
| `lw_diam_crcl_multiplier_1p16666666667_full_veins` | `calibre/width/vein/length-weighted` | exact |  |
| `full_cre_veins` | `calibre/CRE-knudtson/vein/B` | exact |  |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | exact |  |
| `lw_tort_dist_max_segment_len_0p15_crcl_multiplier_1p16666666667_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.15 disc diameters, over its circle at 2.33 disc radii |
| `lw_tort_dist_max_segment_len_0p25_crcl_multiplier_1p16666666667_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.25 disc diameters, over its circle at 2.33 disc radii |
| `lw_tort_curv_crcl_multiplier_1p16666666667_full_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over its circle at 2.33 disc radii |
| `vd_crcl_multiplier_1p16666666667_full_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over its circle at 2.33 disc radii |
| `median_temporal_angle_veins` | `topology/temporal-angle/vein` | close | measured from the disc–fovea axis; on a synthetic shape that axis is this atlas's convention, so the column is kept under VascX's name |
| `disc_fovea_distance_retina` | `landmarks/disc-fovea-distance` | close | from the disc's edge; on a synthetic shape the fovea is this atlas's convention |
| `disc_fovea_distance_center_retina` | `landmarks/disc-fovea-distance` | close | from the disc's centre; on a synthetic shape the fovea is this atlas's convention |
| `mean_sparsity_vessels` | `density/sparsity/vessels/mean` | close | divided by the disc–fovea distance, so dimensionless; over the whole image |
| `mean_sparsity_crcl_multiplier_1p16666666667_full_vessels` | `density/sparsity/vessels/mean` | close | divided by the disc–fovea distance, so dimensionless; over its circle at 2.33 disc radii |
| `mn_bifangle_crcl_multiplier_1p16666666667_full_arteries` | `topology/branching-angle/artery/mean` | close | over its circle at 2.33 disc radii |
| `mn_bifangle_crcl_multiplier_1p16666666667_full_veins` | `topology/branching-angle/vein/mean` | close | over its circle at 2.33 disc radii |
| `mn_bifangle_crcl_multiplier_1p16666666667_superior_arteries` | `topology/branching-angle/artery/mean` | close | over the superior quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_superior_veins` | `topology/branching-angle/vein/mean` | close | over the superior quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_inferior_arteries` | `topology/branching-angle/artery/mean` | close | over the inferior quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_inferior_veins` | `topology/branching-angle/vein/mean` | close | over the inferior quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_temporal_arteries` | `topology/branching-angle/artery/mean` | close | over the temporal quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_temporal_veins` | `topology/branching-angle/vein/mean` | close | over the temporal quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_nasal_arteries` | `topology/branching-angle/artery/mean` | close | over the nasal quadrant of its circle, on the disc–fovea axis |
| `mn_bifangle_crcl_multiplier_1p16666666667_nasal_veins` | `topology/branching-angle/vein/mean` | close | over the nasal quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_superior_arteries` | `calibre/width/artery/length-weighted` | close | over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_superior_veins` | `calibre/width/vein/length-weighted` | close | over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_inferior_arteries` | `calibre/width/artery/length-weighted` | close | over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_inferior_veins` | `calibre/width/vein/length-weighted` | close | over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_temporal_arteries` | `calibre/width/artery/length-weighted` | close | over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_temporal_veins` | `calibre/width/vein/length-weighted` | close | over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_nasal_arteries` | `calibre/width/artery/length-weighted` | close | over the nasal quadrant of its circle, on the disc–fovea axis |
| `lw_diam_crcl_multiplier_1p16666666667_nasal_veins` | `calibre/width/vein/length-weighted` | close | over the nasal quadrant of its circle, on the disc–fovea axis |
| `nasal_cre_arteries` | `calibre/CRE-knudtson/artery/B` | close | over the nasal half of its circle, at 2.33 disc radii, inside zone B rather than across it |
| `nasal_cre_veins` | `calibre/CRE-knudtson/vein/B` | close | over the nasal half of its circle, at 2.33 disc radii, inside zone B rather than across it |
| `temporal_cre_arteries` | `calibre/CRE-knudtson/artery/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it |
| `temporal_cre_veins` | `calibre/CRE-knudtson/vein/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_superior_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_superior_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_inferior_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_inferior_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_temporal_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_temporal_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_nasal_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the nasal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_dist_max_segment_len_0p2_crcl_multiplier_1p16666666667_nasal_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the nasal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_superior_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_superior_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the superior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_inferior_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_inferior_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the inferior quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_temporal_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_temporal_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the temporal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_nasal_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the nasal quadrant of its circle, on the disc–fovea axis |
| `lw_tort_curv_crcl_multiplier_1p16666666667_nasal_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the nasal quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_superior_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the superior quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_superior_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the superior quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_inferior_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the inferior quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_inferior_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the inferior quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_temporal_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the temporal quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_temporal_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the temporal quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_nasal_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the nasal quadrant of its circle, on the disc–fovea axis |
| `vd_crcl_multiplier_1p16666666667_nasal_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the nasal quadrant of its circle, on the disc–fovea axis |
| `sharpness_crcl_multiplier_1p16666666667_full_vessels` | — | none | how sharply the photograph is focused at the vessels' edges; it needs the photograph |
| `mn_bifangle_arteries` | `topology/branching-angle/artery/mean` | close | over the whole image |
| `mn_bifangle_veins` | `topology/branching-angle/vein/mean` | close | over the whole image |
| `mn_bifangle_hf_superior_arteries` | `topology/branching-angle/artery/mean` | close | over the superior hemifield, split along the disc–fovea axis |
| `mn_bifangle_hf_superior_veins` | `topology/branching-angle/vein/mean` | close | over the superior hemifield, split along the disc–fovea axis |
| `mn_bifangle_hf_inferior_arteries` | `topology/branching-angle/artery/mean` | close | over the inferior hemifield, split along the disc–fovea axis |
| `mn_bifangle_hf_inferior_veins` | `topology/branching-angle/vein/mean` | close | over the inferior hemifield, split along the disc–fovea axis |
| `md_diam_arteries` | `calibre/width/artery/median` | close | over the whole image |
| `md_diam_veins` | `calibre/width/vein/median` | close | over the whole image |
| `md_diam_hf_superior_arteries` | `calibre/width/artery/median` | close | over the superior hemifield, split along the disc–fovea axis |
| `md_diam_hf_superior_veins` | `calibre/width/vein/median` | close | over the superior hemifield, split along the disc–fovea axis |
| `md_diam_hf_inferior_arteries` | `calibre/width/artery/median` | close | over the inferior hemifield, split along the disc–fovea axis |
| `md_diam_hf_inferior_veins` | `calibre/width/vein/median` | close | over the inferior hemifield, split along the disc–fovea axis |
| `lw_diam_arteries` | `calibre/width/artery/length-weighted` | close | over the whole image |
| `lw_diam_veins` | `calibre/width/vein/length-weighted` | close | over the whole image |
| `lw_diam_hf_superior_arteries` | `calibre/width/artery/length-weighted` | close | over the superior hemifield, split along the disc–fovea axis |
| `lw_diam_hf_superior_veins` | `calibre/width/vein/length-weighted` | close | over the superior hemifield, split along the disc–fovea axis |
| `lw_diam_hf_inferior_arteries` | `calibre/width/artery/length-weighted` | close | over the inferior hemifield, split along the disc–fovea axis |
| `lw_diam_hf_inferior_veins` | `calibre/width/vein/length-weighted` | close | over the inferior hemifield, split along the disc–fovea axis |
| `lw_diam_disc_full_arteries` | `calibre/width/artery/length-weighted` | close | over a disc-centred circle (`disc_full`) |
| `lw_diam_disc_full_veins` | `calibre/width/vein/length-weighted` | close | over a disc-centred circle (`disc_full`) |
| `temporal_cre_hf_superior_arteries` | `calibre/CRE-knudtson/artery/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it, superior hemifield only |
| `temporal_cre_hf_superior_veins` | `calibre/CRE-knudtson/vein/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it, superior hemifield only |
| `temporal_cre_hf_inferior_arteries` | `calibre/CRE-knudtson/artery/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it, inferior hemifield only |
| `temporal_cre_hf_inferior_veins` | `calibre/CRE-knudtson/vein/B` | close | over the temporal half of its circle, at 2.33 disc radii, inside zone B rather than across it, inferior hemifield only |
| `md_tort_dist_arteries` | `tortuosity/hart-tau1/artery/median` | close | over the whole image |
| `md_tort_dist_veins` | `tortuosity/hart-tau1/vein/median` | close | over the whole image |
| `md_tort_curv_arteries` | `tortuosity/spline-curvature/artery/median` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the whole image |
| `md_tort_curv_veins` | `tortuosity/spline-curvature/vein/median` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the whole image |
| `lw_tort_dist_vessels_arteries` | `tortuosity/vessel-hart-tau1/artery/length-weighted` | close | arc over chord of whole vessels rather than segments, over the whole image |
| `lw_tort_dist_vessels_veins` | `tortuosity/vessel-hart-tau1/vein/length-weighted` | close | arc over chord of whole vessels rather than segments, over the whole image |
| `lw_tort_dist_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | over the whole image |
| `lw_tort_dist_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | over the whole image |
| `lw_tort_dist_max_segment_len_0p2_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the whole image |
| `lw_tort_dist_max_segment_len_0p2_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the whole image |
| `lw_tort_curv_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the whole image |
| `lw_tort_curv_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the whole image |
| `lw_tort_dist_etdrs_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | over the ETDRS grid, centred on the fovea |
| `lw_tort_dist_etdrs_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | over the ETDRS grid, centred on the fovea |
| `lw_tort_dist_max_segment_len_0p2_etdrs_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over the ETDRS grid, centred on the fovea |
| `lw_tort_dist_max_segment_len_0p2_etdrs_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over the ETDRS grid, centred on the fovea |
| `lw_tort_curv_etdrs_full_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the ETDRS grid, centred on the fovea |
| `lw_tort_curv_etdrs_full_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over the ETDRS grid, centred on the fovea |
| `lw_tort_dist_disc_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | over a disc-centred circle (`disc_full`) |
| `lw_tort_dist_disc_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | over a disc-centred circle (`disc_full`) |
| `lw_tort_dist_max_segment_len_0p2_disc_full_arteries` | `tortuosity/hart-tau1/artery/length-weighted` | close | segments capped at 0.2 disc diameters, over a disc-centred circle (`disc_full`) |
| `lw_tort_dist_max_segment_len_0p2_disc_full_veins` | `tortuosity/hart-tau1/vein/length-weighted` | close | segments capped at 0.2 disc diameters, over a disc-centred circle (`disc_full`) |
| `lw_tort_curv_disc_full_arteries` | `tortuosity/spline-curvature/artery/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over a disc-centred circle (`disc_full`) |
| `lw_tort_curv_disc_full_veins` | `tortuosity/spline-curvature/vein/length-weighted` | close | mean curvature multiplied by the disc–fovea distance, so dimensionless; over a disc-centred circle (`disc_full`) |
| `vd_elps_full_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over an ellipse on the disc–fovea axis |
| `vd_elps_full_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over an ellipse on the disc–fovea axis |
| `vd_disc_full_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over a disc-centred circle (`disc_full`) |
| `vd_disc_full_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over a disc-centred circle (`disc_full`) |
| `vd_etdrs_full_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the ETDRS grid, centred on the fovea |
| `vd_etdrs_full_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the ETDRS grid, centred on the fovea |
| `vd_hf_superior_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the superior hemifield, split along the disc–fovea axis |
| `vd_hf_superior_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the superior hemifield, split along the disc–fovea axis |
| `vd_hf_inferior_arteries` | `density/over-fov/artery` | close | vessel area over the area of its region rather than the field of view; over the inferior hemifield, split along the disc–fovea axis |
| `vd_hf_inferior_veins` | `density/over-fov/vein` | close | vessel area over the area of its region rather than the field of view; over the inferior hemifield, split along the disc–fovea axis |
| `max_sparsity_vessels` | `density/sparsity/vessels/max` | close | divided by the disc–fovea distance, so dimensionless; over the whole image |
| `mean_sparsity_elps_full_vessels` | `density/sparsity/vessels/mean` | close | divided by the disc–fovea distance, so dimensionless; over an ellipse on the disc–fovea axis |
| `max_sparsity_elps_full_vessels` | `density/sparsity/vessels/max` | close | divided by the disc–fovea distance, so dimensionless; over an ellipse on the disc–fovea axis |
| `mean_sparsity_disc_full_vessels` | `density/sparsity/vessels/mean` | close | divided by the disc–fovea distance, so dimensionless; over a disc-centred circle (`disc_full`) |
| `max_sparsity_disc_full_vessels` | `density/sparsity/vessels/max` | close | divided by the disc–fovea distance, so dimensionless; over a disc-centred circle (`disc_full`) |
| `mean_sparsity_etdrs_full_vessels` | `density/sparsity/vessels/mean` | close | divided by the disc–fovea distance, so dimensionless; over the ETDRS grid, centred on the fovea |
| `max_sparsity_etdrs_full_vessels` | `density/sparsity/vessels/max` | close | divided by the disc–fovea distance, so dimensionless; over the ETDRS grid, centred on the fovea |

</details>
<!-- /generated -->

## 7. Examples and notebooks

- The two-command run on the repository's own `samples/fundus/original/` folder, given in the
  README — start here. It produces segmentations and then a biomarker CSV from a handful of [DRIVE](../datasets/drive.md),
  [CHASE-DB1](../datasets/chase-db1.md) and [HRF](../datasets/hrf.md) images, so a new user can confirm the install end to end.
- `notebooks/2_feature_extraction.ipynb` — the biomarker stage on its own, and the clearest place to
  see how a feature object, a grid and an aggregator combine into one output column. The numbered
  notebooks `0_preprocess`, `1_segment_preprocessed`, `2_feature_extraction`, `3_post_process` and
  `4_plot_feature_set` follow the pipeline in order; `4_plot_feature_set` draws a feature set's
  regions on an image, which is the fastest way to understand what a region name means.

## 8. Known defects

### 8.1 The optic disc is resized to 1024 pixels whatever the image is

*Our finding, 2026-09-22.* `rtnls_enface.disc.OpticDisc.__init__` takes `size=1024`, and nothing
passes the retina's own resolution to it. A disc mask handed to a retina built at any other
resolution is therefore resized to 1024, after which every feature measured on a circle around the
disc indexes outside the mask and fails.

- **What it affects:** calibre, the central retinal equivalents, tortuosity and bifurcation angles —
  everything anchored on the disc. On a 2048-pixel frame this atlas measured **34 of the 36
  otherwise computable features lost**.
- **How it presents:** not as an exception. `calc_features` catches each failure, warns, and returns
  `None` in that column, so a caller reading the result sees empty columns rather than an error.
- **Inside the shipped pipeline it does not arise**, because that pipeline works at 1024. It is
  sharp for anyone calling the feature machinery on their own masks at another size.
- **Working around it:** rebuild the disc at the frame's size —
  `retina.disc = OpticDisc(mask, fundus=retina, size=side)` — which is what this repository's
  biomarker adapter (`src/biomarkers/vascx.py`) does.

Not reported upstream by this atlas as of 2026-09-22.

### 8.2 Two features are normalised by the disc-fovea distance, and neither name says so

*Our finding, 2026-10-01.* `Sparsity` takes `normalize=True` by default and **divides** by that
distance; `TortuosityMeasure.Curvature` **multiplies** by it —
`np.mean(spline.curvatures()) * self._get_curvature_scale(...)`, where the scale is
`layer.retina.disc_fovea_distance`. Both results are therefore **dimensionless, in disc-to-fovea
units**, and both were mapped by this atlas onto canonical names that declare a physical unit:
`mean_sparsity` to a distance in microns, `lw_tort_curv` to a curvature in 1/µm. Both mappings are
withdrawn ([BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §5); both columns are still measured and
stored under VascX's own names.

**This is a property of the pipeline rather than a defect in it.** VascX is built around the
disc-to-fovea axis, and expressing a length in units of it is a reasonable thing for it to do. What
it means for anyone reading these numbers is that **a VascX feature cannot be compared with another
project's unless the axis is the same**, and the axis depends on where a fovea model put the fovea.

A real photograph is what exposed it: on HRF the curvature column reads about 1.5, which as 1/µm
would be a vessel turning through a radius of two thirds of a micron. On this atlas's synthetic
shapes the same column reads 0.0002 to 0.013 and merely looked noisy.

### 8.3 An arteriovenous crossing cuts a vessel, and nothing rejoins it

*Our finding, 2026-10-01.* Two facts compound, and together they decide several biomarkers.

**The segmentation cannot express a crossing.** VascX's artery/vein model emits a four-way softmax
whose channels sum to exactly 1.000000, so a pixel is artery *or* vein and the two masks never
overlap — alone among the artery/vein models in this atlas, against an expert reference where 3.4%
of vessel pixels are crossings. At the expert's crossing pixels, 31% to 39% reach neither mask.
[vascx-artery-vein](../models/vascx-artery-vein.md) §10.1 carries the measurements.

**The tracer does not repair it.** A vessel severed in the mask is resolved as **two vessels**, and
a gap of **one pixel** is enough: measured through VascX's own classes, an unbroken 567-pixel vein
resolves as one vessel, and the same vein with a single pixel removed resolves as two of about 293
and 274. No gap width behaves differently. Four stages could have bridged it —
`fill_small_holes`, the degree-2 collapse, `correct_digraph`, and `_build_vessels`, whose
`merge_edges` raises `ValueError("The edges are not consecutive!")` — and none does.
[Vessel tracing](../biomarkers/vessel-tracing.md) §3.2 traces the whole mask-to-vessel path and
§3.2.1 is the gap experiment.

- **What it affects:** anything counted or measured per vessel or per segment. On real photographs
  free vessel ends are **4.4× to 16.7× denser within 25 px of an expert crossing** than elsewhere.
- **It is uneven, and the pattern is the evidence.** Arc-over-chord tortuosity barely moves, because
  VascX already splits long segments deliberately — `max_segment_len` defaults to 0.2 of the
  disc-fovea distance and applies *only* to segment-mode distance tortuosity. Curvature and the
  vessel-level modes get no such splitting. Measured on one HRF photograph against the expert's own
  map, τ1 moved −1.5% where the curvature column moved −39%.
- **The orphan is kept, not dropped.** `make_trees` roots one tree per *connected component*, so a
  severed piece becomes its own vessel rather than disappearing the way [PVBM](pvbm.md)'s
  disc-rooted walk discards a vessel that never reaches the nerve head. Better behaviour; still two
  vessels where the retina has one.
- **Not a reason to prefer another pipeline on its own.** A segmenter that emits overlap has
  recorded the ambiguity rather than resolved it, and this atlas has no measurement saying whose
  crossings are right. What it does mean is that a VascX count of vessels, endpoints or components
  is not comparable with one from a pipeline that bridges gaps, such as
  [AutoMorphClass](automorphclass.md), which bridges up to 22 pixels before tracing.

Not reported upstream by this atlas as of 2026-10-01.

Nothing else was found: an absence of findings, not a clean bill of health.

## 9. Notes

- **Output naming.** Columns follow `[AGGREGATION]_[BIOMARKER]_[PARAMETERS]_[REGION]_[LAYER]`, where
  layer distinguishes arteries, veins and all vessels. A JSON name-mapping file is written next to
  the CSV. Names differ between the `resolved` and `canonical` naming modes, so keep the mapping
  file with the results.
- **Visualisation.** VascX can render an image for every biomarker showing what was measured. For a
  clinician judging whether a number is trustworthy this is the most useful feature in the toolbox,
  and there is no equivalent in the other entries in this catalogue.
- **Units.** Calibre and CRE values derive from segment diameters in pixels; converting to microns
  requires the image scale, which comes from the disc–fovea distance or from camera metadata. Check
  which convention applies before comparing against a pipeline that reports microns directly, such
  as AutoMorph.
- **The missing code license** (section 2) is the most important open question about this project.
  It is publicly downloadable and installable, which is not the same as being licensed for reuse.
- The authors publish a comparison against AutoMorph reporting better preprocessing success rates,
  higher Dice scores and stronger agreement with ground-truth-derived biomarkers. Those are the
  authors' own measurements of their own pipeline, reported here as their claim; this repository's
  independent comparisons are separate.
- **What this atlas measures of it.** *Our observation, 2026-11-22.* `calc-biomarkers` takes no
  default feature set; the README recommends `full_v3`. This atlas's adapter runs both `full_v3`
  and the disc-centred `od_centered` on one retina and keeps all **132** columns the two compute —
  until that date it kept 20 of `od_centered`'s 67 and discarded the rest. Every feature VascX
  declines is recorded with the warning it gave. The ones built on the disc-to-fovea axis
  (superior, inferior, temporal, nasal, the hemifields, the ETDRS and ellipse grids) are kept under
  their own names: on a synthetic shape that axis is a convention of the fixture.

---

**Links and license last checked:** 2026-09-10
