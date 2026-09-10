# DRIVE

40 photographs at 565×584 from a Dutch diabetic-retinopathy screening programme, with a manual vessel
segmentation on each — the oldest and most cited vessel-segmentation benchmark in the field, and by
today's standards a very small, very low-resolution one. Two decades of published Dice scores are
measured on it, which is its main value and also its main trap: it is training data for almost every
model in this catalogue, and it is smaller than the grid any of them measure on.

## 1. What it is

- **Images:** 40 — 20 training, 20 test, as split by the authors. 33 show no diabetic retinopathy and
  7 show mild early changes.
- **Collected at:** a diabetic-retinopathy screening programme in the Netherlands, from 400 subjects
  aged 25 to 90.
- **Purpose:** to provide a common reference standard for comparing vessel-segmentation methods.

## 2. Original publication

- Staal J, Abràmoff MD, Niemeijer M, Viergever MA, van Ginneken B. *Ridge-based vessel segmentation
  in color images of the retina.* IEEE Transactions on Medical Imaging 2004;23(4):501–509. DOI:
  [10.1109/TMI.2004.825627](https://doi.org/10.1109/TMI.2004.825627)

## 3. Access

- **Home:** <https://drive.grand-challenge.org/>
- **Direct download:** **Registration required** — the data sits behind a grand-challenge account,
  and the historical direct URL at `isi.uu.nl` no longer serves the archive.
- **Arrives as:** a zip with `training/` and `test/` trees, each holding images, manual segmentations
  and field-of-view masks.
- Third-party mirrors exist on Kaggle and elsewhere. They are convenient and they are not the
  authors' distribution; the registration terms are what govern use.

## 4. Licence

- **Images:** research use, subject to the terms accepted at registration. **No open licence** —
  DRIVE predates Creative Commons practice in this field.
- **Annotations:** same.
- **Restrictions worth knowing:** redistribution is not granted, which is why the mirrors are
  awkward rather than helpful.

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | 565×584 (the field-of-view crop of a 768×584 capture) |
| Microns per pixel | Unknown — not published |
| Camera | Canon CR5 non-mydriatic 3CCD |
| Field of view | 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | One per image on the training split; **two observers on the test split**, kept separate | Native | The second observer is the reason DRIVE can state a human agreement ceiling |
| Field-of-view mask | — | Native | Supplied per image |

## 7. Inheritance

- **Reuses images from:** No shared images established — DRIVE is an original collection.
- **Its images are reused by:** **[RITE](rite.md) is DRIVE** — the same 40 photographs with an
  artery/vein reference standard drawn on them, distributed by a different group under a different
  name. Also annotated again by [REYIA](reyia.md). A paper listing DRIVE and RITE as two datasets has
  one camera's worth of images.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  (in `ALL-SIX`), [LWNet](../models/lwnet.md), [BF-Net](../models/bf-net.md) and
  [Big W-Net](../models/big-wnet.md) (via DRIVE-AV, the RITE labels),
  [OCULARNet](../models/ocularnet.md) and [OCULARNet-nano](../models/ocularnet-nano.md). **In-sample
  for essentially every vessel model here.**
- **Below a model's measuring grid:** **Yes, and this matters.** At 565×584 it is smaller than every
  grid in [MODELS.md](../MODELS.md) — 912 for vessels, 720 for artery/vein, 512 for disc/cup, 1024
  and up for the newer models. Scores here are computed on **upsampled** images, which is a
  different regime from every other dataset in this catalogue, where the image is downsampled.
- **What it can answer:** comparability with two decades of literature. Not generalisation, and not
  performance at native resolution.

## 9. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 10. Notes

- The 565×584 size is not the sensor's output: the original captures are 768×584 and the released
  images are cropped to the field of view. Papers occasionally quote either figure.
- Its ubiquity is self-reinforcing: because everyone reports DRIVE, everyone trains on DRIVE, so a
  DRIVE score is now closer to a reproducibility check than to an evaluation.

---

**Links, licence and access last checked:** 2026-09-11
