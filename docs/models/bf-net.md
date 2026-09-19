# BF-Net

BF-Net separates arteries from veins in a colour-fundus photograph. Its contribution is
specifically about the places where that separation usually breaks: where an artery and a vein
cross, pixel labels are ambiguous, and networks trained directly on them mislabel whole stretches of
vessel. BF-Net avoids learning on those ambiguous pixels by first segmenting vessels as one class
and then fusing that binary result into the multi-class decision — hence "binary-to-multi fusion".

## 1. Code reference

- **Repository:** https://github.com/rmaphoh/Learning-AVSegmentation
- **Version described here:** commit `f7de674e` (2023-02-23). No tags or releases.
- **Most recent commit:** 2023-02
- **Training code included:** Yes, in this repository — `train.py`, with the dataset selectable as
  `DRIVE_AV`, `LES-AV` or `HRF-AV`, and `test.py` for inference.
- **Language and how it runs:** Python with PyTorch 1.6. The authors state a GPU is essential and
  report using one Tesla T4 with 15 GB.

## 2. License

- **Code:** GPL-3.0. This matters downstream: three pipelines that run this model are themselves
  Apache-2.0 or MIT, and a combined redistribution would have to answer to the GPL.
- **Model weights:** No separate license stated.

## 3. Major publications by the authors

