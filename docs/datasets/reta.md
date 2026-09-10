# RETA

81 photographs with vessel masks produced through a multi-stage annotation workflow with explicit
inter- and intra-annotator disambiguation. **The annotation quality is the point**: its authors argue
that the older vessel sets everyone trains on are noisier than their reputation suggests, and publish
a comparison to make the case.

Two facts decide how it can be used: only 54 of the 81 masks are public, and the photographs are
[IDRiD](idrid.md)'s — downsized to a quarter of their original width.

## 1. What it is

- **Images:** 81, split 54 with public masks and 27 withheld as a test set.
- **Collected at:** not collected — annotated on IDRiD's photographs.
- **Purpose:** a vessel benchmark whose contribution is annotation rigour rather than new imagery,
  with an online leaderboard.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://reta-benchmark.org>, data at figshare DOI [10.6084/m9.figshare.16960855](https://doi.org/10.6084/m9.figshare.16960855) |
| Download | **direct, no registration** — 6.6 MB for the images part, about 878 MB for all six parts |
| Citation | Lyu X, Jajal P, Tahir MZ, Zhang S. *The RETA Benchmark for Retinal Vascular Tree Analysis.* Scientific Data 2022;9:397. DOI: [10.1038/s41597-022-01507-y](https://doi.org/10.1038/s41597-022-01507-y). The photographs are IDRiD's and that citation is owed too — Porwal P et al., Data 2018;3(3):25, DOI [10.3390/data3030025](https://doi.org/10.3390/data3030025) |
| Licence | **CC BY 4.0** |
| Content | 81 images at 1024×1024 — IDRiD's photographs, downsized |
| Annotations | Vessel masks on 54 of the 81; the other 27 are withheld |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1024×1024 |
| Microns per pixel | Unknown |
| Camera | Kowa VX-10α (IDRiD's) |
| Field of view | 50° (IDRiD's) |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

The 1024×1024 figure is the **authors' rendition**, not the camera's output: IDRiD's originals are
4288×2848, so RETA's copies carry about a quarter of the linear detail.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Multi-stage workflow with inter- and intra-annotator disambiguation | 1024×1024 | On 54 images. The disambiguation record is the dataset's distinguishing feature |

## 5. Inheritance

- **Reuses images from:** **[IDRiD](idrid.md)** — the same 81 photographs and the same 54/27 split,
  **resized** from 4288×2848 to 1024×1024.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — RETA postdates the AutoMorph
  family's vessel training and is absent from the other models' stated lists. **Genuinely held out**,
  which is rare for a vessel dataset here.
- **Below a model's measuring grid:** No — 1024 sits above the 912 vessel grid, just.
- **What it can answer:** held-out vessel accuracy against an unusually careful annotation. Its 54
  usable images make it small, so treat differences as indicative.

## 7. Known defects

- **Only 54 of 81 masks are public.** The 27 test masks are deliberately withheld to keep the
  authors' leaderboard meaningful — published state, not a broken download.
- The resolution is inherited and reduced (section 3); a Dice measured here is measured on a
  downsized rendition of somebody else's photographs.

## 8. Notes

- RETA and IDRiD are the same eyes at two sizes. Anyone quoting a RETA score alongside an IDRiD-based
  one should say which resolution each was measured at.

---

**Links, licence and access last checked:** 2026-09-11
