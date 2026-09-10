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
| `M1_Retinal_Image_quality_EyePACS` | EfficientNet quality grader | Image quality grade, not anatomy | Borrowed from [EyeQ](https://github.com/HzFu/EyeQ) |
| `M2_Vessel_seg` | SEGAN-style adversarial segmenter — a generator (`Segmenter`) trained against a `Discriminator`; the module's own script is headed "This is sh file for SEGAN" and its weight files are named `G_best_F1_epoch.pth` for the generator | Blood vessels only, as one class | Borrowed. The GAN backbone is the SEGAN method of [A Refined Equilibrium Generative Adversarial Network for Retinal Vessel Segmentation](https://arxiv.org/abs/1909.11936) (Neurocomputing 2021); [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) states its backbone is a revision of that method |
| `M2_Artery_vein` | BF-Net — a binary-to-multi fusion network: `Generator_main` fused with a `Generator_branch`, plus a discriminator | Arteries against veins (multi-class) | Borrowed from [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) (GPL-3.0), the MICCAI 2021 paper [Learning to Address Intra-segment Misclassification in Retinal Imaging](https://doi.org/10.1007/978-3-030-87193-2_46); the module's script is headed "This is SH file for LearningAIM" |
| `M2_lwnet_disc_cup` | lwnet (little W-Net) | Optic disc and cup | Borrowed from [lwnet](https://github.com/agaldran/lwnet) (MIT) |

Why the split matters to a reader: the binary vessel mask and the artery/vein mask are produced by
two independent networks trained on different datasets (`ALL-SIX` versus `ALL-AV`, see section 5),
so they can disagree with each other on the same photograph. A vessel present in the binary mask
need not appear in the artery/vein mask.

The architectures are all borrowed. What AutoMorph adds is a set of weights it trained itself for
those architectures, plus the ensembling and the plumbing between stages — see section 5.

## 5. Models introduced here

No new architecture is introduced. AutoMorph does train and ship its own weights for the borrowed
architectures, as ensembles over several random seeds, so those weights are documented here.

### 5.1 Retrained ensemble weights

- **Training data** (as reported in the paper of section 3):
  - Image-quality grading: EyePACS-Q training split, 12,543 images.
  - Blood-vessel segmentation: DRIVE, STARE, CHASE-DB1, HRF, IOSTAR and LES-AV combined (the
    repository names this combination `ALL-SIX`).
  - Artery/vein segmentation: DRIVE-AV, HRF-AV and LES-AV combined (`ALL-AV` in the repository).
  - Optic disc and cup: REFUGE (800 images) and GAMMA (100 images).
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
| Tortuosity (three variants: distance measure, squared curvature, tortuosity density) | Prior literature cited in the AutoMorph paper | [retipy](https://github.com/alevalv/retipy) (GPL-3.0) | Reused — the README names retipy as the feature-measurement component |
| CRAE, CRVE and their ratio AVR — the estimated calibre of the central retinal artery and vein, and the artery-to-vein ratio | Hubbard and Knudtson formulas, cited in the AutoMorph paper | retipy | Reused |
| Fractal dimension (Minkowski–Bouligand) | Prior literature cited in the paper | retipy | Reused |
| Vessel density, average vessel width | Prior literature cited in the paper | retipy | Reused |
| Optic cup-to-disc ratio | Standard ophthalmic measure | — | Computed from this pipeline's disc and cup segmentations |

Widths and calibre measurements are reported in microns, which requires a per-image pixel
resolution supplied in `resolution_information.csv`. Without real resolution values those columns
are not in physical units. Measurements are produced both for the whole image (`M3_feature_whole_pic`)
and for zones around the optic disc (`M3_feature_zone`). Failed segmentations appear as `NAN`
rather than as silently wrong numbers.

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
  2026-08-11, with a per-feature before-and-after benchmark against FIVES expert annotations.
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

---

**Links and license last checked:** 2026-09-10
