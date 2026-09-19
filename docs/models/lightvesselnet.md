# LightVesselNet

LightVesselNet takes a colour fundus photograph and returns one mask: vessel or not vessel, with no
separation of arteries from veins. Its claim is size. At **75,000 parameters** it is the smallest
network in this catalogue by an order of magnitude — [LWNet](lwnet.md), itself published as a
minimal model, has about seventy thousand *more* — and it is built for machines that cannot hold a
large network at all: a phone, a handheld camera, a clinic with no GPU.

It is catalogued here with a warning attached. The paper reports results on five datasets; the code
its authors published is a single notebook that cannot reproduce them as committed, and no trained
weights were released (sections 7 and 10).

## 1. Code reference

- **Repository:** <https://github.com/ShadmanSobhan/LightVesselNet>
- **Version described here:** the `main` branch as of 2026-09-19; the repository publishes no tags
  or releases, so there is no version to pin but the commit.
- **Most recent commit:** 2026-06
- **Training code included:** Yes, in this repository — the whole of it. The repository is one
  Jupyter notebook, `lightvesselnet.ipynb`, holding preprocessing, augmentation, the model, the
  loss, the training loop and the evaluation. There is no inference script and no package: running
  this on a photograph of your own means lifting the model definition out of the notebook.
- **Language and how it runs:** Python with PyTorch, in a notebook written for Kaggle — its first
  cell pip-installs its dependencies and its configuration points at Kaggle paths
  (`/kaggle/input/...`, `/kaggle/working/...`).

## 2. License

- **Code:** **None stated.** The repository carries no licence file, which means no permission to
  use, copy or modify has been granted. The paper itself is under arXiv's perpetual
  non-exclusive licence, which covers the *paper* and says nothing about the code.
- **Model weights:** Not applicable — none are published.

## 3. Major publications by the authors

- Sobhan S, Jalil F. *LightVesselNet: An Ultra-Lightweight Sub-100K Parameter Network for Retinal
  Blood Vessel Segmentation.* arXiv, submitted 2026-06-03.
  [arXiv:2606.05354](https://arxiv.org/abs/2606.05354) — a preprint, so not peer reviewed.

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** one — vessel against background, as a probability per pixel. An auxiliary
  output is used during training (`AUX_WEIGHT = 0.2`) and is not part of the answer.
- **Input grid:** **the photograph's own size.** *Our finding, 2026-09-19:* the published notebook
  does not resize at all — its augmentation cell is headed "native resolution, no resize", its
  inference transform is commented "no resize — images are passed at native resolution", and the
  `IMAGE_SIZE = 512` line in its configuration is **commented out**. This **disagrees with the
  paper**, whose experiments table says FIVES was resized to 512×512 and HRF to 1752×1168. Which of
  the two produced the published numbers is not established here.
- **Output grid:** the same as the input, so the mask is already in the photograph's own pixels.
- **Grid set in:** `CFG_S1` in cell 3 of `lightvesselnet.ipynb`, where `IMAGE_SIZE` is commented
  out, and the `norm_inf` transform in cell 12a.
- **Input expected:** a colour fundus photograph. No cropping to the field of view is performed by
  the code, and no framing is assumed.
- **Preprocessing in the published code:** the notebook defines several modes, including
  **green channel plus CLAHE** (clip limit 4, 8×8 tiles) — the classical vessel-segmentation
  preparation, and what the paper describes — and a background-corrected weighted fusion with
  tuned CLAHE. Training adds flips, rotations, elastic deformations, grid distortions, brightness
  and contrast jitter, gamma adjustment, MixUp and CutMix.

## 5. Architecture

- **Family:** a three-level encoder–bottleneck–decoder, in the shape of a U-Net but built out of
  cheap parts: depthwise-separable convolutions with squeeze-and-excitation attention
  (`MicroBlockSE`), a 5×5 depthwise kernel at the deepest level, a bottleneck that looks at four
  dilation rates at once (Multi-Scale Feature Aggregation, with spatial attention), PixelShuffle
  rather than transposed convolution on the way back up, and an edge pathway carrying low-level
  detail past the bottleneck.
- **Parameters:** **75,000**, as claimed by the authors and not verified here — the notebook
  contains a profiling cell that would report it, and no weights exist to load.
- **Single model or ensemble:** a single model. Monte-Carlo dropout sampling (`MC_SAMPLES = 12`) is
  configured, which is uncertainty estimation from one network rather than an ensemble of several.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE](../datasets/drive.md) | Training and test | The dataset's own authors | Yes: the standard 20/20 |
