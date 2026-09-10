# REYIA

589 photographs with artery/vein annotation — **compiled from nine other datasets**, not collected.
That makes it the clearest case in this catalogue of why the inheritance question is asked: 153 of
its photographs are already here under their own names, so scoring REYIA and its sources counts the
same eyes twice.

What it genuinely adds is artery/vein colouring on photographs that had none — PAPILA has disc and
cup but no A/V, FIVES has binary vessels but no A/V — plus a new 111-image set.

## 1. What it is

- **Images:** 589 complete image-and-annotation sets (the paper reports 586).
- **Assembled from:** nine sources — [FIVES](fives.md) (75 photographs), [PAPILA](papila.md) (78),
  [MESSIDOR](messidor.md), MAGREBHIA, [mBRSET](mbrset.md), [GRAPE](grape.md), TREND-AV, a
  re-annotated AV-WIDE, and **ENRICH**, a new 111-image set appearing here first.
- **Purpose:** training data for a generative approach to vessel-segmentation generalisation.

## 2. Provenance

| | |
| --- | --- |
| Home | Kaggle, shared by link rather than published openly. The link-share URL is <https://www.kaggle.com/datasets/ba1b909c12dbe6c08df00b3ee6fc22d2fef632870359f91384b9001a870f67bf>, which is how a link-shared dataset is addressed; the canonical slug embedded in that page, <https://www.kaggle.com/datasets/fhimjo15/reyia-dataset>, returns 404 for an account that has not been granted access |
| Download | **no.** The dataset is private and link-shared: the Kaggle API answers 403 for an account without access, and the web endpoint wants a browser session rather than an API key. The archive has to be fetched by hand once |
| Citation | Fhima J, et al. *Enhancing Retinal Vessel Segmentation Generalization via Layout-Aware Generative Modelling.* [arXiv:2503.01190](https://arxiv.org/abs/2503.01190) |
| Licence | **MIT on the compilation**, as stated on the Kaggle record — but **each source keeps its own terms, and they are stricter**: mBRSET is PhysioNet-credentialed, MESSIDOR is research-only, [PAPILA](papila.md) is GPL-3.0. Anything redistributed from REYIA inherits the strictest of the nine |
| Content | 589 image-and-annotation sets (the paper reports 586), at nine sources' native sizes |
| Annotations | Artery/vein maps, and a source-dataset attribution per photograph |

Annotation was done with the same tool used for [Leuven-Haifa](leuven-haifa.md).

### 2.1 The one added source with its own publication

Five of the nine sources are catalogued here in their own right — [FIVES](fives.md),
[PAPILA](papila.md), [MESSIDOR](messidor.md), [mBRSET](mbrset.md) and [GRAPE](grape.md) — and their
provenance is on those pages. Of the remaining four, one has an original publication:

| | |
| --- | --- |
| Layer | **AV-WIDE**, 26 photographs |
| Home | The authors' own release, linked from the paper below; inside REYIA it arrives as part of the compilation |
| Download | **direct** from the authors for the original WIDE data; not separable from REYIA's archive |
| Citation | Estrada R, Allingham MJ, Mettu PS, Cousins SW, Tomasi C, Farsiu S. *Retinal artery-vein classification via topology estimation.* IEEE Transactions on Medical Imaging 2015;34(12):2518–2534. DOI: [10.1109/TMI.2015.2443117](https://doi.org/10.1109/TMI.2015.2443117) · [PMC4685460](https://pmc.ncbi.nlm.nih.gov/articles/PMC4685460/) |
| Licence | The authors state the wide-field images and ground-truth labels are freely available; no formal licence was established |
| Content | The original **WIDE** release is 30 ultra-wide-field images captured at 3900×3072 on an Optos 200Tx and analysed downsampled by two. REYIA carries 26 of them at 829×1531 |
| Annotations | Supplies artery/vein labels from **two independent raters**, the second — a fellowship-trained medical retina specialist — taken as ground truth |

Collected at Duke University Medical Center between 2010 and 2014, from healthy eyes and eyes with
age-related macular degeneration including geographic atrophy, drusen and fibrotic scarring.

### 2.2 The three added sources with no established publication

- **ENRICH** — 111 photographs from Belgium at 1958×2196, 45°. REYIA's own new contribution, with no
  separate dataset paper. The name matches the ERA-CVD project *Endothelial Retinal Imaging as
  Indicator of Cognitive Vascular Health*, which would fit the Belgian origin, but no publication
  tying that project to these images was established.
- **TREND-AV** — 48 photographs at 1444×1444, 45°, healthy eyes. **No describing publication and no
  independent distribution were found**; it appears in the literature only as a REYIA subset.
- **MAGREBHIA** — 69 photographs at 1444×1444, 30°, from North Africa, with glaucoma. Likewise no
  describing publication established. Note the near-collision with **Magrabia**, which is something
  else entirely: a 95-image Saudi subcollection of [RIGA](riga.md) from the Magrabi Eye Center.
  Sources listing REYIA's contents as including "Magrabia" most likely mean MAGREBHIA.

## 3. The images

Mixed by construction, so the subcollections are listed individually. Counts, resolutions, fields
and regions follow the tabulation published with the [OCULAR](../models/ocularnet.md) collection,
which redistributes these subsets under these names.

| Subcollection | Images | Resolution | Field | Region | Pathology | Source of the photographs |
| --- | --- | --- | --- | --- | --- | --- |
| ENRICH | 111 | 1958×2196 | 45° | Belgium | — | New in REYIA (section 2.2) |
| PAPILA subset | 78 | 1444×1444 | 30° | Spain | glaucoma | [PAPILA](papila.md) |
| FIVES-AV | 75 | 1444×1444 | 45° | China | — | [FIVES](fives.md) |
| MAGREBHIA | 69 | 1444×1444 | 30° | North Africa | glaucoma | None established (section 2.2) |
| MESSIDOR-AV | 66 | 1444×1444 | 45° | France | diabetic retinopathy | [MESSIDOR](messidor.md) |
| TREND-AV | 48 | 1444×1444 | 45° | Not stated | healthy | None established (section 2.2) |
| **AV-WIDE** | 26 | 829×1531 | **200°** | United States | AMD | Estrada et al. 2015 (section 2.1) |
| mBRSET and GRAPE subsets | the remainder | per source | per source | Brazil, China | mixed | [mBRSET](mbrset.md), [GRAPE](grape.md) |

Two things stand out. Most subsets arrive at **1444×1444** whatever their source camera produced, so
they are renditions rather than natives — resized copies of other people's photographs, and a
measurement in pixels is on REYIA's grid rather than the camera's. And **AV-WIDE is
ultra-wide-field at 200°**, a different instrument from everything else here: pooling it with 30–45°
photographs mixes fields of view by a factor of four or more.

| | |
| --- | --- |
| Microns per pixel | Unknown for every subcollection |
| Modality | Colour fundus photography, with AV-WIDE's ultra-wide-field images a separate case |

Annotation was done with the same tool used for [Leuven-Haifa](leuven-haifa.md).

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | One standard | Per-source native size | The dataset's contribution |
| Other labels | — | — | A source-dataset attribution per photograph, which is what makes the overlap traceable |

## 5. Inheritance

- **Reuses images from:** **[FIVES](fives.md) (75), [PAPILA](papila.md) (78),
  [MESSIDOR](messidor.md), MAGREBHIA, [mBRSET](mbrset.md), [GRAPE](grape.md), TREND-AV and a
  re-annotated AV-WIDE** — 478 of its 589 photographs come from elsewhere; only the 111-image ENRICH
  set is new. MAGREBHIA, TREND-AV, AV-WIDE and ENRICH have no pages of their own — they are documented as
  subcollections in sections 2.1, 2.2 and 3. No resizing was
  established, but each source arrives at its own native size. Note that
  [RITE](rite.md)/[DRIVE](drive.md) photographs also reach it through the MESSIDOR-era A/V
  collections it draws on.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established directly. But because its
  photographs come from datasets that *are* training data for several models here, a REYIA score is
  **partly in-sample for reasons that have nothing to do with REYIA** — which is exactly the trap
  the per-photograph source attribution exists to expose.
- **Below a model's measuring grid:** Mixed, by source.
- **What it can answer:** artery/vein accuracy across nine cameras at once, provided the overlapping
  153 photographs are excluded when its sources are also scored.

## 7. Known defects

- **Not downloadable programmatically** (section 2), which makes reproducible use awkward.
- The paper's count (586) and the archive's (589) disagree.
- 153 photographs duplicate other datasets in this catalogue; pooling without exclusion
  double-counts them.

## 8. Notes

- A compilation is not a camera. REYIA's value is breadth of appearance in one place, and its risk is
  that breadth looking like independence.

---

**Links, licence and access last checked:** 2026-09-11
