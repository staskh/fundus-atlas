# STARE

20 photographs with vessel segmentations from **two independent observers**, published in 2000 — the
oldest dataset in this catalogue, and one of the two (with [DRIVE](drive.md)) on which two decades of
vessel-segmentation literature is measured. It is small, low-resolution and training data for most
models here, but the second observer makes it one of the few sets that can state a human agreement
ceiling.

## 1. What it is

- **Images:** 20 for vessel segmentation, drawn from a larger collection of 397 photographs the
  project distributes for other tasks. Ten of the twenty show pathology.
- **Collected at:** the STructured Analysis of the Retina project, University of California San
  Diego and Shiley Eye Center.
- **Purpose:** to support automated diagnosis of retinal disease; the vessel subset became the
  benchmark.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://cecas.clemson.edu/~ahoover/stare/> |
| Download | **direct, no registration** — individual files from the project pages |
| Citation | Hoover AD, Kouznetsova V, Goldbaum M. *Locating blood vessels in retinal images by piecewise threshold probing of a matched filter response.* IEEE Transactions on Medical Imaging 2000;19(3):203–210. DOI: [10.1109/42.845178](https://doi.org/10.1109/42.845178) |
| Licence | **Not stated.** No licence accompanies the distribution; it has been used freely in research for 25 years, which is convention rather than permission |
| Content | 20 images at 700×605 for the vessel task |
| Annotations | Two independent observers' vessel segmentations, kept separate |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 700×605 |
| Microns per pixel | Unknown — not published |
| Camera | TopCon TRV-50 |
| Field of view | 35° — the narrowest in this catalogue |
| Centring | Mixed |
| Modality | Colour fundus photography, digitised from slides |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **Two, kept separate** — Adam Hoover's set is the one used as ground truth, Valentina Kouznetsova's as a human baseline | Native | The second set is what lets a model's score be compared against a person's |
| Disease | Per image | — | Ten of the twenty show pathology |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md),
  as part of AutoMorph's `ALL-SIX` combination. In-sample for that model.
- **Below a model's measuring grid:** **Yes** — 700×605 sits below the 912 vessel grid and every
  larger one, so scores here are computed on upsampled images.
- **What it can answer:** comparability with the oldest literature, and — through the second
  observer — what human disagreement on vessel tracing looks like.

## 7. Known defects

- The images are digitised from film slides, so their noise characteristics differ from every
  digital-native dataset here. A model that does well on STARE has not been shown to do well on a
  modern camera.

## 8. Notes

- 35° is unusually narrow, which means the vessels occupy more pixels per degree than in a 45° set of
  the same size. Field of view, not just resolution, decides what a vessel-width figure means.

---

**Links, licence and access last checked:** 2026-09-11
