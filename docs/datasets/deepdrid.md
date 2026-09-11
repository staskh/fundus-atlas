# DeepDRiD

**2,000** photographs from an ISBI 2020 challenge, with diabetic-retinopathy grades, **dual-view
pairs of the same eye**, and quality scores — an overall grade plus artefact, clarity and
field-definition subscores. It also carries a separate 256-image ultra-wide-field split for one of
its sub-challenges.

## 1. What it is

- **Images:** **2,000 regular fundus photographs** — 1,200 training, 400 validation and 400
  online-evaluation — from **500 patients**, two photographs of each of 1,000 eyes. A further 256
  ultra-wide-field frames belong to a third sub-challenge and are counted separately.
- **Labels:** all three splits are labelled. The evaluation split was released unlabelled for the
  competition and its grades were published afterwards, in July 2022, as two spreadsheets.
- **Collected at:** Chinese clinical sites, released for the ISBI 2020 Diabetic Retinopathy
  challenge.
- **Purpose:** DR grading, image-quality assessment and transfer learning, with two views per eye.

## 2. Provenance

| | |
| --- | --- |
| Home | GitHub, [deepdrdoc/Deep-Diabetic-Retinopathy-Image-Dataset-DeepDRiD-](https://github.com/deepdrdoc/Deep-Diabetic-Retinopathy-Image-Dataset-DeepDRiD-) (also mirrored at [AIMedLab/DeepDRiD](https://github.com/AIMedLab/DeepDRiD)) |
| Download | **direct, no registration** — the photographs are committed to the repository itself rather than attached to a release, so the route is a clone (or a subtree checkout) at a pinned commit |
| Citation | Liu R, Wang X, Wu Q, Dai L, Fang X, Yan T, et al. *DeepDRiD: Diabetic Retinopathy—Grading and Image Quality Estimation Challenge.* Patterns 2022;3(6):100512. DOI: [10.1016/j.patter.2022.100512](https://doi.org/10.1016/j.patter.2022.100512) |
| Licence | **CC BY-SA 4.0** — attribution and **share-alike**, so derivatives of the dataset carry the same obligation. The only share-alike dataset in this catalogue |
| Content | 2,000 regular fundus images plus a 256-image ultra-wide-field split |
| Annotations | DR grades, overall image quality plus artefact, clarity and field-definition subscores, from two ophthalmologists confirmed or revised by a senior third. **Only the final value is published**, not the individual readers', so reader disagreement cannot be measured here |
| Provenance of the photographs | Three screening programmes, named per image in a companion CSV added in April 2022: the Niching Diabetes Screening Project (`Nicheng`, 1,140 of the 1,600 labelled train and validation images), the Nationwide Screening for Complications of Diabetes (`Nation`, 36) and the Shanghai Diabetic Complication Screening Project (`Shanghai`, 24). The evaluation split is not attributed |

### 2.1 How to fetch

```bash
uv run python -m datasets.deepdrid                          # clones and builds 512 and 1024
uv run python -m datasets.deepdrid --sizes 512,720,1024     # any sizes a model needs
```

- **Downloads:** a subtree checkout of the repository at commit `56d8af71`, taking only
  `regular_fundus_images` — about 2 GB. No account, no form; the commit is what pins the bytes,
  since a repository has no archive to checksum.
- **Builds:** the photograph and its field-of-view mask, at `native/` plus each requested size.
  There are no vessel, artery/vein or disc annotations in this dataset to build.
- **Not built:** the ultra-widefield sub-challenge (sub-challenge 3), 256 images left in the
  repository. It is a different instrument, and pooling a 200° frame with these would make every
  measurement in the store mean two things at once.
- **Quality:** `quality` is the authors' own overall grade mapped to the atlas's vocabulary —
  their `1` ("good enough for the diagnosis of retinal diseases") becomes `good` and their `0`
  becomes `bad`, with `quality_source` recording that it is theirs rather than ours. The three
  subscores are kept as columns of their own, unmapped.
- **Extra columns:** `overall_quality` (the authors' 0/1, verbatim), `artifact` (0 none, then 1, 4,
  6, 8, 10 by how much of the frame is covered), `clarity` (1–10), `field_definition` (1–10),
  `patient_dr_level` (the grade from both eyes together), `view` (which photograph of this eye) and
  `screening_project` (`Nicheng`, `Shanghai`, `Nation`, or empty for the evaluation split).
- **Grouping:** `patient` is the dataset's own id and is unique across all three splits, so a
  by-person split is possible. `eye` is read from the filename suffix the authors document
  (`_l` left, `_r` right). `visit` is empty: the dataset photographs each patient once.
- **Peculiarities:** the labels arrive in three different shapes — a CSV per split for training and
  validation, a second CSV naming the screening project, and two spreadsheets for the evaluation
  split whose grades were published two years after the competition. `disease` is the grade for
  *this* eye, taken from whichever of the two per-eye columns applies.

## 3. The images

### 3.1 Regular fundus photographs — 2,000 images

| | |
| --- | --- |
| Resolution (pixels) | Six sizes: 1736×1824 (1,294 images), 1976×1984 (660), 1734×1821 (18), 2230×1725 (10), 2232×1727 (10), 1592×1728 (8). Every one is near-square, the circular field already cropped close |
| Microns per pixel | Unknown |
| Camera | Not stated uniformly |
| Field of view | Not stated |
| Centring | **Dual view per eye** — one macula-centred and one disc-centred photograph of the same eye |
| Modality | Colour fundus photography |

### 3.2 Ultra-wide-field split — 256 images

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
| Quality | **Two ophthalmologists, confirmed or revised by a senior third** | — | Overall grade plus artefact, clarity and field-definition subscores. Only the arbitrated result is published, so the readers cannot be compared against each other |
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

- **The figure 2,256 is the whole dataset, not the regular split.** Later work citing it as the
  number of regular fundus photographs is over-counting by 256: the repository holds exactly 2,000
  regular images and 256 ultra-wide-field ones. Verified by counting the archive at commit
  `56d8af71`.
- **Eight photographs are not numbered as a pair.** The dual-view design holds for 998 of the 1,000
  eyes; in the training split, patients 56, 77, 164 and 167 have views numbered 3 and 4. Patient 164
  breaks it outright — one photograph of the left eye and three of the right. Code that assumes
  `_l1`/`_l2` exist for every eye will miss images or raise.
- **Share-alike is easy to overlook.** Anything published that qualifies as a derivative of this
  dataset inherits CC BY-SA — a real constraint if it is mixed into a corpus meant to be released
  under something else.

## 8. Notes

- The dual-view design is the underused asset here: two photographs of one eye should produce the
  same biomarker, and this is the only dataset in the catalogue that lets that be tested directly.

---

**Links, licence and access last checked:** 2026-09-11
