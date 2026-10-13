# CF-Loss U-Net

A plain U-Net that labels each pixel of a colour-fundus photograph as artery, vein, uncertain or
background. What sets it apart is how it was trained: besides matching the annotator pixel by pixel,
it was penalised whenever the **vessel density** or the **fractal dimension** computed from its mask
differed from the annotator's — the loss function its paper calls CF-Loss. It exists to produce masks
whose measurements are right, not only masks that overlap well. The authors publish three sets of
weights, each trained on one dataset.

## 1. Code reference

- **Repository:** https://github.com/rmaphoh/feature-loss
- **Version described here:** commit `bd50916` (2023-05-20). No tags or releases.
- **Most recent commit:** 2023-05
- **Training code included:** Yes, in this repository — `train.py`, with the dataset selectable as
  `DRIVE_AV`, `LES-AV` or `HRF-AV` and the loss as `CF`, `cldice`, `GC` or `AC`; `test.py` for
  evaluation.
- **Language and how it runs:** Python with PyTorch. `test.py` picks CUDA when present; training
  needs CUDA, because the loss moves a tensor to `'cuda'` unconditionally.
  There is no inference script for a new photograph: `test.py` scores the published test split and
  writes metrics, not masks.

## 2. License

- **Code:** MIT, copyright Yukun Zhou 2023 (`LICENSE`).
- **Model weights:** No separate license stated. The weights are a Google Drive file linked from the
  README, which says nothing about their terms.

## 3. Major publications by the authors

- Zhou Y, Xu M, Hu Y, Blumberg SB, Zhao A, Wagner SK, Keane PA, Alexander DC. *CF-Loss:
  Clinically-relevant feature optimised loss function for retinal multi-class vessel segmentation and
  vascular feature measurement.* Medical Image Analysis 2024;93:103098. DOI:
  [10.1016/j.media.2024.103098](https://doi.org/10.1016/j.media.2024.103098) — catalogued as
  [Zhou 2024](../papers/zhou-2024.md).

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four, exclusive — background, artery, vein and **uncertain**, as softmax
  channels 0 to 3. The paper defines the uncertain class, following HRF-AV's labelling, as
  **crossings between arteries and veins together with vessels nobody could identify**, so on these
  annotations it is not a crossings class alone. The published evaluation scores it as a class of its
  own and does not fold it into artery or vein.
- **Input grid:** 720×720, the photograph resized with its aspect ratio ignored. This is the only grid
  the code supports: `Define_image_size` returns 720×720 when `--uniform=True` and fails otherwise.
- **Output grid:** 720×720 logits, resampled bicubically to the photograph's own size before the
  softmax and the arg-max, in `scripts/eval.py`.
- **Grid set in:** `Define_image_size` in `scripts/utils.py`.
- **Input expected:** a colour-fundus photograph and a field-of-view mask of the same size; the
  evaluation reads the mask and scores only inside it. Trained on macula-centred
  ([DRIVE-AV](../datasets/rite.md), [HRF-AV](../datasets/hrf.md)) and disc-centred
  ([LES-AV](../datasets/les-av.md)) photographs, one dataset per set of weights.
- **Preprocessing in the published code:** resize to 720×720, then **scale** each channel by the
  statistics of the photograph's lit pixels — those with any red in them. The expression is
  `(image - mean) / 1.0 * std`, the same as [BF-Net](bf-net.md)'s, which multiplies by the standard
  deviation rather than dividing by it (section 10).

## 5. Architecture

- **Family:** U-Net — an encoder that shrinks the image in four steps while widening it from 64 to
  1,024 channels, and a decoder that grows it back with transposed convolutions, joined at each scale.
  `UNet(input_channels=3, n_classes=4, bilinear=False)` in `scripts/model.py`.
- **Parameters:** not stated by the authors. *This atlas's count, 2026-10-13:* each checkpoint holds
  34,540,932 floating-point values, batch-normalisation statistics included.
- **Single model or ensemble:** **one model per set of weights.** The paper reports means over eight
  models trained on different subsets of each training split; the archive holds one checkpoint per
  dataset, and nothing says which of the eight it is.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE-AV](../datasets/rite.md) | Training — of the `DRIVE_AV` weights; test split held out | The dataset's own artery/vein annotators | Yes: 20 training, 20 test, committed under `data/DRIVE_AV/` |
