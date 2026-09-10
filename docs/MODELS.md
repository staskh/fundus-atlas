# Segmentation and classification models

Single trained networks that turn a colour-fundus photograph into masks, landmark locations or a
grade. Each row links to a detail page describing that model: what it produces, what it was trained
on, where its weights are, what its authors report about it, and which catalogued pipelines run it.

Models that go on to compute vessel width, tortuosity or other measurements are pipelines, and are
catalogued in [PROJECTS.md](PROJECTS.md) instead.

This is a lookup table, not a ranking. A model that scores well on the images it was trained on may
do poorly on yours, which is why the training data is a column here.

## 1. Summary

Grouped by purpose. Within each group the most recently committed model comes first.

### 1.1 Quality — is this photograph good enough to measure?

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [VascX quality](models/vascx-quality.md) | Image-quality assessment | U-Net ensemble | 15+ published datasets plus Rotterdam Study images | Yes | No | Code not stated; weights AGPL-3.0 | [VascX](projects/vascx.md) | 2026-08 | 2026-09-10 |
| [AutoMorph quality grader](models/automorph-quality-grader.md) | Good / Usable / Reject | EfficientNet, ensemble of 8 | EyeQ training split, 12,543 EyePACS images | Yes | No | Apache-2.0 (host repository) | [AutoMorph](projects/automorph.md) | 2025-06 | 2026-09-10 |
| [QuickQual](models/quickqual.md) | Good / Usable / Bad probabilities | Frozen DenseNet121 features plus an SVM | EyeQ (SVM fitted); ImageNet (frozen features) | Yes | Not applicable — nothing is trained | None stated | [AutoMorphalyzer](projects/automorphalyzer.md) | 2023-11 | 2026-09-10 |

### 1.2 Vessels — blood vessels as a single class

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [VascX vessels](models/vascx-vessels.md) | Blood vessels, one class | U-Net ensemble | 15+ published datasets plus Rotterdam Study images | Yes | No | Code not stated; weights AGPL-3.0 | [VascX](projects/vascx.md) | 2026-08 | 2026-09-10 |
| [SEGAN vessel segmenter](models/segan-vessel.md) | Blood vessels, one class | GAN-based U-Net, ensemble of 10 | DRIVE, STARE, CHASE-DB1, HRF, IOSTAR, LES-AV (`ALL-SIX`) | Yes | No | Apache-2.0 (host repository) | [AutoMorph](projects/automorph.md), [AutoMorphalyzer](projects/automorphalyzer.md), [AutoMorphClass](projects/automorphclass.md) | 2025-06 | 2026-09-10 |
| [LWNet](models/lwnet.md) | Blood vessels, one class | W-Net, two chained U-Nets, ~70k parameters | DRIVE, CHASE-DB, HRF | Yes | Yes, in the repository | MIT | — | 2024-01 | 2026-09-10 |

### 1.3 Artery/vein — arteries separated from veins

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [OCULARNet](models/ocularnet.md) | Artery, vein, **crossings**, background | U-Net with RepVGG-b3 encoder | 14 public A/V datasets | Yes | Yes, in the repository | None stated | [OCULARNet](projects/ocularnet.md) | 2026-08 | 2026-09-10 |
| [OCULARNet-nano](models/ocularnet-nano.md) | Artery, vein, **crossings**, background | U-Net with RepVGG-a0 encoder, ensemble of 5 | The same 14 datasets, five folds | Yes | Yes, in the repository | None stated | [OCULARNet](projects/ocularnet.md) | 2026-08 | 2026-09-10 |
| [VascX artery/vein](models/vascx-artery-vein.md) | Artery against vein | U-Net ensemble | 15+ published datasets plus Rotterdam Study images | Yes | No | Code not stated; weights AGPL-3.0 | [VascX](projects/vascx.md) | 2026-08 | 2026-09-10 |
| [LUNet](models/lunet.md) | Arterioles and venules | U-Net variant, TensorFlow | UZLF (Leuven-Haifa) 1444×1444 | Yes | Yes, in the repository | **CC BY-NC 4.0 — non-commercial** | — | 2024-12 | 2026-09-10 |
| [Big W-Net](models/big-wnet.md) | Artery against vein | W-Net, larger configuration | DRIVE-AV, HRF-AV | Yes | Yes, in the repository | MIT | — | 2024-01 | 2026-09-10 |
| [BF-Net](models/bf-net.md) | Artery against vein, by binary-to-multi fusion | GAN-based, main plus branch generator | DRIVE-AV, LES-AV, HRF-AV | Yes | Yes, in the repository | GPL-3.0 | [AutoMorph](projects/automorph.md), [AutoMorphalyzer](projects/automorphalyzer.md), [AutoMorphClass](projects/automorphclass.md) | 2023-02 | 2026-09-10 |

