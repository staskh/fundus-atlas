# RIM-ONE DL

485 photographs from three Spanish hospitals with optic disc and cup segmentations, published with a
deliberate **hospital-based split**: train on one hospital's images, test on the other two. That
design is rare and valuable — it measures the domain shift that actually breaks deployed models,
rather than a random split's optimistic estimate.

## 1. What it is

- **Images:** 485 — 313 normal, 172 glaucomatous.
- **Collected at:** Hospital Universitario de Canarias, Hospital Universitario Miguel Servet, and
  Hospital Clínico San Carlos, Spain.
- **Purpose:** a unified, deep-learning-ready reworking of the earlier RIM-ONE releases, with
  reference segmentations and evaluation splits.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://github.com/miag-ull/rim-one-dl> |
| Download | **direct, no registration** — images, reference segmentations and the authors' trained weights are three separate downloads linked from the README |
| Citation | Fumero Batista FJ, Diaz-Aleman T, Sigut J, Alayon S, Arnay R, Angel-Pereira D. *RIM-ONE DL: A Unified Retinal Image Database for Assessing Glaucoma Using Deep Learning.* Image Analysis and Stereology 2020;39(3):161–167. DOI: [10.5566/ias.2346](https://doi.org/10.5566/ias.2346) |
| Licence | **Research and educational use, free of charge, no permission needed** — the authors' own wording. Not a standard licence, and not a grant of commercial use |
| Content | 485 images |
| Annotations | Optic disc and cup reference segmentations; two published partitions |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Not stated on the distribution page |
| Microns per pixel | Unknown |
| Camera | Not stated per hospital |
| Field of view | Not stated |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Reference segmentation; reader count not clearly stated | Native | The earlier RIM-ONE releases carried multiple experts; how that carries into RIM-ONE DL is unclear from the distribution |
| Optic cup | As above | Native | — |
| Disease | Per eye | — | Normal 313 / glaucoma 172 |
| Other labels | — | — | Two partitions: a random split, and a **hospital split** — train on Canarias, test on the other two |

## 5. Inheritance

- **Reuses images from:** the earlier **RIM-ONE r1, r2 and r3** releases, which it unifies and
  re-partitions. Anyone comparing against a paper that used RIM-ONE r3 is looking at overlapping
  photographs under a different name.
- **Its images are reused by:** None established. Note that [BEAL](../models/beal.md) and
  [ISFA](../models/isfa.md) both use **RIM-ONE-r3** as an unlabelled target domain.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on RIM-ONE DL itself, but its r3
  ancestor is the target domain for BEAL and ISFA — so those two have seen a subset of these
  photographs.
- **Below a model's measuring grid:** Unknown, since the resolution is not stated.
- **What it can answer:** cross-hospital generalisation with a split the authors designed for it —
  the closest thing in this catalogue to a deployment test.

## 7. Known defects

- **Resolution is not stated** by the distributor, which is unusual and makes grid comparisons
  guesswork until the archive is opened.
- The relationship to the earlier RIM-ONE releases means "RIM-ONE" in a paper can mean any of four
  things.

## 8. Notes

- The hospital split is the reason to use it. A random split over three hospitals measures
  interpolation; this one measures transfer, and the gap between the two numbers is the interesting
  result.

---

**Links, licence and access last checked:** 2026-09-11
