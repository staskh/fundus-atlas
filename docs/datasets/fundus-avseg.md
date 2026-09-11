# Fundus-AVSeg

100 photographs from routine clinical work at Shenzhen Eye Hospital with pixel-level artery/vein
annotation, published in 2025 — which makes it one of the few artery/vein datasets **newer than the
models in this catalogue**, and therefore one of the few that can evaluate them rather than having
trained them. It also carries per-image quality labels, which almost nothing else with A/V
annotation does.

## 1. What it is

- **Images:** 100 — 40 normal, 20 diabetic retinopathy, 20 age-related macular degeneration, 20
  glaucoma.
- **Collected at:** Shenzhen Eye Hospital, China, from routine clinical work rather than a research
  protocol.
- **Purpose:** an artery/vein segmentation dataset spanning several diseases and two cameras.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, <https://figshare.com/articles/dataset/Fundus-AVSeg/27938034> |
| Download | **direct, no registration** — about 213 MB |
| Citation | *A Fundus Image Dataset for AI-based Artery-Vein Vessel Segmentation.* Scientific Data, 2025. DOI: [10.1038/s41597-025-05381-2](https://doi.org/10.1038/s41597-025-05381-2) |
| Licence | **CC BY 4.0** — with [GAVE](gave.md), one of the two most permissive artery/vein datasets in this catalogue |
| Content | 100 images — 21 at 2656×1992 and 79 at 1280×1280 |
| Annotations | Pixel-level artery/vein standard, per-image quality label, disease class, eye side |

The archive holds `image/` and `annotation/` folders, the A/V standard as RGB PNGs sharing each
image's filename stem.

## 3. The images

Two subcollections, by sensor. The archive does not say which camera took which photograph, and
states **no field angle for either**, so the sensor size is the only separator available.

### 3.1 The large set — 21 images

| | |
| --- | --- |
| Resolution (pixels) | 2656×1992 |
| Microns per pixel | Unknown — not published |
| Camera | Zeiss VISUCAM 200 or Canon (the archive names both, without attributing images) |
| Field of view | **Not stated** |
| Centring | Mixed |
| Modality | Colour fundus photography |

### 3.2 The square set — 79 images

| | |
| --- | --- |
| Resolution (pixels) | 1280×1280 |
| Microns per pixel | Unknown |
| Camera | As above |
| Field of view | **Not stated** |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | Pixel-level, one standard | The size stated per image | The vessel mask is **derived from** the A/V labels rather than annotated independently — so it cannot be used to cross-check them without circularity |
| Quality | Per photograph | — | 83 high-quality, 17 low-quality |
| Disease | One label per eye | — | Four classes |
| Other labels | — | — | Eye side |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** **None established.** Published after the AutoMorph
  family's artery/vein model, and absent from [OCULARNet](../models/ocularnet.md)'s and
  [VascX](../models/vascx-artery-vein.md)'s stated training lists — though VascX's "more than fifteen
  published datasets" is not enumerated per dataset, so treat that one as unverified rather than
  confirmed held out.
- **Below a model's measuring grid:** No — 1280 and 2656 both sit at or above the grids in
  [MODELS.md](../MODELS.md).
- **What it can answer:** held-out artery/vein accuracy, stratified by disease and — unusually — by
  image quality, on a permissive licence.

## 7. Known defects

- Neither camera nor field angle is attributed per image, so the two subcollections can be separated
  by size but not by device.
- The derived vessel mask is not an independent annotation; a paper reporting both vessel and A/V
  agreement on this dataset is reporting one measurement twice.

## 8. Notes

- Small, but permissively licensed, quality-labelled and genuinely held out — a rare combination,
  and the reason to prefer it over [RITE](rite.md) or [HRF](hrf.md) for an artery/vein evaluation.

---

**Links, licence and access last checked:** 2026-09-11
