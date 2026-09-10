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
- **Output classes:** multi-class vessel segmentation — artery, vein, and (in the fused output)
  vessel. The published inference writes artery, vein and combined-vessel maps separately.
- **Input expected:** a colour-fundus photograph; the repository's own pipeline resizes per dataset,
  and the authors note image size settings must be reduced for weaker GPUs.
- **Preprocessing in the published code:** dataset-specific resizing and normalisation, with a
  `--uniform` option used throughout their commands.

## 5. Architecture

- **Family:** GAN-based segmentation. A main generator is fused with a branch generator
  (`Generator_main`, `Generator_branch` in the code) and trained against a U-Net discriminator. The
  README states the GAN backbone is a revision of the SEGAN vessel-segmentation method — see
  [segan-vessel.md](segan-vessel.md).
- **Parameters:** Unknown.
- **Single model or ensemble:** the published training runs one model per random seed; downstream
  users ensemble several seeds themselves (AutoMorph ships eight).

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| DRIVE-AV | Training and test | The dataset's own authors | Yes: train, validation and test CSVs generated per dataset |
| LES-AV | Training and test | The dataset's own authors | Yes |
| HRF-AV | Training and test | The dataset's own authors | Yes |

A fair benchmark of these weights therefore cannot use DRIVE, LES-AV or HRF. Note that AutoMorph
retrained the same architecture on a combined set it calls `ALL-AV` (DRIVE-AV, HRF-AV and LES-AV),
so the same caution applies to the weights AutoMorph ships.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://drive.google.com/drive/folders/1c_UZaq69RmPZjFvccot6GWqnhx2VzFRs — the
  pretrained models linked from the repository README, to be unzipped at the project folder.
- **Format and size:** PyTorch checkpoints. The copies redistributed inside AutoMorph are about
  35 MB each: `CP_best_F1_A.pth` (artery), `CP_best_F1_V.pth` (vein) and `CP_best_F1_all.pth`
  (combined) per seed.
- **Files in an ensemble:** one set per random seed; AutoMorph ships eight seed folders under
  `M2_Artery_vein/ALL-AV/`.

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
| [AutoMorph](../projects/automorph.md) | The `M2_Artery_vein` module | Retrained by AutoMorph on `ALL-AV`, shipped as an eight-seed ensemble |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Artery/vein stage, unchanged from AutoMorph | AutoMorph's weights, republished as a release asset |
| [AutoMorphClass](../projects/automorphclass.md) | `AV_classification.py` | AutoMorph's weights, vendored into the package |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. The tortuosity
defect that affects the pipelines above lives in the biomarker code, not in this model; see
[retipy.md](../projects/retipy.md) section 8.

## 11. Notes

- The same repository trains only artery/vein models. The binary vessel model that AutoMorph pairs
  with this one is a different network — see [segan-vessel.md](segan-vessel.md).
- Reference 6 of the README credits the GAN backbone to the SEGAN paper, which is how the two models
  come to share an ancestry while remaining distinct.

---

**Links and license last checked:** 2026-09-10