### 1.4 Disc/cup — the optic disc, the optic cup, or both

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [VascX disc](models/vascx-disc.md) | Optic disc (no cup) | U-Net ensemble | 15+ published datasets plus Rotterdam Study images | Yes | No | Code not stated; weights AGPL-3.0 | [VascX](projects/vascx.md) | 2026-08 | 2026-09-10 |
| [AutoMorph disc-and-cup](models/automorph-disc-cup.md) | Optic disc **and cup** | W-Net retrained for this task, ensemble of 8 | REFUGE (800), GAMMA (100) | Yes | No — architecture's training code is in lwnet | Apache-2.0 (host); MIT architecture | [AutoMorph](projects/automorph.md), [AutoMorphalyzer](projects/automorphalyzer.md), [AutoMorphClass](projects/automorphclass.md) | 2025-06 | 2026-09-10 |
| [LUNet v2 disc (`lunetv2_odc`)](models/lunetv2-odc.md) | Optic disc | Unknown | **Unknown** | Yes, from an unversioned Google Drive file | No | None stated; ancestor is CC BY-NC 4.0 | [PVBM](projects/pvbm.md), [OCULARNet](projects/ocularnet.md) | Not applicable | 2026-09-10 |

### 1.5 Other — landmarks and everything else

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [VascX fovea](models/vascx-fovea.md) | Fovea location, as a point | U-Net ensemble | 15+ published datasets plus Rotterdam Study images | Yes | No | Code not stated; weights AGPL-3.0 | [VascX](projects/vascx.md) | 2026-08 | 2026-09-10 |

## 2. How to read this table

- **Purpose groups** — every model belongs to exactly one of five: quality, vessels, artery/vein,
  disc/cup, other. A repository that publishes several models appears once per model, in the group
  each belongs to, because a reader comparing artery/vein models needs one row per model rather than
  one row per release.
- **Trained on** — the datasets used to fit the model. A model cannot be fairly evaluated on a
  dataset it was trained on, so this column decides which benchmarks mean anything for a given
  model. `Unclear` means the papers or code did not state a split.
- **Architecture** — `ensemble of N` matters: running one member of an ensemble is not the same model
  as the published one, and some pipelines do exactly that to save time.
- **Weights** — whether trained weights can be obtained from the authors. `Unknown` means we could
  not establish it, not that they are unavailable.
- **Training code** — whether the model can be retrained on your own images, and where that code
  lives. Weights and training code are often published in different repositories.
- **Used by** — which pipelines in [PROJECTS.md](PROJECTS.md) run this model. A model used by
  several pipelines is a shared dependency: those pipelines agreeing with each other is weaker
  evidence than it appears.
- **Last commit** — the year and month of the model repository's most recent commit, as a rough
  signal of maintenance. An old date is not a fault; a published model may need no changes.
- **Known defects** are not in this table. Every detail page carries a section 10 recording bugs
  that change the masks or the numbers derived from them. `None recorded` there means no finding,
  not a clean bill of health.

## 3. Considered and not included

- **Classical, untrained methods** — retipy's OpenCV vessel segmentation and ARIA's wavelet-based
  vessel detection are algorithms, not trained models, so there is nothing to record about training
  data or weights. They are described on their project pages,
  [retipy](projects/retipy.md) and [ARIA](projects/aria.md).
- **MCF-Net** (the model published with the EyeQ dataset) — its authors state the original weights
  are no longer usable after library version changes and recommend retraining, and no catalogued
  pipeline uses it. It is named on the
  [AutoMorph quality grader](models/automorph-quality-grader.md) page, which learns from EyeQ's
  labels rather than from this model.
- **BEAL and ISFA** — optic disc and cup segmentation by domain adaptation. No catalogued pipeline
  uses either, so they are recorded in [PROJECTS.md](PROJECTS.md) section 3 for now; both are
  reasonable future entries here.

## 4. Adding a model

Model pages follow a fixed structure so they can be read against each other. Load the
`document-model` skill, which defines that structure and this table's columns, before adding or
changing an entry.
