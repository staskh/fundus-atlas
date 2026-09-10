# AutoMorph disc-and-cup model

This is the model that produces the optic disc and cup masks in AutoMorph and the two pipelines
derived from it, and therefore the cup-to-disc ratio they report — a measurement used in glaucoma
assessment. It is the [little W-Net](lwnet.md) architecture retrained by AutoMorph's authors on
optic disc data, which is a different task from anything in the W-Net paper.

It is catalogued separately from LWNet for exactly that reason. Citing the W-Net paper as evidence
for these masks would be a mistake: the paper measures vessel segmentation, and these weights were
never evaluated in it.

## 1. Code reference

- **Repository:** the inference code and weights are distributed inside
  https://github.com/rmaphoh/AutoMorph, module `M2_lwnet_disc_cup`. The architecture comes from
  [lwnet](https://github.com/agaldran/lwnet).
- **Version described here:** AutoMorph commit `9a953e5e` (2025-06-21).
- **Most recent commit:** 2025-06 (of the host repository)
- **Training code included:** No, not in the host repository — it ships `test_outside.sh` and
  `generate_av_results.py` for inference. Training code for the architecture is in the
  [lwnet](https://github.com/agaldran/lwnet) repository (`train_cyclical.py`), but the configuration
  used for this disc-and-cup retraining was not found.
- **Language and how it runs:** Python with PyTorch, as the disc-and-cup stage of AutoMorph's
  `run.sh`.

## 2. License

- **Code:** the architecture is MIT (from lwnet); the host repository is Apache-2.0.
- **Model weights:** No separate license stated; committed in the AutoMorph repository.

## 3. Major publications by the authors

- The weights are described as part of: Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M, Struyven R,
  Alexander DC, Keane PA, et al. *AutoMorph: Automated Retinal Vascular Morphology Quantification
  Via a Deep Learning Pipeline.* Translational Vision Science & Technology 2022;11(7):12.
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)
- The architecture: Galdran A, Anjos A, Dolz J, Chakor H, Lombaert H, Ben Ayed I. *The Little W-Net
  That Could.* 2020. [arXiv:2009.01907](https://arxiv.org/abs/2009.01907)

## 4. What it produces

- **Purpose:** `disc/cup`
- **Output classes:** optic disc and optic cup. The pipeline derives disc and cup height, width and
  the cup-to-disc ratio from these masks.
- **Input expected:** a preprocessed colour-fundus photograph from AutoMorph's cropping stage; the
  experiment name records a working resolution of 1024 pixels.
- **Preprocessing in the published code:** cropping and resizing by the host pipeline.

## 5. Architecture

- **Family:** W-Net — two chained U-Nets — from lwnet, here with disc and cup output classes.
- **Parameters:** approximately 70,000 for the architecture, as stated by its authors.
- **Single model or ensemble:** ensemble of eight, one per random seed, in folders named `28` to
  `42`.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| REFUGE, 800 images | Training | The challenge organisers | Reported in the AutoMorph paper; the split is not restated in the repository |
| GAMMA, 100 images | Training | The challenge organisers | As above |

REFUGE and GAMMA cannot be used to benchmark these weights. Note how small this training set is —
900 images in total, against the thousands behind the vessel models — which is worth keeping in mind
when a cup-to-disc ratio disagrees with a clinician's reading.

## 7. Weights

- **Publicly available:** Yes, committed in the host repository.
- **Download URL:**
  https://github.com/rmaphoh/AutoMorph/tree/main/M2_lwnet_disc_cup/experiments/wnet_All_three_1024_disc_cup
  — eight seed folders, each with `model_checkpoint.pth` (about 1 MB) and a `config.cfg`.
- **Format and size:** PyTorch, about 1 MB per seed — small, because the architecture is small.
- **Files in an ensemble:** eight.

## 8. Performance as reported by the authors

The AutoMorph paper reports optic disc segmentation performance for this module. Numbers are in that
paper and are not restated here. The W-Net paper's results do **not** apply to this model.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | The `M2_lwnet_disc_cup` module | These weights, eight-seed ensemble |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Optic disc and cup stage, unchanged | The same weights, republished as a release asset |
| [AutoMorphClass](../projects/automorphclass.md) | `Optic_disc_and_cup.py` at 512 px | The same weights, vendored; `lightweight=True` uses one seed |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Note that
AutoMorphalyzer infers which eye a photograph shows from vessel density either side of the optic
cup, so a displaced cup mask can mislabel laterality as well as the ratio.

## 11. Notes

- **Disc and cup, not disc alone.** This is the only model in the catalogue that segments the cup,
  which is why the AutoMorph family can report a cup-to-disc ratio and VascX cannot.
- Running one seed instead of eight, as AutoMorphClass offers, is an undocumented model.

---

**Links and license last checked:** 2026-09-10
