# RAVIR

42 released images, 23 of them with artery and vein segmentations — and **not colour fundus
photographs**: they are infrared reflectance images from a Heidelberg Spectralis. That makes RAVIR a modality test rather
than a performance test: it asks whether an artery/vein model fails safely on imagery it has never
seen, which nothing else in this catalogue asks.

## 1. What it is

- **Images:** 46 by the paper's count (26 training, 20 test); 42 in the release (23 training with
  masks, 19 test without) — see section 7.
- **Collected at:** the UCLA Stein Eye Institute's imaging database, Los Angeles. The paper says 23
  of its 46 images are normal and 23 show retinal pathology, with diabetic and hypertensive
  retinopathy represented.
- **Purpose:** semantic segmentation and quantitative analysis of arteries and veins in infrared
  reflectance imaging.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://ravirdataset.github.io/data/> |
| Download | **direct, no registration** — `RAVIR Dataset.zip`, 14,551,034 bytes, from the Google Drive link on the home page: <https://drive.google.com/file/d/1ZlZoSStvE9VCRq3bJiGhQH931EF0h3hh/view?usp=sharing>. No sign-in needed (checked 2026-10-14). The home page states that downloading means agreeing to its data usage terms |
| Citation | Hatamizadeh A, Hosseini H, Patel N, Choi J, Pole CD, Hoeferlin CM, Schwartz SD, Terzopoulos D. *RAVIR: A Dataset and Methodology for the Semantic Segmentation and Quantitative Analysis of Retinal Arteries and Veins in Infrared Reflectance Imaging.* IEEE Journal of Biomedical and Health Informatics 2022;26(7):3272–3283. DOI: [10.1109/JBHI.2022.3163352](https://doi.org/10.1109/JBHI.2022.3163352) |
| Licence | **CC BY-NC-SA 4.0** — non-commercial use only, derivatives under the same licence — as stated on the home page, which also requires citing the paper above and Hatamizadeh's 2020 UCLA dissertation |
| Content | 42 images at 768×768: 23 training, 19 test |
| Annotations | Artery and vein segmentations for the 23 training images; the test masks are withheld for the [challenge leaderboard](https://ravir.grand-challenge.org/) |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 768×768 |
| Microns per pixel | **12.5, published** on the home page ("each pixel … has a reference length of 12.5 microns") |
| Camera | Heidelberg Spectralis |
| Field of view | 30°. **The whole square frame is the field**: there is no circular aperture and no black border (under 1% near-black pixels in any image, checked 2026-10-14), so nothing needs cropping to a field-of-view circle |
| Centring | Disc-centred |
| Modality | **Infrared reflectance (815 nm scanning laser ophthalmoscopy) — not colour fundus photography.** Single-channel greyscale PNGs. Vessels appear with inverted, higher-contrast appearance and no colour information at all, so artery/vein separation cannot rely on the colour cues every model here was trained on |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | Reference standard | Native, 768×768 | One greyscale PNG per image: background 0, artery 128, vein 255 (the challenge page writes "256", which an 8-bit image cannot hold). Test masks withheld for the leaderboard, as with [RETA](reta.md) |
| Disease | — | — | The paper describes the mix (diabetic and hypertensive retinopathy among 23 pathological images); **the release carries no per-image disease label** |
| Optic disc, by [OCULAR](../projects/ocularnet.md) | OCULAR's authors | OCULAR's 1024×1024 copy | No field-of-view mask: OCULAR treats these images as already cropped to the field. A Google Drive folder that asks for a Google sign-in (checked 2026-10-12) — not openly downloadable, and no licence stated |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on it. [OCULARNet](../models/ocularnet.md)
  uses RAVIR as a **far out-of-distribution test set**, which is exactly the right use.
- **Below a model's measuring grid:** Yes at 768 relative to the 912 and 1024 grids, though the
  modality difference matters more than the size.
- **What it can answer:** whether an artery/vein model degrades gracefully or catastrophically off
  its modality. A poor score here is not a failure of the model on its intended input.

## 7. Known defects

- Test masks are withheld, so only the 23 training images can be scored locally.
- **Counts differ from the paper** (our finding, 2026-10-14): the paper describes 46 images, 26
  training and 20 test; the release holds 23 training and 19 test. The challenge page says
  `IR_Case_002` was removed from the test set; nothing found explains the three missing training
  images.
- The modality is the point and also the trap: pooling RAVIR with colour datasets produces a number
  that means nothing.

## 8. Notes

- Infrared reflectance is standard on OCT devices, so images like these are abundant in clinics even
  though almost no fundus model is trained for them. That gap is worth measuring, and this is the
  only dataset here that measures it.

---

**Links, licence and access last checked:** 2026-10-14
