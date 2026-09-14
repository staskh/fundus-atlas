# VascX image quality model

Judges whether a colour-fundus photograph is good enough to measure. VascX reports its verdict alongside the biomarkers rather than refusing to process an image, so it behaves as a column to filter on rather than as a gate.

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
  be replaced with `--quality-model`, or by placing a file at `quality/quality.pt` inside a directory given by
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

- **Purpose:** `quality`
- **Output classes:** **three**, emitted as unnamed logits and written to `quality.csv` as the
  columns `q1`, `q2`, `q3`. Nothing published says what the three are; the checkpoint's
  configuration names [EyeQ](../datasets/eyeq.md) as the data it was trained on, and EyeQ grades
  Good, Usable and Reject in that order. *(This atlas's observation; section 10.)* VascX also
  computes classical image-quality metrics without a model — edge strength, sharpness and variance
  of the Laplacian — which are separate from this model's output.
- **Input grid:** **224×224 — not 1024.** Preprocessing crops to the detected fundus bounds and
  resamples so the fundus diameter fills a 1024-pixel square, which is the grid every other VascX
  model works on and what makes VascX biomarkers comparable across cameras. This model then
  **resizes that square down to 224** before the network sees it. *(This atlas's observation, read
  from the published checkpoint on 2026-09-14 — see section 10.)*
- **Output grid:** not a mask — three class scores. The grids still matter, because quality is
  judged on a 224-pixel rendition of the resampled image rather than on the original.
- **Grid set in:** the checkpoint's own stored configuration, `datamodule.test_transform`, which
  holds `square_size: 1024`, `resize: 224`, `contrast_enhance: false`; the 1024 square comes from
  `square_size=1024` in `rtnls_fundusprep/preprocessor.py`, and `resize` is applied by
  `FundusTestTransform` in `rtnls_inference`.
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
| [EyeQ](../datasets/eyeq.md) — **for this model specifically** | Training | The EyeQ authors | Not stated. *(This atlas's observation: the published checkpoint's own configuration points its data at an `eyeq` dataset file — see section 10)* |

The training set absorbs most of the public annotated data, so few public datasets remain for a
blind benchmark of this model. That cuts both ways: broad training is why it generalises, and also
why an independent evaluation is hard to construct.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://huggingface.co/Eyened/vascx — file `quality/quality.pt`.
- **Format and size:** PyTorch `.pt`, fetched automatically by the inference code.
- **Files in an ensemble:** one file, itself an ensemble checkpoint.

## 8. Performance as reported by the authors

Reported in the VascX Models paper. Numbers are in that paper and are not restated here. For context on the task, the authors of [QuickQual](quickqual.md) and of MCF-Net report accuracies around 0.88 on the [EyeQ](../datasets/eyeq.md) test set — a different test set and different models, listed only to place the task.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [VascX](../projects/vascx.md) | One stage of `vascx run-models` | The published weights |

## 10. Known defects

- **The package that runs the models is not declared as a dependency.** `retinalysis-vascx`
  installs without `retinalysis-inference` or `retinalysis-fundusprep`, and importing anything that
  runs a model then fails with `ModuleNotFoundError`. Found 2026-09-14 on commit `d0cde1c7`; a user
  must know to install both, and nothing tells them which versions go together.
- **Nothing published states what the three outputs mean.** They reach the user as `q1`, `q2`,
  `q3`. A pipeline filtering on the wrong column filters on the wrong thing, silently.
- **The documented 1024 grid is not the grid the network sees** (section 4). A reader comparing
  this model against one that works at 512 would conclude it has four times the linear resolution
  to work with; it has rather less.

These three are this atlas's findings, from reading the code and the published checkpoint on
2026-09-14, not the authors' statements.

## 11. Notes

- Unlike the other four, this file is not stamped `july24`, so it may have been produced at a
  different time; no version statement was found.
- Reporting quality rather than acting on it means every image is measured. Filtering is the user's
  job, the same trade-off [AutoMorphalyzer](../projects/automorphalyzer.md) makes with QuickQual.
- **The checkpoint carries its own training configuration**, which is where the facts in sections 4
  and 6 come from. That is unusually good practice — most published weights carry nothing — and it
  is what let this page correct its own grid.

---

**Links and license last checked:** 2026-09-14
