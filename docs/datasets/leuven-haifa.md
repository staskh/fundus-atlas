# Leuven-Haifa (UZLF)

240 disc-centred photographs from the University Hospitals of Leuven, with arterioles and venules
drawn by a junior annotator and **corrected by a senior one** — so the test split preserves both,
which makes it the one public artery/vein dataset that can state a human agreement ceiling. It is
also [LUNet](../models/lunet.md)'s training set, and it carries a quality score and twelve published
vessel measurements.

Its cost is access: a signed data transfer agreement, and non-commercial terms.

## 1. What it is

- **Images:** 240, from 224 patients — both eyes in 16 of them.
- **Collected at:** University Hospitals Leuven (UZ Leuven), Belgium; published jointly with a group
  at the Technion in Haifa, which is where the name comes from.
- **Purpose:** retinal blood vessel segmentation and glaucoma diagnosis, at high resolution.

## 2. Original publication

- Van Eijgen J, Fhima J, Billen Moulin-Romsée M-I, Behar JA, Christinaki E, Stalmans I.
  *Leuven-Haifa High-Resolution Fundus Image Dataset for Retinal Blood Vessel Segmentation and
  Glaucoma Diagnosis.* Scientific Data 2024;11:257. DOI:
  [10.1038/s41597-024-03086-6](https://doi.org/10.1038/s41597-024-03086-6)

## 3. Access

- **Home:** KU Leuven Research Data Repository, DOI
  [10.48804/Z7SHGO](https://doi.org/10.48804/Z7SHGO)
- **Direct download:** **No — request, then a signed agreement.** Access is requested on the record
  page, after which KU Leuven's legal office draws up a **Data Transfer Agreement**; the images stay
  restricted until it is signed. The request asks for affiliation and intended research goals. A
  draft agreement is published on the record as a PDF, so the terms can be read before applying.
- **Arrives as:** about 407 MB once granted.

## 4. Licence

- **Images and annotations:** **custom terms, non-commercial only** — not a Creative Commons
  licence. The data may not be used by any party for a commercial purpose.
- **Restrictions worth knowing:** the agreement is with the institution, not a public grant, so
  redistribution is out of the question and access does not transfer between groups.

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | 1444×1444 |
| Microns per pixel | Unknown — not published |
| Camera | Zeiss Visucam 500 |
| Field of view | 30° |
| Centring | **Disc-centred** |
| Modality | Colour fundus photography |

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | **Two, kept separate in the test split** — a junior annotator's drawing and a senior's correction | Native | The only public A/V dataset here that preserves both, and therefore the only one that can measure human disagreement on arteries and veins |
| Quality | Scored per photograph | — | Produced with an automated quality network rather than by a grader |
| Disease | One label per eye | — | Glaucoma, in three categories, plus healthy |
| Other labels | — | — | Age, sex, and **twelve published vessel measurements** — tortuosity, fractal dimensions, branching |

## 7. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [OCULARNet](../models/ocularnet.md) uses these photographs in its
  training collection, listed there under the Leuven-Haifa name.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** [LUNet](../models/lunet.md) trains on it entirely —
  its `UZLF_TRAIN` / `UZLF_VAL` / `UZLF_TEST` splits *are* this dataset — and
  [OCULARNet](../models/ocularnet.md) includes it. Held out of the AutoMorph family and, as far as
  can be established, of [VascX](../models/vascx-artery-vein.md).
- **Below a model's measuring grid:** No. Note that LUNet resamples even these 1444 images to 1472
  before inference.
- **What it can answer:** two questions nothing else here can — held-out artery/vein accuracy against
  a **second reader**, and whether a pipeline's tortuosity and fractal dimension agree with the
  dataset's own published values for the same eyes.

## 9. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 10. Notes

- The published vessel measurements make this the most interesting dataset in the catalogue for
  [biomarker](../BIOMARKERS.md) comparison rather than segmentation comparison: the numbers, not just
  the masks, can be checked.
- The senior-correction design is worth copying. Most datasets publish a single consensus and discard
  the disagreement that would let anyone calibrate against it.

---

**Links, licence and access last checked:** 2026-09-11
