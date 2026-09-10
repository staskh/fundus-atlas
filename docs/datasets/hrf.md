# HRF (High-Resolution Fundus)

45 photographs at 3504×2336 — fifteen healthy, fifteen glaucomatous and fifteen with diabetic
retinopathy — and the most heavily re-annotated small dataset in this catalogue. Three separate
groups have published annotations on the *same* 45 images: the original vessel gold standard and
optic disc centres, an artery/vein reference standard, and a later release adding optic disc and cup
contours. That makes it one dataset with three papers, three downloads and three licence positions,
which is why sections 2 to 4 below are split per layer.

## 1. What it is

- **Images:** 45 — 15 healthy, 15 glaucoma, 15 diabetic retinopathy.
- **Collected at:** Friedrich-Alexander University Erlangen-Nürnberg, Germany.
- **Purpose:** a high-resolution vessel-segmentation benchmark, published with a robust vessel
  segmentation method.

## 2. Original publications

### 2.1 HRF — images, vessel gold standard, disc centres

- Budai A, Bock R, Maier A, Hornegger J, Michelson G. *Robust Vessel Segmentation in Fundus Images.*
  International Journal of Biomedical Imaging 2013;2013:154860. DOI:
  [10.1155/2013/154860](https://doi.org/10.1155/2013/154860)
- **Supplies:** the photographs, a manual vessel segmentation, field-of-view masks, and **two
  independent experts' optic disc centres and diameters**.

### 2.2 HRF-AV — artery/vein reference standard

- Hemelings R, Elen B, Stalmans I, Van Keer K, De Boever P, Blaschko MB. *Artery-vein segmentation in
  fundus images using a fully convolutional network.* Computerized Medical Imaging and Graphics
  2019;76:101636. DOI:
  [10.1016/j.compmedimag.2019.101636](https://doi.org/10.1016/j.compmedimag.2019.101636)
- **Supplies:** arteries and veins distinguished, on the same 45 photographs. This is the layer the
  artery/vein models in this catalogue train on.

### 2.3 HRF-Seg+ — optic disc and cup contours

- *HRF-Seg+: A Multi-Structure Annotated Fundus Image Dataset with Optic Disc, Cup, Vessels, Alpha
  and Beta Zones.* Zenodo, 2025. [Record 16744782](https://zenodo.org/records/16744782)
- **Supplies:** optic **disc and cup contours** — HRF itself gives only a disc centre — plus alpha
  and beta zone annotations, on 40 of the 45 photographs.

## 3. Access

### 3.1 HRF

- **Home:** <https://www5.cs.fau.de/research/data/fundus-images/>
- **Direct download:** **Yes** — unattended, no registration.
- **Arrives as:** `all.zip` (about 76 MB) with images, vessel masks and field-of-view masks. The two
  experts' disc centres are a **separate 14 KB spreadsheet** listed well below the archives on the
  same page, in legacy `.xls` format that modern spreadsheet libraries cannot read.

### 3.2 HRF-AV

- **Direct download:** **Yes** — 45 PNGs, published on GitHub by the authors.

### 3.3 HRF-Seg+

- **Direct download:** **Yes** — from Zenodo, about 3.4 MB.

## 4. Licence

### 4.1 HRF

- **Images and original annotations:** **CC BY 4.0.**

### 4.2 HRF-AV

- **Annotations:** Unknown — no licence statement was established for the artery/vein layer. It is
  publicly downloadable and widely used, which is not the same as licensed; ask the authors before
  redistributing.

### 4.3 HRF-Seg+

- **Annotations:** as stated on its Zenodo record. Check the record before reuse.

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | 3504×2336 — the largest in this catalogue |
| Microns per pixel | Unknown — not published |
| Camera | Canon CR-1, non-mydriatic |
| Field of view | 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | One gold standard | Native | From the original release |
| Artery/vein | One | Native | HRF-AV, section 2.2 |
| Optic disc centre | **Two independent experts**, kept separate | Native | Centre and diameter, not a contour |
| Optic disc and cup contours | One | Native | HRF-Seg+, 40 of 45 images |
| Disease | One label per eye | — | Healthy / glaucoma / diabetic retinopathy, 15 each |
| Field-of-view mask | — | Native | Supplied per image |

The two experts' disc centres are the useful rarity here: they sit a median of about 10 pixels apart
on a disc roughly 379 pixels across — under 3% of a disc diameter — which gives a human agreement
figure to read automated disc results against, rather than assuming one.

## 7. Inheritance

- **Reuses images from:** No shared images established — HRF is an original collection.
- **Its images are reused by:** HRF-AV and HRF-Seg+ annotate these same 45 photographs and are
  documented here as layers rather than as separate datasets. Both are widely cited under their own
  names, so a paper listing "HRF and HRF-AV" as two training sets has one camera's worth of images.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** [SEGAN vessel segmenter](../models/segan-vessel.md)
  (as part of `ALL-SIX`), [BF-Net](../models/bf-net.md) and [Big W-Net](../models/big-wnet.md) (via
  HRF-AV), [LWNet](../models/lwnet.md), [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md), and [LUNet](../models/lunet.md) uses a cropped HRF
  as external test data. **A score on HRF is in-sample for almost every vessel and artery/vein model
  in this catalogue.**
- **Below a model's measuring grid:** No — far above it, so it is downsampled heavily before
  measurement.
- **What it can answer:** what human disagreement on the optic disc looks like; how a model behaves
  at high resolution. It cannot answer generalisation for any of the models above.

## 9. Known defects

- The disc-centre spreadsheet is easy to miss on the download page and is in a format that requires
  a legacy reader.
- The disc **centre** from the original release and the disc **contour** from HRF-Seg+ do not always
  agree; anyone using both should measure the offset rather than assume they coincide.

## 10. Notes

- One set of 45 photographs annotated by three groups is the clearest example in this catalogue of
  why the inheritance question matters: HRF, HRF-AV and HRF-Seg+ are three citations, three
  downloads and three licence positions over the same pixels.

---

**Links, licence and access last checked:** 2026-09-11
