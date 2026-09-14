# QuickQual

QuickQual scores the quality of a fundus photograph — Good, Usable or Bad — with deliberately little
machinery: an off-the-shelf ImageNet-pretrained DenseNet121, used only to turn the image into a
feature vector, and a support vector machine over those features. Nothing is fine-tuned. Its authors
report it outperforming a purpose-built quality network on the same test set, which makes it a
useful reminder that a task can be easier than the literature around it suggests.

Its practical appeal is size and speed: a few lines of code, one small classifier file, and no
training.

## 1. Code reference

- **Repository:** https://github.com/justinengelmann/QuickQual
- **Version described here:** commit `a94feb02` (2023-11-06); release `1.0` carries the classifier.
- **Most recent commit:** 2023-11
- **Training code included:** Not applicable in the usual sense — the deep network is used frozen,
  off the shelf. The repository provides inference notebooks and `compute_metrics.ipynb`; the code
  that fitted the support vector machine is not included, so the classifier can be used but not
  refitted from this repository.
- **Language and how it runs:** Python. `timm` (or torchvision) supplies
  `densenet121.tv_in1k`; the SVM is loaded with `joblib` from a `.pkl` file, and prediction is a
  single `clf.predict_proba(features)` call.

## 2. License

- **Code:** **None stated.** No LICENSE file and GitHub reports no license, so no reuse permission
  has been granted. This is worth raising with the authors, because a pipeline in this catalogue
  depends on it.
- **Model weights:** the DenseNet121 weights are torchvision's ImageNet weights, under their own
  terms; the SVM classifier file published here carries no stated license.

## 3. Major publications by the authors

- Engelmann J, et al. *QuickQual: Lightweight, convenient retinal image quality scoring with
  off-the-shelf pretrained models.* The repository is the primary reference; a preprint is linked
  from it. No DOI was established at the time of checking.

## 4. What it produces

- **Purpose:** `quality`
- **Output classes:** three probabilities, in order Good, Usable, Bad. AutoMorphalyzer stores the
  probability of rejection rather than a hard decision.
- **Input grid:** shorter side 512 pixels, **aspect ratio preserved** — `F.resize(img, 512)` with a
  single integer scales the smaller edge and leaves the other proportional, so unlike every
  segmentation model here the input is not square and its pixel count varies with the source image.
- **Output grid:** not applicable — three class probabilities, no mask.
- **Grid set in:** the `F.resize(img, 512)` call in the README's inference example; the classifier
  file is named `quickqual_dn121_512.pkl` after it.
- **Input expected:** a fundus photograph resized to 512 pixels and normalised with mean and
  standard deviation 0.5 per channel, per the README's example. The authors' evaluation uses
  [EyePACS](../datasets/eyeq.md) images preprocessed by their `image_preprocessing.py`.
- **Preprocessing in the published code:** resize to 512, normalise; no cropping is performed for
  you.

## 5. Architecture

- **Family:** a frozen DenseNet121 feature extractor with a scikit-learn support vector machine as
  the classifier.
- **The MEME variant is a different model**, provided in a separate notebook: it selects nine of
  the same features by index and applies nine weights and a bias, emitting **one probability that
  the photograph is bad** rather than three class probabilities. It therefore cannot answer the
  three-way question this page's model answers, and it is what
  [AutoMorphalyzer](../projects/automorphalyzer.md) actually runs — see section 9. It has no page
  of its own in this catalogue yet.
- **Parameters:** DenseNet121's, unchanged and not trained; the SVM adds a few kilobytes.
- **Single model or ensemble:** single model.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [EyeQ](../datasets/eyeq.md) — quality-graded [EyePACS](../datasets/eyeq.md) images | Fitting the support vector machine, and evaluation | The EyeQ authors | Yes: EyeQ's train and test splits; results are reported on the test split |
| ImageNet | Pretraining of the frozen feature extractor | ImageNet's annotators | Not applicable — the network is used as published |

EyeQ cannot be used to benchmark this classifier. It shares that limitation with the
[AutoMorph quality grader](automorph-quality-grader.md), which was trained on the same labels — so
those two models cannot be compared on EyeQ against each other in a way that favours neither.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:**
  https://github.com/justinengelmann/QuickQual/releases/download/1.0/quickqual_dn121_512.pkl — the
  fitted SVM. The DenseNet121 weights come from `timm`/torchvision at runtime.
- **Format and size:** a joblib pickle, small. Note that loading a pickle executes code from the
  file, so fetch it only from this official release.
- **Files in an ensemble:** one.

## 8. Performance as reported by the authors

On the EyeQ test set, from the repository README:

| Method | Accuracy | AUC | F1 | Quadratic kappa |
| --- | --- | --- | --- | --- |
| MCF-Net (the EyeQ authors' model) | 0.880 | 0.959 | 0.861 | 0.896 |
| QuickQual | 0.886 | 0.969 | 0.867 | 0.902 |

These are the QuickQual authors' measurements, including their re-statement of a competitor's
result. Recorded as their claim.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Replaces AutoMorph's quality module; one probability that the photograph is bad is written into the collated results file, no image is rejected, and nothing downstream reads the column | **Not this classifier** — the MEME variant of section 5, whose ten numbers are copied into its source. *(This atlas's observation, `preprocess/preprocess.py`, read 2026-09-15)* |

## 10. Known defects

- **The published classifier was pickled by scikit-learn 1.2.2**, a release from 2023 that cannot
  be installed on Python 3.12 at all. Any current environment therefore unpickles it with a much
  later scikit-learn, which warns that the result "might lead to breaking code or invalid results".
  Found 2026-09-14 while loading `quickqual_dn121_512.pkl` with scikit-learn 1.9.1. Nothing
  observed was wrong — the classifier's probabilities behave as the README describes — but it is
  an unverifiable dependency on a version nobody can reproduce, and it is inherited by
  [AutoMorphalyzer](../projects/automorphalyzer.md), which depends on this file.
- **Loading it runs code from it.** A joblib pickle is executable content, and this one is fetched
  over plain HTTPS from a release asset with no published checksum. This atlas pins its sha256
  (`7ed87654…`) and refuses anything else; a user following the README has nothing to check
  against.

## 11. Notes

- **A score, not a gate.** Because AutoMorphalyzer records the probability instead of acting on it,
  every photograph is measured. Filtering on that column is the user's job, and forgetting to do it
  is the likeliest way to get unreliable biomarkers out of that pipeline.
- Depends on `timm` resolving `densenet121.tv_in1k` at runtime, so results depend on the ImageNet
  weights that library serves.
- The missing license (section 2) is inherited by anyone redistributing AutoMorphalyzer.

---

**Links and license last checked:** 2026-09-14
