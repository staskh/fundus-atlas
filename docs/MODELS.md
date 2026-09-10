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
| [SegFormer disc/cup (pamixsun)](models/segformer-disc-cup.md) | Optic disc and cup | SegFormer transformer, single model | REFUGE | Yes, on Hugging Face | No | Apache-2.0 | — | 2023-09 | 2026-09-10 |
| [ISFA](models/isfa.md) | Optic disc and cup | DeepLabv3+ with edge attention, image synthesis and feature alignment | REFUGE (source); Drishti-GS, RIM-ONE-r3 (unlabelled targets) | **No** | Partly — the image-synthesis stage was never released | None stated | — | 2021-08 | 2026-09-10 |
| [BEAL](models/beal.md) | Optic disc and cup | DeepLabv3+ with MobileNetV2 backbone, boundary and entropy discriminators | REFUGE (source); Drishti-GS, RIM-ONE-r3 (unlabelled targets) | Yes | Yes, in the repository | MIT | — | 2021-05 | 2026-09-10 |
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

**What decides inclusion here:** a public fundus model whose provenance a reader can establish —
published weights or training code, plus enough documentation to say what the model is: its
architecture, its training data, its licence, and how to run it. Any one of a publication, a stated
evaluation, use by a catalogued pipeline, or evident adoption with a working interface is enough to
justify a page. Being used by a pipeline is not required; several entries above have none, because
the comparison tables need baselines and readers arrive looking for models by name.

Two entries show the edges. [ISFA](models/isfa.md) publishes no weights, but its method is published
and cited, and its page records what is missing. [SegFormer disc/cup](models/segformer-disc-cup.md)
publishes no metrics and no paper, but states its architecture, training set and licence and runs
from four lines of code — an unmeasured model with clear provenance is precisely what an independent
comparison is for. What stays out is the undocumented upload: weights with no stated training data,
no licence, or a model card left as "[More Information Needed]". A model nobody can establish
anything about teaches a reader nothing, however genuine it may be.

Everything below was looked at and left out, with the reason, so nobody repeats the search.

### 3.1 Not trained models

- **Classical, untrained methods** — retipy's OpenCV vessel segmentation and ARIA's wavelet-based
  vessel detection are algorithms, not trained models, so there is nothing to record about training
  data or weights. They are described on their project pages,
  [retipy](projects/retipy.md) and [ARIA](projects/aria.md).
