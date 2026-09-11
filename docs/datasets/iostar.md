# IOSTAR

30 images at 1024×1024 with vessels, arteries and veins, the optic disc — and, uniquely in this
catalogue, **annotated vessel junctions**: bifurcations and crossovers marked as points. It is also
**not colour fundus photography**: the images are scanning laser ophthalmoscopy, which looks similar
in a file browser and is a different modality.

## 1. What it is

- **Images:** 30.
- **Collected at:** the RetinaCheck project, Eindhoven University of Technology, with i-Optics.
- **Purpose:** vessel segmentation and vascular-tree analysis on SLO images, including junction
  detection.

## 2. Provenance

| | |
| --- | --- |
| Home | <http://www.retinacheck.org/> — the IOSTAR and RetinaCheck datasets are distributed from the project's dataset pages |
| Download | **request** in practice; the project page has served direct links at times, so check current state |
| Citation | Zhang J, Dashtbozorg B, Bekkers E, Pluim JPW, Duits R, ter Haar Romeny BM. *Robust Retinal Vessel Segmentation via Locally Adaptive Derivative Frames in Orientation Scores.* IEEE Transactions on Medical Imaging 2016;35(12):2631–2644. DOI: [10.1109/TMI.2016.2587062](https://doi.org/10.1109/TMI.2016.2587062) |
| Licence | **Research use**; no Creative Commons grant established |
| Content | 30 images at 1024×1024 |
| Annotations | Vessels, artery/vein, optic disc, and **bifurcation and crossover points** |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1024×1024 |
| Microns per pixel | Unknown — not published |
| Camera | EasyScan (i-Optics), a **scanning laser ophthalmoscope** |
| Field of view | 45° |
| Centring | Mixed |
| Modality | **Scanning laser ophthalmoscopy — not colour fundus photography.** SLO forms its image by scanning a laser rather than photographing with white light, so vessel contrast, colour and noise all differ. Never pool it with colour photographs |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Manual | Native | — |
| Artery/vein | Manual | Native | — |
| Optic disc | Manual | Native | — |
| Other labels | — | Native | **Junctions** — bifurcations and crossovers as points, from the RetinaCheck junction ground truth. The only junction annotation in this catalogue |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established. An artery/vein re-annotation circulates as
  **IOSTAR-AV**, used as an out-of-distribution test set by [OCULARNet](../models/ocularnet.md).

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  includes IOSTAR in AutoMorph's `ALL-SIX` combination — so a colour-fundus vessel model has SLO
  images in its training data, which is worth knowing when its behaviour on unusual contrast is
  questioned. [OCULARNet](../models/ocularnet.md) uses IOSTAR-AV as a **near out-of-distribution
  test**, deliberately.
- **Below a model's measuring grid:** No.
- **What it can answer:** the only dataset here that can evaluate junction detection directly, which
  is the input to [bifurcation angles](../biomarkers/bifurcation-angle.md) and
  [junction counts](../biomarkers/junction-counts.md). Also a modality-shift test.

## 7. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 8. Notes

- Two properties make IOSTAR unusual and they pull in opposite directions: it has the annotation this
  catalogue most lacks (junctions), and it is the wrong modality for the pipelines that would use it.
  Treat a score on it as a measure of the tracer, not of colour-fundus performance.

---

**Links, licence and access last checked:** 2026-09-11
