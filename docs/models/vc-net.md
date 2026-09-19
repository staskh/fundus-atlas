# VC-Net

VC-Net takes a colour fundus photograph and returns two things at once: a map of which pixels are
blood vessel, and a map of which of those vessels are **arteries** and which are **veins**. Its
idea is in its name — a *vessel-constraint* network. One branch of the network learns where the
vessels are, and its answer is turned into a weight map that multiplies the features of the branch
doing the artery/vein work, so that the classification is pushed to happen on the vessels and
suppressed everywhere else. The authors built it for **multi-centre** images: their argument is
that a network trained on one hospital's camera degrades on another's, and that constraining the
classification to the vessel network is what survives the change of camera.

It is catalogued here for its documentation rather than for its use: **the authors published no
trained weights**, so the model cannot be run on a new photograph without retraining it first
(section 7).

## 1. Code reference

- **Repository:** <https://github.com/yiyg510/VC-Net>
- **Version described here:** `7ad70960` on `master`, the repository's only branch
- **Most recent commit:** 2021-04
- **Training code included:** Yes, in this repository — `main.py` trains and evaluates. There is no
  separate inference script: running the model on a photograph of your own means writing one.
- **Language and how it runs:** Python with PyTorch. The entry point is `python main.py`, and the
  dataset it runs on is chosen by editing `cfg_path` in `main.py` rather than by a command-line
  argument. A GPU is required rather than preferred: the code calls `.cuda()` unconditionally, and
  the GPU index comes from `"gpu"` in the configuration file.

## 2. License

- **Code:** **None stated.** The repository carries no licence file and GitHub reports none, which
  means the default applies: no permission to use, copy or modify has been granted. This is worth
  noticing twice over, because the repository also **redistributes other people's photographs and
  annotations** — DRIVE, HRF and LES-AV images and labels, under `data/` — with no statement of the
  terms they arrived under (section 11).
- **Model weights:** Not applicable — none are published.

## 3. Major publications by the authors

- Hu J, Wang H, Cao Z, Wu G, Jonas JB, Wang YX, Zhang J. *Automatic Artery/Vein Classification Using
  a Vessel-Constraint Network for Multicenter Fundus Images.* Frontiers in Cell and Developmental
  Biology 2021;9:659941. DOI:
  [10.3389/fcell.2021.659941](https://doi.org/10.3389/fcell.2021.659941)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** the network has **two heads and returns both**. The artery/vein head emits a
  four-class map — **background, crossing, vein, artery**, in that channel order — and the vessel
  head emits a single vessel probability. The channel order is read out of
  `utils/data_utils.py:288` (`decomposition_av`), which builds the training labels from the
  colours of the reference drawing: red becomes class 3, blue class 2, green class 1. The
  `"v_a": [2, 3]` entry in each configuration file names the vein and artery channels for scoring
  and agrees with it. **The Tongren configuration is the exception** — three classes, with
  `"v_a": [1, 2]` — so a reader taking channel numbers from one configuration and weights from
  another gets silently wrong answers.
- **Input grid:** **native resolution, padded rather than resized.** Nothing is scaled. At test
  time the photograph is padded with zeros until each side is a multiple of 512 — or of 32, for
  DRIVE, whose images are small enough to pass through whole — and the padding is split evenly
  between the two sides. In training, the photograph is randomly rotated and a random 512×512 crop
  is taken from it.
- **Output grid:** the same raster as the padded input, so the masks are in the photograph's own
  pixels once the padding is removed. For every dataset but DRIVE the padded image is cut into
  512×512 patches at stride 512 and the answers are stitched back together (`recompone_overlap` in
  `utils/data_flow.py:98`); DRIVE is segmented in one pass.
- **Grid set in:** `"patch_size": 512` and `"patch_stride": 512` in
  `experiments/<dataset>/standard.json`, and the padding rule in `utils/mydataset.py` — `p = 32` for
  `DRIVE_AV`, `p = self.input_size` for everything else.
- **Input expected:** an RGB photograph, uncropped, at whatever size the camera produced. Neither
  disc-centred nor macula-centred framing is assumed. A field-of-view mask is loaded alongside each
  photograph but is used only to restrict the scoring, never to modify the image.
- **Preprocessing in the published code:** at test time, **none beyond scaling to 0–1**. The
  loader's only step is `transforms.ToTensor()`; a `dataset_normalized` helper exists and its call
  is commented out (`utils/mydataset.py`). In training, and only there, the photograph is randomly
  flipped, rotated and colour-jittered.

## 5. Architecture

- **Family:** a U-Net-shaped encoder-decoder — an encoder that shrinks the image while learning
  what is in it, and a decoder that grows it back to a per-pixel map — whose encoder is a
  **Res2Net-50** initialised from ImageNet. What makes it VC-Net is the join between its two
  decoder heads: the vessel head's probability is passed through a sigmoid and then through
  `exp(−|p − 0.5|)`, which is largest where the vessel head is *least* certain, and the product of
  the two multiplies the artery/vein features. Vessel edges and vessel ends — the places a vessel
  map is least certain — are therefore the places the artery/vein branch is pushed hardest to look
  at, and flat background is suppressed.
- **Parameters:** Unknown — not stated by the authors, and not counted here because no weights
  exist to count.
- **Single model or ensemble:** a single model. There is, however, **one set of weights per
  dataset** rather than one model for all of them: each configuration file names its own
  `net_params_best.pkl`, and the paper reports each dataset separately.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE-AV](../datasets/rite.md) | Training and test | The published artery/vein standard | Yes: 20 train, 20 test |
