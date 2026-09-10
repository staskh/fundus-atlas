# AutoMorph quality grader

This model judges whether a colour-fundus photograph is good enough to measure, grading it Good,
Usable or Reject. It is not anatomy segmentation: it is the gate in front of it, and in AutoMorph it
decides which photographs get measured at all.

It is easily miscredited. The grading *labels* come from the EyeQ dataset, and EyeQ published its
own model (MCF-Net); this is neither. It is an EfficientNet classifier that AutoMorph's authors
trained themselves on EyeQ's labelled EyePACS images, and it is distributed only inside AutoMorph.

## 1. Code reference

- **Repository:** https://github.com/rmaphoh/AutoMorph, module
  `M1_Retinal_Image_quality_EyePACS`. There is no standalone repository.
- **Version described here:** AutoMorph commit `9a953e5e` (2025-06-21).
- **Most recent commit:** 2025-06 (of the host repository)
- **Training code included:** No — the module ships `test_outside.py` and `test_outside.sh` for
  inference only.
- **Language and how it runs:** Python with PyTorch, using `efficientnet_pytorch`. Run as the M1
  stage of AutoMorph's `run.sh`; skippable with `--no_quality`.

## 2. License

- **Code:** Apache-2.0, as part of the AutoMorph repository.
- **Model weights:** No separate license stated; committed in the AutoMorph repository. Note that
  the training labels come from EyeQ, whose repository states no license, and the underlying images
  are EyePACS, which carries its own competition terms.

## 3. Major publications by the authors

- The model is described as the image-quality module of: Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M,
  Struyven R, Alexander DC, Keane PA, et al. *AutoMorph: Automated Retinal Vascular Morphology
  Quantification Via a Deep Learning Pipeline.* Translational Vision Science & Technology
  2022;11(7):12. [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)
- The labels it learns from: Fu H, Wang B, Shen J, Cui S, Xu Y, Liu J, Shao L. *Evaluation of
  Retinal Image Quality Assessment Networks in Different Color-spaces.* MICCAI 2019.
  [arXiv:1907.05345](https://arxiv.org/abs/1907.05345) — the EyeQ dataset and MCF-Net.

## 4. What it produces

- **Purpose:** `quality`
- **Output classes:** three quality grades — Good, Usable, Reject — following EyeQ's grading scheme.
  AutoMorph uses the result to route images; images graded Reject are not carried into measurement.
- **Input expected:** a preprocessed colour-fundus photograph from AutoMorph's own cropping stage.
- **Preprocessing in the published code:** cropping and resizing by the host pipeline.

## 5. Architecture

- **Family:** EfficientNet image classifier, via `efficientnet_pytorch`. The module's `model.py`
  also defines an InceptionV3 variant with a three-class head; the shipped weights are under an
  `efficientnet` folder, so EfficientNet is what runs.
- **Parameters:** Unknown.
- **Single model or ensemble:** ensemble of eight, one per random seed
  (`0_seed_42` … `7_seed_28`).

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| EyeQ training split — 12,543 EyePACS images | Training | Re-annotated for quality by the EyeQ authors | Yes: EyeQ's own train/test division, itself inherited from EyePACS |

EyeQ's test split (16,249 images) is the natural benchmark and was not used for training, but note
that the whole of EyeQ is a re-annotation of EyePACS, so any EyePACS-derived quality benchmark
overlaps this model's training images.

## 7. Weights

- **Publicly available:** Yes, committed in the host repository.
- **Download URL:**
  https://github.com/rmaphoh/AutoMorph/tree/main/M1_Retinal_Image_quality_EyePACS/Retinal_quality/EyePACS_quality/efficientnet
  — eight seed folders.
- **Format and size:** PyTorch checkpoints.
- **Files in an ensemble:** eight.

## 8. Performance as reported by the authors

The AutoMorph paper reports the quality module's performance on EyeQ's test split. Numbers are in
that paper and are not restated here. For context on what a strong result looks like on the same
test set, the EyeQ authors report a corrected accuracy of 0.880 for MCF-Net, and the QuickQual
authors report 0.886 for their method — different models measured by their own authors, listed
here only to place the task, not to rank them.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | The M1 quality stage, which can reject images before measurement | The weights in this repository |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | **Not used** — this module was removed and replaced by [QuickQual](quickqual.md), with no image rejected | — |
| [AutoMorphClass](../projects/automorphclass.md) | **Not used** — no quality stage | — |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **Do not call this EyeQ.** EyeQ is a dataset of 28,792 quality-graded EyePACS images plus MCF-Net;
  this is a separate model trained on those labels. The EyeQ authors also state that MCF-Net's
  original weights are no longer usable after library version changes and recommend retraining, so
  MCF-Net is not a practical alternative off the shelf.
- The gate matters more than its accuracy suggests: an image graded Usable rather than Reject is
  measured, and its biomarkers enter the results table with no further warning.

---

**Links and license last checked:** 2026-09-10