| [LES-AV](../datasets/les-av.md) | Training — of the `LES-AV` weights; test split held out | The dataset's own authors | Yes: 11 training, 11 test, committed under `data/LES-AV/` |
| [HRF-AV](../datasets/hrf.md) | Training — of the `HRF-AV` weights; test split held out | The dataset's own artery/vein annotators | Yes: 24 training (`01`–`08` of each of the three groups), 21 test, committed under `data/HRF-AV/` |

`train.py` holds back a random part of the training split for validation — 5% under its default
`--validation` flag, where the paper says 10%.

**Each set of weights trained on one dataset**, so which dataset is off limits depends on which is
loaded: the `DRIVE_AV` weights are out-of-sample on HRF and LES-AV, and so on round — the arrangement
[BF-Net](bf-net.md) uses too. On its own dataset each set is out-of-sample only on that dataset's
published test split.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://drive.google.com/file/d/1HDquRTSafMJE-9KfhDRBfGpZgPbXrRCC/view — one zip,
  linked from the repository README, to be unzipped into the repository folder.
- **Format and size:** `checkpoints.zip`, 385,278,580 bytes, holding three PyTorch state dictionaries
  of 138,218,697 bytes each: `checkpoints/DRIVE_AV/CF/CP_best.pth`, `checkpoints/LES-AV/CF/CP_best.pth`
  and `checkpoints/HRF-AV/CF/CP_best.pth`.
- **Files in an ensemble:** three files, one per training dataset; no ensemble.

**A Google Drive file carries no version and no checksum**, so this atlas records its own digest,
taken 2026-10-13: `checkpoints.zip` sha256
`4f980c6cfc23acd7679a796cb57decef03b55b8ffe9757749df21608585ce73c`. The archive was listed and one
checkpoint opened to count its parameters; none has been run.

## 8. Performance as reported by the authors

A Dice (F1) score measures how far a predicted mask overlaps the annotator's, from 0 to 100 here; the
paper's F1 is the per-class score averaged with each class weighted by its pixel count. An ICC
(intraclass correlation) measures how closely a number computed from the predicted mask agrees with
the same number computed from the annotator's, from 0 to 1.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DRIVE-AV | F1 / fractal-dimension ICC / vessel-density ICC | 73.79 ± 0.81 / 0.83 / 0.86 | [Zhou 2024](../papers/zhou-2024.md), Table 1 (U-Net, `LossCF-VB`) |
| LES-AV | F1 / fractal-dimension ICC / vessel-density ICC | 64.71 ± 1.44 / 0.78 / 0.73 | Zhou 2024, Table 1 |
| HRF-AV | F1 / fractal-dimension ICC / vessel-density ICC | 71.82 ± 1.14 / 0.84 / 0.83 | Zhou 2024, Table 1 |

These are the authors' measurements on each dataset's own test split, as means over eight models;
the variant is the one the repository's loss implements (section 11). This atlas's own comparisons
are separate.

## 9. Used by

Not applicable — no catalogued project runs this model, as of 2026-10-13.

## 10. Known defects

- **The input is scaled, not standardised.** `(image - mean) / 1.0 * std` multiplies by the standard
  deviation (section 4). It is the same at training and inference, so it does not break these weights;
  but a reimplementation that divides, as the code appears to intend, feeds the network something it
  never saw. *Observed by this atlas reading `scripts/dataset.py`, 2026-10-13.*
- **There is no way to segment a new photograph.** `test.py` only evaluates the published test split
  against its labels; it writes metrics and keeps no mask. A user has to write the inference loop.
- **Only one grid works.** `Define_image_size` returns nothing unless `--uniform=True`, and the
  default is `'False'`, so the scripts fail when the flag is left off.
- **The weights cannot be pinned by anything the authors publish** (section 7).

None of these is recorded upstream: the repository has no issues filed, as of 2026-10-13.

## 11. Notes

- **Which CF-Loss variant these weights are is inferred, not stated.** The paper compares three —
  vessel density alone, box count alone, and both — and the repository's `CF_Loss` implements both
  together, with the README's weights 0.5 and 1.0 matching the paper's for that variant. The archive
  directory is named only `CF`.
- **The paper's stroke result used BF-Net masks, not these.** It trained BF-Net with CF-Loss too, and
  those weights are not published.
- **The repository commits the three datasets' photographs and labels** under `data/`. They remain
  under each dataset's own terms; the repository's MIT licence does not cover them.
- **Same group, same preprocessing, different network from BF-Net.** The authors also wrote
  [BF-Net](bf-net.md) and [AutoMorph](../projects/automorph.md); this model shares BF-Net's 720 grid,
  its four classes and its scaling, but is a single U-Net rather than a fusion of generators.

---

**Links and license last checked:** 2026-10-13
