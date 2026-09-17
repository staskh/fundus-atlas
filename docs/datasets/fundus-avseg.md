# Fundus-AVSeg

100 photographs from routine clinical work at Shenzhen Eye Hospital with pixel-level artery/vein
annotation, published in 2025. It carries per-image quality labels, which almost nothing else with
artery/vein annotation does, and a permissive licence.

**It is not held out.** An earlier version of this page called it newer than the models catalogued
here and therefore able to evaluate them; that is wrong. [OCULARNet](../models/ocularnet.md)'s own
README tabulates Fundus-AVSeg among its training datasets, checked against the repository on
2026-09-17. Section 6 has what that leaves it good for.

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

### 2.1 How to fetch

```bash
uv run python -m datasets.fundus_avseg                      # downloads and builds 512 and 1024
uv run python -m datasets.fundus_avseg --sizes 512,768,1024
uv run python -m datasets.fetch_um_resolution --dataset fundus-avseg
```

One 213 MB zip from figshare, unattended. It builds 100 photographs with their **artery/vein map** as
three binary masks at native resolution — `artery`, `vein`, and `vessels` for their union —
translated from the archive's red, blue, green and white. **A crossing is in both the artery and the
vein mask**, being one vessel over another rather than a third kind; the 
white pixels, where the annotator marked a vessel without saying which kind, are in `vessels` and in
neither of the others.

The annotations are written at **native only**. The photograph and its field-of-view mask are
resized to 512 and 1024 because that is what a model is handed; the answer is scored in the frame
the annotator drew in. The authors' `training.txt` and `testing.txt` become the
`split` column (80 train, 20 test), and `metadata.xlsx` supplies the eye side, the disease and the
quality grade.

**The `vessels` mask is derived**, being that union rather than an independent tracing — which is
also true of the vessel mask the dataset itself publishes (section 7). A model scored against both
it and the artery/vein masks has been scored twice against one annotation, and the second score is
not corroboration.

Two dataset-specific columns:

| Column | Meaning |
| --- | --- |
| `published_quality` | The authors' own grade, verbatim: `High-quality` or `Low-quality` |

The authors publish no microns-per-pixel scale and state no field angle, so the second command is
**required** to finish the store: it measures each sensor size separately — 10.012 µm/px for the 79
square photographs, 6.105 for the 21 large ones.

The store's `subset` column separates the two sensor sizes, `square` and `large`, which is the only
separator the archive offers: it names a Zeiss VISUCAM and a Canon without saying which photograph
came from which.

## 3. The images

Two subcollections, by sensor. The archive does not say which camera took which photograph, and
states **no field angle for either**, so the sensor size is the only separator available.

### 3.1 The large set — 21 images

| | |
| --- | --- |
| Resolution (pixels) | 2656×1992 |
| Microns per pixel | Not published. **Inferred: 6.105 µm/px** — from the median optic disc of 21 photographs, [evidence](../../results/um_resolution/fundus-avseg.json). Good to roughly a tenth (§9 of the `fetch-um-resolution` skill); a camera scale, not a per-eye calibration |
| Camera | Zeiss VISUCAM 200 or Canon (the archive names both, without attributing images) |
| Field of view | **Not stated** |
| Centring | Mixed |
| Modality | Colour fundus photography |

### 3.2 The square set — 79 images

| | |
| --- | --- |
| Resolution (pixels) | 1280×1280 |
| Microns per pixel | Not published. **Inferred: 10.012 µm/px** — from the median optic disc of 32 photographs, [evidence](../../results/um_resolution/fundus-avseg.json). Good to roughly a tenth (§9 of the `fetch-um-resolution` skill); a camera scale, not a per-eye calibration |
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

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) — their shared README lists Fundus-AVSeg with 100
  images at 1280×1280, so a score for either model on this dataset is **in-sample**. It is held out
  of [BF-Net](../models/bf-net.md), which the AutoMorph family runs, and of
  [LUNet](../models/lunet.md). [VascX](../models/vascx-artery-vein.md) enumerates nothing, so it is
  `unknown` here as everywhere.
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

- Small, permissively licensed and quality-labelled — the quality labels are the rare part, and they
  make it the one artery/vein dataset here where accuracy can be read against how good the
  photograph is. It is **not** the held-out dataset this page once claimed: for a genuinely
  uncontaminated artery/vein evaluation of every model here, [RAV](rav.md) is the candidate, being
  absent from every stated training list.

---

**Links, licence and access last checked:** 2026-09-17
