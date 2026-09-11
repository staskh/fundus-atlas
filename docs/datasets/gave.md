# GAVE

50 colour fundus photographs with vessel and artery/vein annotation, released for the GAVE Challenge
at MICCAI 2025. It is small, recent and **CC BY 4.0** — which makes it, with [AVRDB](avrdb.md), one of
the two most permissively licensed artery/vein datasets in this catalogue, and the only recent one
that no model here can have trained on.

## 1. What it is

- **Images:** 50.
- **Collected in:** China.
- **Purpose:** the development set for the GAVE 2025 challenge — Generalized Analysis of Vessels in
  Eye — organised by Fang H, Xu Y, Yang W, Bogunović H and Fu H.

## 2. Provenance

| | |
| --- | --- |
| Home | Zenodo, DOI [10.5281/zenodo.15081506](https://doi.org/10.5281/zenodo.15081506) |
| Download | **unclear — check before planning work around it.** The Zenodo record resolves and downloads, but what it contains is the challenge's registration document; the image archive is distributed through the challenge platform, and whether the photographs are served from a URL or only to participants was not established |
| Citation | **No describing publication established.** The deposit holds the GAVE 2025 challenge proposal rather than a dataset paper; cite the challenge and the Zenodo record until one appears. Organisers: Fang H, Xu Y, Yang W, Bogunović H, Fu H |
| Licence | **CC BY 4.0** as recorded on the deposit — attribution only, commercial use permitted |
| Content | 50 images at 1536×1024 |
| Annotations | Vessel and artery/vein labels; reader counts not stated |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1536×1024 |
| Microns per pixel | Unknown — not published |
| Camera | Unknown make |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Unknown | Native | — |
| Artery/vein | Unknown | Native | The challenge's target task |

Reader counts are not stated on the record.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list GAVE in their training data. It is held out of
  the AutoMorph family and of [VascX](../models/vascx-artery-vein.md) by date — published after both.
- **Below a model's measuring grid:** No.
- **What it can answer:** held-out artery/vein accuracy on a Chinese cohort under a permissive
  licence — for the AutoMorph family and VascX, though not for OCULARNet, which trained on it.

## 7. Known defects

- The access route is unresolved (section 2). A dataset that cannot be obtained reliably cannot be
  part of a reproducible comparison, however good its licence.

## 8. Notes

- 50 images is a challenge development set, not a cohort. Its licence and its date are what make it
  worth tracking; its size means a score on it will be noisy.

---

**Links, licence and access last checked:** 2026-09-11
