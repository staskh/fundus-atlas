# FQS

2,246 photographs with a **continuous** image-quality score — a mean opinion score from 0 to 100 —
alongside the usual three-way Good/Usable/Reject label. Every other quality dataset in this
catalogue grades into classes; this one puts a number on it, which makes it the only place where a
quality model's output can be correlated rather than merely confused-matrixed.

And it keeps its raters apart: **six doctors** score every photograph and **three graders** class
it, with the published mean and median over them. That is a human ceiling as well as a target.

## 1. What it is

- **Images:** 2,246.
- **Collected at:** Chinese clinical sources, published with a quality-assessment network.
- **Purpose:** to make fundus image quality a continuous, regressable quantity.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, [FIQS Dataset (Fundus Image Quality Scores)](https://figshare.com/articles/dataset/FIQS_Dataset_Fundus_Image_Quality_Scores_/28129847) |
| Download | **direct, no registration** — from the same record |
| Citation | *Acquire continuous and precise score for fundus image quality assessment: FTHNet and FQS dataset.* Scientific Reports 2025. DOI: [10.1038/s41598-025-24423-8](https://doi.org/10.1038/s41598-025-24423-8) |
| Licence | **CC BY 4.0**, as the figshare record's own licence field states, matching the paper |
| Content | 2,246 photographs, **published twice over**: `full_size_images/` at about 1942×1942 as the camera produced them, and `images/` resized to 1024×1024 |
| Annotations | Six doctors' scores from 0 to 100 and their published mean; three graders' three-class verdicts and their published median. Ten cross-validation folds are shipped alongside |

Reference code: [HudenJear/BasiQA](https://github.com/HudenJear/BasiQA).

### 2.1 How to fetch

```bash
uv run python -m datasets.fqs                          # downloads and builds 512 and 1024
uv run python -m datasets.fqs --sizes 512,720,1024     # any sizes a model needs
```

- **Downloads:** `FIQSDataset.zip`, 9.7 GB, from figshare. No account, no form. It is read where it
  lies rather than unpacked, since more than a fifth of it is the copy we do not build.
- **Builds:** the photograph and its field-of-view mask, from `full_size_images/`, at `native/`
  plus each requested size. This dataset has no vessel, artery/vein or disc annotations.
- **Not built:** `images/` — the same 2,246 photographs resized to 1024, which the store builds for
  itself from the originals.
- **Quality:** `quality` is the published `qualityLevel` mapped to the atlas's vocabulary — `0`
  becomes `good`, `1` `usable`, `2` `bad` — with `quality_source` recording that the grade is the
  authors' rather than ours. Because three graders are kept apart, `multi_reader` names `quality`
  on every row and `labels.csv` holds all three verdicts plus the published median.
- **Extra columns:** `quality_class` (the published code, verbatim), `mos` (the published mean
  opinion score) and `cv_00` to `cv_09` (this photograph's role — train, val or test — in each of
  the ten shipped folds; see section 7 on what those folds are worth).
- **Per-reader values:** `labels.csv` holds each of the six doctors' scores under the field `mos`
  and each of the three graders' verdicts under `quality`, with the published mean and median as
  the `consensus` reader.
- **Grouping:** none. `patient`, `visit` and `eye` are empty, because the dataset publishes no
  identity — see section 7.
- **Peculiarities:** the fold spreadsheets name photographs with a `.jpeg` extension the archive
  does not use, so they are matched without it.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | About **1942×1942** in `full_size_images/`, and 1024×1024 in the `images/` copy |
| Microns per pixel | Unknown |
| Camera | Not stated |
| Field of view | Not stated |
| Centring | Mixed |
| Modality | Colour fundus photography |

Both copies are in the one archive, so **take the originals**. The resize is harmless for a quality
classifier, which never reports physical units, but nothing measured in pixels on the 1024 copy
means what it appears to, and a paper that says "FQS at 1024" may mean either the published resize
or its own.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality score | **Six doctors, kept separate** (`doc1`–`doc6`) | — | 0 to 100 each. The published `meanOpinionScore` is exactly their mean, verified over all 2,246 rows |
| Quality class | **Three graders, kept separate** (`level1`–`level3`) | — | `0` good, `1` usable, `2` reject — **0 is the best class**. The published `qualityLevel` is their median, which is their majority wherever one exists; on **6 photographs all three disagree** and the median is what breaks the tie |

### 4.1 What the classes are worth

The two annotations agree in the way you would hope, which is itself worth recording: mean opinion
score averages 82 for class 0, 69 for class 1 and 41 for class 2. The classes overlap, though —
class 0 runs down to 66 and class 1 up to 86 — so a model matched against the class and one matched
against the score are not being asked the same question.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of both quality models
  here.
- **Below a model's measuring grid:** No, at 1024 — but the effective detail is that of a resized
  image.
- **What it can answer:** whether a three-class quality gate's decisions are monotonic in a
  continuous human score, and where its thresholds actually sit. Neither
  [AutoMorph's grader](../models/automorph-quality-grader.md) nor
  [QuickQual](../models/quickqual.md) has been evaluated that way.

## 7. Known defects

- **The shipped cross-validation folds come from an unseeded shuffle.** `dataset_fetch.py` in the
  archive builds them with `sample(frac=1)` and no random seed, so the ten folds are one arbitrary
  draw rather than a split the authors fixed: running the script again gives different folds, and
  nothing outside the archive can reproduce the ones inside it. Use the shipped files if you want
  to compare against the paper.
- **The fold files name photographs that are not in the archive under those names.** They list
  `00232.jpeg`; the archive holds `00232.PNG`. Match on the name without its extension.
- **No patient identity is published**, so a by-person split is impossible and two photographs of
  one eye — if there are any — cannot be told apart from two of different people.

## 8. Notes

- A continuous target changes what "quality" can mean for a pipeline: instead of rejecting an image,
  a measurement could be weighted by its score. Nothing in this catalogue does that yet, and this is
  the dataset that would support it.

---

**Links, licence and access last checked:** 2026-09-11
