# Fundus Image Toolbox quality ensemble

Given a whole fundus photograph, this returns one number between 0 and 1 — how confident ten
networks are, on average, that the image is gradeable. It exists because the two quality graders
already in this catalogue both learned from [EyeQ](../datasets/eyeq.md), and this one did not: it
was trained on [DeepDRiD](../datasets/deepdrid.md) and [DRIMDB](../datasets/drimdb.md) instead,
with photographs of the outer eye counted as ungradeable, which makes it the only quality model
here that can be scored against an EyeQ-trained one on common ground.

It is a **binary** grader — gradeable against ungradeable — where AutoMorph's and QuickQual's are
three-way. Anything finer has to come from the probability, and the authors are explicit that the
threshold on it is not transferable between datasets.

## 1. Code reference

- **Repository:** https://github.com/berenslab/fundus_image_toolbox
- **Version described here:** commit `d7757e28` (2026-08-13)
- **Most recent commit:** 2026-08
- **Training code included:** **Yes, in this repository** —
  `0_example_usage/training and evaluation/training_quality_cli.py` trains and evaluates a single
  model from a config file or command-line arguments, with notebooks for the same.
- **Language and how it runs:** Python with PyTorch. `pip install fundus-image-toolbox`, then
  `get_ensemble()` and `ensemble_predict(ensemble, image)`. Weights are fetched from Zenodo on
  first use. Runs on CPU or CUDA; batch prediction is supported.

## 2. License

- **Code:** **MIT**.
- **Model weights:** the Zenodo record the code downloads from
  ([11174749](https://zenodo.org/records/11174749)) is not stated separately in the repository;
  check the record's own licence field before redistributing.

## 3. Major publications by the authors

- Gervelmeyer J, Müller S, Huang Z, Berens P. *Fundus Image Toolbox: A Python package for fundus
  image processing.* Journal of Open Source Software 2025;10(108):7101. DOI:
  [10.21105/joss.07101](https://doi.org/10.21105/joss.07101)

## 4. What it produces

- **Purpose:** `quality`
- **Output classes:** a confidence in [0, 1] that the photograph is **gradeable**, and a binary
  class from thresholding it at 0.5 by default. `1` is good quality.
- **Input grid:** **512×512** by default, the whole image resized. The size is a parameter
  (`img_size`), and 512 is kept as the default for backward compatibility with version 0.1.1 rather
  than because it suits every image.
- **Output grid:** not applicable — the output is a number, not a mask.
- **Grid set in:** `fundus_image_toolbox/quality_prediction/scripts/ensemble_inference.py`,
  `ensemble_predict(..., img_size: int = 512)`, applied through
  `get_transforms(split="test", img_size=img_size)`.
- **Input expected:** a **whole fundus photograph**. The authors warn that it was trained on whole
  images and not on zoomed-in cutouts.
- **Preprocessing in the published code:** resize to `img_size`, tensor conversion and
  normalisation from the training transforms. No field-of-view cropping and no contrast
  enhancement.

## 5. Architecture

- **Family:** torchvision classifiers with ImageNet-initialised backbones and a linear head —
  ResNets and EfficientNets, as the authors describe the mixture.
- **Parameters:** Unknown as a total; it varies by member.
- **Single model or ensemble:** **an ensemble of 10**, listed by training timestamp in
  `quality_prediction/scripts/default.py`. Each member returns a probability and the ensemble
  returns their **mean**, which is then thresholded — so a member's vote is never binarised before
  averaging.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DeepDRiD](../datasets/deepdrid.md) | Training and test | The dataset's own binary overall-quality label | Yes: the authors report on a DeepDRiD test split |
| [DRIMDB](../datasets/drimdb.md) | Training and test | The dataset's own three-class grade, with its **outlier** class — images that are not fundus photographs — counted as ungradeable | Yes: a DRIMDB test split |

**[DeepDRiD](../datasets/deepdrid.md) and [DRIMDB](../datasets/drimdb.md) are therefore both
unavailable for a fair benchmark of this model.** Between them they are also the reason it behaves
differently from the other two quality graders here: DRIMDB asks it to reject images that are not
retinas at all, which neither EyeQ nor FQS contains.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://zenodo.org/records/11174749/files/weights.tar.gz — fetched automatically
  on first use.
- **Format and size:** a tar archive of ten PyTorch checkpoint directories, one per ensemble member.
- **Files in an ensemble:** ten, named by training timestamp (`2024-05-03 14-38-34` and nine
  others).

## 8. Performance as reported by the authors

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DeepDRiD test split | Accuracy | 0.78 | `1_read_more/Readmore_quality_prediction.md` |
| DeepDRiD test split | ROC AUC | 0.84 | as above |
| DRIMDB test split | Accuracy | 1.0 | as above |
| DRIMDB test split | ROC AUC | 1.0 | as above |

The authors note that predicting DeepDRiD's binary quality label is a hard task and give 0.75 /
0.75 as the previous state of the art
([Tummala et al., 2023](https://doi.org/10.3390/diagnostics13040622)). These are their measurements
on their own test splits; this atlas's own comparisons are separate.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs it | — |

## 10. Known defects

- **The predicted probability moves with image size.** The authors record this themselves, from
  [issue 20](https://github.com/berenslab/fundus_image_toolbox/issues/20#issuecomment-2895195087),
  and advise comparing scores only across images of the same size. Because `img_size` defaults to
  512 and resizing is unconditional, a set of small photographs is upsampled before scoring and a
  set of large ones is downsampled — so the number depends on a decision the caller may not know
  they are making. Status: documented, not fixed; pass an explicit `img_size` to control it.
- **The threshold is not transferable.** The authors state that the 0.5 cut between good and bad
  has to be re-chosen per dataset, suggesting a percentile of the predicted scores instead. A study
  that keeps 0.5 across cohorts is not applying one standard to both.

## 11. Notes

- It is the only quality model in this catalogue that did not learn from
  [EyeQ](../datasets/eyeq.md), which is what makes it worth having beside
  [AutoMorph's grader](automorph-quality-grader.md) and [QuickQual](quickqual.md). The corollary is
  that it cannot be scored on DeepDRiD, which those two can.
- Binary against their three classes: mapping "gradeable" onto Good/Usable/Reject is a decision, not
  a translation, and has to be made explicit before any comparison.

---

**Links and license last checked:** 2026-09-12
