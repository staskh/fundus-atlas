# INSPIRE-AVR

40 disc-centred photographs with a vessel reference, an optic disc reference, and **a published
arteriovenous ratio per image** — the average of two experts' measurements made with the IVAN
semi-automated tool used in large epidemiological studies. Together with [AVRDB](avrdb.md) it is one
of only two datasets here that publish the biomarker rather than only the mask.

## 1. What it is

- **Images:** 40.
- **Collected at:** the University of Iowa, from an ophthalmology practice.
- **Purpose:** to support automated arteriolar-to-venular width ratio measurement, with a
  human-derived AVR as the reference.

## 2. Provenance

| | |
| --- | --- |
| Home | [Iowa INSPIRE datasets](https://eye.medicine.uiowa.edu/inspire-datasets) |
| Download | **direct from that page** — a single archive of about 80 MB. It **must** be obtained from that site: copying and redistribution are prohibited |
| Citation | Niemeijer M, Xu X, Dumitrescu AV, Gupta P, van Ginneken B, Folk JC, Abràmoff MD. *Automated Measurement of the Arteriolar-To-Venular Width Ratio in Digital Color Fundus Photographs.* IEEE Transactions on Medical Imaging 2011;30(11):1941–1950. DOI: [10.1109/TMI.2011.2159619](https://doi.org/10.1109/TMI.2011.2159619) |
| Licence | **Research and educational use, free of charge, until further notice. Copying, redistribution and any commercial use are prohibited.** Not a Creative Commons licence; reporting on the data requires citing the paper |
| Content | 40 JPEG images at 2392×2048 |
| Annotations | Vessel reference, optic disc reference, and **two experts' AVR values with their average as the published standard** |

The same page hosts INSPIRE-stereo, a separate 30-image glaucoma collection with OCT depth, and a
Tromsø subset that is not yet available.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 2392×2048 |
| Microns per pixel | Unknown — not published |
| Camera | Not stated |
| Field of view | 30°, per the collection protocol |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Reference standard | Native | — |
| Optic disc | Reference standard | Native | Which, with the vessels, is what a zone-based calibre measurement needs |
| Other labels | **Two experts, plus their average** | — | **AVR as a number per image**, measured with IVAN. It is a scalar, not a pixel map of a measurement zone — so reproducing it means running a pipeline's own calibre code and comparing the number |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [PVBM](../projects/pvbm.md) distributes INSPIRE among the external
  test sets its downloader fetches, and [LUNet](../models/lunet.md) uses it as external test data.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None trained on it. [OCULARNet](../models/ocularnet.md)
  lists INSPIRE in its **training** collection, so it is in-sample for that model;
  [LUNet](../models/lunet.md) uses it as a held-out external test.
- **Below a model's measuring grid:** No.
- **What it can answer:** whether a pipeline's [AVR](../biomarkers/avr.md) agrees with two experts'
  IVAN measurements — the same check [AVRDB](avrdb.md) supports, on a different population and with
  the tool epidemiological studies actually used.

## 7. Known defects

- Redistribution is explicitly prohibited, so any reproducible pipeline must document the download
  rather than ship the data — and third-party copies of "INSPIRE" in circulation are not licensed.

## 8. Notes

- IVAN is the semi-automated tool behind much of the published AVR literature. An agreement figure
  against it is therefore not just a comparison with two people, but with the method the field's
  epidemiology was built on.

---

**Links, licence and access last checked:** 2026-09-11
