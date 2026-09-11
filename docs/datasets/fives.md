# FIVES

800 colour fundus photographs at 2048×2048 with a pixel-level vessel annotation on every one, 200
each of age-related macular degeneration, diabetic retinopathy, glaucoma and normal eyes — and, more
unusually, a **quality grade for every photograph**. It is the largest vessel-segmentation dataset in
this catalogue by a wide margin, and the only large one whose accuracy can be read against image
quality rather than assumed independent of it.

## 1. What it is

- **Images:** 800 — 200 AMD, 200 diabetic retinopathy, 200 glaucoma, 200 normal; split 600 train /
  200 test by the authors.
- **Collected at:** the Eye Center of the Second Affiliated Hospital, Zhejiang University School of
  Medicine, China.
- **Purpose:** a purpose-built vessel-segmentation dataset, annotated by crowdsourcing among medical
  experts with a standardised protocol and a per-image quality assessment.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.19688169](https://doi.org/10.6084/m9.figshare.19688169) |
| Download | **direct, no registration** — one RAR5 archive, about 1.8 GB |
| Citation | Jin K, Huang X, Zhou J, Li Y, Yan Y, Sun Y, Zhang Q, Wang Y, Ye J. *FIVES: A Fundus Image Dataset for Artificial Intelligence based Vessel Segmentation.* Scientific Data 2022;9:475. DOI: [10.1038/s41597-022-01564-3](https://doi.org/10.1038/s41597-022-01564-3) |
| Licence | **CC BY 4.0** — attribution only, commercial use permitted |
| Content | 800 images at 2048×2048, PNG |
| Annotations | Consensus vessel masks, per-image quality assessment, disease class |

The archive holds `train/` and `test/` with `Original/` and `Ground truth/` subfolders plus
`Quality Assessment.xlsx`. RAR5 needs `bsdtar` or another libarchive tool — the Python standard
library cannot read it. Third-party Kaggle re-uploads exist — for example
<https://www.kaggle.com/datasets/nikitamanaenkov/fundus-image-dataset-for-vessel-segmentation> and
<https://www.kaggle.com/datasets/sushanthreddypotu/fives-dataset> — with the usual caveat that a
re-upload's licence field is the uploader's. The figshare release is the citable copy and the only
one carrying the quality spreadsheet.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 2048×2048, PNG |
| Microns per pixel | Unknown — not published |
| Camera | Topcon TRC-NW8, tabletop non-mydriatic |
| Field of view | 50° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Crowdsourced among medical experts, released as a single consensus mask | Native 2048×2048 | Three-channel PNG with values {0, 255} |
| Quality | Graded per photograph | — | Illumination, blur and low-contrast components in `Quality Assessment.xlsx`, per split |
| Disease | One label per eye | — | Four classes, encoded in the filename letter: `A` AMD, `D` DR, `G` glaucoma, `N` normal |

## 5. Inheritance

- **Reuses images from:** No shared images established — FIVES is an original collection.
- **Its images are reused by:** [REYIA](reyia.md), a compilation that draws artery/vein labels on
  photographs taken from several sources including this one.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. FIVES appears in
  [OCULARNet](../models/ocularnet.md)'s training list as **FIVES-AV** — a separate artery/vein
  annotation of 75 of these photographs — so the images are in-sample for that model even though
  this vessel annotation is not.
- **Below a model's measuring grid:** No. At 2048 it is above every grid in
  [MODELS.md](../MODELS.md), so it is downsampled before measurement, which loses the thinnest
  vessels its annotation contains.
- **What it can answer:** how vessel segmentation accuracy varies with image quality and with
  disease, on a permissively licensed set large enough to stratify.

## 7. Known defects

- A stray `Thumbs.db` sits in the training image folder and must be skipped by any loader that
  enumerates files by extension.
- Two of the 800 photographs are commonly reported as unusable by downstream users; the archive
  itself contains 800.

## 8. Notes

- The four-class disease balance is by design, so a model's error rate can be read per disease — a
  property almost nothing else here has at this size.
- Because the annotation is a single consensus mask rather than several readers kept separate, FIVES
  cannot measure human disagreement. [HRF](hrf.md) and [PAPILA](papila.md) can.

---

**Links, licence and access last checked:** 2026-09-11
