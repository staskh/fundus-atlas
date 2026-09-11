# EyeQ (and EyePACS)

28,792 photographs re-annotated with a three-level image-quality grade — Good, Usable, Reject. It is
by far the largest dataset in this catalogue, and it is the training data behind **every quality
model here**: AutoMorph's grader learned on its labels, and QuickQual's classifier was fitted on
them. The photographs themselves are not new: EyeQ is a quality annotation of images from the EyePACS
diabetic-retinopathy screening collection.

## 1. What it is

- **Images:** 28,792 — a subset of EyePACS, split 12,543 training and 16,249 test, following
  EyePACS's own division.
- **Collected at:** EyePACS, a diabetic-retinopathy screening service in the United States; the
  photographs were released for a Kaggle competition and re-annotated for quality by the EyeQ
  authors.
- **Purpose:** to make image quality a measurable property rather than a subjective aside, with
  enough images to train on.

## 2. Provenance

Two provenances: the photographs are EyePACS's, the quality grades are EyeQ's.

### 2.1 EyePACS — the photographs

| | |
| --- | --- |
| Home | <https://www.kaggle.com/c/diabetic-retinopathy-detection> |
| Download | **registration** — a Kaggle account and acceptance of the competition rules, at <https://www.kaggle.com/c/diabetic-retinopathy-detection/data> |
| Citation | The Kaggle Diabetic Retinopathy Detection competition, 2015, sponsored by the California Healthcare Foundation with data from EyePACS |
| Licence | **Competition terms** — research use; not a Creative Commons grant, and redistribution is not offered |
| Content | About 88,000 photographs in total, of which EyeQ annotates 28,792 |
| Annotations | Supplies the images and a five-level diabetic-retinopathy grade |

### 2.2 EyeQ — the quality grades

| | |
| --- | --- |
| Home | <https://github.com/HzFu/EyeQ> |
| Download | **direct, no registration** — the label CSVs and preprocessing code are in the repository; the images must come from EyePACS |
| Citation | Fu H, Wang B, Shen J, Cui S, Xu Y, Liu J, Shao L. *Evaluation of Retinal Image Quality Assessment Networks in Different Color-spaces.* MICCAI 2019. [arXiv:1907.05345](https://arxiv.org/abs/1907.05345) |
| Licence | **Not stated** for the labels; the repository carries no licence file |
| Content | 28,792 quality grades over EyePACS photographs |
| Annotations | Supplies a three-level quality grade — Good 16,817, Usable 6,435, Reject 5,540 |

The authors also publish **MCF-Net**, a quality model, and state that its original weights are no
longer usable after library version changes — so the labels, not the model, are what survives.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **Highly mixed** — EyePACS photographs come from many sites and devices, with no single size |
| Microns per pixel | Unknown |
| Camera | **Many, unrecorded per image** — a screening programme's accumulated devices |
| Field of view | Not stated; screening practice is typically 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

This heterogeneity is the point rather than a flaw: a quality model needs to see bad photographs from
many cameras, and no curated dataset supplies them.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Graded per photograph by the EyeQ authors | — | Three levels: Good, Usable, Reject |
| Disease | From EyePACS | — | Five-level diabetic-retinopathy grade, distributed across the quality classes |

## 5. Inheritance

- **Reuses images from:** **EyePACS** — all 28,792, unresized, though EyeQ ships a preprocessing
  script that crops and resizes them for training.
- **Its images are reused by:** [FunPiQ](funpiq.md) samples from EyeQ; anything trained on EyePACS
  shares these photographs.

## 6. Use as a benchmark

- **Catalogued models trained on these images:**
  [AutoMorph's quality grader](../models/automorph-quality-grader.md) trained on the 12,543-image
  training split, and [QuickQual](../models/quickqual.md) fitted its classifier on EyeQ and reports
  its accuracy on the EyeQ test split. **So the two quality models in this catalogue share their
  training labels**, and neither can be evaluated on EyeQ against the other in a way that favours
  neither.
- **Below a model's measuring grid:** Mixed, by image.
- **What it can answer:** quality grading at a scale nothing else approaches. It cannot answer
  held-out quality performance for either catalogued model.

## 7. Known defects

- The images are not distributed with the labels, so obtaining EyeQ means obtaining EyePACS first —
  a competition registration, and a large download.
- Neither the label licence nor the label provenance per grader is stated.

## 8. Notes

- Everything this catalogue says about image quality traces back to one annotation of one screening
  programme's photographs. That is a single point of failure for the quality dimension, and
  [MSHF](mshf.md), [DeepDRiD](deepdrid.md) and [BRSET](brset.md) are the documented alternatives.

---

**Links, licence and access last checked:** 2026-09-11
