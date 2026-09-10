# ISFA

ISFA segments the optic disc and cup across cameras, tackling the same problem as [BEAL](beal.md) —
a model trained on one clinic's photographs does worse on another's — and building on BEAL's code.

Its approach is to build a bridge rather than to align the two ends directly. A generative network
synthesises "target-like query images": the labelled source photographs repainted in the target
camera's appearance, with the disc and cup boundaries preserved. Those synthetic images sit between
the two domains, and the method then aligns what the network sees in all three — source, synthetic
and target — at the level of content and style features, aligns the outputs adversarially, and adds
an edge-attention module so boundary structure survives the process.

Two practical cautions come before anything else: **the image-synthesis code was never released**,
and **no trained weights are published**. The repository as it stands cannot reproduce the paper.

## 1. Code reference

- **Repository:** https://github.com/thinkobj/ISFA
- **Version described here:** commit `7680ad9d` (2021-08-18). No tags or releases.
- **Most recent commit:** 2021-08
- **Training code included:** Partly. `train.py` and `test.py` are published, but the README states
  that the image-synthesis step — which produces the target-like query images the method depends on
  — "will release soon". It has not appeared in the years since, so the published pipeline is
  incomplete.
- **Language and how it runs:** Python with PyTorch.
  `python train.py --data_dir=/path/to/ISFA/data/`, then
  `python test.py --data_dir=… --model-file=./logs/your_checkpoint_dir`.

## 2. License

- **Code:** **None stated.** No LICENSE file, so no reuse or redistribution permission has been
  granted. This is compounded by the README's own statement that part of the code is revised from
  [BEAL](beal.md), which is MIT-licensed and therefore requires its licence and copyright notice to
  be carried along — a condition an unlicensed repository does not meet.
- **Model weights:** Not applicable — none are published.

## 3. Major publications by the authors

- Lei H, Liu W, Xie H, Zhao B, Yue G, Lei B. *Unsupervised Domain Adaptation Based Image Synthesis
  and Feature Alignment for Joint Optic Disc and Cup Segmentation.* IEEE Journal of Biomedical and
  Health Informatics, 2021. DOI:
  [10.1109/JBHI.2021.3085770](https://doi.org/10.1109/JBHI.2021.3085770)

## 4. What it produces

- **Purpose:** `disc/cup`
- **Output classes:** joint optic disc and optic cup masks.
- **Input grid:** 256×256 — the smallest grid in this catalogue, a quarter of BEAL's training grid
  on each side despite ISFA being built on BEAL's code. On a 256-pixel disc crop the cup boundary is
  a few pixels wide, which is worth remembering when reading the reported cup Dice improvement.
- **Output grid:** joint disc and cup masks at 256×256.
- **Grid set in:** `tr.Resize(256)` in both `train.py` and `test.py`.
- **Input expected:** a colour-fundus photograph cropped around the optic disc, in the repository's
  `data/` layout. The method additionally expects synthesised target-like images at training time,
  which the published code cannot generate.
- **Preprocessing in the published code:** handled by the dataloaders, inherited from BEAL's
  structure.

## 5. Architecture

- **Family:** a DeepLabv3+-style segmentation network (`networks/Segmentor.py`, with `aspp.py` and
  `decoder.py`) plus adversarial components (`GAN.py`) and an edge-attention module
  (`attention.py`) applied to low-level feature maps. Three mechanisms are combined: GAN-based image
  synthesis, content and style feature alignment, and output-level adversarial alignment.
- **Parameters:** Unknown. A MobileNetV2 ImageNet backbone (9 MB) is committed in
  `pretrained_model/`, which is the standard torchvision starting point, not a trained ISFA model.
- **Single model or ensemble:** a single model, trained per target domain.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| REFUGE | Source domain, labelled training | The challenge organisers | Yes, the REFUGE training set |
| Drishti-GS | Target domain, unlabelled during training; then test | The dataset's own authors | Yes |
| RIM-ONE-r3 | Target domain, unlabelled during training; then test | The dataset's own authors | Yes |

As with BEAL, the test images take part in training without their labels, so neither target dataset
is a blind benchmark. The authors also discuss the method's robustness when the target dataset is
small, which is the realistic case for a single clinic.

## 7. Weights

- **Publicly available:** **No.** The `checkpoint/` and `logs/` folders contain only placeholder
  files. The only committed weights are the ImageNet MobileNetV2 backbone
  (`pretrained_model/mobilenet_v2-6a65762b.pth`), which is not a trained ISFA model.
- **Download URL:** None.
- **Format and size:** Not applicable.
- **Files in an ensemble:** Not applicable.

## 8. Performance as reported by the authors

The paper reports an improvement of about 3% in Dice score for optic cup segmentation on Drishti-GS
over the next best method — a Dice score measures overlap between the predicted mask and a
human-drawn one, and the cup is the harder of the two structures. The authors also report results on
RIM-ONE-r3 and discuss robustness on small target datasets.

These are the authors' measurements. Because no weights are published and the synthesis code is
missing, nobody outside the group can currently reproduce them, which is the most important fact on
this page.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued pipeline runs this model | — |

## 10. Known defects

### 10.1 The published code cannot reproduce the published method

- **What is wrong:** the image-synthesis stage that generates the target-like query images — the
  intermediate domain the whole method rests on — is not in the repository. The README says it "will
  release soon"; the repository has not changed since 2021-08.
- **What it affects:** everything. Without those images the feature-alignment stages have nothing to
  align against, so the method as published cannot be trained as described.
- **Evidence:** the README's own statement, under "Preparation for dataset".
- **Status:** open, and effectively abandoned. No weights are published either, so there is no way
  around it by using a trained model.

## 11. Notes

- **Relationship to BEAL.** The authors state part of the code is revised from BEAL. Two
  consequences: results from the two are not independent evidence about this family of methods, and
  the licensing question in section 2 needs resolving before anyone reuses this code.
- Read this page as documentation of a published *method* whose implementation is incomplete, rather
  than of software you can run.

---

**Links and license last checked:** 2026-09-10
