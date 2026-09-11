# GAMMA

300 paired fundus photographs and OCT volumes for glaucoma grading, with optic disc and cup
segmentations and fovea locations on the fundus images. It is one of the two datasets the AutoMorph
family's disc-and-cup model trained on — the other being [REFUGE](refuge.md) — and its 100 training
photographs are therefore in-sample for every disc measurement that pipeline reports.

## 1. What it is

- **Images:** 300 fundus–OCT pairs, released in three sets of about 100: training, preliminary and
  final. Only the training set carries public labels.
- **Collected at:** Chinese clinical sites, released through the MICCAI 2021 challenge series by
  Baidu and collaborators.
- **Purpose:** glaucoma grading from two modalities at once — the first public multi-modality
  glaucoma dataset — with disc/cup segmentation and fovea localisation as secondary tasks.

## 2. Provenance

| | |
| --- | --- |
| Home | The GAMMA challenge on Baidu AI Studio; the challenge description and data pages are linked from the paper |
| Download | **registration** — challenge account; the labelled training split is what circulates |
| Citation | Wu J, Fang H, Li F, Fu H, Lin F, Li X, et al. *GAMMA challenge: Glaucoma grAding from Multi-Modality imAges.* Medical Image Analysis 2023;90:102938. DOI: [10.1016/j.media.2023.102938](https://doi.org/10.1016/j.media.2023.102938) · [arXiv:2202.06511](https://arxiv.org/abs/2202.06511) |
| Licence | **Challenge terms** — research use; no Creative Commons grant established |
| Content | 300 fundus–OCT pairs; the fundus photographs are the part used here |
| Annotations | Glaucoma grade in three classes, optic disc and cup segmentation, fovea location |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Mixed — the fundus photographs come from more than one device |
| Microns per pixel | Unknown — not published |
| Camera | Not stated per image |
| Field of view | Not stated |
| Centring | Posterior pole |
| Modality | Colour fundus photography, **paired with OCT volumes**; the OCT half is a different modality and is not interchangeable with the photographs |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Challenge annotators | Native | Masks |
| Optic cup | Challenge annotators | Native | Masks |
| Disease | Per case | — | Normal, early glaucoma, progressive (intermediate and advanced) glaucoma |
| Other labels | — | — | Fovea coordinates; the paired OCT volume |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:**
  [AutoMorph's disc-and-cup model](../models/automorph-disc-cup.md) trained on GAMMA's 100 images
  together with REFUGE's 800 — so **GAMMA cannot evaluate it**, and between them these two datasets
  account for the whole of that model's 900-image training set.
- **Below a model's measuring grid:** No.
- **What it can answer:** whether a disc/cup method's errors track glaucoma severity, since the grade
  is three-way rather than binary. For the AutoMorph family, nothing — it is training data.

## 7. Known defects

- Only the training split has public labels, so the effective public size is about 100 images rather
  than 300.

## 8. Notes

- The AutoMorph family's disc-and-cup model rests on 900 images from REFUGE and GAMMA, both challenge
  sets from Chinese clinical populations. That is a narrow foundation for a measurement — the
  cup-to-disc ratio — used worldwide, and it is the clearest argument in this catalogue for
  evaluating on [PAPILA](papila.md) and [G1020](g1020.md) instead.

---

**Links, licence and access last checked:** 2026-09-11
