# MAPLES-DR

198 [MESSIDOR](messidor.md) photographs annotated by retinologists with **vessels, optic disc, optic
cup and six lesion classes on the same eyes** — the only dataset in this catalogue combining a vessel
map with a disc *and* cup on identical photographs. That combination is what an end-to-end pipeline
needs to be checked against, and outside [HRF](hrf.md)'s 45 images nothing else here provides it.

## 1. What it is

- **Images:** 198 — 200 were selected and two were dropped as MESSIDOR duplicates.
- **Collected at:** not collected; annotated in Montreal on MESSIDOR's French photographs.
- **Purpose:** anatomical and pathological labels for explainable diabetic-retinopathy screening.

## 2. Provenance

Two provenances: the labels are MAPLES-DR's, the photographs are MESSIDOR's and are **not** in the
label archive.

### 2.1 MAPLES-DR — the labels

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.24328660](https://doi.org/10.6084/m9.figshare.24328660); documentation at <https://liv4d.github.io/MAPLES-DR/en/> |
| Download | **direct, no registration**. A Python helper package, `maples_dr`, matches, crops and resizes MESSIDOR frames onto the label grid |
| Citation | Lepetit-Aimon G, Playout C, Boucher MC, Duval R, Brent MH, Cheriet F. *MAPLES-DR: MESSIDOR Anatomical and Pathological Labels for Explainable Screening of Diabetic Retinopathy.* Scientific Data 2024;11:914. DOI: [10.1038/s41597-024-03739-6](https://doi.org/10.1038/s41597-024-03739-6) |
| Licence | **CC BY 4.0** |
| Content | Labels for 198 photographs |
| Annotations | Supplies vessels, optic disc, optic cup (on 192), six lesion classes, macula location, and regraded DR and macular-oedema grades |

### 2.2 MESSIDOR — the photographs

| | |
| --- | --- |
| Home | <https://www.adcis.net/en/third-party/messidor/> |
| Download | **registration** — a licence agreement on the ADCIS page |
| Citation | Decencière E, et al. *Feedback on a publicly distributed image database: the Messidor database.* Image Analysis & Stereology 2014;33(3):231–234. DOI: [10.5566/ias.1155](https://doi.org/10.5566/ias.1155) |
| Licence | **Research and educational use only** — stricter than the labels' CC BY 4.0. The combined result inherits MESSIDOR's terms |
| Content | The 198 photographs, at MESSIDOR's three native sizes |
| Annotations | Supplies only the images and its own image-level grades |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | MESSIDOR's natives — 1440×960, 2240×1488 and 2304×1536 |
| Microns per pixel | Unknown |
| Camera | Topcon TRC NW6 |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Retinologists | **1500×1500** | Photographs were cropped and resized to 1500×1500 **before** annotation; the public archive then stores the masks back at MESSIDOR's native dimensions |
| Optic disc | Retinologists | 1500×1500 | As above |
| Optic cup | Retinologists | 1500×1500 | On 192 of the 198 |
| Disease | Regraded | — | DR and macular-oedema grades, regraded rather than inherited |
| Other labels | Retinologists | 1500×1500 | Six lesion classes, macula location |

**The annotation grid is not the image grid.** Labels were drawn at 1500×1500 and stored at native
size, so their effective precision is the 1500 grid's, whatever their file dimensions say. Treating
"MESSIDOR native" and "the grid the retinologist drew on" as the same thing is the mistake this page
exists to prevent.

## 5. Inheritance

- **Reuses images from:** **[MESSIDOR](messidor.md)** — 198 photographs, at native size in the
  archive but annotated at a 1500×1500 rendition.
- **Its images are reused by:** None established. Note that [RIGA](riga.md) annotates a different
  460 MESSIDOR photographs, and [REYIA](reyia.md) a further selection — three annotation projects on
  one collection.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established for the MAPLES-DR labels;
  MESSIDOR-AV, a different annotation of the same collection, is in
  [OCULARNet](../models/ocularnet.md)'s training data, so the *photographs* are in-sample for that
  model.
- **Below a model's measuring grid:** No.
- **What it can answer:** an end-to-end check — vessels, disc and cup on one photograph, held out of
  the AutoMorph family. The obvious target for a whole-pipeline comparison outside HRF.

## 7. Known defects

- Two of the 200 selected photographs were MESSIDOR duplicates and were dropped, which is why the
  count is 198.

## 8. Notes

- The label archive without MESSIDOR access is unusable, and MESSIDOR access requires a registration
  the labels' own CC BY 4.0 does not cover. A dataset can be permissively licensed and still not be
  obtainable permissively.

---

**Links, licence and access last checked:** 2026-09-11
