# VascX (retinalysis-vascx)

VascX takes colour-fundus photographs and returns a table of vascular biomarkers, in two commands:
one that runs the segmentation models, and one that computes biomarkers from those segmentations.
Its authors emphasise two things — deep ensembles trained on a large and varied mix of images, and
biomarkers that can be computed in more than one published variant, so a user can state exactly
which definition a number follows. Measurements can be restricted to standard regions defined
relative to the axis between the optic disc and the fovea (the centre of vision).

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
  automatically.

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
  [PubMed 40699175](https://pubmed.ncbi.nlm.nih.gov/40699175/) — the models.
- Vargas Quiros JV, Beyeler MJ, Vela SO, Bergmann S, Klaver CCW, Liefers B. *retinalysis-vascx: An
  explainable software toolbox for the extraction of retinal vascular biomarkers.* arXiv preprint,
  2026. [arXiv:2602.08580](https://arxiv.org/abs/2602.08580) — the biomarker toolbox and its
  configurable definitions.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| VascX vessel ensemble | Blood vessels | Introduced here |
| VascX artery/vein ensemble | Arteries against veins | Introduced here |
| VascX disc ensemble | Optic disc | Introduced here |
| VascX fovea model | Fovea location (a point, not a region) | Introduced here |
| VascX quality model | Image quality assessment | Introduced here |
| fundusprep preprocessing | Image bounds, cropping, contrast enhancement — not a segmentation | Borrowed from [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) (AGPL-3.0), by the same group |

## 5. Models introduced here

### 5.1 VascX model ensembles (vessels, artery/vein, disc, fovea, quality)

- **Training data:** the VascX Models paper reports combining more than 15 published annotated
  datasets with colour-fundus images from Dutch cohort studies, principally the Rotterdam Study,
  using U-Net ensembles with strong data augmentation. Per-model training and validation splits are
  in the paper; they are not restated here.
- **Weights publicly available:** Yes.
- **Download URL:** https://huggingface.co/Eyened/vascx — the authors' own Hugging Face model
  repository, holding the vessel, artery/vein, disc, fovea and quality ensembles. The inference
  code downloads them from there; they are not copied into this atlas.
- **Training code:** Not published as far as could be established. The training procedure is
  described in the VascX Models paper, but no training script was found in this repository.

## 6. Biomarkers computed

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Central retinal equivalents (CRAE, CRVE) and artery-vein ratio | Hubbard and Knudtson formulas from prior literature | — | Reimplemented, with the variant and its parameters selectable by the user |
| Vessel calibers (widths) | Prior literature | — | Reimplemented |
| Vascular density | Prior literature | — | Reimplemented |
| Tortuosity | Prior literature | — | Reimplemented; multiple published definitions supported |
| Bifurcation angles, temporal angles | Prior literature | — | Reimplemented |
| Sparsity and further features | Prior literature | — | Reimplemented |
| Image quality metrics | This project | — | Introduced here |

The authors' stated design point is that many biomarkers have several accepted definitions, so each
supports multiple implementations and configuration arguments, documented in the toolbox paper and
in the code for each biomarker. Two consequences for a reader: a VascX number is only comparable to
another VascX number computed with the same options, and the chosen `--feature_set` (for example
`full_v3`) must be recorded alongside any result. Where a required region is not visible in the
photograph, the biomarker is not computed rather than estimated. VascX can also render a
visualisation for every biomarker, which is the practical way to check a measurement by eye.

## 7. Examples and notebooks

- The two-command run on the repository's own `samples/fundus/original/` folder, given in the
  README — start here. It produces segmentations and then a biomarker CSV from a handful of DRIVE,
  CHASE-DB1 and HRF images, so a new user can confirm the install end to end.
- `notebooks/2_feature_extraction.ipynb` — the biomarker stage on its own, useful for understanding
  what each output column means. The numbered notebooks `0_preprocess`, `1_segment_preprocessed`,
  `2_feature_extraction`, `3_post_process` and `4_plot_feature_set` follow the pipeline in order.

## 8. Notes

- Output column names follow the pattern `[AGGREGATION]_[BIOMARKER]_[PARAMETERS]_[REGION]_[LAYER]`,
  and a JSON name-mapping file is written next to the CSV. Column names are not stable across
  naming modes (`resolved` versus `canonical`), so keep the mapping file with the results.
- The missing code license (section 2) is the most important open question about this project. It is
  publicly downloadable and installable, which is not the same as being licensed for reuse.
- The authors publish a comparison against AutoMorph (see [automorph.md](automorph.md)) reporting
  better preprocessing success rates, higher Dice scores and stronger agreement with
  ground-truth-derived biomarkers. Those are the authors' own measurements of their own pipeline,
  and are reported here as their claim; this repository's independent comparisons are separate.

---

**Links and license last checked:** 2026-09-10