| [HRF-AV](../datasets/hrf.md) | Training and test | Hemelings et al.'s artery/vein standard | Yes: 15 train, 30 test |
| [LES-AV](../datasets/les-av.md) | Training and test | The dataset's own artery/vein maps | Yes: 11 train, 11 test |
| Tongren | Training and test | Two ophthalmologists, ITK-SNAP | Yes: half train, half test, per category |
| Kailuan | Training and test | One experienced ophthalmologist, ITK-SNAP | Yes: 15 train, 15 test |

**DRIVE, HRF and LES-AV are unavailable for a fair benchmark of this model** — it trained on part of
each, and on HRF it trained on 15 of the 45 photographs this atlas benchmarks against. Tongren (30
photographs, Beijing Tongren Hospital, Canon CR6-45NM) and Kailuan (30 photographs, from the
community-based Kailuan Cohort Study) are the authors' own and are **not in the repository**: the
README asks anyone wanting them to write to `hujingfei24@163.com`. They are not catalogued here,
because a dataset obtainable only by private correspondence cannot be checked.

## 7. Weights

- **Publicly available:** **No.**
- **Download URL:** none. Every configuration file points at a path *inside a training run* —
  `./results/<DATASET>/vc_net/net_params_best.pkl` — which `utils/utils.py` writes during training
  and which the repository does not contain. `results/` holds nothing but a `.DS_Store`.
- **Format and size:** not applicable.
- **Files in an ensemble:** not applicable.

**What follows from this.** Every number in section 8 is a claim that cannot be reproduced from
what was published without first retraining the model on the authors' splits, and this model cannot
join this repository's own artery/vein benchmark. It is catalogued so that a reader meeting the
paper knows that, rather than discovering it after cloning.

## 8. Performance as reported by the authors

