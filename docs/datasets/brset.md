# BRSET

16,266 photographs from Brazil with multi-label disease annotations, demographics and per-image
quality flags — the largest colour-fundus dataset in this catalogue after [EyeQ](eyeq.md), and the
only large one from South America. Its cost is access: PhysioNet credentialing, a training course
and a signed data use agreement.

## 1. What it is

- **Images:** 16,266 JPEG photographs.
- **Collected at:** Brazilian ophthalmological services, published through PhysioNet.
- **Purpose:** a large, demographically documented multi-label dataset for ophthalmological machine
  learning — including fairness work, which is why the demographics matter.

## 2. Provenance

| | |
| --- | --- |
| Home | PhysioNet, [brazilian-ophthalmological](https://physionet.org/content/brazilian-ophthalmological/1.0.2/) — cite the version you actually pull |
| Download | **credentialed access** — CITI "Data or Specimens Only Research" training, then sign the Data Use Agreement. Not a simple registration |
| Citation | Nakayama LF, et al. *BRSET: A Brazilian Multilabel Ophthalmological Dataset of Retina Fundus Photos.* PLOS Digital Health 2024;3(7):e0000454. DOI: [10.1371/journal.pdig.0000454](https://doi.org/10.1371/journal.pdig.0000454). PhysioNet record: DOI [10.13026/z9zv-g542](https://doi.org/10.13026/z9zv-g542) |
| Licence | **PhysioNet Credentialed Health Data License 1.5.0** plus the Credentialed Health Data Use Agreement 1.5.0. **Not CC BY**, and redistribution of the files is restricted by the agreement |
| Content | 16,266 images at 45°, macula-centred, with no extra preprocessing applied |
| Annotations | Multi-label disease annotations, DR grades, quality flags, anatomical flags, demographics |

Helper code: <https://github.com/luisnakayama/BRSET>.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Mixed, by device |
| Microns per pixel | Unknown — not published |
| Camera | Nikon NF505 and Canon CR-2 |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Per photograph | — | Focus, illumination, image field and artefact flags — four separate judgements rather than one grade |
| Disease | Per eye | — | Multi-label, plus diabetic-retinopathy grades in two schemes |
| Other labels | — | — | Anatomical flags, and **patient demographics** — age, sex, and comorbidity data |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [FunPiQ](funpiq.md) samples some of these photographs for
  pixel-level quality annotation. [mBRSET](mbrset.md) is the handheld companion collection, **not** a
  subset of this one.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of every model here.
- **Below a model's measuring grid:** No, generally.
- **What it can answer:** whether a quality grader or a vessel model behaves the same on a Brazilian
  screening population as on the North American one behind EyeQ, with demographics available to
  stratify by. It is the best fairness-analysis substrate in this catalogue.

## 7. Known defects

- The credentialing requirement makes reproducible pipelines awkward: a reader cannot verify a
  result by downloading the data without completing the training and agreement first.

## 8. Notes

- Four separate quality flags rather than one grade is a better fit for real screening decisions than
  a single Good/Usable/Reject label, and a harder target for a model trained on the latter.

---

**Links, licence and access last checked:** 2026-09-11
