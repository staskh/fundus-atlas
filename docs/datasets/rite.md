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

## 2. Provenance

Two provenances: the photographs are [DRIVE](drive.md)'s, the artery/vein standard is Iowa's.

### 2.1 DRIVE — the photographs

| | |
| --- | --- |
| Home | <https://drive.grand-challenge.org/> |
| Download | **registration** |
| Citation | Staal J, Abràmoff MD, Niemeijer M, Viergever MA, van Ginneken B. *Ridge-based vessel segmentation in color images of the retina.* IEEE TMI 2004;23(4):501–509. DOI: [10.1109/TMI.2004.825627](https://doi.org/10.1109/TMI.2004.825627) |
| Licence | Research use under DRIVE's registration terms |
| Content | 40 images at 565×584 |
| Annotations | Supplies the images themselves |

### 2.2 RITE — the artery/vein reference standard

| | |
| --- | --- |
| Home | <https://eye.medicine.uiowa.edu/rite-dataset> |
| Download | **request** — a form, after which the page points at `AV_groundTruth.zip` (about 30 MB). That link is known to fail in some browsers while working with `wget` or `curl` |
| Citation | Hu Q, Abràmoff MD, Garvin MK. *Automated separation of binary overlapping trees in low-contrast color retinal images.* MICCAI 2013, LNCS 8150:436–443. DOI: [10.1007/978-3-642-40763-5_54](https://doi.org/10.1007/978-3-642-40763-5_54) |
| Licence | Research use; the authors require the citation above |
| Content | The same 40 photographs, unresized |
| Annotations | Supplies artery, vein, overlap and uncertain classes, plus its own vessel labels |

Two sets of terms govern one archive, because the images and the labels come from different groups.

### 2.3 VC-Net — a secondary copy of the photographs and artery/vein labels

| | |
| --- | --- |
| Home | <https://github.com/yiyg510/VC-Net/tree/master/data> — the DRIVE copies are in `data/DRIVE_AV/` |
| Download | **direct, no registration** — 40 photographs with their labels, 20 under `training/` and 20 under `test/`, renamed `0.png` … `19.png` |
| Citation | Hu J, Wang H, Cao Z, Wu G, Jonas JB, Wang YX, Zhang J. *Automatic Artery/Vein Classification Using a Vessel-Constraint Network for Multicenter Fundus Images.* Frontiers in Cell and Developmental Biology 2021;9:659941. DOI: [10.3389/fcell.2021.659941](https://doi.org/10.3389/fcell.2021.659941) — cite 2.1 and 2.2 as well, since the data is theirs |
| Licence | **None stated, and none inherited.** VC-Net's repository carries no licence file. DRIVE's registration terms and RITE's request terms still govern this data, and a copy cannot loosen them |
| Content | The same 40 photographs at 565×584 |
| Annotations | Artery, vein and crossing classes, a vessel layer and field-of-view masks |

**This is the only route to these labels that asks for nothing** — no registration, as DRIVE
requires, and no request form, as RITE requires. That is precisely why it should be used carefully:
the terms in 2.1 and 2.2 are what a user is bound by, whichever copy they downloaded.

**The uncertain class is not in it.** *Our finding, 2026-09-19:* the label examined
(`data/DRIVE_AV/test/label/0.png`) holds four colours — black background, red, blue and green —
and no white, while RITE's own standard carries a fourth, *uncertain* class. What was dropped, and
whether it was folded into background or into a vessel class, has not been established here, and
cannot be until RITE itself is fetched. **Which published standard these labels are a copy of is
not stated by their authors**, and this page does not assert it: the check that settled the HRF
copies ([hrf.md](hrf.md) §2.4) cannot be run for DRIVE until there is a store to run it against.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 565×584 — DRIVE's images, unchanged |
| Microns per pixel | Unknown |
| Camera | Canon CR5 non-mydriatic 3CCD (DRIVE's) |
| Field of view | 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | One reference standard | Native | Four classes: artery, vein, overlap, uncertain — the overlap class is unusual and is what the paper's method addresses |
| Vessels | Derived | Native | RITE's vessel labels are **not identical to DRIVE's**: the training split is a modified version of DRIVE's first manual annotation and the test split follows DRIVE's *second* observer |

That last row is the subtlety worth carrying: the images are identical to DRIVE's, the vessel
annotations are not, so a Dice against RITE is not a Dice against DRIVE.

## 5. Inheritance

- **Reuses images from:** **[DRIVE](drive.md) — all 40, unresized.**
- **Its images are reused by:** the same 40 photographs also appear in [REYIA](reyia.md)'s
  compilation.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [BF-Net](../models/bf-net.md) and
  [Big W-Net](../models/big-wnet.md) train on it as DRIVE-AV;
  [OCULARNet](../models/ocularnet.md) and [OCULARNet-nano](../models/ocularnet-nano.md) include
  DRIVE in their training list; every model that trained on DRIVE has seen these pixels.
- **Below a model's measuring grid:** **Yes** — 565×584, below every grid in
  [MODELS.md](../MODELS.md), so scores are computed on upsampled images.
- **What it can answer:** comparability with the artery/vein literature, which is almost entirely
  reported on this dataset. Not generalisation.

## 7. Known defects

- The download link from the request form does not work in some browsers; fetching it with a
  command-line tool succeeds.

## 8. Notes

- Because "DRIVE-AV" and "RITE" name the same thing, a training-data list containing both looks
  broader than it is. This catalogue records it once, here, and cross-references from DRIVE.

---

**Links, licence and access last checked:** 2026-09-11
