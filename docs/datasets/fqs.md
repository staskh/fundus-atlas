# FQS

2,246 photographs with a **continuous** image-quality score — a mean opinion score from 0 to 100 —
alongside the usual three-way Good/Usable/Reject label. Every other quality dataset in this
catalogue grades into classes; this one puts a number on it, which makes it the only place where a
quality model's output can be correlated rather than merely confused-matrixed.

## 1. What it is

- **Images:** 2,246.
- **Collected at:** Chinese clinical sources, published with a quality-assessment network.
- **Purpose:** to make fundus image quality a continuous, regressable quantity.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, [FIQS Dataset (Fundus Image Quality Scores)](https://figshare.com/articles/dataset/FIQS_Dataset_Fundus_Image_Quality_Scores_/28129847) |
| Download | **direct, no registration** — from the same record |
| Citation | *Acquire continuous and precise score for fundus image quality assessment: FTHNet and FQS dataset.* Scientific Reports 2025. DOI: [10.1038/s41598-025-24423-8](https://doi.org/10.1038/s41598-025-24423-8) |
| Licence | The accompanying paper is **CC BY 4.0**; confirm the figshare record's own licence field at download time, since the two are not automatically the same |
| Content | 2,246 images, originally about 1942×1942, **standardised to 1024×1024 in the public files** |
| Annotations | A mean opinion score from 0 to 100, plus a Good/Usable/Reject class |

Reference code: [HudenJear/BasiQA](https://github.com/HudenJear/BasiQA).

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **1024×1024 in the public release** — a resize, not a camera native; the originals are about 1942×1942 |
| Microns per pixel | Unknown |
| Camera | Not stated |
| Field of view | Not stated |
| Centring | Mixed |
| Modality | Colour fundus photography |

The resize is harmless for a quality classifier, which never reports physical units. It would be
misleading for anything measuring vessels, and these photographs should not be fed to a
measurement pipeline as if 1024 were their native size.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Mean opinion score aggregated from multiple raters | — | **Continuous, 0–100**, plus the three-way class. The continuous score is the dataset's contribution |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of both quality models
  here.
- **Below a model's measuring grid:** No, at 1024 — but the effective detail is that of a resized
  image.
- **What it can answer:** whether a three-class quality gate's decisions are monotonic in a
  continuous human score, and where its thresholds actually sit. Neither
  [AutoMorph's grader](../models/automorph-quality-grader.md) nor
  [QuickQual](../models/quickqual.md) has been evaluated that way.

## 7. Known defects

- The public files are pre-resized (section 3), and the record's licence field needs checking
  separately from the paper's.

## 8. Notes

- A continuous target changes what "quality" can mean for a pipeline: instead of rejecting an image,
  a measurement could be weighted by its score. Nothing in this catalogue does that yet, and this is
  the dataset that would support it.

---

**Links, licence and access last checked:** 2026-09-11
