# AutoMorph

AutoMorph takes a folder of colour-fundus photographs and returns a table of vascular measurements
— vessel width, tortuosity, fractal dimension, artery-to-vein ratio and optic cup-to-disc ratio —
one row per image. It runs in four stages: preprocessing, an automatic image-quality grade, four
segmentation steps (vessels, arteries against veins, optic disc and cup), then the measurement
step. Its authors present it as a pipeline for large cohort studies, and it can be run in Google
Colab, in Docker, or on a local machine.

## 1. Code reference

- **Repository:** https://github.com/rmaphoh/AutoMorph
- **Version described here:** commit `9a953e5e` (2025-06-21). The project publishes no tags or
  releases, so a commit is the only way to pin a version.
- **Most recent commit:** 2025-06
- **Training code included:** No — inference only. Every module ships `test_outside` scripts and
  trained weights; no training script is present. Training code for the vessel and artery/vein
  models lives in [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation)
  (`train.py`), and for the disc/cup model in [lwnet](https://github.com/agaldran/lwnet).
- **Language and how it runs:** Python (3.11, PyTorch 2.3). Three routes are documented — a
  [Colab notebook](https://colab.research.google.com/drive/13Qh9umwRM1OMRiNLyILbpq3k9h55FjNZ),
  Docker (`DOCKER.md`), or a local install (`LOCAL.md`). The authors state a GPU is essential,
  though CPU and Apple GPU support have been added.

## 2. License

- **Code:** Apache License 2.0 (`LICENSE` in the repository). Note that two of the borrowed
  components listed in section 4 carry GPL-3.0 licenses at their own source, which matters if you
  redistribute a combined work.
- **Model weights:** No separate license is stated. The weights are committed inside this
  repository, so the repository license is the only statement available.

## 3. Major publications by the authors

- Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M, Struyven R, Alexander DC, Keane PA, et al. *AutoMorph:
  Automated Retinal Vascular Morphology Quantification Via a Deep Learning Pipeline.* Translational
  Vision Science & Technology 2022;11(7):12.
  [Article](https://tvst.arvojournals.org/article.aspx?articleid=2783477) ·
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)

## 4. Segmentation models used

Four modules, four different models. The binary vessel model and the artery/vein model are not the
same network, a point easily missed because both descend from the same group's work:

| Module | Model | Segments | Origin |
| --- | --- | --- | --- |
| `M1_Retinal_Image_quality_EyePACS` | [AutoMorph quality grader](../models/automorph-quality-grader.md) — an EfficientNet classifier, ensemble of eight | Image quality grade, not anatomy — and a **gate**: see below | Introduced here. The grading *labels* come from the [EyeQ](https://github.com/HzFu/EyeQ) dataset, but the model is AutoMorph's own, trained on them — it is not [EyeQ](../datasets/eyeq.md)'s published MCF-Net |
| `M2_Vessel_seg` | [SEGAN vessel segmenter](../models/segan-vessel.md) — an adversarial segmenter — a generator (`Segmenter`) trained against a `Discriminator`; the module's own script is headed "This is sh file for SEGAN" and its weight files are named `G_best_F1_epoch.pth` for the generator | Blood vessels only, as one class | Borrowed. The GAN backbone is the SEGAN method of [A Refined Equilibrium Generative Adversarial Network for Retinal Vessel Segmentation](https://arxiv.org/abs/1909.11936) (Neurocomputing 2021); [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) states its backbone is a revision of that method |
| `M2_Artery_vein` | [AutoMorph artery/vein](../models/automorph-artery-vein.md) — [BF-Net](../models/bf-net.md)'s binary-to-multi fusion network, retrained here on all three artery/vein datasets at once and shipped as eight seeds | Arteries against veins (multi-class) | Borrowed from [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) (GPL-3.0), the MICCAI 2021 paper [Learning to Address Intra-segment Misclassification in Retinal Imaging](https://doi.org/10.1007/978-3-030-87193-2_46); the module's script is headed "This is SH file for LearningAIM" |
| `M2_lwnet_disc_cup` | [AutoMorph disc-and-cup model](../models/automorph-disc-cup.md) — the [lwnet](../models/lwnet.md) architecture retrained for this task | Optic disc and cup | Borrowed from [lwnet](https://github.com/agaldran/lwnet) (MIT) |

Why the split matters to a reader: the binary vessel mask and the artery/vein mask are produced by
two independent networks trained on different datasets (`ALL-SIX` versus `ALL-AV`, see section 5),
so they can disagree with each other on the same photograph. A vessel present in the binary mask
need not appear in the artery/vein mask.

The architectures are all borrowed. What AutoMorph adds is a set of weights it trained itself for
those architectures, plus the ensembling and the plumbing between stages — see section 5.

**The quality stage decides what the rest of the pipeline ever sees.**
`merge_quality_assessment.py` sorts every photograph into `Results/M1/Good_quality/` or
`Results/M1/Bad_quality/`, and all three segmentation modules read the first of those only. The
rule is not the grader's own verdict: a photograph passes when the grader's argmax is Good, **or**
when it is Usable and the mean probability of the Reject class is below 0.25. So the middle class
is admitted conditionally, on a threshold that appears in no paper, and a photograph dropped here
is absent from the output table entirely rather than flagged in it. *(This atlas's observation, read
at commit `9a953e5e` on 2026-09-15.)*

## 5. Models introduced here

No new architecture is introduced. AutoMorph does train and ship its own weights for the borrowed
architectures, as ensembles over several random seeds, so those weights are documented here.

### 5.1 Retrained ensemble weights

- **Training data** (as reported in the paper of section 3):
  - Image-quality grading: EyePACS-Q training split, 12,543 images.
  - Blood-vessel segmentation: [DRIVE](../datasets/drive.md), [STARE](../datasets/stare.md), [CHASE-DB1](../datasets/chase-db1.md), HRF, [IOSTAR](../datasets/iostar.md) and [LES-AV](../datasets/les-av.md) combined (the
    repository names this combination `ALL-SIX`).
  - Artery/vein segmentation: [DRIVE-AV](../datasets/rite.md), [HRF-AV](../datasets/hrf.md) and LES-AV combined (`ALL-AV` in the repository).
  - Optic disc and cup: [REFUGE](../datasets/refuge.md) (800 images) and [GAMMA](../datasets/gamma.md) (100 images).
- **Weights publicly available:** Yes — committed inside the repository, so cloning it downloads
  them and nothing else needs fetching.
- **Download URLs** (one per module, each holding one folder per random seed):
  - Vessels: https://github.com/rmaphoh/AutoMorph/tree/main/M2_Vessel_seg/Saved_model/train_on_ALL-SIX
    — for example the seed-24 generator at
    https://github.com/rmaphoh/AutoMorph/blob/main/M2_Vessel_seg/Saved_model/train_on_ALL-SIX/20210630_uniform_thres40_ALL-SIX_savebest_randomseed_24/G_best_F1_epoch.pth
    (about 35 MB)
  - Artery/vein: https://github.com/rmaphoh/AutoMorph/tree/main/M2_Artery_vein/ALL-AV
  - Optic disc and cup: https://github.com/rmaphoh/AutoMorph/tree/main/M2_lwnet_disc_cup/experiments/wnet_All_three_1024_disc_cup
  - Image quality: https://github.com/rmaphoh/AutoMorph/tree/main/M1_Retinal_Image_quality_EyePACS/Retinal_quality/EyePACS_quality
- **Training code:** Not in this repository — see the training-code note in section 1. Upstream
  pretrained weights for the vessel and artery/vein networks are also offered by
  Learning-AVSegmentation from a Google Drive folder, separately from the copies committed here.

## 6. Biomarkers computed

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| [Tortuosity](../biomarkers/tortuosity.md) (three variants: distance measure, squared curvature, tortuosity density) | Prior literature cited in the AutoMorph paper | [retipy](https://github.com/alevalv/retipy) (GPL-3.0) | Reused — the README names retipy as the feature-measurement component |
| [CRAE, CRVE](../biomarkers/calibre.md) and their ratio [AVR](../biomarkers/calibre.md) — the estimated calibre of the central retinal artery and vein, and the artery-to-vein ratio | Hubbard and Knudtson formulas, cited in the AutoMorph paper | retipy | Reused |
| [Fractal dimension](../biomarkers/density.md) (Minkowski–Bouligand) | Prior literature cited in the paper | retipy | Reused |
| [Vessel density](../biomarkers/density.md), [average vessel width](../biomarkers/calibre.md) | Prior literature cited in the paper | retipy | Reused |
| [Optic cup-to-disc ratio](../biomarkers/landmarks.md) | Standard ophthalmic measure | — | Computed from this pipeline's disc and cup segmentations |

Widths and calibre measurements are reported in microns, which requires a per-image pixel
resolution supplied in `resolution_information.csv`. Without real resolution values those columns
are not in physical units. Measurements are produced both for the whole image (`M3_feature_whole_pic`)
and for zones around the optic disc (`M3_feature_zone`). Failed segmentations appear as `NAN`
rather than as silently wrong numbers.

### 6.1 Every column it writes

*Added 2026-11-22.* Every number the implementation returns, under its own name, beside the
canonical name it answers to — or, where it answers to none, the nearest one and what keeps
it from being that name.

<!-- generated: columns -->
**72 columns**: 53 answer to a canonical name exactly, 15 are close to one and 4 to none. A close name is a pointer for a reader, never a mapping: nothing is compared against it. Rendered from the naming table in `src/biomarkers/automorph.py` by `python -m biomarkers.pages`.

| Its column | Canonical name | Match | What differs |
| --- | --- | :-: | --- |
| `fractal_dimension_binary` | `density/box-counting/vessels` | exact |  |
| `vessel_density_binary` | `density/over-image/vessels` | exact |  |
| `average_width_binary` | `calibre/width/vessels/length-weighted` | exact |  |
| `distance_tortuosity_binary` | `tortuosity/hart-tau1/vessels/mean` | exact |  |
| `squared_curvature_tortuosity_binary` | `tortuosity/hart-tau3/vessels/mean` | close | named for Hart's τ3, the integral of squared curvature; it integrates curvature over the sample index instead, and is out by orders of magnitude on the shapes |
| `tortuosity_density_binary` | `tortuosity/grisan-density/vessels/mean` | exact |  |
| `fractal_dimension_artery` | `density/box-counting/artery` | exact |  |
| `vessel_density_artery` | `density/over-image/artery` | exact |  |
| `average_width_artery` | `calibre/width/artery/length-weighted` | exact |  |
| `distance_tortuosity_artery` | `tortuosity/hart-tau1/artery/mean` | exact |  |
| `squared_curvature_tortuosity_artery` | `tortuosity/hart-tau3/artery/mean` | close | named for Hart's τ3, the integral of squared curvature; it integrates curvature over the sample index instead, and is out by orders of magnitude on the shapes |
| `tortuosity_density_artery` | `tortuosity/grisan-density/artery/mean` | exact |  |
| `fractal_dimension_vein` | `density/box-counting/vein` | exact |  |
| `vessel_density_vein` | `density/over-image/vein` | exact |  |
| `average_width_vein` | `calibre/width/vein/length-weighted` | exact |  |
| `distance_tortuosity_vein` | `tortuosity/hart-tau1/vein/mean` | exact |  |
| `squared_curvature_tortuosity_vein` | `tortuosity/hart-tau3/vein/mean` | close | named for Hart's τ3, the integral of squared curvature; it integrates curvature over the sample index instead, and is out by orders of magnitude on the shapes |
| `tortuosity_density_vein` | `tortuosity/grisan-density/vein/mean` | exact |  |
| `fractal_dimension_binary_zone_b` | `density/box-counting/vessels/B` | exact |  |
| `vessel_density_binary_zone_b` | `density/over-image/vessels/B` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_binary_zone_b` | `calibre/width/vessels/B/length-weighted` | exact |  |
| `distance_tortuosity_binary_zone_b` | `tortuosity/hart-tau1/vessels/B/mean` | exact |  |
| `squared_curvature_tortuosity_binary_zone_b` | `tortuosity/hart-tau3/vessels/B/mean` | close | as the whole-picture column, inside zone B |
| `tortuosity_density_binary_zone_b` | `tortuosity/grisan-density/vessels/B/mean` | exact |  |
| `fractal_dimension_artery_zone_b` | `density/box-counting/artery/B` | exact |  |
| `vessel_density_artery_zone_b` | `density/over-image/artery/B` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_artery_zone_b` | `calibre/width/artery/B/length-weighted` | exact |  |
| `distance_tortuosity_artery_zone_b` | `tortuosity/hart-tau1/artery/B/mean` | exact |  |
| `squared_curvature_tortuosity_artery_zone_b` | `tortuosity/hart-tau3/artery/B/mean` | close | as the whole-picture column, inside zone B |
| `tortuosity_density_artery_zone_b` | `tortuosity/grisan-density/artery/B/mean` | exact |  |
| `fractal_dimension_vein_zone_b` | `density/box-counting/vein/B` | exact |  |
| `vessel_density_vein_zone_b` | `density/over-image/vein/B` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_vein_zone_b` | `calibre/width/vein/B/length-weighted` | exact |  |
| `distance_tortuosity_vein_zone_b` | `tortuosity/hart-tau1/vein/B/mean` | exact |  |
| `squared_curvature_tortuosity_vein_zone_b` | `tortuosity/hart-tau3/vein/B/mean` | close | as the whole-picture column, inside zone B |
| `tortuosity_density_vein_zone_b` | `tortuosity/grisan-density/vein/B/mean` | exact |  |
| `CRAE_Hubbard_zone_b` | `calibre/CRE-hubbard/artery/B` | exact |  |
| `CRVE_Hubbard_zone_b` | `calibre/CRE-hubbard/vein/B` | exact |  |
| `CRAE_Knudtson_zone_b` | `calibre/CRE-knudtson/artery/B` | exact |  |
| `CRVE_Knudtson_zone_b` | `calibre/CRE-knudtson/vein/B` | exact |  |
| `AVR_Hubbard_zone_b` | `calibre/AVR-hubbard/both/B` | exact |  |
| `AVR_Knudtson_zone_b` | `calibre/AVR-knudtson/both/B` | exact |  |
| `fractal_dimension_binary_zone_c` | `density/box-counting/vessels/C` | exact |  |
| `vessel_density_binary_zone_c` | `density/over-image/vessels/C` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_binary_zone_c` | `calibre/width/vessels/C/length-weighted` | exact |  |
| `distance_tortuosity_binary_zone_c` | `tortuosity/hart-tau1/vessels/C/mean` | exact |  |
| `squared_curvature_tortuosity_binary_zone_c` | `tortuosity/hart-tau3/vessels/C/mean` | close | as the whole-picture column, inside zone C |
| `tortuosity_density_binary_zone_c` | `tortuosity/grisan-density/vessels/C/mean` | exact |  |
| `fractal_dimension_artery_zone_c` | `density/box-counting/artery/C` | exact |  |
| `vessel_density_artery_zone_c` | `density/over-image/artery/C` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_artery_zone_c` | `calibre/width/artery/C/length-weighted` | exact |  |
| `distance_tortuosity_artery_zone_c` | `tortuosity/hart-tau1/artery/C/mean` | exact |  |
| `squared_curvature_tortuosity_artery_zone_c` | `tortuosity/hart-tau3/artery/C/mean` | close | as the whole-picture column, inside zone C |
| `tortuosity_density_artery_zone_c` | `tortuosity/grisan-density/artery/C/mean` | exact |  |
| `fractal_dimension_vein_zone_c` | `density/box-counting/vein/C` | exact |  |
| `vessel_density_vein_zone_c` | `density/over-image/vein/C` | close | the zone's vessel pixels over every pixel of the 912 × 912 frame, not over the zone |
| `average_width_vein_zone_c` | `calibre/width/vein/C/length-weighted` | exact |  |
| `distance_tortuosity_vein_zone_c` | `tortuosity/hart-tau1/vein/C/mean` | exact |  |
| `squared_curvature_tortuosity_vein_zone_c` | `tortuosity/hart-tau3/vein/C/mean` | close | as the whole-picture column, inside zone C |
| `tortuosity_density_vein_zone_c` | `tortuosity/grisan-density/vein/C/mean` | exact |  |
| `CRAE_Hubbard_zone_c` | `calibre/CRE-hubbard/artery/C` | exact |  |
| `CRVE_Hubbard_zone_c` | `calibre/CRE-hubbard/vein/C` | exact |  |
| `CRAE_Knudtson_zone_c` | `calibre/CRE-knudtson/artery/C` | exact |  |
| `CRVE_Knudtson_zone_c` | `calibre/CRE-knudtson/vein/C` | exact |  |
| `AVR_Hubbard_zone_c` | `calibre/AVR-hubbard/both/C` | exact |  |
| `AVR_Knudtson_zone_c` | `calibre/AVR-knudtson/both/C` | exact |  |
| `Disc_height` | — | none | a bounding-box extent; the catalogue has no disc or cup size |
| `Disc_width` | — | none | a bounding-box extent; the catalogue has no disc or cup size |
| `Cup_height` | — | none | a bounding-box extent; the catalogue has no disc or cup size |
| `Cup_width` | — | none | a bounding-box extent; the catalogue has no disc or cup size |
| `CDR_vertical` | `landmarks/CDR-vertical` | exact |  |
| `CDR_horizontal` | `landmarks/CDR-horizontal` | exact |  |
<!-- /generated -->

## 7. Examples and notebooks

- The [Colab notebook](https://colab.research.google.com/drive/13Qh9umwRM1OMRiNLyILbpq3k9h55FjNZ) —
  start here. It runs the whole pipeline on a free cloud GPU with no local setup, which is the
  fastest way to see the output table.
- `run.sh` in the repository — the local entry point, and the place to read how the four stages are
  chained. It accepts flags such as `--no_quality` and `--no_segmentation` to skip stages.

## 8. Known defects

### 8.1 Tortuosity measures are invalidated by vessel-segment ordering (inherited from retipy)

- **What is wrong:** AutoMorph's feature measurement reuses retipy's code, and inherits its defect:
  vessel segment pixels are returned in flood-fill discovery order rather than in order along the
  vessel, while every tortuosity formula consumes them as an ordered curve. The root cause is
  described in [retipy.md](retipy.md) section 8.1.
- **What it affects:** all three tortuosity columns — distance measure, squared curvature and
  tortuosity density. Calibre, density, fractal dimension and the disc measurements do not depend on
  segment ordering.
- **Evidence:** [rmaphoh/AutoMorph#19](https://github.com/rmaphoh/AutoMorph/issues/19), filed
  2026-08-11, with a per-feature before-and-after benchmark against [FIVES](../datasets/fives.md) expert annotations.
- **Status:** open and unfixed in this project as of 2026-09-10. Two forks fixed it independently
  and separately from each other — see [automorphalyzer.md](automorphalyzer.md) and
  [automorphclass.md](automorphclass.md) — so tortuosity values from AutoMorph and from either fork
  are not comparable.

### 8.2 Hardcoded values in the same code path

- **What is wrong:** the issue above also reports two hardcoded constants in the tortuosity code
  path that its author argues should be configurable.
- **Status:** open; reported in the same issue. Details are in that issue rather than restated here.

## 9. Notes

- The authors state that invalid results (for instance a failed optic disc segmentation) are written
  as `NAN` values in the output CSV files, so output rows need filtering before analysis.
- Memory is a practical constraint: the README documents reducing batch sizes for the quality,
  artery/vein and disc stages when a 16 GB GPU is not available.
- A competing group (the VascX authors, see [vascx.md](vascx.md)) has published a comparison
  reporting lower preprocessing success and lower segmentation agreement for AutoMorph than for
  their own pipeline. That is their measurement, not ours; this repository's own comparisons are
  reported separately.
- **What this atlas measures of it.** *Our observation, 2026-11-22.* Its run writes 72 numbers a
  picture into `Disc_Features.csv` (or `Macular_Features.csv`): six for the disc and cup, 18 over
  the whole picture, and 24 in each of zones B and C — the zone stage adding Hubbard's and
  Knudtson's equivalents and both arteriovenous ratios. Until that date this atlas's adapter reached
  only the 18 whole-picture ones. It now reaches all 72 by running AutoMorph's own post-segmentation
  steps on a temporary copy of the file tree they read: the two M2 stages' `filter_frag`,
  `optic_disc_centre` from the disc stage, and both vendored copies of retipy. Two things about its
  run that matter to anyone calling those steps outside it: every map is handed to M3 at
  **912 × 912**, so a width is in 912-pixels until multiplied by `Scale_resolution`; and the drivers
  read `resources/retipy.config` (15 pixels per window, R² 0.96), not `evaluate_window`'s defaults.

---

**Links and license last checked:** 2026-09-10
