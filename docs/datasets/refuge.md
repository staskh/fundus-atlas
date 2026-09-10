# REFUGE and REFUGE2

The Retinal Fundus Glaucoma Challenge — 1,200 photographs in its first edition and 2,000 in its
second, each with a glaucoma label, optic disc and cup masks and a fovea coordinate. It is the
disc-and-cup training set of record: the AutoMorph family's disc model and the Hugging Face
SegFormer both learned on it, so it is the reason most disc-and-cup results in this catalogue cannot
be evaluated on it.

Its other distinguishing feature is a **deliberate domain shift**: the training images come from one
camera and the test images from another, at a different resolution, on purpose.

## 1. What it is

- **Images:** REFUGE 1,200 — 400 training, 400 offline test, 400 online test, of which 10% are
  glaucomatous. REFUGE2 raises the total to 2,000 and **contains REFUGE's 1,200**.
- **Collected at:** Chinese clinical sites, published through the MICCAI challenge series.
- **Purpose:** to compare automated glaucoma screening and disc/cup segmentation on one dataset, with
  a camera change built in between training and test.

## 2. Provenance

Two editions, and the second contains the first.

### 2.1 REFUGE — the 2018 edition, 1,200 images

| | |
| --- | --- |
| Home | <https://refuge.grand-challenge.org/> |
| Download | **registration** — an account and joining the challenge. This is the organisers' distribution and the route whose agreement you actually accept |
| Citation | Orlando JI, Fu H, Barbosa Breda J, van Keer K, Bathula DR, Diaz-Pinto A, et al. *REFUGE Challenge: A unified framework for evaluating automated methods for glaucoma assessment from fundus photographs.* Medical Image Analysis 2020;59:101570. DOI: [10.1016/j.media.2019.101570](https://doi.org/10.1016/j.media.2019.101570) · [arXiv:1910.03667](https://arxiv.org/abs/1910.03667) |
| Licence | **Research and educational use** under the challenge terms. Not a Creative Commons grant; commercial use is not offered |
| Content | 1,200 JPEG images — 400 at 2124×2056 and 800 at 1634×1634 |
| Annotations | Supplies glaucoma labels, optic disc and cup masks, fovea coordinates |

### 2.2 REFUGE2 — the 2020 edition, 2,000 images

| | |
| --- | --- |
| Home | <https://refuge.grand-challenge.org/>, also on [IEEE DataPort](https://ieee-dataport.org/documents/refuge2-challenge-treasure-trove-multi-dimension-analysis-and-evaluation-glaucoma) |
| Download | **registration** on either route. A third-party Kaggle mirror is the easiest (about 1.4 GB compressed, 4.2 GB unpacked) and its licence field reads `Unknown` |
| Citation | Fang H, Li F, Fu H, Sun X, Cao X, Lin F, et al. *REFUGE2 Challenge: A Treasure Trove for Multi-Dimension Analysis and Evaluation in Glaucoma Screening.* [arXiv:2202.08994](https://arxiv.org/abs/2202.08994) |
| Licence | Challenge terms, as above |
| Content | 2,000 images — the 1,200 above plus 800 on further devices |
| Annotations | Supplies the same label set on the added photographs |

**A mirror cannot grant rights the depositor never had.** The challenge terms bind whichever route
the files arrive by, so work built from the Kaggle copy inherits them exactly as if it had come from
the organisers. Read the agreement at download time.

## 3. The images

Three subcollections, by camera. The split is the domain shift, not an accident of collection.

### 3.1 REFUGE training set — 400 images

| | |
| --- | --- |
| Resolution (pixels) | 2124×2056, JPEG |
| Microns per pixel | Unknown — not published |
| Camera | Zeiss Visucam 500 |
| Field of view | Not stated by the authors |
| Centring | Posterior pole — both macula and disc visible |
| Modality | Colour fundus photography |

### 3.2 REFUGE offline and online test sets — 800 images

| | |
| --- | --- |
| Resolution (pixels) | 1634×1634, JPEG |
| Microns per pixel | Unknown |
| Camera | Canon CR-2 |
| Field of view | Not stated |
| Centring | Posterior pole |
| Modality | Colour fundus photography |

### 3.3 REFUGE2 additions — 800 images

| | |
| --- | --- |
| Resolution (pixels) | Varies by device |
| Microns per pixel | Unknown |
| Camera | Topcon and Kowa devices, added in the second edition |
| Field of view | Not stated |
| Centring | Posterior pole |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Consensus of a panel of ophthalmologists | Native | Masks |
| Optic cup | Consensus | Native | Masks |
| Disease | One label per eye | — | Glaucoma yes/no; about 10% glaucomatous in REFUGE |
| Fovea | — | Native | Coordinate per image |

## 5. Inheritance

- **Reuses images from:** No shared images established — REFUGE is an original collection.
- **Its images are reused by:** **REFUGE2 contains all 1,200 REFUGE photographs.** A number quoted
  on "REFUGE2" is partly a number on REFUGE. The two editions are catalogued together here for that
  reason.

## 6. Use as a benchmark

- **Catalogued models trained on these images:**
  [AutoMorph's disc-and-cup model](../models/automorph-disc-cup.md) (REFUGE's 800, with GAMMA), the
  [Hugging Face SegFormer](../models/segformer-disc-cup.md) (fine-tuned on REFUGE), and
  [BEAL](../models/beal.md) and [ISFA](../models/isfa.md), both of which use REFUGE as their
  **labelled source domain** for domain adaptation. **REFUGE cannot fairly evaluate any of those
  four**, which leaves [PAPILA](papila.md) and [G1020](g1020.md) as the practical alternatives.
- **Below a model's measuring grid:** No.
- **What it can answer:** how a disc/cup method behaves across a camera change, which is the
  challenge's own design. Not generalisation for the models above.

## 7. Known defects

- **Editions are routinely confused.** Some mirrors labelled `refuge2` contain REFUGE's 1,200 rather
  than the full 2,000; check the count before assuming which edition you have.
- Kaggle's mirror carries no data dictionary and an `Unknown` licence field.

## 8. Notes

- The training-versus-test camera split makes REFUGE unusually honest as a challenge and unusually
  awkward as a training set: a model trained only on its 400 Zeiss images has seen one camera.

---

**Links, licence and access last checked:** 2026-09-11
