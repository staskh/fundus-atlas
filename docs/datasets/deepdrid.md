# DeepDRiD

Around 2,256 photographs from an ISBI 2020 challenge, with diabetic-retinopathy grades, **dual-view
pairs of the same eye**, and quality scores from three readers — overall quality plus artefact,
clarity and field-definition subscores. It also carries a separate ultra-wide-field split for one of
its sub-challenges.

## 1. What it is

- **Images:** on the order of 2,256 regular fundus photographs, in training, validation and
  unlabelled online-evaluation splits, plus ultra-wide-field frames for a third sub-challenge.
- **Collected at:** Chinese clinical sites, released for the ISBI 2020 Diabetic Retinopathy
  challenge.
- **Purpose:** DR grading, image-quality assessment and transfer learning, with two views per eye.

## 2. Provenance

| | |
| --- | --- |
| Home | GitHub, [deepdrdoc/Deep-Diabetic-Retinopathy-Image-Dataset-DeepDRiD-](https://github.com/deepdrdoc/Deep-Diabetic-Retinopathy-Image-Dataset-DeepDRiD-) (also mirrored at [AIMedLab/DeepDRiD](https://github.com/AIMedLab/DeepDRiD)) |
| Download | **direct, no registration** — from the repository releases: training, validation and an unlabelled online-evaluation set |
| Citation | The ISBI 2020 DeepDRiD challenge report (Liu et al.); confirm the exact citation from the repository README at download time |
| Licence | **CC BY-SA 4.0** — attribution and **share-alike**, so derivatives of the dataset carry the same obligation. The only share-alike dataset in this catalogue |
| Content | About 2,256 regular fundus images plus an ultra-wide-field split |
| Annotations | DR grades, overall image quality plus artefact, clarity and field-definition subscores, from two ophthalmologists confirmed or revised by a senior third |

## 3. The images

### 3.1 Regular fundus photographs — about 2,256 images

| | |
| --- | --- |
| Resolution (pixels) | Mixed |
| Microns per pixel | Unknown |
| Camera | Not stated uniformly |
| Field of view | Not stated |
| Centring | **Dual view per eye** — one macula-centred and one disc-centred photograph of the same eye |
| Modality | Colour fundus photography |

### 3.2 Ultra-wide-field split

| | |
| --- | --- |
| Resolution (pixels) | Mixed |
| Microns per pixel | Unknown |
| Camera | Ultra-wide-field device |
| Field of view | Ultra-wide |
| Centring | Not applicable |
| Modality | **Ultra-wide-field imaging, not standard colour fundus photography** |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | **Two ophthalmologists, confirmed or revised by a senior third** | — | Overall grade plus artefact, clarity and field-definition subscores |
| Disease | As above | — | DR grades, per image and per patient |
| Other labels | — | — | The dual-view pairing, which allows within-eye agreement to be measured |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of both quality models
  here.
- **Below a model's measuring grid:** Mixed.
- **What it can answer:** two things nothing else does — whether a quality model agrees with itself
  across two views of one eye, and whether its errors track the artefact, clarity and field
  subscores separately.

## 7. Known defects

- Counts vary between the challenge materials and later papers; 2,256 is the figure later work
  cites for the regular split.
- **Share-alike is easy to overlook.** Anything published that qualifies as a derivative of this
  dataset inherits CC BY-SA — a real constraint if it is mixed into a corpus meant to be released
  under something else.

## 8. Notes

- The dual-view design is the underused asset here: two photographs of one eye should produce the
  same biomarker, and this is the only dataset in the catalogue that lets that be tested directly.

---

**Links, licence and access last checked:** 2026-09-11
