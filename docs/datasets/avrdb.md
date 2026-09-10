# AVRDB

100 photographs from the Armed Forces Institute of Ophthalmology in Pakistan, annotated for arteries,
veins, **the arteriovenous ratio itself**, the optic nerve head, and image-level hypertensive
retinopathy and papilloedema labels. It is the only dataset in this catalogue that publishes an AVR
per image — the check for [calibre biomarkers](../biomarkers/avr.md) that
[ORIGA](origa.md) provides for cup-to-disc ratio — and it is **CC BY 4.0**.

## 1. What it is

- **Images:** 100, annotated by four expert ophthalmologists.
- **Collected at:** Armed Forces Institute of Ophthalmology (AFIO), Rawalpindi, Pakistan.
- **Purpose:** hypertensive-retinopathy assessment, where the artery-to-vein ratio is the measurement
  of clinical interest.

## 2. Provenance

| | |
| --- | --- |
| Home | Mendeley Data, DOI [10.17632/3csr652p9y.2](https://doi.org/10.17632/3csr652p9y.2) — [record](https://data.mendeley.com/datasets/3csr652p9y/2). Historically distributed through the [BIOMISA](http://biomisa.org/index.php/dataset-for-hypertensive-retinopathy/) page, which is where most citations still point and which has been unreliable |
| Download | **direct, no registration** — one archive of about 201 MB, served over Mendeley's public API with no account and no request form |
| Citation | Akram MU, Akbar S, Hassan T, Khawaja SG, Yasin U, Basit I. *Data on fundus images for vessels segmentation, detection of hypertensive retinopathy, diabetic retinopathy and papilledema.* Data in Brief 2020;29:105282. DOI: [10.1016/j.dib.2020.105282](https://doi.org/10.1016/j.dib.2020.105282) |
| Licence | **CC BY 4.0** on the Mendeley deposit — attribution only, commercial use permitted. The older BIOMISA page offered only "for the research community", which grants nothing |
| Content | 100 images at 1504×1000 |
| Annotations | Vessel network, artery/vein network, optic nerve head, **a published arteriovenous ratio per image**, hard exudates, cotton-wool spots, hypertensive retinopathy and papilloedema labels |

**Searching for "AVRDB" will not find it.** The deposit is titled after the paper — *Data on Fundus
Images for Vessels Segmentation, Detection of Hypertensive Retinopathy, Diabetic Retinopathy and
Papilledema* — and its description names the AFIO source, the four ophthalmologists and the AVR.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1504×1000 |
| Microns per pixel | Unknown — not published |
| Camera | Topcon TRC-NW8 |
| Field of view | Not stated by the authors |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Four ophthalmologists contributed; how many marked each image is not stated | Native | Vessel network |
| Artery/vein | As above | Native | A/V network |
| Optic nerve head | As above | Native | On the same photographs |
| Disease | One label per image | — | Hypertensive retinopathy and papilloedema |
| Other labels | — | — | **A published arteriovenous ratio per image**, plus hard exudates and cotton-wool spots |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list AVRDB in their training data. Held out of the
  AutoMorph family and of [LUNet](../models/lunet.md).
- **Below a model's measuring grid:** No.
- **What it can answer:** the one thing nothing else here can — whether a pipeline's computed
  [AVR](../biomarkers/avr.md) agrees with a clinician's published AVR on the same eye, on
  hypertensive retinopathy, under a permissive licence.

## 7. Known defects

- **Reader structure unknown.** Four ophthalmologists annotated the set, but whether their marks ship
  separately or as one consensus was not established from the record, so it cannot yet be said
  whether a human agreement ceiling is available.
- The widely cited BIOMISA link is unreliable; use the Mendeley DOI.

## 8. Notes

- Of everything in this catalogue, this is the dataset most directly useful for checking a
  *biomarker* rather than a mask. A published AVR is a number a human committed to, and calibre
  pipelines have nothing else to be measured against.

---

**Links, licence and access last checked:** 2026-09-11
