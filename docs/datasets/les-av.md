# LES-AV

22 photographs with arteries and veins drawn on them, published alongside a glaucoma-risk paper
rather than as a segmentation challenge. That origin gives it things nothing else in this catalogue
has: a **glaucoma subtype** per eye, and the patient's blood pressure, heart rate and intraocular
pressure. It is small, and it is training data for the AutoMorph family's vessel and artery/vein
models, so it functions as a third camera in that lineage rather than as an evaluation set.

## 1. What it is

- **Images:** 22 — 11 glaucomatous and 11 healthy eyes, with the glaucoma cases subtyped.
- **Collected at:** published by a group spanning Argentina, Belgium and Brazil, with the
  photographs from a Leuven glaucoma clinic.
- **Purpose:** to support a simulated-haemodynamics glaucoma risk index, which is why the clinical
  measurements accompany the images.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://figshare.com/articles/dataset/LES-AV_dataset/11857698> |
| Download | **direct, no registration** — about 46 MB |
| Citation | Orlando JI, Breda JB, van Keer K, Blaschko MB, Blanco PJ, Bulant CA. *Towards a glaucoma risk index based on simulated hemodynamics from fundus images.* MICCAI 2018, LNCS 11071:65–73. DOI: [10.1007/978-3-030-00934-2_8](https://doi.org/10.1007/978-3-030-00934-2_8) |
| Licence | **Research use only; commercial use forbidden**, per the archive's own `README.txt`: "Any commercial usage is forbidden. This data set can only be used for scientific purposes." |
| Content | 22 images — 21 at 1444×1620, 1 at 1958×2196 |
| Annotations | Artery/vein maps, glaucoma subtype per eye, blood pressure, heart rate and intraocular pressure |

**Two licences disagree.** figshare's metadata records the item as **GPL**, a software licence and an
odd fit for photographs. Where the two conflict, the narrower text inside the archive governs: treat
LES-AV as research-only.

## 3. The images

Two subcollections, by field of view.

### 3.1 The 30° set — 21 images

| | |
| --- | --- |
| Resolution (pixels) | 1444×1620 |
| Microns per pixel | Unknown — not published |
| Camera | Unknown make; a clinical fundus camera at the collecting site |
| Field of view | 30° |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

### 3.2 The 45° image — 1 image

| | |
| --- | --- |
| Resolution (pixels) | 1958×2196 |
| Microns per pixel | Unknown |
| Camera | Unknown |
| Field of view | 45° |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

One image out of 22 at a different field and size is easy to miss and will break any loader that
assumes a fixed shape.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | One | Native | Manual |
| Vessels | Derived from the A/V labels | Native | — |
| Disease | One label per eye | — | **Glaucoma subtype**: normal, normal-tension, open-angle — the only subtype labels in this catalogue |
| Clinical measurements | — | — | Blood pressure, heart rate, intraocular pressure per patient |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  (in `ALL-SIX`) and [BF-Net](../models/bf-net.md) (in `ALL-AV`) — so **in-sample twice** for the
  AutoMorph family. Also in [OCULARNet](../models/ocularnet.md)'s training list.
- **Below a model's measuring grid:** No — 1444×1620 sits above the AutoMorph grids and near the
  newer models' 1024.
- **What it can answer:** whether accuracy varies with glaucoma subtype, and — uniquely here —
  whether a vascular biomarker tracks a patient's blood pressure, since both are published for the
  same eyes.

## 7. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 8. Notes

- 22 images is too few for a segmentation score to be stable; its value is the clinical metadata,
  not the sample size.

---

**Links, licence and access last checked:** 2026-09-11
