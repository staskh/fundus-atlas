# PAPILA

488 disc-centred photographs — both eyes of 244 patients — with the **optic disc and the optic cup
outlined by two independent experts**, plus a full clinical record per eye. It is the largest
two-reader disc-and-cup dataset in this catalogue, and the only one that can say what human
disagreement on the cup looks like at scale, which is exactly what a cup-to-disc ratio needs to be
read against.

## 1. What it is

- **Images:** 488 — both eyes of 244 patients: 333 healthy, 87 glaucoma-suspect, 68 glaucoma.
- **Collected at:** Hospital General Universitario Reina Sofía, Murcia, Spain.
- **Purpose:** glaucoma assessment with both eyes and the clinical record of the same patient, so
  that image findings can be read alongside the ophthalmologist's own data.

## 2. Original publication

- Kovalyk O, Morales-Sánchez J, Verdú-Monedero R, Sellés-Navarro I, Palazón-Cabanes A,
  Sancho-Gómez J-L. *PAPILA: Dataset with fundus images and clinical data of both eyes of the same
  patient for glaucoma assessment.* Scientific Data 2022;9:291. DOI:
  [10.1038/s41597-022-01388-1](https://doi.org/10.1038/s41597-022-01388-1)

## 3. Access

- **Home:** figshare, DOI [10.6084/m9.figshare.14798004](https://doi.org/10.6084/m9.figshare.14798004)
- **Direct download:** **Yes** — unattended, no registration; about 591 MB.
- **Arrives as:** one archive with the images, per-expert contour files and the clinical spreadsheet.

## 4. Licence

- **Images and annotations:** **GPL 3.0 or later**, as recorded on figshare. As with LES-AV, this is
  a software licence applied to a data release; it is nonetheless what the distributor states, and it
  carries share-alike obligations that a CC BY dataset does not.

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | 2576×1934, JPEG |
| Microns per pixel | Unknown — not published, but the camera and field are both known, so an approximate scale is derivable from the optic disc's typical size |
| Camera | Topcon TRC-NW400, non-mydriatic |
| Field of view | 30° |
| Centring | **Disc-centred** (centred on the papilla) |
| Modality | Colour fundus photography |

This is one of very few datasets in this catalogue where both the camera and its field angle are
stated by the authors rather than inferred.

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Two experts, kept separate** | Native | Contours, published as floating-point coordinates |
| Optic cup | **Two experts, kept separate** | Native | The only two-reader cup annotation of this size here |
| Disease | Three assessments per eye | — | Healthy / suspect / glaucoma |
| Clinical record | — | — | Age, sex, refraction, intraocular pressure, visual-field indices, pachymetry and more |

## 7. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [REYIA](reyia.md), whose compilation includes PAPILA photographs —
  so scoring both counts some of these images twice.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list PAPILA in their training data. It is **held out**
  of the AutoMorph family's disc-and-cup model, which trained on REFUGE and GAMMA, and of the
  [Hugging Face SegFormer](../models/segformer-disc-cup.md), which trained on REFUGE.
- **Below a model's measuring grid:** No.
- **What it can answer:** genuine generalisation for the disc-and-cup models in this catalogue, and
  the human agreement ceiling those models should be read against. Of everything here it is the best
  candidate for a cup-to-disc ratio comparison.

## 9. Known defects

- The published contour coordinates are floating point; rounding them to pixels costs at most half a
  pixel on a 2576-pixel image, far below the distance between the two experts. Worth knowing, not
  worth worrying about.

## 10. Notes

- Disc-centred at 30° means the disc fills much more of the frame than in a 45° macula-centred
  photograph. A disc model trained on wider fields will see a differently-scaled disc here even
  after resampling to its own grid.

---

**Links, licence and access last checked:** 2026-09-11
