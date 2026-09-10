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
  cropping, contrast enhancement) and `rtnls_enface` (the grid definitions used to place regions on
  the retina).

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
- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B. *retinalysis-vascx: An
  explainable software toolbox for the extraction of retinal vascular biomarkers.* arXiv preprint,
  2026. [arXiv:2602.08580](https://arxiv.org/abs/2602.08580) — the biomarker toolbox. Its
  reproducibility analysis reports that most VascX biomarkers reach moderate to excellent agreement
  (intraclass correlation above 0.5) when the same eye is imaged twice, with, in the authors' words,
  "important differences in the level of robustness of different biomarkers". That is their
  measurement, and it is a useful warning: robustness is per-biomarker, not a property of the
  pipeline as a whole.
- A companion paper covers the preprocessing package:
  [arXiv:2512.16044](https://arxiv.org/pdf/2512.16044), *retinalysis-fundusprep: A python package
  for robust color fundus image bounds extraction*.

## 4. Segmentation models used

| Model | Weight file | Segments | Origin |
| --- | --- | --- | --- |
| VascX vessel ensemble | `vessels/vessels_july24.pt` | Blood vessels | Introduced here |
| VascX artery/vein ensemble | `artery_vein/av_july24.pt` | Arteries against veins | Introduced here |
| VascX disc ensemble | `disc/disc_july24.pt` | Optic disc | Introduced here |
| VascX fovea model | `fovea/fovea_july24.pt` | Fovea location (a point, not a region) | Introduced here |
| VascX quality model | `quality/quality.pt` | Image quality assessment, not anatomy | Introduced here |
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

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Caliber (vessel width) | Prior literature | — | Reimplemented; aggregated by median or weighted by vessel length |
| Central retinal equivalents (CRAE, CRVE) | Hubbard reduction, √(d₁²+d₂²), with the artery and vein constants 0.88 and 0.95; the Knudtson variant is implemented separately in `cre_knudtson.py` | — | Reimplemented, with documented parameters: number of concentric circles around the disc, inner and outer radius in disc-diameter multiples, how many largest vessels to keep per circle (6 for the full mode, 4 for temporal or nasal), and orientation mode (temporal, nasal or full) |
| Artery-vein ratio | Ratio of the two equivalents above | — | Derived from the CRE values |
| Tortuosity | Three published families: distance ratio (arc length over chord length), mean curvature along a spline, and inflection counts | — | Reimplemented; selectable per segment or per whole vessel, spline or skeleton length, with optional caps on segment length and on implausible values |
| Vascular density | Prior literature | — | Reimplemented |
| Sparsity | Prior literature | — | Reimplemented, with mode options |
| Bifurcation angles and counts | Prior literature | — | Reimplemented |
| Temporal angles | Prior literature | — | Reimplemented |
| Disc and fovea geometry (including disc-to-fovea distance) | Standard landmarks | — | Implemented here; also the scale reference for other biomarkers |
| Image quality metrics (edge strength, sharpness, variance of Laplacian) | Standard image-quality measures | — | Implemented here, alongside the learned quality model |

### 6.1 Regions

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

### 6.2 Feature sets

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

## 7. Examples and notebooks

- The two-command run on the repository's own `samples/fundus/original/` folder, given in the
  README — start here. It produces segmentations and then a biomarker CSV from a handful of DRIVE,
  CHASE-DB1 and HRF images, so a new user can confirm the install end to end.
- `notebooks/2_feature_extraction.ipynb` — the biomarker stage on its own, and the clearest place to
  see how a feature object, a grid and an aggregator combine into one output column. The numbered
  notebooks `0_preprocess`, `1_segment_preprocessed`, `2_feature_extraction`, `3_post_process` and
  `4_plot_feature_set` follow the pipeline in order; `4_plot_feature_set` draws a feature set's
  regions on an image, which is the fastest way to understand what a region name means.

## 8. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Nothing in this
project's issue tracker or code was found to change the numbers a user would report.

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

---

**Links and license last checked:** 2026-09-10
