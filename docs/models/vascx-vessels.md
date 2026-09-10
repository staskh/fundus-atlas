# VascX vessel segmentation

Marks every blood vessel in a colour-fundus photograph as one class, without separating arteries from veins. Its authors' claim rests on training breadth rather than architecture: more than fifteen public annotated datasets combined with Dutch cohort images, so that the model holds up across cameras and populations.

It is one of five models released together as the VascX ensembles; each is catalogued separately.
The others are [vessels](vascx-vessels.md), [artery/vein](vascx-artery-vein.md),
[disc](vascx-disc.md), [fovea](vascx-fovea.md) and [quality](vascx-quality.md) — minus this one.

## 1. Code reference

- **Repository:** https://github.com/Eyened/retinalysis-vascx (inference and biomarkers); model
  execution lives in the companion package `retinalysis-inference`.
- **Version described here:** commit `d0cde1c7` (2026-08-07), tag `v0.2.0`; PyPI
  `retinalysis-vascx` 1.4.0.
- **Most recent commit:** 2026-08
- **Training code included:** No. No training script was found in the repository; the training
  procedure is described in the paper only, so this model can be run but not retrained.
- **Language and how it runs:** Python with PyTorch, as part of `vascx run-models`. This model can
  be replaced with `--vessels-model`, or by placing a file at `vessels/vessels_july24.pt` inside a directory given by
  `--model-dir` or the `VASCX_MODEL_DIR` environment variable.

## 2. License

- **Code:** Not stated — the repository has no LICENSE file and the PyPI metadata leaves the field
  empty.
- **Model weights:** AGPL-3.0, as stated on the
  [Hugging Face model page](https://huggingface.co/Eyened/vascx). Strong copyleft, with
  consequences for network services.

## 3. Major publications by the authors

- Vargas Quiros JD, Liefers B, van Garderen KA, Vermeulen JP, Klaver CCW. *VascX Models: Deep
  Ensembles for Retinal Vascular Analysis From Color Fundus Images.* Translational Vision Science &
  Technology 2025;14(7):19. [PMC12306690](https://pmc.ncbi.nlm.nih.gov/articles/PMC12306690/) ·
  [PubMed 40699175](https://pubmed.ncbi.nlm.nih.gov/40699175/)

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** one class — blood vessel against background.
- **Input grid:** 1024×1024. Preprocessing crops to the detected fundus bounds and resamples so the
  fundus diameter fills a 1024-pixel square, so every VascX model sees the retina at the same scale
  regardless of the camera's native resolution — which is what makes VascX biomarkers comparable
  across cameras without a per-image scale factor.
- **Output grid:** the vessel mask at 1024×1024, the grid every downstream biomarker is measured on.
- **Grid set in:** `square_size=1024` in `rtnls_fundusprep/preprocessor.py` (the default passed by
  its batch entry point), with `rescale(image, resolution=1024)` in the same package's `utils.py`.
- **Input expected:** a colour-fundus photograph, in standard image formats or DICOM. Preprocessing
  is not optional: the pipeline crops to the field of view and enhances contrast first.
- **Preprocessing in the published code:** performed by
  [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) (AGPL-3.0), which the
  authors report succeeds in detecting image bounds on 99.5% of a diverse set — their measurement.

## 5. Architecture

- **Family:** U-Net, per the paper, trained with a new preprocessing algorithm and strong data
  augmentation.
- **Parameters:** Unknown.
- **Single model or ensemble:** an ensemble; the member count is in the paper.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| More than fifteen published annotated datasets, combined | Training | Their own authors | In the paper; the per-model split is not restated here |
| Dutch cohort images, principally the Rotterdam Study | Training | The cohort's graders | In the paper |

The training set absorbs most of the public annotated data, so few public datasets remain for a
blind benchmark of this model. That cuts both ways: broad training is why it generalises, and also
why an independent evaluation is hard to construct.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://huggingface.co/Eyened/vascx — file `vessels/vessels_july24.pt`.
- **Format and size:** PyTorch `.pt`, fetched automatically by the inference code.
- **Files in an ensemble:** one file, itself an ensemble checkpoint.

## 8. Performance as reported by the authors

The VascX Models paper reports a Dice score of 0.833 against 0.732 for AutoMorph, and better connectivity of the vascular tree. A Dice score measures overlap between a predicted mask and a human-drawn one. This is the authors' own comparison of their model against a competitor, recorded as their claim.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [VascX](../projects/vascx.md) | One stage of `vascx run-models` | The published weights |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- The weight file is stamped `july24`: the models predate the 2026 toolbox paper, so a newer
  toolbox release does not mean a newer model.
- Because the model can be swapped at the command line, a VascX result is interpretable only if the
  weights used are recorded with it.

---

**Links and license last checked:** 2026-09-10
