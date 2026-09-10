# RITE (DRIVE-AV)

**RITE is DRIVE.** The same 40 photographs, from a different group, with an **artery/vein reference
standard** drawn on top — arteries, veins, overlaps and uncertain vessels as separate classes. It is
the reference artery/vein dataset for the field, cited as often as "DRIVE-AV" as by its own name, and
it is the single most important entry in this catalogue for understanding why the inheritance
question is asked at all: score DRIVE and RITE and you have measured one set of images twice.

## 1. What it is

- **Images:** 40 — DRIVE's 20 training and 20 test photographs, split unchanged.
- **Collected at:** not collected; annotated at the University of Iowa on
  [DRIVE](drive.md)'s photographs.
- **Purpose:** to provide an artery/vein reference standard, published with a method for separating
  overlapping vascular trees.

## 2. Original publication

- Hu Q, Abràmoff MD, Garvin MK. *Automated separation of binary overlapping trees in low-contrast
  color retinal images.* MICCAI 2013, LNCS 8150:436–443. DOI:
  [10.1007/978-3-642-40763-5_54](https://doi.org/10.1007/978-3-642-40763-5_54)
- The photographs' own publication is [DRIVE](drive.md)'s, Staal et al. 2004 — cite both.

## 3. Access

- **Home:** <https://eye.medicine.uiowa.edu/rite-dataset>
- **Direct download:** **Request** — the Iowa page asks for a download request form, after which it
  points at `AV_groundTruth.zip`. That link is known to fail in some browsers while working with
  `wget` or `curl`.
- **Arrives as:** `AV_groundTruth.zip`, about 30 MB — 40 TIFF images plus 80 PNG label files and two
  text files.

## 4. Licence

- **Images:** DRIVE's terms apply to the photographs themselves — research use under DRIVE's
  registration.
- **Annotations:** research use; the authors require the citation in section 2.
- **Restrictions worth knowing:** two sets of terms govern one archive, since the images and the
  labels come from different groups.

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | 565×584 — DRIVE's images, unchanged |
| Microns per pixel | Unknown |
| Camera | Canon CR5 non-mydriatic 3CCD (DRIVE's) |
| Field of view | 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | One reference standard | Native | Four classes: artery, vein, overlap, uncertain — the overlap class is unusual and is what the paper's method addresses |
| Vessels | Derived | Native | RITE's vessel labels are **not identical to DRIVE's**: the training split is a modified version of DRIVE's first manual annotation and the test split follows DRIVE's *second* observer |

That last row is the subtlety worth carrying: the images are identical to DRIVE's, the vessel
annotations are not, so a Dice against RITE is not a Dice against DRIVE.

## 7. Inheritance

- **Reuses images from:** **[DRIVE](drive.md) — all 40, unresized.**
- **Its images are reused by:** the same 40 photographs also appear in [REYIA](reyia.md)'s
  compilation.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** [BF-Net](../models/bf-net.md) and
  [Big W-Net](../models/big-wnet.md) train on it as DRIVE-AV;
  [OCULARNet](../models/ocularnet.md) and [OCULARNet-nano](../models/ocularnet-nano.md) include
  DRIVE in their training list; every model that trained on DRIVE has seen these pixels.
- **Below a model's measuring grid:** **Yes** — 565×584, below every grid in
  [MODELS.md](../MODELS.md), so scores are computed on upsampled images.
- **What it can answer:** comparability with the artery/vein literature, which is almost entirely
  reported on this dataset. Not generalisation.

## 9. Known defects

- The download link from the request form does not work in some browsers; fetching it with a
  command-line tool succeeds.

## 10. Notes

- Because "DRIVE-AV" and "RITE" name the same thing, a training-data list containing both looks
  broader than it is. This catalogue records it once, here, and cross-references from DRIVE.

---

**Links, licence and access last checked:** 2026-09-11
