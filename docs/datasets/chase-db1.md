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

### 2.1 CHASE-DB1 — the photographs and vessel tracings

| | |
| --- | --- |
| Home | Kingston University Research Data Repository, <https://researchdata.kingston.ac.uk/96/> |
| Download | **direct, no registration** |
| Citation | Fraz MM, Remagnino P, Hoppe A, Uyyanonvara B, Rudnicka AR, Owen CG, Barman SA. *An ensemble classification-based approach applied to retinal blood vessel segmentation.* IEEE Transactions on Biomedical Engineering 2012;59(9):2538–2548. DOI: [10.1109/TBME.2012.2205687](https://doi.org/10.1109/TBME.2012.2205687) |
| Licence | **Not established** — check the repository record before redistributing |
| Content | 28 images; see section 3 on the two resolutions in circulation |
| Annotations | Two independent observers' vessel segmentations, kept separate |

### 2.2 OCULAR — artery/vein labels

| | |
| --- | --- |
| Home | The OCULAR repository, <https://github.com/GonzaloPlaaza/OCULAR>, section "Release of New Artery-Vein Annotations" |
| Download | **direct, no registration** — a public Google Drive folder, <https://drive.google.com/drive/folders/1jPAG5RtM_bwzvYWlwGnHWCdUdYBEShr-> |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030 — [Plaza 2026](../papers/plaza-2026.md) |
| Licence | **not stated** — the OCULAR repository has no LICENSE file |
| Content | 28 PNG label maps, one per photograph (checked 2026-10-12) |
| Annotations | Supplies artery, vein and crossing labels, drawn by [OCULARNet](../models/ocularnet.md) at 1024×1024, cut back to this dataset's own vessel tracing and corrected by hand |

These are the first artery/vein labels for CHASE-DB1, and they are a model's. Every vessel pixel in them is one the CHASE observers drew; what OCULAR adds is which class each is, and that is OCULARNet's call wherever its authors did not overrule it.

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
| Artery, vein and crossing, by [OCULAR](../projects/ocularnet.md) | One model, refined by OCULAR's authors | **1024×1024**, not this dataset's native size | A model's output corrected by hand, not an independent reader: where the model and the corrector agree on a mistake, it stays. Section 2.2 |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [OCULAR](../projects/ocularnet.md), which adds artery/vein labels to them (section 2.2). It did not train or evaluate OCULARNet on them.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  (in `ALL-SIX`), [LWNet](../models/lwnet.md) and [VascX vessels](../models/vascx-vessels.md), on all 28 (VascX paper, Table 1). In-sample for all three.
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