| [STARE](../datasets/stare.md) | Training and test | The dataset's own authors | Leave-one-out over 20 |
| [CHASE-DB1](../datasets/chase-db1.md) | Training and test | The dataset's own authors | 7-fold cross-validation over 28 |
| [FIVES](../datasets/fives.md) | Training and test | The dataset's own authors | Yes: 600 train, 200 test |
| [HRF](../datasets/hrf.md) | Training and test | The dataset's own authors | 5-fold cross-validation over 45 |

**All five are unavailable for a fair benchmark of this model**, which is every vessel dataset this
repository has built. Cross-validation and leave-one-out mean every photograph of STARE, CHASE-DB1
and HRF was in training for some fold, so no part of them is held out.

## 7. Weights

- **Publicly available:** **No.**
- **Download URL:** none. The notebook writes its checkpoint to
  `/kaggle/working/best_lightvesselnet_v6.pth`, a path inside a Kaggle session, and the repository
  contains no `.pth` file — it is 21 KB in total.
- **Format and size:** not applicable.
- **Files in an ensemble:** not applicable.

## 8. Performance as reported by the authors

Their measurements, on their own test splits. **Dice** (called F1 here, the same quantity) measures
overlap with the expert's tracing, 0 to 1; **AUC** is the area under the ROC curve, which asks how
well the model ranks vessel pixels above background ones without committing to a threshold.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DRIVE | Dice · AUC | 0.8070 · 0.9830 | Sobhan & Jalil 2026 |
| STARE | Dice · AUC | 0.8072 · 0.9878 | Sobhan & Jalil 2026 |
| CHASE-DB1 | Dice · AUC | 0.8181 · 0.9896 | Sobhan & Jalil 2026 |
| FIVES | Dice · AUC | 0.8649 · 0.9907 | Sobhan & Jalil 2026 |
| HRF | Dice · AUC | 0.7686 · 0.9763 | Sobhan & Jalil 2026 |

These are the authors' own measurements on their own splits, from a preprint that has not been peer
reviewed. They are **not comparable with this repository's vessel figures**: those are computed over
whole datasets in the photograph's native frame, against a vessel map derived the same way for every
model.

**A threshold chosen on the data.** *Our finding, 2026-09-19:* the notebook contains
`find_best_threshold`, which sweeps the decision threshold on a validation split and sets
`BEST_THRESHOLD` from it, rather than using the 0.5 its metric function defaults to. A Dice score
reported at a threshold fitted for that dataset is not the score the same weights would give on
somebody else's photographs.

## 9. Used by

No catalogued project runs LightVesselNet. Without weights, none could without training it first.

## 10. Known defects

- **The published notebook cannot reproduce the paper as committed.** *Our finding, 2026-09-19:*
  its configuration sets `EPOCHS = 1` and `DEBUG = True`, and its dataset root is a Kaggle dataset
  path. What is published is the state of a debugging run rather than the configuration that
  produced the reported numbers, and the paper does not state the real one. Open.
- **No weights, so no result can be checked.** *Our finding, 2026-09-19:* the repository holds one
  notebook and a README. Every number in section 8 would have to be reproduced by retraining, on
  five datasets, at settings the repository does not carry. Open.
- **The code and the paper disagree about resizing.** *Our finding, 2026-09-19:* section 4. A model
  evaluated at native resolution and one evaluated at 512×512 are two different measurements, and
  the vessel widths a biomarker would take from them differ accordingly. Open.
- **No licence at all**, so the code cannot be reused by anyone who respects the default. Open.

## 11. Notes

- **Its size is the reason to watch it.** 75,000 parameters is small enough to run where nothing
  else here will, and that is a real contribution if the numbers hold. What would establish them is
  weights — this repository could then measure the model on the same terms as every other, which is
  exactly what it cannot do today.
- **Sub-100K is a claim about deployment, not about accuracy.** A model a fiftieth the size of
  [SEGAN](segan-vessel.md) reporting a comparable Dice is interesting precisely because size and
  agreement usually trade against each other; that is a reason to test it rather than to believe it.

---

**Links and license last checked:** 2026-09-19