- Zhou Y, Xu M, Hu Y, Lin H, Jacob J, Keane PA, Alexander DC. *Learning to Address Intra-segment
  Misclassification in Retinal Imaging.* MICCAI 2021, pp. 482–492. DOI:
  [10.1007/978-3-030-87193-2_46](https://doi.org/10.1007/978-3-030-87193-2_46)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four, exclusive — background, artery, vein, and a fourth class the authors'
  own evaluation code calls *uncertainty*. **On the annotations it was trained on, that fourth class
  is the crossings**: where an artery passes over a vein, an annotator marks the pixels as belonging
  to both vessels, and a network emitting exclusive classes has to put them somewhere. This atlas
  measured that rather than assuming it — see section 11 — and reads an artery as the artery class
  plus the fourth class, which is what [AutoMorph](../projects/automorph.md)'s postprocessing does
  with the same network's output. The published inference writes artery, vein and combined-vessel
  maps separately.
- **Input grid:** 720×720 when run with `--uniform=True`, which is how both this repository's own
  scripts and AutoMorph invoke it. Without that flag the grid is per-dataset and non-square:
  [HRF-AV](../datasets/hrf.md) 880×592, [DRIVE-AV](../datasets/rite.md) 592×592, [LES-AV](../datasets/les-av.md) 800×720. Note this is a **different grid from the vessel
  model that runs beside it in AutoMorph** ([SEGAN](segan-vessel.md), 912×912).
- **Output grid:** artery, vein and combined masks at the input grid, resampled back to the original
  photograph's dimensions with nearest-neighbour interpolation before saving.
- **Grid set in:** `Define_image_size` in `scripts/utils.py` here, and the identical function in
  AutoMorph's `M2_Artery_vein/scripts/utils.py`.
- **Input expected:** a colour-fundus photograph; the repository's own pipeline resizes per dataset,
  and the authors note image size settings must be reduced for weaker GPUs.
- **Preprocessing in the published code:** resize to the grid above, then **scale** each channel by
  the statistics of the photograph's own lit pixels — those with any red in them. The expression is
  `(image - mean) / 1.0 * std`, whose operator precedence multiplies by the standard deviation
  rather than dividing by it, so a low-contrast photograph is scaled towards zero rather than
  stretched. **Both** of the repository's dataset classes carry the same expression, so the weights
  were trained through it; it is recorded in section 10 because it means the input is not
  standardised in the usual sense.

## 5. Architecture

- **Family:** GAN-based segmentation. **Two** branch generators — one for arteries, one for veins —
  each emit a segmentation and a fusion map, and it is the *fusion* maps that condition a main
  generator alongside the photograph (`Generator_branch` and `Generator_main` in
  `scripts/model.py`). A U-Net discriminator takes part in training only. The README states the GAN
  backbone is a revision of the SEGAN vessel-segmentation method — see
  [segan-vessel.md](segan-vessel.md).
- **Parameters:** Unknown.
- **Single model or ensemble:** **one seed.** Each of the three published archives holds a single
  training run — seed 42 — as three checkpoints: the artery branch, the vein branch and the main
  generator. Downstream users ensemble several seeds themselves, which is what
  [AutoMorph's artery/vein model](automorph-artery-vein.md) is: the same architecture retrained on
  three datasets at once and shipped as eight seeds. That is a different model and has its own
  page.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE-AV](../datasets/rite.md) | Training and test — of the `DRIVE_AV` archive | The dataset's own authors | Yes: train, validation and test CSVs generated per dataset |
| [LES-AV](../datasets/les-av.md) | Training and test — of the `LES-AV` archive | The dataset's own authors | Yes |
| [HRF-AV](../datasets/hrf.md) | Training and test — of the `HRF-AV` archive | The dataset's own authors | Yes |

**Each archive trained on one of the three, not all three**, so which dataset is off limits depends
on which archive is loaded: the `DRIVE_AV` weights cannot be scored on
[DRIVE](../datasets/drive.md)/[RITE](../datasets/rite.md) but are out-of-sample on
[HRF](../datasets/hrf.md) and [LES-AV](../datasets/les-av.md), and so on round. That is the whole
reason this atlas runs the DRIVE-trained archive.

[AutoMorph](../projects/automorph.md) retrained the same architecture on all three at once — a
combined set it calls `ALL-AV` — and those weights are in-sample on every one of them. They are
catalogued as [AutoMorph artery/vein](automorph-artery-vein.md).

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://drive.google.com/drive/folders/1c_UZaq69RmPZjFvccot6GWqnhx2VzFRs — the
  pretrained models linked from the repository README, to be unzipped at the project folder.
- **Format and size:** three zip archives, **one per training dataset rather than one per seed**,
  each holding one seed's three PyTorch checkpoints: `CP_best_F1_A.pth` (the artery branch, 35 MB),
  `CP_best_F1_V.pth` (the vein branch, 35 MB) and `CP_best_F1_all.pth` (the main generator, 37 MB).
- **Files in an ensemble:** three files, one seed, no ensemble.

**A Google Drive folder carries no version and no checksum.** The authors can replace a file in
place and nothing downstream would say so, which means two people running "BF-Net" cannot establish
that they ran the same weights. So this atlas takes its own digest of each archive and pins it: a
download that does not match is refused rather than run, and the digest and its date go into every
result the model produces.

| Archive | Trained on | Bytes | sha256 |
| --- | --- | --- | --- |
| `DRIVE_AV.zip` | [DRIVE-AV](../datasets/rite.md) | 98,226,321 | `19ea93738eeadb9f41e502b2a7f7f5470a62b0bc05f1bc8c2abab5a925d37e7b` |
| `HRF-AV.zip` | [HRF-AV](../datasets/hrf.md) | 98,063,648 | `adc67b59b08250343b26137347f877b1f11f3f9b6058d3565529fe05955045ac` |
| `LES-AV.zip` | [LES-AV](../datasets/les-av.md) | 97,984,143 | `a5ef9eafce7a99b9095fda701aae5011be901150567a195b6b5779f94756b8aa` |

**These are this repository's measurements, taken 2026-09-18**, not the authors' — they publish
none. The [artery/vein benchmark](../benchmarks/av-docs.md) runs the **DRIVE-trained** archive,
because it is the only one of the three that trained on none of the datasets that benchmark has a
store for.

## 8. Performance as reported by the authors

From the repository README, after switching the final activation from sigmoid to softmax. A
sensitivity of 70.8 means the model found 70.8% of the vessel pixels a human marked; an F1 score
balances that against false positives.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DRIVE-AV | Sensitivity / AUC-ROC / F1 | 70.8 ± 0.1 / 84.7 ± 0.05 / 71.99 ± 0.04 | Repository README |
| LES-AV | Sensitivity / AUC-ROC / F1 | 64.41 ± 0.09 / 81.72 ± 0.04 / 67.22 ± 0.06 | Repository README |
| HRF-AV | Sensitivity / AUC-ROC / F1 | 71.85 ± 0.29 / 85.38 ± 0.13 / 71.92 ± 0.03 | Repository README |

These are the authors' measurements on their own test splits, and the datasets are the ones the
model was trained on. This atlas's own comparisons are separate.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | The `M2_Artery_vein` module | **Not these weights** — retrained on `ALL-AV` and shipped as eight seeds, catalogued as [AutoMorph artery/vein](automorph-artery-vein.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Artery/vein stage, unchanged from AutoMorph | AutoMorph's weights, republished as a release asset |
| [AutoMorphClass](../projects/automorphclass.md) | `AV_classification.py` | AutoMorph's weights, vendored into the package |

None of the three runs the weights on this page. They run the same architecture with other weights,
which is why those have a page of their own.

## 10. Known defects

- **The weights cannot be pinned by anything the authors publish.** They are files in a Google Drive
  folder: no version, no release, no checksum, and no notice if one is replaced (section 7). This
  repository's own digests are a workaround, not a fix.
- **The input is scaled, not standardised.** `(image - mean) / 1.0 * std` multiplies by the standard
  deviation (section 4). It is consistent between training and inference, so it is not a bug that
  breaks these weights — but the network's sensitivity to contrast is the opposite of what the code
  reads as, and anyone retraining from it inherits that silently.

The tortuosity defect that affects the pipelines above lives in the biomarker code, not in this
model; see [retipy.md](../projects/retipy.md) section 8.

## 11. Notes

- **The fourth class is the crossings, and this atlas measured that.** The repository ships its own
  indexed label maps, and scored against this repository's [HRF](../datasets/hrf.md) store, their
  class 3 matches our crossing layer pixel for pixel — 56,690 pixels on `09_dr`, with none left
  over, and class 1 and class 2 matching the arteries and veins outside the crossings exactly. The
  authors' evaluation code calls the class *uncertainty* and scores it in its own right;
  AutoMorph's biomarker stage folds it into both vessels. This atlas follows the latter, because it
  is what the annotator drew.
- **[RITE](../datasets/rite.md) also publishes vessels of uncertain type**, distinct from its
  crossings, and a four-class network trained on it has nowhere else to put them. So on the
  DRIVE-trained archive the fourth class may carry both, while on HRF — where there are no uncertain
  pixels — it is crossings exactly.
- The same repository trains only artery/vein models. The binary vessel model that AutoMorph pairs
  with this one is a different network — see [segan-vessel.md](segan-vessel.md).
- Reference 6 of the README credits the GAN backbone to the SEGAN paper, which is how the two models
  come to share an ancestry while remaining distinct.

---

**Links and license last checked:** 2026-09-18
