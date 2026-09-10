# GRAPE

631 photographs from a **longitudinal** glaucoma cohort — the same eyes followed over time — with
visual fields, OCT and intraocular pressure alongside the images, and disc and cup contours drawn on
a crop around the nerve head. It is the only dataset in this catalogue with follow-up visits, which
makes it the only one that could show whether a biomarker tracks progression in an individual rather
than differing between people.

## 1. What it is

- **Images:** 631 fundus photographs from a glaucoma-management cohort with repeat visits.
- **Collected at:** Chinese clinical sites.
- **Purpose:** glaucoma management research across modalities and over time.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare collection, DOI [10.6084/m9.figshare.c.6406319.v1](https://doi.org/10.6084/m9.figshare.c.6406319.v1) |
| Download | **direct, no registration** — the collection holds an Excel sheet, four archives and a `draw.py` helper that redraws the contours |
| Citation | Huang X, Kong X, Shen Z, et al. *GRAPE: A multi-modal dataset of longitudinal follow-up visual field and fundus images for glaucoma management.* Scientific Data 2023;10:520. DOI: [10.1038/s41597-023-02424-4](https://doi.org/10.1038/s41597-023-02424-4) |
| Licence | **CC BY 4.0** — both the paper and the collection |
| Content | 631 images at 50°, macula-centred |
| Annotations | Optic disc and cup contours as JSON, **on a region-of-interest crop**; visual fields, OCT measurements, intraocular pressure, follow-up structure |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | Full frames as captured by the camera; the contour coordinates live in a crop's coordinate system |
| Microns per pixel | Unknown — not published |
| Camera | Topcon TRC-NW8 |
| Field of view | 50° |
| Centring | Macula-centred |
| Modality | Colour fundus photography, with paired visual field and OCT data |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **One** ophthalmologist | **A region-of-interest crop around the nerve, not the full 50° frame** | JSON contours; `draw.py` redraws them on the ROI |
| Optic cup | One | As above | — |
| Disease | Per eye and per visit | — | Glaucoma, longitudinally |
| Other labels | — | — | Visual field indices, OCT measurements, intraocular pressure, visit dates |

**The annotation coordinate system is not the photograph's.** Contours are in the ROI's frame, so
importing them as full-frame masks would silently change every physical-scale figure derived from
them. The mapping has to be carried, not assumed.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [REYIA](reyia.md) includes GRAPE photographs in its nine-source
  compilation.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list GRAPE in their training data. Held out of the
  AutoMorph family.
- **Below a model's measuring grid:** No.
- **What it can answer:** the only longitudinal question available here — whether a biomarker moves
  in the same eye over time, and whether that movement tracks the visual field. Cross-sectional
  differences between people are what every other dataset supports.

## 7. Known defects

- The ROI coordinate system (section 4) is the trap; a full-frame import would be wrong in a way
  that produces plausible-looking numbers.
- One annotator, so no human ceiling.

## 8. Notes

- Longitudinal data is what a biomarker ultimately has to justify itself against: a measurement that
  cannot track change in one patient is of limited clinical use however well it separates groups.
  This is the only entry here that would support that test.

---

**Links, licence and access last checked:** 2026-09-11
