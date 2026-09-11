# MESSIDOR

1,200 photographs with diabetic-retinopathy and macular-oedema risk grades, from three French
ophthalmology departments. It has no pixel-level annotations of its own — and it is nonetheless one
of the most consequential entries in this catalogue, because **three other datasets are built on its
photographs**: MAPLES-DR, 460 of RIGA's images, and part of REYIA's compilation.

## 1. What it is

- **Images:** 1,200 — 400 from each of three departments, two thirds with pupil dilation.
- **Collected at:** three French ophthalmology departments, under the MESSIDOR programme funded by
  the French Ministry of Research and Defence.
- **Purpose:** to support automated diabetic-retinopathy screening research with graded images.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://www.adcis.net/en/third-party/messidor/> |
| Download | **registration** — a licence agreement is accepted on the ADCIS page before download |
| Citation | Decencière E, Zhang X, Cazuguel G, Laÿ B, Cochener B, Trone C, et al. *Feedback on a publicly distributed image database: the Messidor database.* Image Analysis & Stereology 2014;33(3):231–234. DOI: [10.5566/ias.1155](https://doi.org/10.5566/ias.1155) |
| Licence | Free for research use under the ADCIS agreement; **not a Creative Commons grant**, and redistribution is not offered |
| Content | 1,200 TIFF images in three sizes — see section 3 |
| Annotations | Diabetic-retinopathy grade (0–3) and macular-oedema risk grade (0–2), per image |

## 3. The images

Three subcollections, one per acquisition site and sensor.

### 3.1 1440×960 — 400 images

| | |
| --- | --- |
| Resolution (pixels) | 1440×960 |
| Microns per pixel | Unknown — not published |
| Camera | Topcon TRC NW6 non-mydriatic |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

### 3.2 2240×1488 — 400 images

| | |
| --- | --- |
| Resolution (pixels) | 2240×1488 |
| Microns per pixel | Unknown |
| Camera | Topcon TRC NW6 |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

### 3.3 2304×1536 — 400 images

| | |
| --- | --- |
| Resolution (pixels) | 2304×1536 |
| Microns per pixel | Unknown |
| Camera | Topcon TRC NW6 |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Disease | Graded per image | — | Diabetic retinopathy 0–3, macular-oedema risk 0–2 |

**No pixel-level annotation ships with MESSIDOR.** Everything of that kind on these photographs comes
from the datasets in section 5.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:**
  - **[MAPLES-DR](maples-dr.md)** — 198 MESSIDOR photographs with vessels, disc, cup and lesion
    classes added, labels drawn at 1500×1500.
  - **[RIGA](riga.md)** — 460 of its 750 images are MESSIDOR photographs, with disc and cup contours
    from six experts.
  - **[REYIA](reyia.md)** — draws artery/vein labels on MESSIDOR photographs among its nine sources.
  - **MESSIDOR-AV**, an artery/vein annotation used in [OCULARNet](../models/ocularnet.md)'s training
    collection.

  Four annotation projects on one set of photographs. Scoring any two of them is not two cameras'
  worth of evidence.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md), via MESSIDOR-AV.
- **Below a model's measuring grid:** No.
- **What it can answer:** disease-graded appearance at three sensor sizes from one camera family —
  and, through its derivatives, several annotation protocols on identical pixels, which is a rare
  chance to separate annotation disagreement from image difficulty.

## 7. Known defects

- A well-known erratum: the original release contained duplicate images and some grading errors,
  corrected in later distributions. Check which version you have before quoting counts.

## 8. Notes

- MESSIDOR is the clearest example in this catalogue of a dataset whose importance lies in what
  others built on it. Its own labels are image-level only, but its pixels underpin four annotation
  projects.

---

**Links, licence and access last checked:** 2026-09-11
