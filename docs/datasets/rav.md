# RAV (Rotterdam Artery-Vein)

206 photographs from the Rotterdam Study with artery and vein annotation, published by the group
behind [VascX](../projects/vascx.md) — which makes it the dataset most likely to be **in-sample for
VascX** and held out of everything else. It is drawn from a population cohort of adults over 40
rather than a clinic series, and it is deliberately mixed in image quality.

Its licence is stated twice, and the two statements contradict each other.

## 1. What it is

- **Images:** 206, already cropped to the circular field and resized to 1024×1024.
- **Collected at:** the **Rotterdam Study** — four population cohorts of adults aged 40 and over —
  with oversampling from the AMD-Life and MYST studies. Annotated by the EyeNED Reading Center.
- **Purpose:** artery/vein reference data for population-scale retinal vascular analysis.

## 2. Provenance

| | |
| --- | --- |
| Home | DataverseNL, DOI [10.34894/9OIMWY](https://doi.org/10.34894/9OIMWY) — [record](https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/9OIMWY) |
| Download | **direct, no registration** for the public 206. Additional images exist under a separate agreement on request |
| Citation | Vargas Quiros JD, Liefers B, van Garderen KA, Vermeulen JP, EyeNED Reading Center, Klaver CCW. *Rotterdam artery-vein segmentation (RAV) dataset.* [arXiv:2512.17322](https://arxiv.org/abs/2512.17322), 2025 |
| Licence | **CC BY-NC 4.0 — attribution, non-commercial**, per the authors' own README inside the archive. ⚠️ **DataverseNL's structured licence field on the same record says `CC0-1.0`**, which would waive both conditions. See below |
| Content | 206 images at 1024×1024, pre-cropped and resized |
| Annotations | Artery/vein segmentation, with mixed image quality by design |

**The licence is stated twice and the two disagree.** The authors' README says CC BY-NC 4.0; the
repository's own metadata field says CC0-1.0 — public domain, no attribution, no non-commercial
clause. Nothing available settles which the depositors meant, so treat the **stricter** statement as
binding: a non-commercial clause written by the authors is not waived by a metadata field.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1024×1024 — **the authors' rendition**, cropped to the circular field and resized, not a camera native |
| Microns per pixel | Unknown — not published |
| Camera | Rotterdam Study protocol devices; not stated per image |
| Field of view | Not stated per image |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | EyeNED Reading Center | 1024×1024 | — |
| Quality | — | — | **Mixed on purpose** — the selection includes poor-quality photographs rather than excluding them, which is unusual and useful |

## 5. Inheritance

- **Reuses images from:** the **Rotterdam Study** image archive, which is not itself a public dataset.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** none stated explicitly, but
  [VascX](../models/vascx-artery-vein.md) trains on "more than fifteen published annotated datasets
  with colour-fundus images from Dutch studies, principally the Rotterdam Study" — these
  photographs' own cohort, annotated by the same group. **Treat RAV as in-sample for VascX unless
  its authors say otherwise**, and as held out of the AutoMorph family.
- **Below a model's measuring grid:** No, at 1024 — which is also VascX's own grid.
- **What it can answer:** artery/vein accuracy on a population cohort rather than a clinic series,
  across a realistic quality range. For VascX, it answers a regression question rather than a
  generalisation one.

## 7. Known defects

- **Contradictory licence statements** (section 2), unresolved.
- The images are a pre-processed rendition, so a measurement in pixels is on the authors' grid, not
  the camera's.

## 8. Notes

- Population cohorts and clinic series differ systematically — in age, in disease prevalence and in
  photograph quality. RAV is the only artery/vein dataset here from a population cohort, which makes
  it valuable and makes its likely in-sample status for VascX unfortunate.

---

**Links, licence and access last checked:** 2026-09-11