- **[MCF-Net](https://github.com/HzFu/EyeQ)** (the model published with the EyeQ dataset) — its
  authors state the original weights are no longer usable after library version changes and
  recommend retraining, and no catalogued pipeline uses it. It is named on the
  [AutoMorph quality grader](models/automorph-quality-grader.md) page, which learns from EyeQ's
  labels rather than from this model.

### 3.2 Kaggle's model hub

Searched for fundus, retinal, vessel, optic disc, artery/vein and segmentation terms. It holds two
retinal vessel U-Nets, neither with a publication or a stated evaluation, so neither is assessable:

- [adityabhongade/unet-for-retinal-blood-vessel-segmentation](https://www.kaggle.com/models/adityabhongade/unet-for-retinal-blood-vessel-segmentation)
  — trained on DRIVE, expecting a preprocessed green channel, with a model card left half-templated.
- [prashantdixit07/retina_blood-vessel-segmentation](https://www.kaggle.com/models/prashantdixit07/retina_blood-vessel-segmentation)
  — no description at all.

The rest of the fundus material there is disease classification or general-purpose models, which is
a different task from vascular segmentation and out of this catalogue's scope:
[R-FAMNet](https://www.kaggle.com/models/kunalsinghh25/r-famnet-retinal-disease-classification),
[MaxGRNet](https://www.kaggle.com/models/fuyadhasanbhoyan/maxgrnet),
[a RETFound copy](https://www.kaggle.com/models/tantai31124/retfound-mae-fundus) and
[Qwen-VL fine-tunes](https://www.kaggle.com/models/durgeshrao9993/qwen-2-5-vl-7b-finetuned).

### 3.3 Hugging Face

Searched for fundus, retina, vessel, optic disc, artery/vein, cup and glaucoma segmentation terms.
One model was catalogued from it: [SegFormer disc/cup](models/segformer-disc-cup.md). The rest
divides into three groups.

**Out of scope by task.** Diabetic-retinopathy grading classifiers — the
[ClementP/FundusDRGrading-*](https://huggingface.co/models?search=ClementP/FundusDRGrading) family,
about twenty severity classifiers, one per backbone, MIT-licensed, each carrying per-dataset
quadratic-kappa scores on APTOS, EYEPACS, IDRID and DDR in its model card (for example
[efficientnet_b0](https://huggingface.co/ClementP/FundusDRGrading-efficientnet_b0)). Whole-image
disease grading is a different task from vascular measurement, so those models do not belong here,
but **the project's stated purpose is the same as this atlas's** — "the reported performance metrics
are not always consistent in the literature. Our goal is to provide a fair comparison between
different models using the same datasets and evaluation protocol" — which makes it a precedent worth
reading before designing our own comparison tables, and a model of how to put metrics in a card.
Also out of scope by task: foundation and vision-language models, including
[RETFound](https://huggingface.co/YukunZhou/RETFound_mae_natureCFP) (by AutoMorph's first author) and
its [copies](https://huggingface.co/bitfount/RETFound_MAE),
[Fundus-R1](https://huggingface.co/Kimokcheon/Fundus-R1-7B) and
[RetinaVLM](https://huggingface.co/manifestasi/RetinaVLM-300M); and
[face-detection models](https://huggingface.co/py-feat/retinaface) that merely share the "retina"
name.

**Out of scope by biomarker family**, but a candidate if the atlas ever extends to lesions:
[ClementP/fundus-lesions-segmentation-unet_seresnext50_32x4d](https://huggingface.co/ClementP/fundus-lesions-segmentation-unet_seresnext50_32x4d)
— MIT, with per-dataset metrics for microaneurysms, exudates, haemorrhages and cotton-wool spots on
IDRID, FGADR, DDR, MESSIDOR and RETLES.

**Excluded as undocumented:**

- [ClementP/fundus-odmac-segmentation-unet-maxvit_small_tf_512](https://huggingface.co/ClementP/fundus-odmac-segmentation-unet-maxvit_small_tf_512)
  — optic disc and macula, no licence and an auto-generated card.
- [MHasanUnical/multiscale-input-vessel-segmentation-model](https://huggingface.co/MHasanUnical/multiscale-input-vessel-segmentation-model)
  — MIT, but an empty card.
- [izzudd/retina-segmentation-chase](https://huggingface.co/izzudd/retina-segmentation-chase) — a
  UNet++ whose card leaves dataset and metrics as "[More Information Needed]".

No usable artery/vein model was found on Hugging Face beyond the already-catalogued
[VascX](models/vascx-artery-vein.md) weights, whose repository name the search terms do not match.
Two near-misses by the same author are worth naming so nobody chases them:
[ClementP/AVSeg](https://huggingface.co/ClementP/AVSeg) announces artery/vein segmentation but
contains no weights at all, only a licence file, and
[ClementP/FundusSegmenter](https://huggingface.co/ClementP/FundusSegmenter) holds an
`ensemble_segmenter.onnx` with no model card, no licence and no statement of what it segments. That
[author's account](https://huggingface.co/ClementP) is worth watching regardless: it also holds
choroid segmentation and OCT models, several of which would be in scope if this atlas widens.

### 3.4 SegFormer elsewhere

The architecture itself ([Xie et al., 2021](https://arxiv.org/abs/2105.15203)) is general-purpose,
not a fundus model. Kaggle's SegFormer entries are the
[official Keras port](https://www.kaggle.com/models/keras/segformer) and uploads for unrelated tasks.
It reaches this atlas in three ways: the Hugging Face disc-and-cup model catalogued above; as a
training option in OCULAR's model factory, recorded on [OCULARNet](models/ocularnet.md); and in
small GitHub repositories fine-tuning it for retinal vessels:

- [Acederys/SegFormer-Fundus-AVSeg](https://github.com/Acederys/SegFormer-Fundus-AVSeg) —
  artery/vein, weights apparently committed but no documentation.
- [523vishwanath/retinal-vessel-segmentation](https://github.com/523vishwanath/retinal-vessel-segmentation)
  — claims 78.0% mIoU, no licence.
- [Yves-Byiringiro/retinal-vessel-segmentation](https://github.com/Yves-Byiringiro/retinal-vessel-segmentation)
  and [dusengemedia/Retinal_Vessel_Segmentation_segformer](https://github.com/dusengemedia/Retinal_Vessel_Segmentation_segformer)
  — a duplicated pair from one group evaluating SegFormer across eight public datasets.

None of those four is catalogued: no publication was found and none has more than zero stars.
**The eight-dataset evaluation is worth revisiting for the comparison tables** as prior work, if a
paper appears.

## 4. Adding a model

Model pages follow a fixed structure so they can be read against each other. Load the
`document-model` skill, which defines that structure and this table's columns, before adding or
changing an entry.
