# AVRDB

100 photographs from the Armed Forces Institute of Ophthalmology in Pakistan, whose arteries and
veins were drawn by four ophthalmologists, under **CC BY 4.0**.

The paper describes more: an arteriovenous ratio per image — which would be the check for
[calibre biomarkers](../biomarkers/avr.md) that [ORIGA](origa.md) provides for the cup-to-disc
ratio — plus the optic nerve head, hard exudates, cotton-wool spots and disease labels. **None of
that is in the deposit**, which holds the artery/vein drawings and nothing else (section 7).

## 1. What it is

- **Images:** 100, annotated by four expert ophthalmologists.
- **Collected at:** Armed Forces Institute of Ophthalmology (AFIO), Rawalpindi, Pakistan.
- **Purpose:** hypertensive-retinopathy assessment, where the artery-to-vein ratio is the measurement
  of clinical interest.

## 2. Provenance

| | |
| --- | --- |
| Home | Mendeley Data, DOI [10.17632/3csr652p9y.2](https://doi.org/10.17632/3csr652p9y.2) — [record](https://data.mendeley.com/datasets/3csr652p9y/2). Historically distributed through the [BIOMISA](http://biomisa.org/index.php/dataset-for-hypertensive-retinopathy/) page, which is where most citations still point and which has been unreliable |
| Download | **direct, no registration** — one archive of about 201 MB, served over Mendeley's public API with no account and no request form |
| Citation | Akram MU, Akbar S, Hassan T, Khawaja SG, Yasin U, Basit I. *Data on fundus images for vessels segmentation, detection of hypertensive retinopathy, diabetic retinopathy and papilledema.* Data in Brief 2020;29:105282. DOI: [10.1016/j.dib.2020.105282](https://doi.org/10.1016/j.dib.2020.105282) |
| Licence | **CC BY 4.0** on the Mendeley deposit — attribution only, commercial use permitted. The older BIOMISA page offered only "for the research community", which grants nothing |
| Content | 100 images at 1504×1000 |
| Annotations | Vessel network, artery/vein network, optic nerve head, **a published arteriovenous ratio per image**, hard exudates, cotton-wool spots, hypertensive retinopathy and papilloedema labels |

**Searching for "AVRDB" will not find it.** The deposit is titled after the paper — *Data on Fundus
Images for Vessels Segmentation, Detection of Hypertensive Retinopathy, Diabetic Retinopathy and
Papilledema* — and its description names the AFIO source, the four ophthalmologists and the AVR.

### 2.1 How to fetch

```bash
uv run python -m datasets.avrdb                      # downloads and builds 512 and 1024
uv run python -m datasets.fetch_um_resolution --dataset avrdb
```

One 201 MB zip from Mendeley's public API, unattended. It builds 100 photographs with three binary
masks each at native resolution — `artery`, `vein` and `vessels` — read from the drawings the
ophthalmologists made on white pages. The drawings are JPEG, so every stroke carries a halo of
compression; anything far enough from white counts as ink, and moving that threshold from 40 to 90
changes the annotated area by about 3%.

**Crossings are in both the artery and the vein mask**, about 1,000 to 5,000 pixels an image,
because that is how the dataset itself drew them.

The authors publish no scale and the Topcon TRC-NW8's field angle is selectable and unstated, so
the second command is **required** to finish the store: 13.320 µm/px, from the median optic disc.

Three things about the archive a person running this will meet, all handled by the fetcher:

- **The suffix is misspelled on seven of the hundred folders** — `--artery`, `--artry`,
  `--atertries`, `--vein`, `--veisn`, `--veinds` — and one folder files a drawing under a different
  photograph's id. The fetcher matches a suffix by what it most resembles rather than composing the
  name it expects; composing it reports a dataset with holes in it and no error.
- **`--both` and `--map` are not annotations.** They are the photograph with the vessels painted
  over it, and they are skipped, as is the `.ai` file the drawings were made in.
- **Searching Mendeley for "AVRDB" finds nothing** — the deposit is titled after the paper.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1504×1000 |
| Microns per pixel | Not published. **Inferred: 13.320 µm/px** — from the median optic disc of 32 photographs, [evidence](../../results/um_resolution/avrdb.json). Good to roughly a tenth (§9 of the `fetch-um-resolution` skill); a camera scale, not a per-eye calibration |
| Camera | Topcon TRC-NW8 |
| Field of view | Not stated by the authors |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Four ophthalmologists contributed; how many marked each image is not stated | Native | Vessel network. **Measured here, it is the artery and vein drawings put together**: it agrees with their union to within 0.4–0.6% on every photograph checked, so it is not independent evidence (section 7) |
| Artery/vein | As above | Native | A/V network |
| Optic nerve head | As above | Native | On the same photographs |
| Disease | One label per image | — | Hypertensive retinopathy and papilloedema |
| Other labels | — | — | **A published arteriovenous ratio per image**, plus hard exudates and cotton-wool spots |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list AVRDB in their training data. Held out of the
  AutoMorph family and of [LUNet](../models/lunet.md).
- **Below a model's measuring grid:** No.
- **What it can answer:** the one thing nothing else here can — whether a pipeline's computed
  [AVR](../biomarkers/avr.md) agrees with a clinician's published AVR on the same eye, on
  hypertensive retinopathy, under a permissive licence.

## 7. Known defects

- **The deposit holds only the artery/vein drawings.** *Our finding, 2026-09-17, from both versions
  of the Mendeley record:* it contains one zip of a hundred folders, each with the photograph, three
  drawings, an overlay and the Illustrator file. **The arteriovenous ratio per image is not in it**,
  and neither are the optic nerve head annotation, the hard exudates, the cotton-wool spots, or the
  hypertensive-retinopathy and papilloedema labels the paper describes. Those were presumably on the
  BIOMISA page, which no longer serves them. Anyone citing this dataset for its AVR should say where
  they obtained the numbers, because this route does not carry them.
- **The vessel drawing is not independent of the artery and vein drawings.** *Our finding:* it
  agrees with their union to within 0.4–0.6% on every photograph checked. A model scored against
  both the A/V masks and the vessel mask has been scored twice against one annotation.
- **The suffix is misspelled on seven of the hundred folders**, in six different ways — `--artery`,
  `--artry`, `--atertries`, `--vein`, `--veisn`, `--veinds` — and `IM000168` holds a drawing named
  for a different photograph. *Our finding:* a fetcher composing the expected filename silently
  loses those seven, which is why this one matches by resemblance.
- **Reader structure unknown.** Four ophthalmologists annotated the set, but whether their marks ship
  separately or as one consensus was not established from the record, so it cannot yet be said
  whether a human agreement ceiling is available. Nothing in the deposit distinguishes them.
- The widely cited BIOMISA link is unreliable; use the Mendeley DOI.

## 8. Notes

- Of everything in this catalogue, this is the dataset that *would* be most directly useful for
  checking a **biomarker** rather than a mask: a published AVR is a number a human committed to, and
  calibre pipelines have nothing else to be measured against. **But the AVR is not in the deposit**
  (section 7), so until somebody obtains it the dataset is an artery/vein segmentation set like the
  others — a good one, permissively licensed, and in-sample for
  [OCULARNet](../models/ocularnet.md).

---

**Links, licence and access last checked:** 2026-09-17
