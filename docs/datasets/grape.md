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
| Licence | **CC BY 4.0** per the paper; the figshare files themselves are marked **CC0**. The more permissive of the two is the depositor's own statement, and the paper's is the one this atlas records |
| Content | 631 images at 50°, macula-centred |
| Annotations | Optic disc and cup contours as JSON, **on a region-of-interest crop**; visual fields, OCT measurements, intraocular pressure, follow-up structure |

### 2.1 How to fetch

```bash
uv run python -m datasets.grape                          # downloads and builds 512 and 1024
uv run python -m datasets.grape --sizes 512,720,1024     # any sizes a model needs
```

- **Downloads:** four files from the figshare collection — the photographs (116 MB), the crops
  around the nerve head (20 MB), the contours as JSON (14 MB) and the clinical spreadsheet. No
  account, no form. The three archives are RAR, which needs `bsdtar`; the Python standard library
  cannot read them.
- **Builds:** the photograph, its field-of-view mask, and the disc and cup contours for all 631
  visits, at `native/` plus each requested size.
- **The contours are placed, not assumed.** They are published in the crop's coordinate system and
  the archive never says where the crop came from, so each crop is located in its own photograph by
  correlation. The offset and the correlation go in every row as `roi_x0`, `roi_y0` and
  `roi_match`. Across all 631 the worst match is **0.991** and the median **0.999**, so every crop
  was found; a match below 0.9 would leave the contours unplaced with a note rather than guessed at.
- **Grouping:** the point of this dataset. `patient`, `eye` and `visit` come from the filename —
  **144 subjects, 263 eyes, 1 to 7 visits each** — so a by-person split is possible and an eye can
  be followed through time.
- **Extra columns:** `visit_interval_years`, `iop` and `device` per visit; `age`, `sex`, `cct`,
  `total_visits` and `progression` per eye, from the baseline sheet.
- **Not built:** the annotated images, which are the crops with the contours already drawn on them;
  and the 52 visual-field point sensitivities per visit, which are not an image annotation. Both
  stay in the archives.

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
  that produces plausible-looking numbers. The crop can be recovered — it is published, and
  correlating it against its photograph finds it to better than 0.99 on every one of the 631 — but
  nothing in the archive states the offset.
- One annotator, so no human ceiling.
- The cohort is **not balanced across visits**: 67 eyes appear once and only two reach seven
  visits, so a longitudinal analysis has far less data than the 631 photographs suggest.
- The figshare files and the paper state different licences (section 2).

## 8. Notes

- Longitudinal data is what a biomarker ultimately has to justify itself against: a measurement that
  cannot track change in one patient is of limited clinical use however well it separates groups.
  This is the only entry here that would support that test.

---

**Links, licence and access last checked:** 2026-09-11
