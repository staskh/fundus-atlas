# RIGA

750 photographs with the optic disc and cup outlined by **six ophthalmologists each** — the deepest
multi-reader annotation in this catalogue, three times [PAPILA](papila.md)'s two experts and the only realistic
way to measure what human disagreement on a cup boundary actually is. Its images come from three
sources, and 460 of them are [MESSIDOR](messidor.md) photographs.

## 1. What it is

- **Images:** 750 — BinRushed 195, Magrabia 95, MESSIDOR 460.
- **Collected at:** BinRushed Ophthalmic Center and Magrabi Eye Center, Saudi Arabia, plus the
  MESSIDOR photographs from France.
- **Purpose:** glaucoma analysis with per-annotator disc and cup boundaries.

## 2. Provenance

| | |
| --- | --- |
| Home | University of Michigan Deep Blue, DOI [10.7302/Z23R0R29](https://doi.org/10.7302/Z23R0R29) — [record](https://deepblue.lib.umich.edu/data/concern/data_sets/3b591905z) |
| Download | **direct, no registration** — the BinRushed, Magrabia and MESSIDOR archives from that page, about 13 GB together; Globus for the full deposit |
| Citation | Almazroa A, Alodhayb S, Osman E, Ramadan E, Hummadi M, Dlaim M, et al. *Retinal fundus images for glaucoma analysis: the RIGA dataset.* SPIE Medical Imaging 2018. DOI: [10.1117/12.2293584](https://doi.org/10.1117/12.2293584) |
| Licence | **CC BY-NC 4.0** — attribution, **non-commercial** |
| Content | 750 images from three sources |
| Annotations | Disc and cup outlines from **six ophthalmologists per image**, plus their cup-to-disc ratios |

**RIGA+** ([Zenodo record 6325549](https://zenodo.org/records/6325549)) is a repackaging of the same
annotations for domain-adaptation work, and it is the only copy a script can obtain — see section 2.1.
**It does not contain the photographs.** Its images are 800×800 **crops around the optic nerve**,
resized, with most of the field of view outside the frame; the ones where any field edge is visible
show a sliver of it. Anything measured in pixels on RIGA+ is measured on a crop of a resize, and
cannot be converted back. For vessel calibres, disc diameters in microns, fractal dimensions or any
other physical quantity, **the full-size photographs from Deep Blue are required** — RIGA+ cannot
substitute for them. What RIGA+ does support is disc and cup segmentation, which is what it was
assembled for.

The Deep Blue deposit **includes copies of the 460 MESSIDOR photographs**, which are also
distributed by ADCIS under stricter terms — so the same pixels arrive here under CC BY-NC and there
under a research-use agreement.

### 2.1 How to fetch

```bash
uv run python -m datasets.riga                          # builds RIGA+ — read the caveat first
uv run python -m datasets.riga --sizes 512,720,1024     # any sizes a model needs
```

**Read this before using the store.** The original deposit at Deep Blue answers an automated
request with a bot challenge, so a script cannot fetch it at all; a person with a browser can. The
fetcher therefore builds **RIGA+ from Zenodo**, and RIGA+ ships crops rather than photographs
(section 2). The store is usable for optic disc and cup work and **not** for anything in camera
pixels.

- **Downloads:** `RIGAPlus.zip`, 1.08 GB, from Zenodo. No account, no form. It is read where it
  lies rather than unpacked.
- **Builds:** 744 images with **twelve contours each** — disc and cup from all six ophthalmologists
  — in one `contours/<key>.csv` per image. Each published mask holds both structures: the cup is
  128 and the rim around it 255, so the disc is the two values together.
- **No field of view is looked for.** These are crops, so the frame is taken as it is and
  `fov_source` is `assumed_full_frame` on every row. Fitting a circle to the sliver of field edge
  that is sometimes in frame produced circles 36 and 13,646 pixels across on 800-pixel images.
- **Not built:** the unlabelled MESSIDOR photographs RIGA+ adds for domain adaptation, which carry
  no RIGA annotation and belong to MESSIDOR; and the repackagers' own train and test CSVs, which
  are their split rather than anything RIGA published.
- **Subsets:** `binrushed`, `magrabia` and `messidor`, with the folder inside each — `BinRushed1`,
  `MESSIDOR_Base2` — kept in a column of its own.
- **Counts:** 195 BinRushed and 95 Magrabia as published, but **454 MESSIDOR against the deposit's
  460** — RIGA+ carries six fewer, so the store holds 744 rather than 750.
- **Grouping:** none. No patient identity or laterality is published.

## 3. The images

Three subcollections, one per source.

### 3.1 BinRushed — 195 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated per source in the deposit |
| Microns per pixel | Unknown |
| Camera | Canon CR2, per the paper's description of the BinRushed centre |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

### 3.2 Magrabia — 95 images

| | |
| --- | --- |
| Resolution (pixels) | Not stated per source |
| Microns per pixel | Unknown |
| Camera | Topcon TRC-50DX, per the paper |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

### 3.3 MESSIDOR — 460 images

| | |
| --- | --- |
| Resolution (pixels) | MESSIDOR's natives — 1440×960, 2240×1488, 2304×1536 |
| Microns per pixel | Unknown |
| Camera | Topcon TRC NW6 |
| Field of view | 45° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Six ophthalmologists, kept separate** | Native | Outlines per annotator |
| Optic cup | **Six ophthalmologists, kept separate** | Native | Outlines per annotator |
| Other labels | Six | — | Each annotator's cup-to-disc ratio; RIGA+ adds domain splits |

## 5. Inheritance

- **Reuses images from:** **[MESSIDOR](messidor.md)** — 460 of its 750 photographs, unresized.
- **Its images are reused by:** None established.

[MAPLES-DR](maples-dr.md) annotates a *different* 198 MESSIDOR photographs — a sibling over the same
collection, not a derivative of this one.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established, though the MESSIDOR portion's
  photographs appear in [OCULARNet](../models/ocularnet.md)'s training data through MESSIDOR-AV.
- **Below a model's measuring grid:** No.
- **What it can answer:** the human agreement ceiling on disc and cup, six ways — the single most
  valuable property for judging whether a disc/cup model is as good as a person. Nothing else in
  this catalogue comes close.

## 7. Known defects

- **The original host cannot be fetched by a script.** Deep Blue answers an automated request with
  a Cloudflare challenge, whatever user agent it carries. The photographs have to be downloaded by
  hand in a browser.
- **RIGA+ is not a substitute for the photographs.** Its images are crops around the nerve head,
  800×800 and resized, so no pixel measurement on them relates to the eye. It carries six fewer
  MESSIDOR images than the deposit, 454 against 460.
- **RIGA+ states a more permissive licence than RIGA does** — CC BY 4.0 against CC BY-NC 4.0 — for
  the same annotations. The owner's terms are the ones that hold.

- The MESSIDOR overlap means a "RIGA and MESSIDOR" evaluation double-counts 460 photographs.
- Per-source resolution and camera details are thinner in the deposit than the paper implies; the
  values in section 3 come from the paper's description of the centres rather than per-image
  metadata.

## 8. Notes

- Six readers is the reason to reach for RIGA. Every automated disc or cup result in this catalogue
  is currently compared against one or two humans; this is the dataset that would say how much of
  the residual error is irreducible.

---

**Links, licence and access last checked:** 2026-09-11
