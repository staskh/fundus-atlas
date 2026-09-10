# BEAL

BEAL segments the optic disc and the optic cup, and its subject is really a different problem: what
to do when a model trained on one clinic's photographs meets another clinic's camera. Colour,
illumination, sharpness and field of view all shift, and accuracy drops even though the anatomy is
identical.

BEAL's answer is to exploit a symptom of that shift. On unfamiliar images a segmentation model
becomes hesitant, and the hesitancy shows up in two places: fuzzy boundaries, and a high-entropy
(uncertain) probability map. BEAL adds two discriminator networks that try to tell whether a
boundary prediction and an uncertainty map came from the familiar domain or the unfamiliar one, and
trains the segmenter to be indistinguishable — which pushes it to produce confident, sharply bounded
masks on the new camera's images. No annotations from the new domain are needed, which is the point:
labelling disc and cup boundaries takes an expert.

## 1. Code reference

- **Repository:** https://github.com/emma-sjwang/BEAL — the paper cites the same repository under
  the owner name `EmmaW8`, so links in the literature may point at a renamed account.
- **Version described here:** commit `945cad38` (2021-05-05). No tags or releases.
- **Most recent commit:** 2021-05
- **Training code included:** Yes, in this repository — `train.py`, with the unlabelled target
  domain selected by `--datasetT`, and `test.py` for inference.
- **Language and how it runs:** Python with PyTorch 1.0.1, tested by the authors with Python 3.7.
  `python train.py -g 0 --data-dir <data> --batch-size 8 --datasetT RIM-ONE_r3`, then
  `python test.py --model-file ./logs/DGS_weights.tar --dataset Drishti-GS`.

## 2. License

- **Code:** MIT.
- **Model weights:** No separate license stated; distributed from Google Drive.

## 3. Major publications by the authors

- Wang S, Yu L, Li K, Yang X, Fu C-W, Heng P-A. *Boundary and Entropy-driven Adversarial Learning
  for Fundus Image Segmentation.* MICCAI 2019, pp. 102–110. DOI:
  [10.1007/978-3-030-32239-7_12](https://doi.org/10.1007/978-3-030-32239-7_12) ·
  [arXiv:1906.11143](https://arxiv.org/abs/1906.11143)

## 4. What it produces

- **Purpose:** `disc/cup`
- **Output classes:** optic disc and optic cup masks. Both are needed for the cup-to-disc ratio used
  in glaucoma assessment.
- **Input expected:** a colour-fundus photograph cropped around the optic disc. The authors
  distribute a preprocessed version of their datasets, which is the practical statement of what the
  model expects:
  https://drive.google.com/file/d/1B7ArHRBjt2Dx29a3A6X_lGhD0vDVr3sy/view
- **Preprocessing in the published code:** the dataloaders expect the authors' domain-adaptation
  directory layout, with one folder per dataset.

## 5. Architecture

- **Family:** DeepLabv3+ segmentation network — an encoder with atrous spatial pyramid pooling and a
  decoder — with a MobileNetV2 backbone by default, plus two adversarial discriminators
  (`networks/GAN.py`), one on the boundary prediction and one on the entropy map.
- **Parameters:** Unknown; MobileNetV2 is a deliberately small backbone, and the README notes other
  backbones can be substituted.
- **Single model or ensemble:** a single model, trained per target domain — the published weights
  include a Drishti-GS variant, so the target domain is part of the model's identity.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| REFUGE | Source domain, labelled training | The challenge organisers | Yes, the REFUGE training set |
| Drishti-GS | Target domain, unlabelled during training; then test | The dataset's own authors | Yes |
| RIM-ONE-r3 | Target domain, unlabelled during training; then test | The dataset's own authors | Yes |

This is the unusual case where the *test* images were used in training — without their labels. That
is legitimate for unsupervised domain adaptation and is the method's whole premise, but it means
neither Drishti-GS nor RIM-ONE-r3 is a blind benchmark for these weights: the model has seen those
images, just not their annotations. A genuinely independent evaluation needs a third dataset.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://drive.google.com/open?id=1ZPLX937VT31KOZLtIOZjc2IBpnZIYawU — a Google
  Drive folder holding checkpoint archives such as `DGS_weights.tar`, to be placed in the `logs`
  folder. Not versioned, so the file behind the link can change without a commit.
- **Format and size:** PyTorch checkpoint archives (`.tar`).
- **Files in an ensemble:** one per target domain.

## 8. Performance as reported by the authors

The paper reports better optic disc and cup segmentation than the then state-of-the-art unsupervised
domain adaptation methods, on Drishti-GS and RIM-ONE-r3, with more accurate boundaries and
suppressed high-uncertainty predictions. Per-dataset numbers are in the paper and are not restated
here.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued pipeline runs this model | — |

It is catalogued because it is a well-licensed, widely-cited disc-and-cup model with published
weights and training code, and because [ISFA](isfa.md) is built on its code.

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **The target domain is part of the model.** A checkpoint adapted to Drishti-GS is not a general
  disc-and-cup model; on a third camera it has no particular advantage. Record which target domain a
  checkpoint was adapted to.
- Built on 2019-era dependencies (PyTorch 1.0.1, CUDA 9.0), so expect installation work.
- Domain shift is exactly the failure mode this atlas's checks exist to catch, which is why a model
  aimed at it is worth having in the catalogue even with no pipeline using it.

---

**Links and license last checked:** 2026-09-10
