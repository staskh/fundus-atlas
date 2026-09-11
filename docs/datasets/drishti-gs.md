# Drishti-GS

101 photographs from an Indian glaucoma clinic with the optic disc and cup marked by **multiple
experts**, distributed as soft maps that show where the experts agreed and where they did not. It is
small, it is widely reported in the disc/cup literature, and it is held out of every model in this
catalogue — which makes it useful for literature comparison even though it is too small to settle a
generalisation question.

## 1. What it is

- **Images:** 101 — 50 training with public ground truth, 51 test.
- **Collected at:** Aravind Eye Hospital, Madurai, India; Indian subjects only.
- **Purpose:** optic nerve head assessment for glaucoma, with multi-expert boundaries.

## 2. Provenance

| | |
| --- | --- |
| Home | [CVIT Drishti-GS page](https://cvit.iiit.ac.in/projects/mip/drishti-gs/mip-dataset2/Home.php) |
| Download | **direct** for the training split with its ground truth; the **test split's ground truth is released after registration** on the site |
| Citation | Sivaswamy J, Krishnadas SR, Datt Joshi G, Jain M, Syed Tabish AU. *Drishti-GS: Retinal Image Dataset for Optic Nerve Head (ONH) Segmentation.* IEEE ISBI 2015. DOI: [10.1109/ISBI.2014.6867807](https://doi.org/10.1109/ISBI.2014.6867807). Also Sivaswamy J, et al. *A Comprehensive Retinal Image Dataset for the Assessment of Glaucoma from the Optic Nerve Head Analysis.* JSM Biomedical Imaging Data Papers 2015;2(1):1004 |
| Licence | **"This dataset is free to use"** — the distributor's own words, and not a Creative Commons licence. Cite both papers |
| Content | 101 images at about 2896×1944 |
| Annotations | Optic disc and cup from multiple experts (four in the original ONH paper), commonly distributed as soft maps; cup-to-disc ratio and notching |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | About 2896×1944 |
| Microns per pixel | Unknown — not published |
| Camera | Not stated |
| Field of view | 30°, per the collection protocol |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Four experts** in the original paper | Native | Distributed as soft maps — the value at each pixel reflects how many experts included it, which is agreement information most datasets discard |
| Optic cup | **Four experts** | Native | As above |
| Disease | Per eye | — | Glaucoma |
| Other labels | — | — | Cup-to-disc ratio, notching |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established for training. But
  [BEAL](../models/beal.md) and [ISFA](../models/isfa.md) use Drishti-GS as their **unlabelled target
  domain**, so those two have seen these photographs without their labels — legitimate for
  unsupervised domain adaptation, and it means Drishti-GS is not a blind test for either.
- **Below a model's measuring grid:** No.
- **What it can answer:** comparability with a large disc/cup literature, and — through the soft maps
  — how a model's boundary sits relative to the region experts disagreed about.

## 7. Known defects

- The test ground truth requires a registration step the training split does not, so a paper's
  "Drishti-GS score" may be on either split.

## 8. Notes

- Soft maps are the underused feature. A model whose boundary falls inside the region four experts
  disagreed about is not wrong in any meaningful sense, and a hard Dice cannot express that.

---

**Links, licence and access last checked:** 2026-09-11
