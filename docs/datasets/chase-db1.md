# CHASE-DB1

28 photographs from the eyes of 14 multi-ethnic British schoolchildren, with vessel segmentations
from **two independent observers**. It is the only paediatric dataset in this catalogue, and the only
one drawn from a population health study of children — which matters because a child's retina is not
a small adult's, and every model here trained on adult eyes.

## 1. What it is

- **Images:** 28 — both eyes of 14 children, mean age 10: 8 white, 3 South Asian, 3 of other ethnic
  origin.
- **Collected at:** the Child Heart and Health Study in England (CHASE), through Kingston University
  London and St George's, University of London.
- **Purpose:** a vessel reference standard on a paediatric, multi-ethnic population.

## 2. Provenance

| | |
| --- | --- |
| Home | Kingston University Research Data Repository, <https://researchdata.kingston.ac.uk/96/> |
| Download | **direct, no registration** |
| Citation | Fraz MM, Remagnino P, Hoppe A, Uyyanonvara B, Rudnicka AR, Owen CG, Barman SA. *An ensemble classification-based approach applied to retinal blood vessel segmentation.* IEEE Transactions on Biomedical Engineering 2012;59(9):2538–2548. DOI: [10.1109/TBME.2012.2205687](https://doi.org/10.1109/TBME.2012.2205687) |
| Licence | **Not established** — check the repository record before redistributing |
| Content | 28 images; see section 3 on the two resolutions in circulation |
| Annotations | Two independent observers' vessel segmentations, kept separate |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **1280×960 as described by the distributor; 999×960 as the files are commonly circulated** — see section 7 |
| Microns per pixel | Unknown — not published |
| Camera | Nidek NM-200-D, **hand-held** |
| Field of view | 30° |
| Centring | Mixed |
| Modality | Colour fundus photography |

A hand-held camera is worth noting: framing and illumination vary more than with a tabletop device,
which is closer to a screening setting than most datasets here.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **Two, kept separate** | Native | Both are distributed; the first is conventionally used as ground truth |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  (in `ALL-SIX`) and [LWNet](../models/lwnet.md). In-sample for both.
- **Below a model's measuring grid:** Borderline — 960 pixels tall sits just above the 912 vessel
  grid and below the 1024 of the newer models.
- **What it can answer:** whether a model trained on adult eyes transfers to children, and — through
  the second observer — the human ceiling on a hand-held camera's images.

## 7. Known defects

- **Two resolutions are in circulation.** The distributor describes 1280×960, while the files as
  widely shared are 999×960. Anyone reporting a pixel measurement should say which they had.

## 8. Notes

- The paediatric population is the reason to keep this dataset in mind even though it is small and
  in-sample: no other entry here tests a model on a child's retina.

---

**Links, licence and access last checked:** 2026-09-11
