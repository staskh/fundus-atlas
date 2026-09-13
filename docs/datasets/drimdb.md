# DRIMDB

216 consecutive photographs from a Turkish ophthalmology clinic, each graded into one of three
classes — **good, bad, or outlier** — where "outlier" means the file is not a usable fundus
photograph at all. It is small, and it is the only quality collection in this catalogue that
deliberately includes images which are not of a retina, which is why quality models keep reaching
for it: a grader that has only ever seen retinas has never been asked the easiest question there
is.

Its name says diabetic retinopathy, but nothing in it is graded for disease. The photographs were
collected in the course of diabetic-retinopathy work and published to study image quality.

## 1. What it is

- **Images:** 216 consecutive photographs, in three quality classes: good, bad and outlier. The
  per-class counts are **Unknown** — the paper's abstract states the total and the three-class
  scheme, and the full text is behind a publisher bot-check.
- **Collected at:** Karadeniz Technical University, Trabzon, Turkey — the departments of statistics
  and computer science, computer engineering, and ophthalmology together.
- **Purpose:** to study automated retinal image quality assessment, and specifically to decide which
  photographs are *suitable* for an automated analysis system to work on at all.

## 2. Provenance

| | |
| --- | --- |
| Home | No maintained home page was established. The dataset is distributed through the two third-party routes below |
| Download | **direct, no registration** — a 17 MB `DRIMDB.rar` from Academic Torrents, <https://academictorrents.com/details/99811ba62918f8e73791d21be29dcc372d660305>. Also re-uploaded to Kaggle at <https://www.kaggle.com/datasets/subhajournal/drimdb-diabetic-retinopathy-images-database>, which needs an account |
| Citation | Şevik U, Köse C, Berber T, Erdöl H. *Identification of suitable fundus images using automated quality assessment methods.* Journal of Biomedical Optics 2014;19(4):046006. DOI: [10.1117/1.JBO.19.4.046006](https://doi.org/10.1117/1.JBO.19.4.046006) |
| Licence | **Not stated** by the authors anywhere this atlas could find. The Kaggle re-upload declares **CDLA-Permissive-1.0**, but that is the uploader's declaration on someone else's data and not the depositor's grant |
| Content | 216 photographs; resolution **Unknown** — see section 3 |
| Annotations | A three-class quality grade per photograph: good, bad, outlier |

The licence is the thing to be careful about here. Neither distribution route is the authors', and
the more permissive-looking of the two is a third party's claim about data they did not create. A
paper using these images is ordinary practice; redistributing them, or using them commercially on
the strength of the Kaggle field, is not obviously permitted by anyone who could permit it.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **Unknown.** Not stated in the abstract, and the full text could not be read: the publisher's site returns a bot-protection page to an automated request. Several secondary sources quote a single size, but none of them is the authors and this atlas does not repeat a figure it cannot source |
| Microns per pixel | Unknown — not published |
| Camera | **Unknown**, for the same reason as the resolution |
| Field of view | Unknown |
| Centring | Unknown |
| Modality | Colour fundus photography, plus — by design — a number of images that are **not** fundus photographs at all. Those are the outlier class |

The unknowns in this table are recoverable by anyone who can read the paper or open the archive;
they are recorded as unknown rather than filled from secondary sources that may be quoting each
other.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | Unknown how many, and whether readers were kept separate | — | Three classes: good, bad, outlier. The **outlier** class is the unusual part — images that are not gradeable because they are not of a retina, such as photographs of the outer eye |
| Disease | — | — | None. Despite the name, no diabetic-retinopathy grade is published |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established among catalogued datasets.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** the
  [Fundus Image Toolbox quality ensemble](../models/fit-quality.md), which trained on DRIMDB
  together with [DeepDRiD](deepdrid.md) and treats the outlier class as ungradeable. A score for
  that model on DRIMDB is in-sample.
- **Below a model's measuring grid:** Unknown, the resolution being unestablished. If the commonly
  quoted size is right, it is below every measuring grid in this catalogue — but that is exactly the
  figure this page declines to assert.
- **What it can answer:** whether a quality grader can reject an image that is not a retina.
  [EyeQ](eyeq.md), [FQS](fqs.md), [DeepDRiD](deepdrid.md) and [MSHF](mshf.md) all grade photographs
  that are at least photographs of a fundus; this one does not, and a gate that only ever sees
  retinas will not be tested on the failure that most often reaches a clinic's pipeline — a file
  that should never have entered it.

## 7. Known defects

- **The authors' own distribution could not be found**, so every copy in circulation is a third
  party's, with the licence ambiguity that follows (section 2).
- **The published description could not be read** for resolution, camera and per-class counts: the
  journal's site blocks automated access, checked 2026-09-13. These are gaps in this page rather
  than defects in the dataset.
- **The name misleads.** "Diabetic Retinopathy Image Database" describes where the photographs came
  from, not what is labelled in them, and nothing here is graded for retinopathy.

---

**Links, licence and access last checked:** 2026-09-13