Their measurements, on their own test sets, from the paper in section 3. **Balanced accuracy**
averages how well arteries and veins are each found, so that the more numerous class cannot carry
the score; **F1** is the same quantity as a Dice score — the overlap between what the model marked
and what the expert drew, 0 to 1. The artery/vein rows count only pixels the reference marks as
vessel; the vessel rows are the separate question of finding the vessels at all.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DRIVE-AV | Balanced accuracy, A/V | 0.9554 | Hu et al. 2021 |
| DRIVE-AV | F1, arteries · veins | 0.7616 · 0.7964 | Hu et al. 2021 |
| DRIVE-AV | Vessel F1 · AUC | 0.8296 · 0.9812 | Hu et al. 2021 |
| HRF-AV | Balanced accuracy, A/V | 0.9646 | Hu et al. 2021 |
| HRF-AV | F1, arteries · veins | 0.7389 · 0.7839 | Hu et al. 2021 |
| HRF-AV | Vessel F1 · AUC | 0.8101 · 0.9806 | Hu et al. 2021 |
| LES-AV | Balanced accuracy, A/V | 0.9446 | Hu et al. 2021 |
| LES-AV | F1, arteries · veins | 0.7635 · 0.7988 | Hu et al. 2021 |
| LES-AV | Vessel F1 · AUC | 0.8417 · 0.9821 | Hu et al. 2021 |
| Tongren | Balanced accuracy, A/V | 0.9468 | Hu et al. 2021 |
| Tongren | F1, arteries · veins | 0.7347 · 0.7744 | Hu et al. 2021 |
| Kailuan | Balanced accuracy, A/V | 0.9442 | Hu et al. 2021 |
| Kailuan | F1, arteries · veins | 0.7221 · 0.7741 | Hu et al. 2021 |

These are the authors' measurements on their own test sets, each from a model trained on that same
dataset's training split. They are **not comparable with this atlas's own artery/vein figures**,
which are computed on whole datasets with one set of weights per model, against a different
definition of the vessel map, and with no per-dataset retraining.

## 9. Used by

No catalogued project runs VC-Net. Without published weights, none could without retraining it
first.

## 10. Known defects

- **No weights, and therefore no reproducibility.** *Our finding, 2026-09-19:* the repository
  contains no checkpoint and no link to one; the five configuration files point at paths a training
  run would create. The published results cannot be reproduced from what was released. Open.
- **No licence at all, over redistributed data.** *Our finding, 2026-09-19:* the repository has no
  licence file, and ships 107 photographs with their annotations — DRIVE-AV, HRF-AV and LES-AV —
  under `data/`. LES-AV's own README forbids commercial use; the HRF-AV labels carry no licence
  from their authors either. Anyone reusing this repository's copies inherits that uncertainty
  rather than escaping it. Open.
- **The uncertain class is silently folded into background.** *Our finding, 2026-09-19, from
  `utils/data_utils.py:288`:* `decomposition_av` assigns classes from the red, blue and green
  channels and then zeroes every pixel where red equals green, which sends white pixels — the
  *uncertain* class in the LES-AV and RITE encodings — to background rather than excluding them
  from the loss. In the LES-AV label examined here that is 1,506 pixels. The effect is to train the
  network to call those pixels background. Open.
- **The two class layouts are easy to mix up.** *Our finding, 2026-09-19:* four of the five
  configurations use four classes with vein at 2 and artery at 3; the Tongren configuration uses
  three classes with vein at 1 and artery at 2, and a different label decoder (`decomposition_av3`)
  selected by a dataset-name string. Nothing checks that the configuration, the decoder and the
  weights agree. Open.

## 11. Notes

- **The repository is a data release as much as a code release.** Of its 507 entries, 463 sit under
  `data/` and eleven are Python files: it holds DRIVE-AV, HRF-AV and LES-AV as images, artery/vein
  labels, field-of-view masks and vessel maps, renamed to `0.png`, `1.png` and so on and split into
  `training/` and `test/`. Those copies are recorded as a secondary source on the three dataset
  pages — [HRF](../datasets/hrf.md), [RITE](../datasets/rite.md), [LES-AV](../datasets/les-av.md) —
  with the check that identified them.
- **Its vessel maps are derived, not independent.** *Our finding, 2026-09-19:* in the HRF copies
  examined, the `vessel/` layer is exactly the union of the artery and vein classes of the `label/`
  layer, rather than HRF's own hand-drawn vessel gold standard, which differs from that union by
  about 0.004% of pixels. A vessel score and an artery/vein score measured on this copy are
  therefore one measurement seen twice.
- **Multi-centre is the claim to test, not a result to assume.** The paper's argument is about
  generalising across cameras, and every number in section 8 comes from a model trained on the same
  dataset it was tested on. What would test the claim is a model trained on one centre and measured
  on another, which the paper reports for its own two clinical sets and which nobody outside the
  authors' group can repeat without the weights or the data.

---

**Links and license last checked:** 2026-09-19
