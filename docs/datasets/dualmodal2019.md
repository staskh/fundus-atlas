# DualModal2019

30 images with artery and vein annotation, published to support **simultaneous segmentation across
two imaging modalities of the same eye**. That design — one eye, two ways of photographing it — is
what makes a 30-image dataset interesting: it isolates how much of a measurement difference is the
imaging rather than the anatomy.

## 1. What it is

- **Images:** 30.
- **Collected at:** a Chinese clinical setting; deposited in 2019.
- **Purpose:** dual-modal artery and vein segmentation with a multi-task cascade network.

## 2. Provenance

| | |
| --- | --- |
| Home | [IEEE DataPort](https://ieee-dataport.org/documents/dualmodal2019-dataset), DOI `10.21227/wbpy-mf57` |
| Download | **registration** — an IEEE DataPort account. Some DataPort records are open and others subscriber-only; confirm which applies before planning work |
| Citation | Zhang S, Zheng R, Sun M. *Simultaneous Arteriole and Venule Segmentation of Dual-Modal Fundus Images Using a Multi-Task Cascade Network.* Deposited on IEEE DataPort, 2019 |
| Licence | **Not stated** on the record beyond IEEE DataPort's own terms |
| Content | 30 images at 1024×1024 |
| Annotations | Artery/vein segmentation |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1024×1024 |
| Microns per pixel | Unknown |
| Camera | Not stated |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | **Dual-modal** — the collection pairs two imaging modalities of the same eyes. Whether both halves are colour fundus photography is not clearly stated on the record, so treat modality as **partly unresolved** and check before pooling |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | Reference standard; reader count not stated | Native | The dataset's target task |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on it.
  [OCULARNet](../models/ocularnet.md) uses DualModal as an **in-distribution test set**.
- **Below a model's measuring grid:** No, at 1024.
- **What it can answer:** in principle, how much of a measurement difference is the modality rather
  than the eye — on 30 eyes, so indicatively at best.

## 7. Known defects

- **The modality composition is unresolved** from the record (section 3), which undermines the
  dataset's own headline question until the archive is inspected.
- No licence statement.

## 8. Notes

- The same-eye-two-ways design is the one thing here that could separate imaging effects from
  anatomy directly. Thirty eyes is too few to settle it, but the design is worth copying at scale.

---

**Links, licence and access last checked:** 2026-09-11
