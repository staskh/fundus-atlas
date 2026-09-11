# RAVIR

36 images with artery and vein segmentations — and **not colour fundus photographs**: they are
infrared reflectance images from a Heidelberg Spectralis. That makes RAVIR a modality test rather
than a performance test: it asks whether an artery/vein model fails safely on imagery it has never
seen, which nothing else in this catalogue asks.

## 1. What it is

- **Images:** 36.
- **Collected at:** a United States clinical setting, with diabetic and hypertensive retinopathy
  represented.
- **Purpose:** semantic segmentation and quantitative analysis of arteries and veins in infrared
  reflectance imaging.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://ravirdataset.github.io/data/> |
| Download | **request-gated** — a link on that page, released on agreeing to the stated data usage protocols. Read them before automating anything |
| Citation | Hatamizadeh A, Hosseini H, Patel N, Choi J, Pole CD, Hoeferlin CM, Schwartz SD, Terzopoulos D. *RAVIR: A Dataset and Methodology for the Semantic Segmentation and Quantitative Analysis of Retinal Arteries and Veins in Infrared Reflectance Imaging.* IEEE Journal of Biomedical and Health Informatics 2022;26(7):3272–3283. DOI: [10.1109/JBHI.2022.3163352](https://doi.org/10.1109/JBHI.2022.3163352) |
| Licence | **Not a standard grant** — a usage protocol the downloader accepts |
| Content | 36 images at 768×768 |
| Annotations | Artery and vein segmentations; the test masks are withheld for a public leaderboard |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 768×768 |
| Microns per pixel | Unknown — not published |
| Camera | Heidelberg Spectralis |
| Field of view | 30° |
| Centring | Disc-centred |
| Modality | **Infrared reflectance — not colour fundus photography.** Vessels appear with inverted, higher-contrast appearance and no colour information at all, so artery/vein separation cannot rely on the colour cues every model here was trained on |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | Reference standard | Native | Test masks withheld for the leaderboard, as with [RETA](reta.md) |
| Disease | Per eye | — | Diabetic and hypertensive retinopathy |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on it. [OCULARNet](../models/ocularnet.md)
  uses RAVIR as a **far out-of-distribution test set**, which is exactly the right use.
- **Below a model's measuring grid:** Yes at 768 relative to the 912 and 1024 grids, though the
  modality difference matters more than the size.
- **What it can answer:** whether an artery/vein model degrades gracefully or catastrophically off
  its modality. A poor score here is not a failure of the model on its intended input.

## 7. Known defects

- Test masks are withheld, so only the released split can be scored locally.
- The modality is the point and also the trap: pooling RAVIR with colour datasets produces a number
  that means nothing.

## 8. Notes

- Infrared reflectance is standard on OCT devices, so images like these are abundant in clinics even
  though almost no fundus model is trained for them. That gap is worth measuring, and this is the
  only dataset here that measures it.

---

**Links, licence and access last checked:** 2026-09-11
