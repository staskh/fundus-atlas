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

## 2. Provenance

Three provenances over one set of 45 photographs — the clearest case in this catalogue of why this
section repeats.

### 2.1 HRF — images, vessel gold standard, disc centres

| | |
| --- | --- |
| Home | <https://www5.cs.fau.de/research/data/fundus-images/> |
| Download | **direct, no registration** — `all.zip`, about 76 MB. The two experts' disc centres are a **separate 14 KB spreadsheet** listed well below the archives on the same page, in a legacy `.xls` format that modern spreadsheet libraries cannot read |
| Citation | Budai A, Bock R, Maier A, Hornegger J, Michelson G. *Robust Vessel Segmentation in Fundus Images.* International Journal of Biomedical Imaging 2013;2013:154860. DOI: [10.1155/2013/154860](https://doi.org/10.1155/2013/154860) |
| Licence | **CC BY 4.0** |
| Content | 45 images at 3504×2336 |
| Annotations | Supplies the photographs, a manual vessel gold standard, field-of-view masks, and **two independent experts' optic disc centres and diameters** |

### 2.2 HRF-AV — artery/vein reference standard

| | |
| --- | --- |
| Home | <https://github.com/rubenhx/av-segmentation> — the labels are in `HRF_AV_GT/`, about 7.6 MB |
| Download | **direct, no registration** — 45 PNGs from that repository |
| Citation | Hemelings R, Elen B, Stalmans I, Van Keer K, De Boever P, Blaschko MB. *Artery-vein segmentation in fundus images using a fully convolutional network.* Computerized Medical Imaging and Graphics 2019;76:101636. DOI: [10.1016/j.compmedimag.2019.05.004](https://doi.org/10.1016/j.compmedimag.2019.05.004) |
| Licence | **Not stated.** The repository carries no licence file. It is publicly downloadable and widely used, which is not the same as licensed — ask the authors before redistributing |
| Content | The same 45 photographs |
| Annotations | Supplies arteries and veins as separate classes. **This is the layer the artery/vein models in this catalogue train on** |

### 2.3 HRF-Seg+ — optic disc and cup contours

| | |
| --- | --- |
| Home | <https://zenodo.org/records/16744782> — DOI [10.5281/zenodo.16744782](https://doi.org/10.5281/zenodo.16744782) |
| Download | **direct, no registration** — `HRF-Seg+.zip`, about 3.4 MB |
| Citation | *HRF-Seg+: A Multi-Structure Annotated Fundus Image Dataset with Optic Disc, Cup, Vessels, Alpha and Beta Zones.* Zenodo, 2025. DOI: [10.5281/zenodo.16744782](https://doi.org/10.5281/zenodo.16744782) |
| Licence | As stated on the Zenodo record — check it there before reuse |
| Content | 40 of the same 45 photographs, plus a crop of each |
| Annotations | Supplies optic **disc and cup contours** — HRF itself gives only a disc centre — and alpha and beta zone annotations |

**One annotator, provenance unstated** for HRF-Seg+: the release ships no inter-observer data and does
not say who drew the contours.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 3504×2336 — the largest in this catalogue |
| Microns per pixel | Unknown — not published |
| Camera | Canon CR-1, non-mydriatic |
| Field of view | 45° |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

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

## 5. Inheritance

- **Reuses images from:** No shared images established — HRF is an original collection.
- **Its images are reused by:** HRF-AV and HRF-Seg+ annotate these same 45 photographs and are
  documented here as layers rather than as separate datasets. Both are widely cited under their own
  names, so a paper listing "HRF and HRF-AV" as two training sets has one camera's worth of images.

## 6. Use as a benchmark

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

## 7. Known defects

- The disc-centre spreadsheet is easy to miss on the download page and is in a format that requires
  a legacy reader.
- The disc **centre** from the original release and the disc **contour** from HRF-Seg+ do not always
  agree; anyone using both should measure the offset rather than assume they coincide.

## 8. Notes

- One set of 45 photographs annotated by three groups is the clearest example in this catalogue of
  why the inheritance question matters: HRF, HRF-AV and HRF-Seg+ are three citations, three
  downloads and three licence positions over the same pixels.

---

**Links, licence and access last checked:** 2026-09-11
