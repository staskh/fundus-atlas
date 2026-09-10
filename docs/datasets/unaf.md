# UNAF

15 photographs with artery/vein annotation from Paraguay — one of only two South American
artery/vein collections known here, and the smallest dataset in this catalogue. Its value is
geographic: nothing else here represents a Paraguayan population, and every other A/V set comes from
Europe, China, North America or India.

## 1. What it is

- **Images:** 15, with diabetic retinopathy represented.
- **Collected at:** Universidad Nacional de Asunción, Paraguay.
- **Purpose:** published alongside artery/vein segmentation work rather than as a standalone dataset
  release.

## 2. Provenance

| | |
| --- | --- |
| Home | Published alongside the paper at [Physiological Measurement, DOI 10.1088/1361-6579/ad3d28](https://iopscience.iop.org/article/10.1088/1361-6579/ad3d28) |
| Download | **through the paper rather than a data repository.** In practice the images circulate through [PVBM](../projects/pvbm.md)'s dataset downloader, which fetches UNAF along with Crop_HRF and INSPIRE. Locate the authors' own archive before relying on it |
| Citation | Fhima J, Van Eijgen J, Billen Moulin-Romsée M-I, Brackenier H, Kulenovic H, Debeuf V, Vangilbergen M, Freiman M, Stalmans I, Behar JA. *LUNet: deep learning for the segmentation of arterioles and venules in high resolution fundus images.* Physiological Measurement 2024. DOI: [10.1088/1361-6579/ad3d28](https://doi.org/10.1088/1361-6579/ad3d28) |
| Licence | **Not established** — it depends where the authoritative archive lives, which was not resolved |
| Content | 15 images at 1444×1444 as redistributed |
| Annotations | Artery/vein segmentation |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1444×1444 as redistributed — whether this is the camera's native size or a rendition was not established |
| Microns per pixel | Unknown |
| Camera | Not stated |
| Field of view | 45° |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | Reference standard; reader count not stated | Native | — |
| Disease | Per eye | — | Diabetic retinopathy |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [PVBM](../projects/pvbm.md)'s `PVBMDataDownloader` redistributes it
  as one of three external test sets.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on it. [LUNet](../models/lunet.md) uses
  it as external test data, and [OCULARNet](../models/ocularnet.md) lists it as an in-distribution
  test set.
- **Below a model's measuring grid:** No.
- **What it can answer:** a first look at whether artery/vein performance transfers to a South
  American cohort. Fifteen images cannot support a per-dataset figure.

## 7. Known defects

- **Access and licence are both unresolved** (section 2). The images are easy to obtain through a
  third-party downloader and hard to obtain from an authoritative source with stated terms — the
  worst combination for reproducible work.

## 8. Notes

- Geographic coverage is the thinnest dimension of this whole catalogue: the models here are trained
  overwhelmingly on European and Chinese eyes. Fifteen Paraguayan photographs is not a solution, but
  it names the gap.

---

**Links, licence and access last checked:** 2026-09-11
