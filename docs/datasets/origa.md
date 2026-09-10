# ORIGA

650 photographs from a population-based cohort with optic disc and cup masks — and, rarely, **the
cup-to-disc ratio its own graders recorded**, published as a column alongside the masks. That makes
ORIGA the one dataset in this catalogue whose geometry can be checked against an independent
published number rather than only against itself.

## 1. What it is

- **Images:** 650 — 168 glaucomatous, 482 normal.
- **Collected at:** the **Singapore Malay Eye Study**, a population-based cohort, so the imaging is
  not selected for photogenic discs. Its 26% glaucoma rate reflects sampling for a benchmark rather
  than a screening prevalence.
- **Purpose:** an online database for glaucoma analysis, published with grader-recorded measurements.

## 2. Provenance

| | |
| --- | --- |
| Home | Historically distributed on request through the study; no reliable open host was established |
| Download | **no** from the authors. In practice it arrives inside the third-party Kaggle bundle [`arnavjain1/glaucoma-datasets`](https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets), which also carries [G1020](g1020.md) and REFUGE |
| Citation | Zhang Z, Yin FS, Liu J, Wong WK, Tan NM, Lee BH, Cheng J, Wong TY. *ORIGA-light: An online retinal fundus image database for glaucoma analysis and research.* IEEE EMBC 2010:3065–3068. DOI: [10.1109/IEMBS.2010.5626137](https://doi.org/10.1109/IEMBS.2010.5626137) |
| Licence | **Research use**, historically request-based. No Creative Commons grant was established, and the Kaggle bundle's licence field is the **uploader's**, not the study's |
| Content | 650 images, 2048 tall and 2426–2616 wide |
| Annotations | Optic disc and cup masks, **`ExpCDR`** (the graders' vertical cup-to-disc ratio), glaucoma label, eye side, an A/B subset split |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 2048 tall, 2426–2616 wide — mixed widths |
| Microns per pixel | Unknown — not published |
| Camera | Unknown make; the cohort's own retinal photography protocol |
| Field of view | Not stated |
| Centring | Disc-visible posterior pole |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Graders of the study | Native | Masks |
| Optic cup | Graders of the study | Native | Masks |
| Disease | One label per eye | — | Glaucoma 168 / normal 482 |
| Other labels | — | — | **`ExpCDR`**, the graders' vertical cup-to-disc ratio; eye side; an A/B subset split |

`ExpCDR` is the reason to reach for ORIGA. Measuring the vertical extents of the shipped masks
reproduces it closely — to within 0.001 on every image in checks run for this atlas — which means the
masks and the published ratio are consistent, and that a pipeline's own
[cup-to-disc ratio](../biomarkers/cup-to-disc-ratio.md) can be compared against a human-recorded
value rather than against another algorithm's mask.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established. Its usual distribution bundles it with G1020 and
  REFUGE, which is packaging, not shared photographs.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — ORIGA is **held out** of every
  model in this catalogue.
- **Below a model's measuring grid:** No.
- **What it can answer:** whether a computed cup-to-disc ratio agrees with a clinician's recorded
  one, on a population cohort. Nothing else here supports that check.

## 7. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 8. Notes

- The published ratio is the asset. A disc/cup model can be evaluated against masks anywhere; being
  able to evaluate the *biomarker* against a human's number is what makes this dataset worth the
  awkward access route.

---

**Links, licence and access last checked:** 2026-09-11
