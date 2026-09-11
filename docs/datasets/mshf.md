# MSHF

1,302 photographs assembled specifically to make image quality measurable across **four camera
classes at once** — tabletop, portable, and ultra-wide-field — with three readers scoring
illumination, clarity, contrast and overall quality on every one. It is the only dataset in this
catalogue built around heterogeneity of device rather than of disease, and the only one where a
quality score is available from three separate people.

## 1. What it is

- **Images:** 1,302 — 500 standard colour fundus photographs, 302 from portable cameras, and 500
  ultra-wide-field mosaics. The authors split them 1,042 train / 260 test.
- **Collected at:** Chinese clinical sites; published as a multi-source heterogeneous fundus dataset.
- **Purpose:** image-quality assessment across devices, with per-reader scores retained.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.21507564](https://doi.org/10.6084/m9.figshare.21507564) |
| Download | **direct, no registration** — a zip of photographs plus two Excel score sheets |
| Citation | Jin K, Gao Z, Jiang X, et al. *MSHF: A Multi-Source Heterogeneous Fundus (MSHF) Dataset for Image Quality Assessment.* Scientific Data 2023;10:286. DOI: [10.1038/s41597-023-02188-x](https://doi.org/10.1038/s41597-023-02188-x) |
| Licence | **CC BY 4.0** |
| Content | 1,302 images across three device classes |
| Annotations | Illumination, clarity, contrast and overall quality, each 0/1 from **three readers**, with consensus *and* individual scores both shipped |

## 3. The images

Three subcollections by device class, which is the dataset's whole point.

### 3.1 Colour fundus photographs — 500 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated uniformly |
| Microns per pixel | Unknown |
| Camera | Kowa at 45° and Topcon TRC-NW8 at 50°, per the authors' device list |
| Field of view | 45° and 50° |
| Centring | Mixed |
| Modality | Colour fundus photography |

### 3.2 Portable-camera photographs — 302 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated uniformly |
| Microns per pixel | Unknown |
| Camera | A handheld device (DEC200 class) at 60° |
| Field of view | 60° |
| Centring | Mixed |
| Modality | Colour fundus photography, handheld |

### 3.3 Ultra-wide-field mosaics — 500 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated uniformly |
| Microns per pixel | Unknown |
| Camera | Optos, 200° |
| Field of view | **200°** |
| Centring | Not applicable — a wide-field mosaic |
| Modality | **Ultra-wide-field imaging, not standard colour fundus photography.** Never pool the 500 UWF frames with the others |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | **Three, kept separate as well as merged** | — | Four binary components each: illumination, clarity, contrast, overall |
| Disease | Per eye | — | Diabetic retinopathy, glaucoma, healthy — on the colour-fundus portion |
| Other labels | — | — | Camera class per image |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — **held out of both quality
  models** in this catalogue, which both learned from [EyeQ](eyeq.md).
- **Below a model's measuring grid:** Varies by device class.
- **What it can answer:** whether a quality grader trained on one screening programme's photographs
  transfers to a portable camera — and, through the three readers, how much of a quality
  disagreement is human rather than machine. It is the strongest held-out quality cohort here.

## 7. Known defects

- The three device classes are a single archive; anyone treating MSHF as one dataset will mix a 45°
  photograph with a 200° mosaic.
- Mapping its four binary components onto a three-way Good/Usable/Reject scheme is a decision, not a
  translation, and has to be defined before any comparison with [EyeQ](eyeq.md)-trained models.

## 8. Notes

- Individual reader scores are rare and valuable. Most quality datasets publish a consensus and
  discard exactly the disagreement that would calibrate a model's errors.

---

**Links, licence and access last checked:** 2026-09-11
