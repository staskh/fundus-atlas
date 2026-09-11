# mBRSET

5,164 photographs taken with **handheld** cameras from 1,291 Brazilian patients — the portable-device
companion to [BRSET](brset.md), and the only handheld collection of this size in the catalogue.
Handheld images are what screening outside a clinic actually looks like: more variable framing,
illumination and focus than any tabletop dataset here.

## 1. What it is

- **Images:** 5,164, from 1,291 patients.
- **Collected at:** Brazilian screening settings, published through PhysioNet.
- **Purpose:** a handheld-camera counterpart to BRSET, for machine learning on portable-device
  photographs.

## 2. Provenance

| | |
| --- | --- |
| Home | PhysioNet, <https://physionet.org/content/mbrset/1.0/> |
| Download | **credentialed access** — the same wall as BRSET: CITI training, then a signed Data Use Agreement |
| Citation | Cite the PhysioNet record and the accompanying mBRSET paper listed on that page |
| Licence | **PhysioNet Credentialed Health Data License 1.5.0** plus Data Use Agreement 1.5.0. **Not CC BY**; redistribution restricted |
| Content | 5,164 handheld photographs |
| Annotations | Diabetic-retinopathy grades, quality assessment, demographics |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Mixed, by handheld device |
| Microns per pixel | Unknown |
| Camera | Handheld fundus cameras |
| Field of view | Not stated uniformly; handheld devices typically 40–45° |
| Centring | Mixed and variable |
| Modality | Colour fundus photography, handheld |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Per photograph | — | The reason the dataset matters for the quality models here |
| Disease | Per eye | — | Diabetic-retinopathy grades |
| Other labels | — | — | Demographics, as in BRSET |

## 5. Inheritance

- **Reuses images from:** No shared images established. It is a **companion** to BRSET, not a subset:
  different cameras, different patients.
- **Its images are reused by:** [FunPiQ](funpiq.md) samples from it; [REYIA](reyia.md) includes
  mBRSET photographs in its nine-source compilation.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established directly. Note that REYIA, which
  contains mBRSET photographs, is a training set for nothing here but shares images with several.
- **Below a model's measuring grid:** Varies by device.
- **What it can answer:** whether a quality gate trained on tabletop screening photographs rejects
  handheld images the way a clinician would — the most realistic domain shift in this catalogue for
  the quality models.

## 7. Known defects

- Same credentialing obstacle as BRSET.
- Device metadata is thinner than for tabletop collections, so a per-camera analysis is not
  straightforwardly available.

## 8. Notes

- Handheld imaging is where fundus photography is growing fastest, and this is the only dataset here
  that represents it at scale. A model that works only on tabletop images will not say so on any
  other entry in this catalogue.

---

**Links, licence and access last checked:** 2026-09-11
