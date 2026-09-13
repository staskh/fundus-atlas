# FR-UNet vessel ensemble (Köhler et al.)

Five full-resolution U-Nets, trained on [FIVES](../datasets/fives.md), that return a blood-vessel
mask for a fundus photograph. It is the only vessel segmenter in this catalogue trained on FIVES
alone — 800 photographs at 2048×2048 with a consensus mask on every one, and 200 each of four
disease classes — rather than on the pooled small classics that
[SEGAN](segan-vessel.md) and [LWNet](lwnet.md) learned from.

The ensemble is not for accuracy alone. It comes from a paper about knowing when a segmentation is
wrong: the five members' disagreement is the signal that work uses to predict a mask's quality
before anyone measures anything from it.

## 1. Code reference

- **Repository:** https://github.com/berenslab/MIDL24-segmentation_quality_control — the model and
  its weights. Wrapped for use by the
  [Fundus Image Toolbox](https://github.com/berenslab/fundus_image_toolbox), which is how most
  people will run it.
- **Version described here:** the `segmentation_quality_control` package as the toolbox pins it,
  upstream commit of 2026-05-29.
- **Most recent commit:** 2026-05
- **Training code included:** the upstream repository is the experiment code for the paper and
  contains the training setup; the toolbox wrapper is inference only.
- **Language and how it runs:** Python with PyTorch. Through the toolbox:
  `load_ensemble()` then `ensemble_predict(models, image)`. Weights are fetched from the upstream
  GitHub repository on demand.

## 2. License

- **Code:** **none stated** on the upstream repository — GitHub reports no licence, so no permission
  to reuse or redistribute has been granted whatever the intent. The toolbox wrapper around it is
  MIT, which does not extend to what it wraps.
- **Model weights:** none stated, and they are served from that same repository. This is the trap
  on this entry: a permissively licensed wrapper can make an unlicensed model feel available.

## 3. Major publications by the authors

- Köhler P, Fadugba J, Berens P, Koch LM. *Efficiently correcting patch-based segmentation errors to
  control image-level performance in retinal images.* Medical Imaging with Deep Learning (MIDL)
  2024. [openreview.net/forum?id=DDHRGHfwji](https://openreview.net/forum?id=DDHRGHfwji)
- The architecture is FR-UNet, from Liu et al., *Full-Resolution Network and Dual-Threshold
  Iteration for Retinal Vessel and Coronary Angiograph Segmentation*, IEEE JBHI 2022. DOI:
  [10.1109/JBHI.2022.3188710](https://doi.org/10.1109/JBHI.2022.3188710)

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** blood vessels as one class against background. What the toolbox returns is
  **not binary**: each of the five members is thresholded at 0.5 and the five binary masks are then
  averaged, so a pixel comes back as the **fraction of members that voted for it** — 0, 0.2, 0.4,
  0.6, 0.8 or 1.0 — and the caller must threshold again to obtain a mask.
- **Input grid:** **512×512** by default, the whole image resized with `cv2.resize` and the aspect
  ratio **not** preserved. The size is a parameter.
- **Output grid:** 512×512, then resized back to the original photograph's dimensions before it is
  returned.
- **Grid set in:** `fundus_image_toolbox/vessel_segmentation/inference.py`,
  `ensemble_predict(..., size: Tuple[int, int] = (512, 512))`.
- **Input expected:** a whole fundus photograph in RGB, which the wrapper converts to BGR for the
  contrast step. Nothing requires a field-of-view crop first.
- **Preprocessing in the published code:** **CLAHE** contrast equalisation (`clahe_equalized`), then
  the resize. The contrast step is not optional and is applied per image.

## 5. Architecture

- **Family:** FR-UNet — a U-Net variant that keeps a full-resolution path through the network
  instead of pooling detail away and recovering it, which is what it is for: thin vessels survive.
- **Parameters:** Unknown; not stated by the authors.
- **Single model or ensemble:** **an ensemble of 5**, `FRUNet_0.pth` to `FRUNet_4.pth`, combined by
  averaging their thresholded masks as described in section 4.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [FIVES](../datasets/fives.md) | Training | The dataset's own consensus vessel masks, crowdsourced among medical experts | Unclear from the wrapper; the paper's splits are in the upstream repository |

**[FIVES](../datasets/fives.md) is therefore unavailable for a fair benchmark of this model.** That
matters more here than usual: FIVES is the largest vessel dataset in this catalogue and the obvious
one to test a vessel segmenter on, and this is the model that cannot be tested on it.

## 7. Weights

- **Publicly available:** Yes, though unlicensed (section 2).
- **Download URL:** fetched from the upstream repository at
  https://github.com/berenslab/MIDL24-segmentation_quality_control — the wrapper resolves raw file
  URLs for `FRUNet_0.pth` through `FRUNet_4.pth` and caches them locally.
- **Format and size:** five PyTorch `.pth` checkpoints.
- **Files in an ensemble:** five.

## 8. Performance as reported by the authors

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| FIVES | — | Not restated here | Köhler et al. 2024 |

The MIDL paper's subject is quality control of segmentations rather than a leaderboard figure for
this ensemble, and the toolbox's documentation quotes no accuracy for it. Read the paper for its own
measurements; nothing is reproduced here that this atlas has not checked.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs it | — |

It is reached through the Fundus Image Toolbox, which is a library rather than a pipeline and is
recorded in [PROJECTS.md](../PROJECTS.md) section 3 for that reason.

## 10. Known defects

- **The returned mask is a vote fraction, not a mask.** `ensemble_predict` thresholds each member at
  `threshold` and then averages the five binary results, so what comes back holds values in
  {0, 0.2, 0.4, 0.6, 0.8, 1}. Code that treats the return value as binary — or that measures
  vessel width on it directly — is measuring agreement, not vessels. Read from
  `vessel_segmentation/inference.py` on 2026-09-12; no upstream issue records it, and it may well
  be intended, since the paper is about disagreement.
- **The resize ignores the aspect ratio.** A non-square photograph is squashed to 512×512 before
  segmentation and the mask is stretched back afterwards, so vessels are measured on a distorted
  grid and un-distorted after thresholding. On square photographs — which FIVES is — this does
  nothing.

## 11. Notes

- Trained on 2048×2048 photographs and run at 512×512 by default: that is a four-fold reduction in
  linear resolution against the data it learned from, and thin vessels are exactly what FR-UNet's
  full-resolution path exists to keep. Passing a larger `size` is worth trying before concluding
  anything about the model.
- The unlicensed weights (section 2) are the practical obstacle to using this in anything
  published.

---

**Links and license last checked:** 2026-09-12
