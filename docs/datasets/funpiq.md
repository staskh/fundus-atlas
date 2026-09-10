# FunPiQ

300 photographs with **pixel-level** quality annotation — which region of the image is degraded, not
just how bad the image is overall. Every other quality dataset in this catalogue grades a whole
photograph; this one localises the problem, which is the annotation a measurement pipeline actually
needs, since a blurred periphery and a blurred macula have different consequences.

Its photographs are not new: they are sampled from [EyeQ](eyeq.md), [BRSET](brset.md) and
[mBRSET](mbrset.md).

## 1. What it is

- **Images:** 300, balanced across quality classes.
- **Collected at:** not collected — sampled from three existing datasets and re-annotated under a
  board-certified ophthalmologist's supervision.
- **Purpose:** a benchmark for pixel-level, rather than image-level, fundus quality assessment.

## 2. Provenance

Two provenances: the annotations are FunPiQ's, the photographs are three other datasets'.

### 2.1 FunPiQ — the annotations

| | |
| --- | --- |
| Home | Zenodo [record 21838047](https://zenodo.org/records/21838047), or the [GitHub v1.0.0 release](https://github.com/MICCAI2026-3819/FunPiQ/releases/tag/v1.0.0); code at [penway/FunPiQ](https://github.com/penway/FunPiQ) |
| Download | **direct, no registration** — the annotation archive only |
| Citation | Wang P, Morano J, Mares V, Bogunović H. *FunPiQ: A New Benchmark for Pixel-Level Quality Assessment in Fundus Images.* [arXiv:2606.25915](https://arxiv.org/abs/2606.25915) (MICCAI 2026) |
| Licence | Read the Zenodo record at download time |
| Content | Pixel-level quality annotations for 300 photographs |
| Annotations | Supplies degraded-region masks, annotated under a board-certified ophthalmologist |

### 2.2 EyeQ, BRSET and mBRSET — the photographs

| | |
| --- | --- |
| Home | See [eyeq.md](eyeq.md), [brset.md](brset.md), [mbrset.md](mbrset.md) |
| Download | **Not in the annotation archive.** Each source must be obtained separately, under its own terms — which for BRSET and mBRSET means PhysioNet credentialing |
| Citation | The three source datasets' own citations |
| Licence | **The strictest of the three governs**: PhysioNet's credentialed data use agreement, not the annotations' terms |
| Content | 300 photographs across the three sources |
| Annotations | Supplies only the images |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Mixed — inherited from three sources |
| Microns per pixel | Unknown |
| Camera | Mixed, including handheld (from mBRSET) |
| Field of view | Mixed |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Annotated under a board-certified ophthalmologist | Native, per source | **Pixel-level** — masks of the degraded regions, the only such annotation in this catalogue |

## 5. Inheritance

- **Reuses images from:** **[EyeQ](eyeq.md), [BRSET](brset.md) and [mBRSET](mbrset.md)** — 300
  photographs in total, at their native sizes. EyeQ is the training distribution of
  [AutoMorph's quality grader](../models/automorph-quality-grader.md) and of
  [QuickQual](../models/quickqual.md), so **part of FunPiQ is in-sample for both**.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** indirectly, through EyeQ — see above. Splitting the
  300 by source is necessary before claiming any held-out result.
- **Below a model's measuring grid:** Mixed.
- **What it can answer:** whether an image-level quality gate agrees with *where* the degradation is —
  and it supports a localisation metric, a Dice on the degraded region, that no other quality set
  offers.

## 7. Known defects

- The annotation archive is unusable without three separate downloads, two of them credentialed.
- Because a third of its photographs come from EyeQ, a headline number on FunPiQ is partly in-sample
  for both catalogued quality models unless the sources are separated.

## 8. Notes

- Pixel-level quality is the missing link between the quality models and the measurement pipelines:
  a biomarker measured in a degraded region is unreliable in a way an image-level "Usable" grade
  cannot express.

---

**Links, licence and access last checked:** 2026-09-11
