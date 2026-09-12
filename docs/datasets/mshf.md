# MSHF

1,302 photographs assembled specifically to make image quality measurable across **four camera
classes at once** — tabletop, portable, and ultra-wide-field — with three readers scoring
illumination, clarity, contrast and overall quality on every one. It is the only dataset in this
catalogue built around heterogeneity of device rather than of disease, and the only one where a
quality score is available from three separate people.

## 1. What it is

- **Images:** 1,302 — 500 standard colour fundus photographs, 302 from portable cameras, and 500
  ultra-wide-field mosaics. The authors split them 1,042 train / 260 test.
- **Collected at:** Chinese clinical sites; published as a multi-source heterogeneous fundus dataset.
- **Purpose:** image-quality assessment across devices, with per-reader scores retained.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.21507564](https://doi.org/10.6084/m9.figshare.21507564) |
| Download | **direct, no registration** — a zip of photographs plus two Excel score sheets |
| Citation | Jin K, Gao Z, Jiang X, et al. *MSHF: A Multi-Source Heterogeneous Fundus (MSHF) Dataset for Image Quality Assessment.* Scientific Data 2023;10:286. DOI: [10.1038/s41597-023-02188-x](https://doi.org/10.1038/s41597-023-02188-x) |
| Licence | **CC BY 4.0** |
| Content | 1,302 images across three device classes |
| Annotations | Illumination, clarity, contrast and overall quality, each 0/1 from **three readers** in `Individual_scores.xlsx.xlsx`, plus an agreed score per group in `MSHF_quality_scores.xlsx` — which is missing for one group, see section 7 |

### 2.1 How to fetch

```bash
uv run python -m datasets.mshf                          # downloads and builds 512 and 1024
uv run python -m datasets.mshf --sizes 512,720,1024     # any sizes a model needs
```

- **Downloads:** `MSHF dataset 2.0.zip`, 1.1 GB, from figshare. No account, no form. It is read
  where it lies rather than unpacked.
- **Builds:** the photograph and its field-of-view mask, at `native/` plus each requested size. The
  store holds **802** images: the 500 colour-fundus and 302 portable-camera photographs. The
  DR-XJU group's field is wider than tall (section 3.1), so its square crop is padded above and
  below — a median of 5% of the canvas and up to 26% — rather than shaved at the sides.
- **Not built:** the 500 ultra-wide-field mosaics, a 200° instrument beside 45–60° cameras; and the
  all-zero table described in section 7, which is never read as a score.
- **Subsets:** `cfp` and `portable`, by device class. The publishing group — `DR-XJU`, `Local1` and
  so on — is kept in a column of its own, since the groups differ in size and in disease.
- **Splits:** `train` and `test`, from the `AI-use` folders, matched without the file extension
  because two photographs change extension between the two places (section 7).
- **Per-reader values:** `labels.csv` holds all three readers' verdicts on all four components —
  `illumination`, `clarity`, `contrast` and `quality` — with the agreed score as the `consensus`
  reader where one is published. `multi_reader` names all four on every row.
- **Quality:** binary throughout, mapped to the atlas's vocabulary as `good` and `bad`. Where a
  group has no agreed score, the cell holds the readers' value if all three agree and is empty if
  they do not — 19 DR-ZJU photographs come out empty that way, and every such row carries a note.
- **Grouping:** none. The dataset publishes no patient identity, so `patient`, `visit` and `eye`
  are empty.

## 3. The images

Three subcollections by device class, which is the dataset's whole point.

### 3.1 Colour fundus photographs — 500 images

Four groups, and they are not the same size. **The 235 DR-XJU photographs are thumbnails** — 215 of
them 412×310, the rest 496×470 to 555×419 — while DR-ZJU is 1924×1556 or 3216×2136 and the Glaucoma
and Healthy groups are 1534×1534. A quality score on a 412-pixel image and one on a 3216-pixel image
are not the same measurement, and this is a quality dataset.

**The DR-XJU thumbnails are also cropped photographs**, not whole ones: the field of view runs off
the left and right of the frame, along three quarters of each edge, so a good part of the retina is
simply not there. Their field is wider than tall in frame, which means code that crops to a circle's
bounding square takes another 0.9% off the sides of what did survive.

| | |
| --- | --- |
| Resolution (pixels) | DR-XJU 412×310 to 555×419; DR-ZJU 1924×1556 and 3216×2136; Glaucoma and Healthy 1534×1534 |
| Microns per pixel | Unknown |
| Camera | Kowa at 45° and Topcon TRC-NW8 at 50°, per the authors' device list |
| Field of view | 45° and 50° |
| Centring | Mixed |
| Modality | Colour fundus photography |

### 3.2 Portable-camera photographs — 302 images

| | |
| --- | --- |
| Resolution (pixels) | 2560×1920, but for one photograph at 1705×1705 |
| Microns per pixel | Unknown |
| Camera | A handheld device (DEC200 class) at 60° |
| Field of view | 60° |
| Centring | Mixed |
| Modality | Colour fundus photography, handheld |

### 3.3 Ultra-wide-field mosaics — 500 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated uniformly |
| Microns per pixel | Unknown |
| Camera | Optos, 200° |
| Field of view | **200°** |
| Centring | Not applicable — a wide-field mosaic |
| Modality | **Ultra-wide-field imaging, not standard colour fundus photography.** Never pool the 500 UWF frames with the others |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Quality | **Three, kept separate as well as merged** | — | Four binary components each: illumination, clarity, contrast, overall |
| Disease | Per eye | — | Diabetic retinopathy, glaucoma, healthy — on the colour-fundus portion |
| Other labels | — | — | Camera class per image |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — **held out of both quality
  models** in this catalogue, which both learned from [EyeQ](eyeq.md).
- **Below a model's measuring grid:** Varies by device class.
- **What it can answer:** whether a quality grader trained on one screening programme's photographs
  transfers to a portable camera — and, through the three readers, how much of a quality
  disagreement is human rather than machine. It is the strongest held-out quality cohort here.

## 7. Known defects

- **The tab that should hold DR-ZJU's agreed scores holds an all-zero table instead.** In
  `MSHF_quality_scores.xlsx` the tab named `DR-ZJU` is headed "gold standard" and carries a row for
  every one of the 1,302 images — each of them `0, 0, 0, 0`. Read as scores it marks the entire
  dataset unusable on every component. The consequence is that **DR-ZJU's 187 photographs have no
  agreed score at all**: the other six tabs cover the remaining 1,115. The three readers' individual
  scores are complete and unaffected.
- **DR-XJU-30 and DR-XJU-31 are odd twice over.** They are missing from the agreed-score sheet, and
  they appear in the `AI-use` split as `.png` where every original is `.jpg`.
- **One group is published at thumbnail size and cropped** (section 3.1), which for a quality
  benchmark is a difference in kind rather than degree: the field of view of those 235 photographs
  is cut off at the frame's left and right edges.
- The three device classes are a single archive; anyone treating MSHF as one dataset will mix a 45°
  photograph with a 200° mosaic.
- Mapping its four binary components onto a three-way Good/Usable/Reject scheme is a decision, not a
  translation, and has to be defined before any comparison with [EyeQ](eyeq.md)-trained models.

## 8. Notes

- Individual reader scores are rare and valuable. Most quality datasets publish a consensus and
  discard exactly the disagreement that would calibrate a model's errors.

---

**Links, licence and access last checked:** 2026-09-11
